# Propuesta

## Why

El CU #8 pide que el comerciante cree, modifique y elimine los productos de su local. El modelo de dominio ya contiene `products`, `product_categories` y `product_images`, y el CU #7 dejó al comerciante autenticado con su local en la sesión, pero no existe ningún endpoint, servicio ni pantalla para administrar el catálogo. Además, la base no tiene categorías, por lo que tampoco es posible clasificar productos todavía.

Este cambio implementa exclusivamente la administración del catálogo propio del comerciante, sin exponer búsqueda, feed ni detalle público.

## What Changes

- Se añade la dependencia `require_merchant` para rutas exclusivas del comerciante.
- Se implementan endpoints para listar, consultar, crear, modificar y eliminar productos del local autenticado.
- La propiedad del producto se deriva siempre del local del token; ningún payload acepta `store_id`.
- Se implementa listado con búsqueda por nombre, filtro por estado (vigentes, eliminados, todos), filtro por categoría y paginación.
- Se implementa el alta y la edición con nombre, descripción, precio, precio de oferta, categorías e imágenes por URL.
- Se implementa la baja lógica, idempotente, conservando datos e imágenes.
- Se implementa la restauración de un producto eliminado, devolviéndolo al estado vigente.
- Se añade un endpoint de categorías de solo lectura y una semilla idempotente con diez categorías iniciales.
- Se añade al frontend la ruta protegida `/comerciante/productos` con listado, filtros, paginación, alta, edición y baja.
- Se activa el acceso a Productos desde el panel del comerciante.
- Se añaden pruebas de backend y frontend, incluyendo aislamiento entre locales.

### Alcance

- CRUD del catálogo propio del comerciante.
- Categorías globales de solo lectura y semilla inicial.
- Imágenes por URL, sin subida de archivos.
- Precio de oferta gestionado por el comerciante.
- Baja lógica, restauración y filtros de estado.

### Fuera de alcance

- Búsqueda pública, feed y detalle público (CU #1, #2 y #3).
- Edición de la información del local (CU #9) y estadísticas (CU #10).
- Productos destacados (`is_featured`): pertenecen a la curación del feed.
- Gestión completa de categorías (crear, editar, eliminar).
- Subida de archivos, stock, variantes, multi-moneda y auditoría de cambios.

## Capabilities

### New Capabilities

- `merchant-product-catalog`: consulta paginada del catálogo propio, alta, edición, baja lógica, restauración, categorías, imágenes, validaciones y control de propiedad por local.

### Modified Capabilities

- `merchant-portal`: el panel del comerciante deja de mostrar Productos como funcionalidad no disponible y enlaza al catálogo.

## Impact

- **Backend nuevo:** `app/modules/merchant_catalog/` (schemas, servicio, router), `app/modules/auth/dependencies.py` (`require_merchant`), `scripts/seed_categories.py`.
- **Backend modificado:** `app/main.py` (router del catálogo) y pruebas.
- **Frontend nuevo:** `features/merchant-catalog/` (tipos, API, listado, formulario, filtros, paginación) y rutas de alta/edición.
- **Frontend modificado:** `app/router.tsx`, `pages/MerchantPage.tsx` y pruebas.
- **Migraciones:** ninguna; el esquema existente ya soporta el cambio.
- **Dependencias nuevas:** ninguna.
- **API:** `GET/POST /api/merchant/products`, `GET/PATCH/DELETE /api/merchant/products/{id}` y `GET /api/merchant/categories`.
- **Funcionalidades existentes:** CU #6, CU #7, autenticación y health check no cambian de comportamiento.
- **Dependencias:** `domain-model`, `admin-authentication`, `merchant-administration` y `merchant-portal`.

## Decisiones adoptadas

- Obligatorios: nombre, precio y al menos una categoría; descripción e imágenes opcionales.
- Categorías globales de solo lectura, con semilla de diez categorías.
- Imágenes opcionales por URL, máximo cinco, primera primaria.
- Baja lógica idempotente y restauración idempotente desde el catálogo.
- Precio de oferta editable y menor que el precio; `is_featured` fuera de alcance.
- Listado con búsqueda por nombre, estado y categoría, más paginación.
- `store_id` prohibido en los payloads; la propiedad sale del token.
- Producto de otro local se trata como inexistente (`404`).
