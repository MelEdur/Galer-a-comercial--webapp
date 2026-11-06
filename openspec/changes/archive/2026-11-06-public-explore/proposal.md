# Propuesta

## Why

El CU #2 pide que un visitante descubra productos, categorías y locales sin usar el buscador. Hoy la aplicación solo ofrece búsqueda y fichas individuales: no hay portada de exploración ni listado público de locales. El modelo ya soporta ofertas mediante `offer_price`, pero no existe un mecanismo de curaduría de destacados (`is_featured` nunca se activa).

Este cambio implementa exclusivamente la exploración pública, reutilizando el catálogo, las categorías, el detalle de producto y la ficha de local.

## What Changes

- Se añade `GET /api/public/explore` con destacados, ofertas, categorías con conteo y una selección de locales.
- Se añade `GET /api/public/stores` con todos los locales activos.
- Se añade el filtro `has_offer=true` a `GET /api/public/products` para listar todas las ofertas.
- Se añade la página pública `/explorar` con las secciones de descubrimiento.
- Se añade la página pública `/locales` con el listado completo de locales.
- La portada enlaza a la exploración.
- El buscador acepta y muestra el filtro "Solo ofertas".
- Se añaden pruebas de backend y frontend.

### Alcance

- Descubrimiento de productos disponibles y ofertas.
- Categorías con cantidad de productos y enlace al buscador filtrado.
- Sección y listado de locales activos.
- Navegación a los detalles existentes de producto y local.
- Filtro de ofertas en el buscador existente.

### Fuera de alcance

- Curaduría manual de destacados (`is_featured`).
- Locales destacados.
- Búsqueda nueva o cambio de su lógica (solo se añade un filtro).
- Detalle de producto o local (se reutilizan CU #3 y CU #4).
- Mapa (CU #5) y estadísticas (CU #10).
- Paginación del listado de locales.
- Carrito, favoritos o reseñas.

## Capabilities

### New Capabilities

- `explore`: portada pública de descubrimiento con destacados, ofertas, categorías y locales, y listado público de locales.

### Modified Capabilities

- `product-search`: se añade el filtro opcional `has_offer` para listar solo productos con precio de oferta.

## Impact

- **Backend nuevo:** schemas, servicio y router de exploración en `app/modules/public_catalog/` o un módulo `public_explore`; pruebas.
- **Backend modificado:** `public_catalog/router.py` y `service.py` para `has_offer`; `app/main.py` si se crea un router nuevo.
- **Frontend nuevo:** `features/explore/` (API, tipos, página, secciones) y `features/store-list/`; rutas `/explorar` y `/locales`.
- **Frontend modificado:** `app/router.tsx`, `pages/HomePage.tsx` y el buscador para aceptar `has_offer`.
- **Migraciones:** ninguna.
- **Dependencias nuevas:** ninguna.
- **API:** `GET /api/public/explore`, `GET /api/public/stores` y `has_offer` en `GET /api/public/products`.
- **Funcionalidades existentes:** búsqueda, detalle de producto, ficha de local, CU #6, #7, #8, #9, autenticación y health check no cambian de comportamiento.
- **Dependencias:** `domain-model`, `product-search`, `product-detail` y `store-detail`.

## Decisiones adoptadas

- No se usa `is_featured`: no existe curación y siempre vale `false`.
- Destacados y ofertas son secciones separadas; se acepta que los productos con oferta aparezcan en ambas.
- Destacados: ofertas recientes primero, luego novedades sin repetir, máximo 8.
- Ofertas: máximo 8, ordenadas por creación descendente.
- Categorías: todas, con conteo de productos disponibles.
- Locales: sección de 6 en la portada y listado completo de los 21 activos.
- Sin locales destacados.
- La exploración no registra eventos de búsqueda.
- `has_offer` es aditivo: sin el parámetro, la búsqueda mantiene su comportamiento.
