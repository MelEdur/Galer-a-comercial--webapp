# Propuesta

## Why

El CU #1 pide que un visitante busque productos por nombre, categoría y precio, y vea los locales que los ofrecen. El CU #8 dejó un catálogo completo por comerciante, pero todos sus endpoints exigen sesión y están acotados al local del comerciante: hoy no existe ninguna forma pública de consultar los productos de la galería.

Este cambio implementa exclusivamente la búsqueda pública, sin feed, sin detalle de producto y sin autenticación.

## What Changes

- Se añade `GET /api/public/products`, sin autenticación, con búsqueda por nombre, filtro por categoría, rango de precio, orden y paginación.
- Se añade `GET /api/public/categories` para alimentar el selector de categorías.
- La búsqueda solo devuelve productos no eliminados, activos y de locales activos.
- Cada resultado incluye su local, sus categorías y su imagen primaria.
- El rango de precio se aplica al precio efectivo (oferta si existe, si no el precio).
- Se registra un evento de búsqueda por cada producto devuelto en la página, cuando la consulta tiene al menos un criterio.
- Se añade una página pública `/buscar` con buscador, filtros, orden, paginación y estados de carga, vacío y error.
- Se enlaza el buscador desde la página de inicio.
- Se añaden pruebas de backend y frontend.

### Alcance

- Búsqueda pública de productos disponibles.
- Filtros combinables por nombre, categoría y rango de precio.
- Orden por nombre o precio y paginación.
- Listado del local que ofrece cada producto.
- Registro de eventos para las estadísticas de CU #10.
- Página pública de búsqueda.

### Fuera de alcance

- Feed de destacados y ofertas (CU #2).
- Detalle público de producto (CU #3).
- Información y mapa de locales (CU #4 y CU #5).
- Panel de estadísticas del comerciante (CU #10).
- Búsqueda por descripción, por nombre de local o por texto libre avanzado.
- Autenticación, favoritos, reseñas o carrito.
- Normalización de acentos y búsqueda difusa.

## Capabilities

### New Capabilities

- `product-search`: búsqueda pública de productos disponibles con filtros combinables, orden, paginación, información del local y registro de eventos.

### Modified Capabilities

Ninguna. El registro de eventos de búsqueda ya está exigido por `domain-model`; este cambio lo implementa sin modificar su contrato.

## Impact

- **Backend nuevo:** `app/modules/public_catalog/` (schemas, servicio, router) con endpoints públicos.
- **Backend modificado:** `app/main.py` para registrar el router público; pruebas.
- **Frontend nuevo:** `features/product-search/` (API, tipos, página, filtros, tarjetas, paginación) y ruta `/buscar`.
- **Frontend modificado:** `app/router.tsx` y `pages/HomePage.tsx`.
- **Migraciones:** ninguna; se usan tablas e índices existentes.
- **Dependencias nuevas:** ninguna.
- **API:** `GET /api/public/products` y `GET /api/public/categories`.
- **Funcionalidades existentes:** CU #6, CU #7, CU #8, autenticación y health check no cambian.
- **Dependencias:** `domain-model` y `merchant-product-catalog`.

## Decisiones adoptadas

- Coincidencia parcial sin distinguir mayúsculas, con comodines escapados.
- Filtros combinados con AND.
- Rango de precio inclusivo sobre el precio efectivo.
- Un resultado por producto; cada producto pertenece a un local.
- Disponibilidad: producto no eliminado y activo, y local activo.
- Búsqueda sin criterios devuelve todo el catálogo disponible paginado.
- Orden por nombre ascendente por defecto; precio ascendente o descendente opcional.
- Eventos solo para consultas con criterios y solo para los productos de la página.
- Paginación de 20 por defecto y máximo 100.
