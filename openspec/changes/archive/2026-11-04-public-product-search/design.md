# Diseño

## Context

Ver `proposal.md` para la motivación y `specs/product-search/spec.md` para los requisitos. El catálogo privado del CU #8 ya resuelve listado, filtros y paginación por local; este cambio añade una vista pública sin autenticación. La tabla `product_search_events` existe y la spec de `domain-model` ya exige registrarla.

## Goals / Non-Goals

**Goals:**

- Búsqueda pública simple, rápida y combinable.
- Reutilizar el esquema existente sin migraciones.
- Dejar datos de búsqueda para CU #10.

**Non-Goals:**

- Feed, detalle, mapa, favoritos o autenticación.
- Búsqueda difusa, por descripción o normalización de acentos.
- Agrupar productos por nombre.

## Decisions

### 1. Endpoints públicos

- `GET /api/public/products`
- `GET /api/public/categories`

Router con prefijo `/public`, sin dependencias de autenticación. Se registra en `app/main.py`.

### 2. Consulta de productos

Condiciones base:

- `Product.deleted_at IS NULL`
- `Product.is_active IS TRUE`
- `Store.is_active IS TRUE` mediante `join(Store)`

Filtros opcionales:

- `search`: `ILIKE` sobre `name`, con `%` y `_` escapados.
- `category_id`: `EXISTS` sobre `product_categories`.
- `min_price` / `max_price`: sobre `coalesce(Product.offer_price, Product.price)`, inclusivos.

Todos los filtros se combinan con AND.

### 3. Precio efectivo

Se define `effective_price = coalesce(offer_price, price)` y se usa tanto para el filtro como para el orden por precio. La respuesta incluye `price`, `offer_price` y `effective_price`. Así el visitante ve y filtra por lo que realmente paga.

### 4. Orden y paginación

- `sort=name` (por defecto): `lower(name), id`.
- `sort=price_asc`: precio efectivo ascendente, luego nombre.
- `sort=price_desc`: precio efectivo descendente, luego nombre.
- `page >= 1`, `page_size` 1..100, por defecto 20.
- Conteo y elementos con los mismos filtros.
- Respuesta: `items`, `total`, `page`, `page_size`, `pages`.

### 5. Resultado

Cada elemento incluye:

- `id`, `name`, `description`;
- `price`, `offer_price`, `effective_price`;
- `categories` (`id`, `name`);
- `primary_image` (`url`, `alt_text`) o `null`;
- `store` (`id`, `number`, `name`).

No se incluye `store_id`, `is_active` ni `deleted_at`.

### 6. Categorías

`GET /api/public/categories` devuelve todas las categorías ordenadas por nombre. No se filtran por disponibilidad para que el selector sea estable.

### 7. Eventos de búsqueda

- Se consideran criterios `search`, `category_id`, `min_price` o `max_price`.
- Si no hay ningún criterio, no se registra nada (exploración).
- Si hay criterios y la página tiene productos, se insertan eventos en bloque con `product_id`, `query` (el término o `null`) y `searched_at = now()`.
- Si la página está vacía, no se insertan eventos.
- El registro ocurre después de leer la página y dentro de la misma transacción del request.

Alternativa descartada: registrar todos los productos que coinciden, aunque no estén en la página; infla el conteo con productos que el visitante no vio.

### 8. Rendimiento

- `IX` existentes: `products.store_id`, `products.price`, `products_name_lower`, `product_categories.category_id`.
- El `ILIKE '%texto%'` no aprovecha el btree de nombre; con el volumen actual (21 locales) es aceptable. Un índice trigram se evaluará cuando el catálogo crezca.
- El conteo y la página se ejecutan en dos consultas con los mismos filtros.
- Las relaciones se cargan con `selectinload`; la imagen primaria se obtiene de las imágenes ya cargadas para evitar N+1.

### 9. Frontend

- Página pública `/buscar` con estado en la URL: `search`, `category`, `min_price`, `max_price`, `sort`, `page`.
- Búsqueda con debounce de 300 ms.
- Tarjetas con imagen primaria (o marcador), nombre, descripción, precio, oferta, categorías y local.
- Sin enlace a detalle de producto; las tarjetas no navegan.
- Paginación anterior/siguiente y estados de carga, vacío y error.
- Enlace "Buscar productos" desde la página de inicio.

## Risks / Trade-offs

- **Búsqueda con `ILIKE`** → suficiente para el volumen actual; se optimizará con trigram si crece.
- **Eventos por página** → las páginas repetidas cuentan varias veces; es el comportamiento acordado y mide lo que el visitante vio.
- **Sin normalización de acentos** → "cafe" no encuentra "Café"; se documenta como mejora futura.
- **Exploración sin filtros** → comparte territorio con el feed de CU #2, pero aquí es una lista paginada sin curación.
- **Productos duplicados por local** → el mismo nombre en dos locales aparece dos veces; es coherente con el modelo.

## Migration Plan

No hay cambios de esquema ni datos iniciales. Se despliega el backend público y luego la página `/buscar`.

Rollback: retirar el router público y la ruta del frontend; no hay datos que migrar. Los eventos registrados pueden conservarse.

## Open Questions

Ninguna que afecte al esquema o al alcance. La búsqueda difusa, la normalización de acentos y el índice trigram quedan para cambios posteriores.
