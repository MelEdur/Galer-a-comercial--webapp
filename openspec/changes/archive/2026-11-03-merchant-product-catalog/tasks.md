# Tasks

## 1. Backend: autorización y base

- [x] 1.1 Implementar `require_merchant` en `app/modules/auth/dependencies.py`; verificar `401` sin token, `403` para administradores y `403` para comerciantes sin local.
- [x] 1.2 Crear el módulo `app/modules/merchant_catalog/` con `__init__.py`, schemas y estructura de servicio y router.
- [x] 1.3 Registrar el router bajo `/api` en `app/main.py`.

## 2. Backend: schemas y servicio

- [x] 2.1 Implementar `ProductCreate`, `ProductUpdate`, `ProductRead`, `ImageRead`, `CategoryRead` y `PaginatedProducts` con `extra="forbid"`, límites de nombre, descripción, precio, oferta y URLs.
- [x] 2.2 Implementar el listado con búsqueda escapada, filtro de estado, filtro de categoría, paginación y conteo.
- [x] 2.3 Implementar el alta derivando el local del token, validando categorías e imágenes y marcando la primera imagen como primaria.
- [x] 2.4 Implementar la consulta, la edición parcial y el reemplazo de categorías e imágenes; rechazar la edición de eliminados.
- [x] 2.5 Implementar la baja lógica idempotente y la consulta de categorías de solo lectura.
- [x] 2.6 Traducir los errores de negocio a `404`, `409` y `422` sin exponer detalles internos.
- [x] 2.7 Implementar la restauración idempotente de un producto eliminado propio, conservando categorías e imágenes.

## 3. Backend: semilla y pruebas

- [x] 3.1 Crear `backend/scripts/seed_categories.py` idempotente con las diez categorías acordadas; verificar dos ejecuciones sin duplicados.
- [x] 3.2 Probar listado vacío, con datos, búsqueda, filtros de estado y categoría, y paginación.
- [x] 3.3 Probar alta correcta, local derivado del token, `store_id` rechazado, datos inválidos, categoría inexistente y más de cinco imágenes.
- [x] 3.4 Probar consulta, edición parcial, reemplazo de categorías e imágenes, edición de eliminado y oferta inválida.
- [x] 3.5 Probar baja, baja repetida y conservación de datos e imágenes.
- [x] 3.6 Probar aislamiento: un comerciante no puede consultar, editar ni eliminar productos de otro local.
- [x] 3.7 Probar autorización `401` sin token, `403` para administrador y `403` para comerciante sin local.
- [x] 3.8 Ejecutar la suite completa y confirmar que CU #6, CU #7 y el health check siguen funcionando.
- [x] 3.9 Probar la restauración correcta, la restauración repetida, el aislamiento entre locales y la autorización.

## 4. Frontend: API y tipos

- [x] 4.1 Crear tipos y cliente API para productos, categorías, filtros y respuestas paginadas.
- [x] 4.2 Configurar las claves de TanStack Query para listado, detalle y categorías.

## 5. Frontend: listado

- [x] 5.1 Crear la ruta protegida `/comerciante/productos` con búsqueda, filtros de estado y categoría, y paginación.
- [x] 5.2 Mostrar tabla con nombre, precio, oferta, categorías, cantidad de imágenes, estado y acciones.
- [x] 5.3 Implementar estados de carga, vacío y error, conservando los filtros en la URL.
- [x] 5.4 Implementar la baja con confirmación e invalidación del listado.
- [x] 5.5 Implementar la restauración con confirmación en los productos eliminados e invalidar el listado y el detalle.

## 6. Frontend: formulario

- [x] 6.1 Crear las rutas `/comerciante/productos/nuevo` y `/comerciante/productos/:productId/editar` protegidas.
- [x] 6.2 Implementar campos de nombre, descripción, precio, oferta, categorías e imágenes por URL.
- [x] 6.3 Validar localmente nombre, precio, al menos una categoría, oferta menor que el precio y máximo cinco imágenes.
- [x] 6.4 Mostrar errores `404`, `409` y `422` de forma comprensible y volver al listado tras guardar.
- [x] 6.5 Enlazar Productos desde el panel del comerciante y retirar el marcador "Próximamente" de esa sección.

## 7. Pruebas y verificación

- [x] 7.1 Probar listado, búsqueda, filtros, paginación, alta, edición y baja en el frontend.
- [x] 7.2 Probar errores de validación y de producto eliminado.
- [x] 7.3 Ejecutar `npm test -- --run` y `npm run build`.
- [x] 7.4 Con el stack levantado, crear un producto, editarlo, filtrarlo y darlo de baja.
- [x] 7.5 Verificar que un segundo comerciante no puede acceder a los productos del primero.
- [x] 7.6 Ejecutar `seed_categories` dos veces y comprobar la idempotencia.
- [x] 7.7 Validar el cambio con `openspec validate merchant-product-catalog --strict` y registrar los resultados.
- [x] 7.8 Verificar manualmente que un producto eliminado se restaura y vuelve a los vigentes con sus imágenes.
- [x] 7.9 Volver a ejecutar la suite completa y el build tras la restauración.

## Workflow follow-up

- Revisar y archivar después de la verificación.
- No implementar búsqueda pública, feed, detalle público, CU #9 ni CU #10.
