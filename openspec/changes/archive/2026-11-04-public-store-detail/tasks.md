# Tasks

## 1. Backend

- [x] 1.1 Añadir `PublicStoreHour`, `PublicStoreLink` y `PublicStoreProfile` a `public_catalog/schemas.py`.
- [x] 1.2 Implementar la consulta del local activo con horarios y enlaces ordenados y `selectinload`.
- [x] 1.3 Añadir `GET /api/public/stores/{store_id}` al router público, con `404` para inexistente o inactivo.
- [x] 1.4 Verificar que la respuesta no expone `is_active`, `side`, `position`, cuentas ni productos.

## 2. Pruebas del backend

- [x] 2.1 Probar ficha sin autenticación y contrato de respuesta.
- [x] 2.2 Probar local con y sin descripción/logo y con contacto parcial.
- [x] 2.3 Probar varios tramos por día y orden de horarios y enlaces.
- [x] 2.4 Probar local sin horarios, sin contacto y sin enlaces.
- [x] 2.5 Probar `404` para local inactivo e inexistente.
- [x] 2.6 Mantener las 274 pruebas existentes pasando.

## 3. Frontend: API y tipos

- [x] 3.1 Crear tipos y cliente API para la ficha del local.
- [x] 3.2 Configurar la clave de TanStack Query `['public','store', id]`.

## 4. Frontend: página de la ficha

- [x] 4.1 Crear la ruta pública `/locales/:storeId`.
- [x] 4.2 Mostrar logo o marcador, nombre, número y descripción.
- [x] 4.3 Implementar horarios agrupados por día con "Cerrado" en días sin tramos y ocultar la sección si no hay ninguno.
- [x] 4.4 Implementar contacto con `mailto:`, `tel:` y WhatsApp, ocultando la sección si no hay datos.
- [x] 4.5 Implementar enlaces externos ordenados, en pestaña nueva y con `rel="noreferrer"`, ocultando la sección si está vacía.
- [x] 4.6 Implementar estados de carga, error y local no encontrado con enlace al buscador.
- [x] 4.7 Manejar el error de carga del logo mostrando el marcador.

## 5. Frontend: integración

- [x] 5.1 Enlazar el local del detalle de producto a `/locales/{store.id}`.
- [x] 5.2 Verificar que el enlace es accesible y no rompe el diseño.

## 6. Pruebas del frontend

- [x] 6.1 Probar la ficha completa con logo, horarios, contacto y enlaces.
- [x] 6.2 Probar días sin horario como "Cerrado" y secciones ocultas.
- [x] 6.3 Probar el marcador cuando falta el logo.
- [x] 6.4 Probar carga, error y `404`.
- [x] 6.5 Probar el enlace desde el detalle de producto.
- [x] 6.6 Ejecutar `npm test -- --run` y `npm run build`.

## 7. Verificación de integración

- [x] 7.1 Guardar datos completos desde CU #9 y abrir la ficha pública.
- [x] 7.2 Verificar logo, horarios, contacto y enlaces.
- [x] 7.3 Verificar `404` con un local inactivo y con un id inexistente.
- [x] 7.4 Verificar la navegación desde el detalle de producto.
- [x] 7.5 Validar el cambio con `openspec validate public-store-detail --strict` y registrar los resultados.

## Workflow follow-up

- Revisar y archivar después de la verificación.
- No implementar CU #1, CU #2, CU #5 ni CU #9.
