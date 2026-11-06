# Propuesta

## Why

El CU #5 pide que un visitante visualice un plano de la galería e identifique dónde está cada local. El modelo ya guarda una ubicación semántica real para los 21 locales: 10 del lado izquierdo, 10 del derecho y 1 al fondo, mediante `side` y `position`. No existen coordenadas, pisos ni una imagen del plano.

Este cambio implementa un plano esquemático generado desde esos datos, sin inventar ubicaciones ni incorporar una imagen que no está disponible.

## What Changes

- Se añade `GET /api/public/map`, sin autenticación, con los locales activos y su `side`/`position`.
- Se añade la página pública `/mapa` con un esquema CSS de la galería: dos columnas de 10 locales, un pasillo central y el local del fondo.
- Cada slot muestra el número, el logo y el nombre del local.
- Cada slot es un enlace accesible que abre directamente la ficha pública del local.
- Se enlaza el mapa desde la portada.
- Se añaden pruebas de backend y frontend.
- Se documenta que un plano gráfico real con imagen y coordenadas queda pendiente.

### Alcance

- Mapa público esquemático de los 21 locales.
- Identificación por número, logo y nombre.
- Navegación directa a la ficha existente del local (CU #4).
- Diseño responsive y accesible.

### Fuera de alcance

- Imagen real del plano y coordenadas por local.
- Pisos, sectores múltiples o pasillos adicionales.
- Búsqueda, filtros o productos dentro del mapa.
- Geolocalización, mapas externos o navegación.
- Administración de ubicaciones (no existe flujo para editarlas).

## Capabilities

### New Capabilities

- `store-map`: plano público esquemático de la galería, ubicación de locales y navegación directa a la ficha del local.

### Modified Capabilities

Ninguna. El mapa consume `side`/`position` mediante un endpoint nuevo y no cambia el contrato del listado de locales, la ficha de local ni la exploración.

## Impact

- **Backend nuevo:** schemas, servicio y router del mapa en `app/modules/public_catalog/` o un módulo `public_map`; pruebas.
- **Backend modificado:** `app/main.py` si se registra un router nuevo.
- **Frontend nuevo:** `features/store-map/` (API, tipos, página, esquema y slots enlazados) y ruta `/mapa`.
- **Frontend modificado:** `app/router.tsx` y `pages/HomePage.tsx` para enlazar el mapa.
- **Migraciones:** ninguna; `side` y `position` ya existen con restricciones que garantizan los 21 espacios.
- **Dependencias nuevas:** ninguna; el esquema se construye con CSS.
- **API:** `GET /api/public/map`.
- **Funcionalidades existentes:** búsqueda, exploración, detalle de producto, ficha de local, CU #6-#10, autenticación y health check no cambian.
- **Dependencias:** `domain-model`, `store-detail` y `merchant-portal`.

## Decisiones adoptadas

- Plano esquemático desde `side`/`position`, no una imagen real.
- Sin orientación declarada: no se etiqueta entrada ni sentido de circulación.
- Columnas izquierda y derecha según los datos, 10 posiciones cada una, y el local del fondo.
- Cada slot muestra número, logo y nombre, y enlaza directamente a `/locales/{id}`.
- Solo locales activos.
- Sin coordenadas, pisos ni migraciones.
- Recurso pendiente: si se consigue un plano real, se añadirá imagen y coordenadas en un cambio posterior.
