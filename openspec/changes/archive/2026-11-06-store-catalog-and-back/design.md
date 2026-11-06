# Diseño

## Context

Ver `proposal.md` y las specs delta. La ficha del local ya existe en `/locales/:id`, el producto público se serializa con `PublicProduct` y el buscador no filtra por local. No hay endpoint de productos por local y los botones de volver apuntan fijos a `/buscar`.

## Goals / Non-Goals

**Goals:**

- Catálogo del local con una sola consulta paginada.
- Volver al origen real sin romper entradas directas.
- Reutilizar el schema y la tarjeta de producto.

**Non-Goals:**

- Filtros o búsqueda dentro del catálogo.
- Cambios de administración del catálogo.
- Nuevas tablas, columnas o migraciones.

## Decisions

### 1. Endpoint dedicado

`GET /api/public/stores/{store_id}/products?page=1&page_size=12`, sin autenticación.

- Verifica que el local exista y esté activo; si no, `404`.
- Filtra productos no eliminados, activos y de ese local.
- Devuelve `PaginatedPublicProducts` con el schema `PublicProduct` existente.
- Orden por nombre.
- `page_size` por defecto 12, máximo 100.
- No registra `ProductSearchEvent`.

Se reutilizan las condiciones de disponibilidad y `_to_read` del catálogo público. No se modifica el buscador.

### 2. Sección de catálogo

- `StoreCatalog` se renderiza debajo de `StoreLinks` en `StoreDetailPage`.
- Usa `useQuery` con clave `['public','store',id,'products',page]`.
- Grilla responsive de `ProductCard`.
- `ProductCard` recibe `showStore?: boolean` (por defecto `true`); el catálogo lo usa con `false`.
- Paginación anterior/siguiente; se oculta si solo hay una página.
- Estados de carga, error y vacío.
- Cada tarjeta enlaza a `/productos/{id}`.

### 3. Botón Volver

Helper `useGoBack`:

- si `location.key !== 'default'`, ejecuta `navigate(-1)`;
- si la entrada fue directa, navega a `/`.

Se reemplaza el enlace “Volver a la búsqueda” por un botón “Volver” en:

- `StoreDetailPage`;
- `ProductDetailPage`.

Los CTA de “no encontrado” conservan su enlace al buscador.

### 4. Pruebas

Backend:
- contrato, paginación, orden;
- exclusión de productos de otros locales y no disponibles;
- `404` de local inactivo/inexistente;
- ausencia de eventos.

Frontend:
- catálogo visible debajo de enlaces, con paginación y vacío;
- tarjetas sin línea de local;
- “Volver” usa historial y fallback;
- detalle de producto con el mismo comportamiento;
- pruebas existentes actualizadas.

## Risks / Trade-offs

- **Catálogo grande** → paginación de 12 y máximo 100; suficiente para la primera versión.
- **Historial del navegador** → `location.key` distingue la entrada directa; si el usuario llegó desde otro sitio, el fallback va a `/`.
- **Tarjetas sin local** → el contexto de la sección ya identifica el local.
- **Sin cambios de datos** → riesgo bajo.

## Migration Plan

No hay migraciones. Se despliega el backend y luego el frontend; el endpoint nuevo es aditivo.

Rollback: retirar el endpoint, la sección y el helper de volver.

## Open Questions

Ninguna que afecte al alcance.
