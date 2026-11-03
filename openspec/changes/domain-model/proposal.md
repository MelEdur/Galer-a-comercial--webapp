# Propuesta

## Why

Los diez casos de uso oficiales del sistema (búsqueda de productos, feed, detalle de producto, información y mapa de locales, cuentas de comerciantes y administradores, catálogo, información del local y estadísticas de búsqueda) dependen de una estructura de datos que todavía no existe: la base está vacía y no hay ninguna revisión de Alembic. Sin un modelo de dominio explícito e íntegro, cada caso de uso correría el riesgo de inventar entidades, duplicar datos o fijar decisiones incompatibles entre sí.

Este cambio define y materializa únicamente el modelo de dominio y el esquema de datos que da soporte a los diez casos de uso. No implementa ninguno de ellos.

## What Changes

- Se crea la capability `domain-model` con el contrato de datos del sistema.
- Se añaden nueve tablas: `users`, `stores`, `store_hours`, `store_links`, `categories`, `products`, `product_categories`, `product_images` y `product_search_events`.
- Se modelan los 21 locales fijos de la galería mediante `stores.number`, `stores.side` y `stores.position`, con numeración intercalada: impares a la derecha (`1, 3, … 19`), pares a la izquierda (`2, 4, … 20`) y `21` al fondo.
- Se modelan las cuentas con roles `admin` y `merchant`: el comerciante exige un local asignado y cada local admite un solo comerciante; el administrador no tiene local.
- Se modelan productos pertenecientes a un local, con categorías globales en relación muchos-a-muchos, imágenes ordenadas con una sola primaria, precio en pesos argentinos y un precio de oferta opcional menor al precio.
- Se modelan horarios de atención por día y tramo, y enlaces externos del local.
- Se registran eventos de búsqueda por producto para poder calcular los productos más buscados en un lapso de tiempo.
- Se crea la primera revisión de Alembic, reversible, que materializa el esquema.
- Se crea un script idempotente que precarga los 21 locales con nombre provisional.
- Se añaden pruebas automatizadas de integridad y restricciones del modelo.

### Alcance

- Estructura de datos, modelos SQLAlchemy 2.0, migración inicial y semilla de locales.
- Restricciones e invariantes verificadas en la base de datos.
- Pruebas de persistencia y de restricciones.
- Documentación del modelo en el diseño del cambio.

### Fuera de alcance

- Endpoints, contratos HTTP, autenticación y autorización.
- Pantallas, componentes o llamadas del frontend.
- Algoritmos de búsqueda, feed, mapa o estadísticas: solo se prepara el dato que los soporta.
- Gestión de archivos o subida de imágenes: se almacenan URLs.
- Stock, reseñas, favoritos, multi-moneda, multi-sucursal, jerarquía de categorías, promociones con vigencia y auditoría de cambios.
- Datos reales de los locales (nombre definitivo, logo, contacto, horarios): se cargan en los casos de uso posteriores.

## Capabilities

### New Capabilities

- `domain-model`: estructura persistente del dominio, relaciones y cardinalidades, restricciones de integridad, soporte de estadísticas de búsqueda, precarga de locales y migración inicial.

### Modified Capabilities

Ninguna. Las capabilities existentes (`backend-foundation`, `frontend-foundation`, `local-environment`) describen la base técnica y no cambian su comportamiento.

## Impact

- **Código nuevo:** `backend/app/modules/accounts/`, `backend/app/modules/stores/`, `backend/app/modules/catalog/`, `backend/app/modules/analytics/`, `backend/app/db/registry.py` y `backend/scripts/seed_stores.py`.
- **Código modificado:** `backend/app/db/base.py` (registro de metadata) y `backend/alembic/env.py` si requiere ajuste.
- **Base de datos:** primera revisión de Alembic con nueve tablas, índices y restricciones.
- **Dependencias:** ninguna nueva.
- **API:** sin cambios.
- **Frontend:** sin cambios.
- **Funcionalidades existentes:** el endpoint `GET /api/health` y el arranque del backend no se ven afectados; las migraciones siguen siendo explícitas.
- **Dependencias futuras:** todos los casos de uso de visitante, administrador y comerciante se apoyarán en este esquema.

## Decisiones adoptadas

- Moneda única: pesos argentinos (ARS), sin columna de moneda.
- Zona horaria `America/Argentina/Buenos_Aires`; timestamps de auditoría en UTC.
- Ubicación por `side` y `position`, sin tabla de planos ni coordenadas.
- 21 locales precargados por script idempotente, no por migración.
- Categorías globales con relación muchos-a-muchos.
- Un comerciante por local.
- Borrado lógico de productos y desactivación de usuarios.
- Estadísticas a partir de eventos crudos de búsqueda por producto.
