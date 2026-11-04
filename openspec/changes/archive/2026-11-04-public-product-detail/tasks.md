# Tasks

## 1. Backend: schemas y detalle

- [x] 1.1 Añadir `PublicImageDetail`, `PublicStoreDetail`, `PublicProductDetail` y `PublicSimilarProducts` a `public_catalog/schemas.py`.
- [x] 1.2 Implementar `get_product_detail` con las condiciones de disponibilidad y carga de imágenes, categorías y local.
- [x] 1.3 Añadir `GET /api/public/products/{product_id}` al router público, con `404` cuando no esté disponible.

## 2. Backend: productos similares

- [x] 2.1 Implementar la extracción de palabras significativas del nombre (≥3 letras, minúsculas, sin duplicados).
- [x] 2.2 Implementar la consulta de candidatos disponibles que comparten categoría o contienen alguna palabra, excluyendo el producto actual.
- [x] 2.3 Puntuar y ordenar por categorías compartidas, palabras coincidentes y nombre; limitar a seis.
- [x] 2.4 Añadir `GET /api/public/products/{product_id}/similar`, con `404` si el producto base no está disponible.

## 3. Pruebas del backend

- [x] 3.1 Probar detalle sin autenticación y ausencia de datos internos.
- [x] 3.2 Probar producto con varias imágenes, orden, primaria y oferta.
- [x] 3.3 Probar local con y sin logo/contacto.
- [x] 3.4 Probar `404` para inexistente, eliminado, inactivo y local inactivo.
- [x] 3.5 Probar similares por categoría, por palabra, exclusión del actual, límite de seis y lista vacía.
- [x] 3.6 Probar `404` de similares cuando el producto base no está disponible.
- [x] 3.7 Mantener las 210 pruebas existentes pasando.

## 4. Frontend: API y tipos

- [x] 4.1 Crear tipos y cliente API para detalle y similares.
- [x] 4.2 Configurar las claves de TanStack Query para detalle y similares.

## 5. Frontend: página de detalle

- [x] 5.1 Crear la ruta pública `/productos/:productId`.
- [x] 5.2 Implementar la galería con imagen principal, miniaturas, primaria y marcador "Sin imagen".
- [x] 5.3 Mostrar nombre, descripción, precio, oferta, precio efectivo y categorías.
- [x] 5.4 Mostrar el local con número, nombre, logo y contacto (`mailto:`, `tel:`, WhatsApp).
- [x] 5.5 Implementar los estados de carga, error y producto no encontrado con enlace al buscador.

## 6. Frontend: similares y navegación

- [x] 6.1 Hacer que `ProductCard` enlace a `/productos/{id}`, conservando accesibilidad y diseño.
- [x] 6.2 Añadir la sección de similares como carrusel horizontal, oculta si está vacía.
- [x] 6.3 Verificar que las tarjetas de búsqueda y de similares navegan correctamente.

## 7. Pruebas del frontend

- [x] 7.1 Probar el detalle con imágenes, oferta, categorías y local.
- [x] 7.2 Probar el marcador cuando no hay imágenes.
- [x] 7.3 Probar los similares y su navegación.
- [x] 7.4 Probar carga, error y `404`.
- [x] 7.5 Probar que la tarjeta de búsqueda enlaza al detalle.
- [x] 7.6 Ejecutar `npm test -- --run` y `npm run build`.

## 8. Verificación de integración

- [x] 8.1 Con el stack levantado, abrir el detalle desde una búsqueda y verificar imágenes, precios y local.
- [x] 8.2 Verificar contacto del local y similares.
- [x] 8.3 Verificar `404` con un producto eliminado y con un identificador inexistente.
- [x] 8.4 Validar el cambio con `openspec validate public-product-detail --strict` y registrar los resultados.

## Workflow follow-up

- Revisar y archivar después de la verificación.
- No implementar feed, CU #4, CU #5 ni CU #10.
