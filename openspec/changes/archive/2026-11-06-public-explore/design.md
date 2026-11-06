# Diseño

## Context

Ver `proposal.md` para la motivación y `specs/explore/spec.md` para los requisitos. El catálogo público ya tiene búsqueda, detalle de producto y ficha de local. Las ofertas existen mediante `offer_price`; `is_featured` no se usa porque ningún flujo lo activa. No hay listado público de locales.

## Goals / Non-Goals

**Goals:**

- Portada de descubrimiento con una sola consulta agregada.
- Secciones útiles sin inventar curaduría.
- Reutilizar serialización, tarjetas y detalles existentes.

**Non-Goals:**

- Destacados manuales o locales destacados.
- Búsqueda nueva, mapa o estadísticas.
- Paginación del listado de 21 locales.

## Decisions

### 1. Endpoints

- `GET /api/public/explore` → `featured`, `offers`, `categories`, `stores`.
- `GET /api/public/stores` → todos los locales activos.
- `GET /api/public/products?has_offer=true` → filtro aditivo en la búsqueda existente.

Todos sin autenticación.

### 2. Destacados

Se seleccionan hasta 8 productos:

1. Productos disponibles con `offer_price` no nulo, ordenados por `created_at DESC`, máximo 8.
2. Se completan con productos disponibles sin repetir, ordenados por `created_at DESC`, hasta llegar a 8.

La consulta reutiliza las condiciones de disponibilidad de la búsqueda: producto no eliminado, activo y local activo. Se serializan con el schema `PublicProduct` existente.

### 3. Ofertas

Hasta 8 productos disponibles con `offer_price` no nulo, ordenados por `created_at DESC`. La sección puede repetir productos que ya aparecen en destacados; es una decisión de producto aceptada.

### 4. Categorías con conteo

Una consulta con `outerjoin` desde `categories` hacia productos disponibles cuenta productos distintos por categoría. Se devuelven todas las categorías ordenadas por nombre, incluidas las de conteo cero.

### 5. Locales

- En `explore`: hasta 6 locales activos ordenados por número, con `id`, `number`, `name`, `description`, `logo_url`.
- En `GET /public/stores`: todos los locales activos ordenados por número, con los mismos campos.
- Sin paginación: son 21 locales fijos.

### 6. Filtro `has_offer`

Se añade `has_offer: bool = False` a `GET /public/products`. Cuando es `true`, se agrega `Product.offer_price.is_not(None)` a las condiciones. Sin el parámetro, el comportamiento es el actual.

### 7. Frontend

- `/explorar` con secciones:
  - **Destacados:** grilla de `ProductCard`.
  - **Ofertas:** grilla de `ProductCard` y enlace "Ver todas las ofertas" a `/buscar?has_offer=true`.
  - **Categorías:** tarjetas con nombre y conteo, enlace a `/buscar?category={id}`.
  - **Locales:** hasta 6 tarjetas con logo, número, nombre y descripción, enlace a `/locales/{id}`; enlace "Ver todos los locales" a `/locales`.
  - Enlaces "Ver todos los productos" a `/buscar`.
- `/locales` con todos los locales y enlace a su ficha.
- `StoreCard` reutilizable en portada y listado.
- El buscador lee `has_offer` de la URL, lo envía a la API y muestra un checkbox "Solo ofertas".
- La portada enlaza a `/explorar`.
- Estados de carga, error y secciones vacías.

### 8. Eventos de búsqueda

`explore` no registra `ProductSearchEvent`: es descubrimiento, no una búsqueda del visitante. La búsqueda con `has_offer` sí mantiene el registro actual cuando tiene criterios.

### 9. Rendimiento

- Una consulta por sección de productos y una por categorías y locales.
- Índices existentes por `store_id`, `price` y `name`; el volumen actual es pequeño.
- Se serializa con `selectinload` para evitar N+1.

## Risks / Trade-offs

- **Duplicación entre destacados y ofertas** → decisión de producto aceptada; se prioriza claridad de secciones.
- **Sin curaduría real** → "destacados" es una mezcla automática; si se necesita curación, será un cambio posterior con administración.
- **Categorías con conteo cero** → se muestran igualmente para mantener el filtro estable.
- **Listado de locales sin paginación** → 21 locales fijos; se añadirá si crece.
- **Filtro aditivo en búsqueda** → requiere actualizar `product-search`; se mantiene el comportamiento sin el parámetro.

## Migration Plan

No hay cambios de esquema ni datos. Se despliega el backend y luego las páginas `/explorar` y `/locales`.

Rollback: retirar los endpoints y rutas; no hay datos que migrar.

## Open Questions

Ninguna que afecte al esquema o al alcance. La curaduría de destacados y el mapa quedan para cambios posteriores.
