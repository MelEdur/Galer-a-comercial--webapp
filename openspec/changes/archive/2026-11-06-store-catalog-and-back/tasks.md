# Tasks

## 1. Backend

- [x] 1.1 Implementar el servicio de productos por local con verificación de local activo, filtros de disponibilidad, orden y paginación.
- [x] 1.2 Añadir `GET /api/public/stores/{store_id}/products` con `page` y `page_size` (12 por defecto, máximo 100).
- [x] 1.3 Verificar que el endpoint no registra eventos de búsqueda ni modifica el buscador.

## 2. Pruebas del backend

- [x] 2.1 Probar contrato, total y páginas del catálogo.
- [x] 2.2 Probar exclusión de productos eliminados, inactivos y de otros locales.
- [x] 2.3 Probar `404` de local inexistente e inactivo.
- [x] 2.4 Probar que no se crean eventos de búsqueda.
- [x] 2.5 Mantener las pruebas existentes pasando.

## 3. Frontend: catálogo

- [x] 3.1 Añadir tipos, cliente API y query key para productos por local.
- [x] 3.2 Añadir `showStore` a `ProductCard` con valor por defecto `true`.
- [x] 3.3 Crear `StoreCatalog` con grilla, paginación y estados de carga, error y vacío.
- [x] 3.4 Renderizar el catálogo debajo de los enlaces en `StoreDetailPage`.

## 4. Frontend: Volver

- [x] 4.1 Crear `useGoBack` con historial interno y fallback a `/`.
- [x] 4.2 Reemplazar el enlace “Volver a la búsqueda” por el botón “Volver” en `StoreDetailPage`.
- [x] 4.3 Reemplazar el enlace equivalente en `ProductDetailPage`.

## 5. Pruebas del frontend

- [x] 5.1 Probar catálogo con productos, paginación y estado vacío.
- [x] 5.2 Probar que las tarjetas del catálogo no muestran el local.
- [x] 5.3 Probar el enlace de cada producto a `/productos/{id}`.
- [x] 5.4 Probar “Volver” con historial y con entrada directa en local y producto.
- [x] 5.5 Ejecutar `npm test -- --run` y `npm run build`.

## 6. Verificación de integración

- [x] 6.1 Abrir un local con productos y verificar el catálogo paginado.
- [x] 6.2 Abrir un producto desde el catálogo y volver al local.
- [x] 6.3 Abrir la ficha desde el mapa y verificar el retorno al mapa.
- [x] 6.4 Abrir una ficha por URL directa y verificar el fallback a `/`.
- [x] 6.5 Validar el cambio con `openspec validate store-catalog-and-back --strict`.

## Workflow follow-up

- Revisar y archivar después de la verificación.
- No modificar el buscador ni la administración del catálogo.
