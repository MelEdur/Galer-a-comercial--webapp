# Tasks

## 1. Backend: exploración

- [x] 1.1 Crear los schemas de exploración (destacados, ofertas, categorías con conteo y locales) reutilizando `PublicProduct` y el resumen de local.
- [x] 1.2 Implementar la selección de destacados: ofertas recientes primero y luego novedades sin repetir, máximo 8.
- [x] 1.3 Implementar la sección de ofertas: productos disponibles con oferta, máximo 8, orden por creación descendente.
- [x] 1.4 Implementar categorías con conteo de productos disponibles, incluyendo conteo cero.
- [x] 1.5 Implementar la selección de hasta 6 locales activos ordenados por número.
- [x] 1.6 Añadir `GET /api/public/explore` al router público.

## 2. Backend: locales y filtro de ofertas

- [x] 2.1 Añadir `GET /api/public/stores` con todos los locales activos ordenados por número.
- [x] 2.2 Añadir `has_offer` a `GET /api/public/products`, filtrando por `offer_price` no nulo solo cuando es `true`.
- [x] 2.3 Verificar que sin `has_offer` la búsqueda mantiene su comportamiento actual.
- [x] 2.4 Confirmar que la exploración no registra eventos de búsqueda.

## 3. Pruebas del backend

- [x] 3.1 Probar exploración sin autenticación y contrato de respuesta.
- [x] 3.2 Probar destacados: ofertas primero, completado con novedades, sin repeticiones y límite 8.
- [x] 3.3 Probar ofertas: solo productos con oferta, orden y límite; sección vacía sin ofertas.
- [x] 3.4 Probar categorías con conteo, categoría vacía y exclusión de productos no disponibles.
- [x] 3.5 Probar locales: 6 en exploración, listado completo, orden por número y exclusión de inactivos.
- [x] 3.6 Probar `has_offer=true`, ausencia del filtro y combinación con categoría o precio.
- [x] 3.7 Mantener las 281 pruebas existentes pasando.

## 4. Frontend: API y componentes

- [x] 4.1 Crear tipos y cliente API para exploración y listado de locales.
- [x] 4.2 Crear `StoreCard` reutilizable con logo o marcador, número, nombre y descripción.
- [x] 4.3 Configurar las claves de TanStack Query para exploración y locales.

## 5. Frontend: página `/explorar`

- [x] 5.1 Crear la ruta pública `/explorar`.
- [x] 5.2 Implementar la sección de destacados con `ProductCard`.
- [x] 5.3 Implementar la sección de ofertas con enlace a `/buscar?has_offer=true`.
- [x] 5.4 Implementar categorías con conteo y enlace al buscador filtrado.
- [x] 5.5 Implementar la sección de locales y el enlace al listado completo.
- [x] 5.6 Implementar enlaces "Ver todos los productos" y estados de carga, error y vacío.

## 6. Frontend: listado de locales y buscador

- [x] 6.1 Crear la página pública `/locales` con todos los locales y enlace a su ficha.
- [x] 6.2 Añadir el filtro "Solo ofertas" al buscador, leyendo `has_offer` de la URL y enviándolo a la API.
- [x] 6.3 Enlazar `/explorar` desde la página de inicio.
- [x] 6.4 Mantener los enlaces de productos a `/productos/{id}` y de locales a `/locales/{id}`.

## 7. Pruebas del frontend

- [x] 7.1 Probar la portada con destacados, ofertas, categorías y locales.
- [x] 7.2 Probar el enlace "Ver todas las ofertas" con `has_offer=true`.
- [x] 7.3 Probar el listado de locales y su navegación.
- [x] 7.4 Probar estados de carga, error y secciones vacías.
- [x] 7.5 Probar el filtro de ofertas en el buscador.
- [x] 7.6 Ejecutar `npm test -- --run` y `npm run build`.

## 8. Verificación de integración

- [x] 8.1 Con el stack levantado, explorar sin sesión y verificar las secciones.
- [x] 8.2 Verificar la navegación a producto, local, categoría y ofertas.
- [x] 8.3 Verificar que productos eliminados, inactivos o de locales inactivos no aparecen.
- [x] 8.4 Verificar el listado completo de locales.
- [x] 8.5 Validar el cambio con `openspec validate public-explore --strict` y registrar los resultados.

## Workflow follow-up

- Revisar y archivar después de la verificación.
- No implementar curaduría de destacados, CU #5 ni CU #10.
