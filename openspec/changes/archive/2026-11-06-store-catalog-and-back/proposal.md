# Propuesta

## Why

La ficha pública de un local muestra datos, horarios, contacto y enlaces, pero no sus productos. El visitante debe volver al buscador para descubrir el catálogo del local. Además, el botón “Volver a la búsqueda” asume un origen que no siempre es real: el visitante puede haber llegado desde el mapa, el detalle de un producto o la exploración.

Este cambio agrega el catálogo del local a su ficha y reemplaza el botón de volver por uno que respeta el origen real.

## What Changes

- Se añade `GET /api/public/stores/{store_id}/products`, paginado y público.
- La ficha del local muestra una sección “Catálogo” debajo de los enlaces.
- Las tarjetas del catálogo reutilizan el producto público y ocultan la línea del local.
- Se agrega paginación al catálogo del local.
- Se reemplaza “Volver a la búsqueda” por “Volver” en la ficha del local y en el detalle de producto.
- “Volver” usa el historial interno y, si no existe, navega a `/`.
- Se añaden pruebas de backend y frontend.

### Alcance

- Endpoint de productos por local.
- Sección de catálogo con paginación y estados.
- Botón de volver basado en historial con fallback.
- Pruebas de aislamiento y paginación.

### Fuera de alcance

- Búsqueda dentro del catálogo del local.
- Filtros por categoría/precio en la ficha del local.
- Carrito, favoritos o compra.
- Cambios en la administración del catálogo del comerciante.
- Nuevos datos o migraciones.

## Capabilities

### New Capabilities

Ninguna.

### Modified Capabilities

- `store-detail`: se agrega el catálogo paginado del local y el comportamiento de “Volver”.
- `product-detail`: se agrega el comportamiento de “Volver” basado en historial.

## Impact

- **Backend modificado:** `app/modules/public_catalog/{router,service,schemas}.py` y pruebas.
- **Frontend modificado:** `features/store-detail/` (API, catálogo, página), `features/product-search/ProductCard.tsx`, `features/product-detail/ProductDetailPage.tsx`, helper de navegación y pruebas.
- **Migraciones:** ninguna.
- **Dependencias nuevas:** ninguna.
- **API:** `GET /api/public/stores/{store_id}/products`.
- **Eventos de búsqueda:** el catálogo del local no los registra.
- **Funcionalidades existentes:** buscador, exploración, mapa, asistente, paneles y autenticación no cambian.

## Decisiones adoptadas

- Endpoint dedicado por local en lugar de reutilizar el buscador.
- Productos disponibles únicamente: no eliminados, activos y de local activo.
- Paginación de 12 por defecto, máximo 100.
- Tarjetas sin la línea del local dentro de la ficha.
- “Volver” usa `navigate(-1)` si hay historial interno; si no, `/`.
- El botón se aplica a la ficha del local y al detalle de producto.
- Los CTA de “no encontrado” se mantienen orientados al buscador.
