# Propuesta

## Why

El CU #10 pide que el comerciante consulte qué productos de su local fueron los más buscados en un período. El registro ya existe: CU #1 guarda un `ProductSearchEvent` por cada producto devuelto en una página de búsqueda con criterios, con término y fecha, y los eventos se conservan al eliminar lógicamente un producto. Falta la consulta agregada y la pantalla de estadísticas.

Este cambio implementa exclusivamente las estadísticas de búsquedas de productos del local propio.

## What Changes

- Se añade `GET /api/merchant/stats/products` protegido con `require_merchant`.
- Se agregan los eventos por producto del local autenticado, con conteo y última búsqueda.
- Se admiten períodos predefinidos de 7, 30 y 90 días, y un rango personalizado de fechas.
- Se devuelve un Top 10 ordenado por cantidad descendente y nombre ascendente.
- Los productos eliminados se incluyen con una marca y se conserva su histórico.
- Se añade la página protegida `/comerciante/estadisticas` con selector de período, tabla y barras CSS.
- El panel del comerciante deja de mostrar Estadísticas como "Próximamente".
- Se añaden pruebas de backend y frontend, incluyendo autorización y aislamiento entre locales.

### Alcance

- Ranking de productos más buscados del local del comerciante autenticado.
- Períodos predefinidos y rango personalizado.
- Conteo por producto, última búsqueda y total de eventos del período.
- Productos eliminados marcados.
- Pantalla de estadísticas y acceso desde el panel.

### Fuera de alcance

- Analíticas generales de la aplicación.
- Visitas a locales, ventas, ingresos o conversión.
- Estadísticas de otros locales o del administrador.
- Búsquedas por visitante, clics o sesiones.
- Exportación, comparación de períodos, gráficos avanzados o purga de eventos.
- Cambios en el registro de eventos de CU #1: ya cubre el requisito.

## Capabilities

### New Capabilities

- `product-statistics`: ranking de productos más buscados del local propio, con períodos, conteos, productos eliminados y presentación en el panel.

### Modified Capabilities

Ninguna. El registro de eventos ya está definido en `domain-model` y la búsqueda de CU #1 ya lo implementa; este cambio solo lo consulta.

## Impact

- **Backend nuevo:** `app/modules/analytics/` con schemas, servicio y router de estadísticas; pruebas.
- **Backend modificado:** `app/main.py` para registrar el router.
- **Frontend nuevo:** `features/product-stats/` (API, tipos, página, selector de período, tabla) y ruta `/comerciante/estadisticas`.
- **Frontend modificado:** `app/router.tsx` y `pages/MerchantPage.tsx`.
- **Migraciones:** ninguna; `product_search_events` ya existe con sus índices.
- **Dependencias nuevas:** ninguna; los límites de fecha usan UTC-3 fijo.
- **API:** `GET /api/merchant/stats/products`.
- **Funcionalidades existentes:** búsqueda, exploración, CU #6, #7, #8, #9, autenticación y health check no cambian.
- **Dependencias:** `domain-model`, `product-search` y `merchant-portal`.

## Decisiones adoptadas

- Una búsqueda es una request con criterios; se cuenta un evento por producto visible en la página devuelta.
- La paginación cuenta cada página que el visitante vio.
- Períodos: 7, 30 y 90 días, o rango personalizado.
- Sin parámetros: últimos 30 días.
- Solo productos con al menos una búsqueda en el período.
- Top 10; empates por nombre ascendente.
- Productos eliminados incluidos con marca.
- Límites de fecha en `America/Argentina/Buenos_Aires` (UTC-3 fijo, sin DST).
- `total_searches` suma todos los eventos del local en el período, no solo el Top 10.
- Consultar estadísticas no registra nuevos eventos.
