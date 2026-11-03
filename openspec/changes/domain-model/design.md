# Diseño

## Context

El proyecto cuenta con la fundación técnica (FastAPI, SQLAlchemy 2.0 síncrono con `Session` por request, Alembic, PostgreSQL, Docker) pero no tiene ningún modelo de dominio ni revisión de Alembic. Ver `proposal.md` para la motivación y `specs/domain-model/spec.md` para los requisitos.

Restricciones relevantes:

- Modelo relacional en PostgreSQL; SQLAlchemy 2.0 con `Mapped`/`mapped_column`.
- Sesión síncrona y migraciones explícitas; el arranque no crea tablas.
- 21 locales fijos, preexistentes, con numeración intercalada.
- Moneda única: pesos argentinos (ARS).
- Zona horaria de la galería: `America/Argentina/Buenos_Aires`.
- Alcance limitado a datos: sin endpoints ni frontend.

## Goals / Non-Goals

**Goals:**

- Dejar un esquema íntegro que soporte los diez casos de uso sin cambios estructurales previsibles.
- Concentrar las reglas importantes en restricciones de base de datos, no solo en la aplicación.
- Mantener el modelo simple: nueve tablas, sin jerarquías ni abstracciones innecesarias.
- Permitir estadísticas históricas sin depender del estado actual del producto.

**Non-Goals:**

- Diseñar contratos HTTP o DTOs de respuesta.
- Resolver autenticación, sesiones o hash de contraseñas (solo se reserva la columna).
- Implementar búsqueda, feed, mapa o reportes.
- Gestionar archivos de imagen.
- Modelar stock, promociones con vigencia, reseñas o favoritos.

## Decisions

### 1. Ubicación por lado y posición, sin tabla de planos

`stores.side` (`left`, `right`, `back`) y `stores.position` describen el pasillo regular. La restricción `(side IN ('left','right') AND position BETWEEN 1 AND 10) OR (side = 'back' AND position = 1)` y el `UNIQUE (side, position)` garantizan los 21 espacios.

Alternativas descartadas:

- `floor_plans` con imagen y coordenadas `map_x`/`map_y`: aporta flexibilidad que el plano fijo no necesita y añade una tabla y dos columnas.
- Coordenadas y lado/posición a la vez: dos fuentes de verdad para el mismo dato.

### 2. Numeración intercalada resuelta en la semilla

La base solo exige unicidad. La correspondencia derecha→impares, izquierda→pares, fondo→21 se aplica en el script de precarga, que es idempotente. Así se evita una regla artificial en el esquema y se puede corregir la numeración sin migración.

### 3. Un comerciante por local mediante índice único parcial

`UNIQUE (store_id) WHERE role = 'merchant'` expresa la cardinalidad en PostgreSQL. Se complementa con un `CHECK` que obliga a `store_id` para `merchant` y lo prohíbe para `admin`.

Alternativa descartada: tabla `store_merchants`. Permitiría varios comerciantes, pero la decisión aprobada es uno por local y una tabla intermedia añadiría complejidad sin uso.

### 4. Categorías globales muchos-a-muchos

`product_categories (product_id, category_id)` con PK compuesta. Responde a "categoría" como dimensión transversal del catálogo y permite que un producto aparezca en varias.

Alternativas descartadas: `category_id` en `products` (uno a muchos, descartado por la decisión aprobada); categorías por local (fragmenta la exploración del feed).

### 5. Dinero y tiempo

- `numeric(10,2)` para `price` y `offer_price`; sin columna de moneda porque ARS es la única moneda del sistema.
- `timestamptz` en UTC para auditoría y eventos.
- `time` sin zona para horarios, interpretados en `America/Argentina/Buenos_Aires` por configuración.

Alternativas descartadas: `float` (error de redondeo), columna `currency` (dato constante), `timestamp` sin zona (ambigüedad en cambios de horario).

### 6. Borrado lógico y acciones referenciales explícitas

- `products.deleted_at` + `is_active`: conserva el producto para estadísticas y permite ocultarlo.
- `users.is_active`: CU #6 elimina comerciantes, pero las cuentas no se borran físicamente.
- `stores`: `ON DELETE RESTRICT` desde productos y usuarios; un local con datos no desaparece.
- `product_images`, `store_hours`, `store_links`: `ON DELETE CASCADE` porque dependen del padre.
- `product_categories`: cascada desde producto; restricción desde categoría.
- `product_search_events`: `ON DELETE RESTRICT`; como los productos no se borran físicamente, el histórico se mantiene.

### 7. Estadísticas con eventos crudos

Una fila de `product_search_events` por producto devuelto, con `query` y `searched_at`. Índices `(product_id, searched_at)` y `(searched_at)` para los reportes por producto y por rango.

Alternativas descartadas:

- Registrar solo términos: impide el ranking por producto.
- Registrar aperturas de detalle: mide interés, no búsqueda, y no responde a CU #10.
- Agregado diario desde el inicio: optimización prematura; se puede añadir después sin cambiar el contrato.

### 8. Organización por módulos

- `app/modules/accounts/models.py`: `User`.
- `app/modules/stores/models.py`: `Store`, `StoreHour`, `StoreLink`.
- `app/modules/catalog/models.py`: `Category`, `Product`, `ProductCategory`, `ProductImage`.
- `app/modules/analytics/models.py`: `ProductSearchEvent`.
- `app/db/registry.py`: importa los modelos para registrar la metadata que consume Alembic.
- `app/db/base.py`: mantiene `Base` y no importa modelos, evitando ciclos.

### 9. Restricciones nombradas y verificables

Todas las restricciones e índices llevan nombre explícito (`ck_`, `uq_`, `ix_`, `fk_`) para que Alembic genere migraciones estables y las pruebas puedan referenciarlas.

### 10. Semilla idempotente fuera de las migraciones

`backend/scripts/seed_stores.py` inserta los 21 locales si no existen, usando `number` como clave natural. Las migraciones quedan dedicadas al esquema. Los nombres son provisionales (`Local N`) y se completan en CU #9.

## Risks / Trade-offs

- **Crecimiento de `product_search_events`** → índices por fecha y posibilidad de agregación diaria o purga en un cambio posterior.
- **Productos con borrado lógico pueden aparecer en consultas** → todas las consultas de catálogo deberán filtrar `deleted_at IS NULL`; se documenta en la spec y se prueba.
- **Nombres provisionales en la semilla** → visibles hasta que el comerciante edite su local; aceptado porque los datos reales no existen todavía.
- **Email único administrado en la aplicación** → se normaliza a minúsculas al escribir y se respalda con un índice único sobre `lower(email)`.
- **Zona horaria fija** → si la galería cambiara de zona, se ajusta configuración, no el esquema.
- **Regla de un comerciante por local** → si el negocio necesitara varios, requiere migración y cambio de spec; es una decisión explícita del usuario.

## Migration Plan

1. Crear los modelos y el registro de metadata.
2. Generar y revisar la revisión `0001_domain_model`.
3. Ejecutar `alembic upgrade head` en desarrollo y en `app_test`.
4. Ejecutar la semilla de locales.
5. Verificar con `alembic downgrade base` y volver a aplicar.

Rollback: `alembic downgrade base` elimina las nueve tablas. Al ser un esquema nuevo, no hay datos productivos que preservar.

## Open Questions

Ninguna que afecte al esquema, al enfoque o al desglose de tareas. La retención de eventos y la estrategia de búsqueda textual se resolverán en los cambios de CU #1 y CU #10.
