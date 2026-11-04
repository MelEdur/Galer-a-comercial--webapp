# Diseño

## Context

Ver `proposal.md` para la motivación y `specs/merchant-product-catalog/spec.md` para los requisitos. El esquema ya contiene `products`, `categories`, `product_categories` y `product_images`; no hay endpoints de catálogo ni categorías, la base tiene cero categorías y `require_merchant` todavía no existe. El comerciante autenticado tiene `store_id` en su cuenta y en `/auth/me`.

## Goals / Non-Goals

**Goals:**

- CRUD del catálogo propio con propiedad derivada del token.
- Listado útil con búsqueda, filtros y paginación.
- Categorías e imágenes manejadas con el esquema existente.
- Sin migraciones ni dependencias nuevas.

**Non-Goals:**

- Búsqueda, feed o detalle público.
- CRUD de categorías.
- Subida de archivos, stock o variantes.

## Decisions

### 1. `require_merchant`

Se añade a `app/modules/auth/dependencies.py`:

- token ausente o inválido → `401`;
- rol distinto de `merchant` → `403`;
- comerciante sin local → `403`;
- devuelve el `User` autenticado.

Toda la lógica de propiedad usa `current_user.store_id`. El `store_id` nunca se lee del cuerpo.

### 2. Propiedad y aislamiento

Las consultas filtran siempre por `Product.store_id == current_user.store_id`. Un producto de otro local se trata como inexistente (`404`) para no filtrar su existencia. Los schemas de entrada usan `extra="forbid"`, de modo que enviar `store_id` u otro campo desconocido devuelve `422`.

### 3. Estado del producto

- Vigente: `deleted_at IS NULL`.
- Eliminado: `deleted_at IS NOT NULL`.
- La baja fija `deleted_at = now()` e `is_active = False`.
- `is_active` no se expone como interruptor en este CU; queda reservado para una futura pausa de visibilidad.
- El filtro `status` acepta `active` (por defecto), `deleted` y `all`.
- La baja es idempotente: repetirla devuelve `204`.
- La restauración se expone en `POST /api/merchant/products/{product_id}/restore`, fija `deleted_at = NULL` e `is_active = True`; es idempotente (`200` si ya está vigente) y conserva categorías e imágenes.

### 4. Listado, búsqueda y paginación

`GET /api/merchant/products` acepta `search`, `status`, `category_id`, `page` y `page_size`.

- `search` aplica `ILIKE` sobre `name`, escapando `%` y `_`.
- `category_id` se resuelve con un `EXISTS` sobre `product_categories`.
- `page >= 1`; `page_size` entre 1 y 100, por defecto 20.
- Se ejecutan una consulta de conteo y otra de elementos, ambas con los mismos filtros.
- Orden por `lower(name)` y `id`.
- Respuesta: `items`, `total`, `page`, `page_size`, `pages`.

### 5. Categorías

- `GET /api/merchant/categories` devuelve `{id, name}` ordenado por nombre; solo lectura.
- La semilla `scripts/seed_categories.py` crea de forma idempotente las diez categorías acordadas usando el nombre sin distinguir mayúsculas.
- Al crear o editar se valida que todos los `category_ids` existan; si falta alguno, `422`.

### 6. Imágenes por URL

- `images` es una lista opcional de hasta 5 elementos `{url, alt_text?}`.
- `url` usa `HttpUrl` (http/https) y se guarda como texto de hasta 500 caracteres; `alt_text` hasta 200.
- El orden del array define `position`; el primero se marca `is_primary`.
- En la edición, si se envía `images`, se reemplaza el conjunto completo (se eliminan las filas anteriores y se insertan las nuevas). Si no se envía, no cambia.
- La baja del producto no elimina imágenes, porque es lógica.

### 7. Precios

- `price`: `Decimal` con `ge=0`, `max_digits=10`, `decimal_places=2`.
- `offer_price`: opcional, `ge=0` y menor que `price`; se valida en schema y en servicio, con respaldo del CHECK existente.
- `is_featured` no se acepta en los schemas.

### 8. Contrato de schemas

- `ProductCreate`: `name`, `description?`, `price`, `offer_price?`, `category_ids` (1..N), `images?`.
- `ProductUpdate`: todos opcionales; si `category_ids` o `images` están presentes, reemplazan.
- `ProductRead`: `id`, `name`, `description`, `price`, `offer_price`, `categories`, `images`, `is_active`, `deleted_at`, `created_at`, `updated_at`.
- `ImageRead`: `id`, `url`, `alt_text`, `position`, `is_primary`.
- `PaginatedProducts`: `items`, `total`, `page`, `page_size`, `pages`.

### 9. Errores

| Caso | Código |
|---|---|
| Sin token | `401` |
| Rol no comerciante o sin local | `403` |
| Producto inexistente o de otro local | `404` |
| Modificar eliminado | `409` |
| Categoría inexistente, datos inválidos, `store_id` enviado | `422` |

### 10. Frontend

- Rutas protegidas: `/comerciante/productos`, `/comerciante/productos/nuevo`, `/comerciante/productos/:productId/editar`.
- Estado de filtros en la URL (`search`, `status`, `category`, `page`) para conservarlos al volver del formulario.
- `useQuery` con claves que incluyen los filtros; búsqueda con debounce corto.
- Listado en tabla con nombre, precio, oferta, categorías, imágenes, estado y acciones.
- Formulario con validación local: nombre, precio, al menos una categoría, oferta menor que precio, máximo 5 imágenes.
- Las filas eliminadas muestran su estado y ofrecen "Restaurar" con confirmación; al restaurar vuelven a los vigentes con sus datos e imágenes.
- El panel enlaza a `/comerciante/productos`; información del local y estadísticas siguen como "Próximamente".

## Risks / Trade-offs

- **Productos eliminados visibles solo con filtro** → el comerciante debe cambiar el filtro; se documenta en la interfaz.
- **Reemplazo completo de imágenes** → simplifica el contrato, pero un error del cliente puede borrar imágenes; el formulario envía la lista actual.
- **Conteo y elementos en dos consultas** → consistencia suficiente para un panel; no se requiere snapshot.
- **Categorías globales sin CRUD** → si faltan categorías, se amplía la semilla o se crea un cambio de gestión.
- **Búsqueda con `ILIKE`** → suficiente para el volumen actual; un índice trigram se evaluará con CU #1.

## Migration Plan

No hay cambios de esquema. Pasos:

1. Desplegar backend con `require_merchant` y el router del catálogo.
2. Ejecutar `python -m scripts.seed_categories`.
3. Desplegar frontend con las rutas nuevas.
4. Verificar alta, edición, baja, filtros y aislamiento entre locales.

Rollback: retirar las rutas y el router; no hay datos que migrar. Las categorías sembradas son datos de referencia y pueden conservarse.

## Open Questions

Ninguna que afecte al esquema o al alcance. El CRUD de categorías y los destacados quedan para cambios posteriores.
