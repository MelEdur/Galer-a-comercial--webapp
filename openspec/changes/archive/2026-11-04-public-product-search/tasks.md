# Tasks

## 1. Backend: módulo público

- [x] 1.1 Crear `app/modules/public_catalog/` con `__init__.py`, schemas, servicio y router; registrar el router bajo `/api` en `app/main.py`.
- [x] 1.2 Implementar los schemas de producto público, local, imagen primaria, categorías y respuesta paginada.
- [x] 1.3 Implementar `GET /api/public/categories` ordenado por nombre.

## 2. Backend: búsqueda

- [x] 2.1 Implementar la consulta con disponibilidad (producto no eliminado y activo, local activo) y los filtros combinados de nombre, categoría y precio efectivo.
- [x] 2.2 Implementar el orden por nombre y por precio efectivo, y la paginación con conteo.
- [x] 2.3 Calcular `effective_price` como `coalesce(offer_price, price)` y usarlo en filtro y orden.
- [x] 2.4 Incluir local, categorías e imagen primaria en cada resultado sin N+1.
- [x] 2.5 Validar `min_price <= max_price` y precios no negativos con `422`.

## 3. Backend: eventos de búsqueda

- [x] 3.1 Registrar un evento por producto de la página cuando la consulta tenga criterios; no registrar en exploración ni en páginas vacías.
- [x] 3.2 Incluir el término consultado y la fecha, en una sola operación de inserción.

## 4. Pruebas del backend

- [x] 4.1 Probar búsqueda sin autenticación y respuesta con los campos esperados, sin datos internos.
- [x] 4.2 Probar coincidencia parcial, mayúsculas y comodines literales.
- [x] 4.3 Probar filtro por categoría con y sin resultados.
- [x] 4.4 Probar precio mínimo, máximo, rango, precio efectivo con oferta, rango inválido y precio negativo.
- [x] 4.5 Probar combinación de los tres filtros.
- [x] 4.6 Probar disponibilidad: eliminado, inactivo y local inactivo no aparecen.
- [x] 4.7 Probar orden por nombre y precio, y paginación.
- [x] 4.8 Probar búsqueda sin criterios y categorías públicas.
- [x] 4.9 Probar eventos: por página con criterios, sin eventos en exploración o sin resultados, y conservación tras eliminar el producto.
- [x] 4.10 Ejecutar la suite completa y confirmar que CU #6, #7, #8 y el health check siguen funcionando.

## 5. Frontend: API y tipos

- [x] 5.1 Crear tipos y cliente API para la búsqueda pública y las categorías.
- [x] 5.2 Configurar las claves de TanStack Query para búsqueda y categorías.

## 6. Frontend: página de búsqueda

- [x] 6.1 Crear la ruta pública `/buscar` y enlazarla desde la página de inicio.
- [x] 6.2 Implementar buscador, selector de categoría, precios mínimo y máximo y selector de orden, con estado en la URL.
- [x] 6.3 Implementar las tarjetas de resultado con imagen primaria, nombre, descripción, precio, oferta, categorías y local.
- [x] 6.4 Implementar paginación y estados de carga, vacío y error.
- [x] 6.5 Aplicar debounce a la búsqueda y evitar peticiones innecesarias.

## 7. Pruebas del frontend

- [x] 7.1 Probar búsqueda por nombre y visualización de resultados con local.
- [x] 7.2 Probar filtro por categoría y por precio.
- [x] 7.3 Probar estado vacío, estado de error y paginación.
- [x] 7.4 Probar que la búsqueda sin filtros muestra el catálogo.
- [x] 7.5 Ejecutar `npm test -- --run` y `npm run build`.

## 8. Verificación de integración

- [x] 8.1 Con el stack levantado, buscar sin sesión y verificar resultados y locales.
- [x] 8.2 Verificar combinaciones de filtros y orden por precio.
- [x] 8.3 Verificar que productos eliminados o inactivos no aparecen.
- [x] 8.4 Verificar el registro de eventos en la base de datos.
- [x] 8.5 Validar el cambio con `openspec validate public-product-search --strict` y registrar los resultados.

## Workflow follow-up

- Revisar y archivar después de la verificación.
- No implementar feed, detalle, mapa, CU #9 ni CU #10.
