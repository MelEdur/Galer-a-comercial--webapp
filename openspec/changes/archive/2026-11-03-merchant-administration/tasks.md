# Tasks

## 1. Modelo y migración

- [x] 1.1 Actualizar el índice `uq_users_store_merchant` en `User` para incluir `is_active`; crear la revisión `0003` que elimina y recrea el índice.
- [x] 1.2 Verificar `alembic upgrade head`, `alembic downgrade` y `alembic check`.

## 2. Backend

- [x] 2.1 Crear los schemas `MerchantCreate`, `MerchantRead`, `StoreAdminRead` y las referencias anidadas; verificar validaciones de correo, nombre, contraseña y local.
- [x] 2.2 Implementar el servicio de comerciantes: listar, crear con hash y validaciones, dar de baja de forma idempotente y listar locales con disponibilidad.
- [x] 2.3 Implementar el router administrativo con `GET/POST /api/admin/merchants`, `DELETE /api/admin/merchants/{id}` y `GET /api/admin/stores`, protegido con `require_admin`.
- [x] 2.4 Traducir los errores de negocio a `404`, `409` y `422` sin exponer detalles internos; verificar que no se devuelve `password_hash`.

## 3. Pruebas del backend

- [x] 3.1 Probar listado vacío y con comerciantes; verificar que no se expone el hash.
- [x] 3.2 Probar alta correcta, correo duplicado, local ocupado, local inexistente y datos inválidos.
- [x] 3.3 Probar baja correcta, baja repetida, identificador inexistente y liberación del local.
- [x] 3.4 Probar reasignación del local tras la baja y que un segundo comerciante activo en el mismo local devuelve `409`.
- [x] 3.5 Probar autorización: administrador permitido, comerciante `403` y sin token `401`.
- [x] 3.6 Ejecutar la suite completa y confirmar que el health check sigue funcionando.

## 4. Frontend

- [x] 4.1 Crear tipos y cliente API para comerciantes y locales administrativos.
- [x] 4.2 Implementar la página `/admin/comerciantes` protegida con listado, estado de carga, error y estado vacío.
- [x] 4.3 Implementar el formulario de alta con correo, nombre completo, contraseña y selector de locales disponibles; invalidad las consultas al crear.
- [x] 4.4 Implementar la baja con confirmación y actualización del listado y de la disponibilidad.
- [x] 4.5 Mostrar mensajes comprensibles para `409`, `403` y `401`.
- [x] 4.6 Añadir pruebas de listado, alta, error de local ocupado y baja; ejecutar `npm test -- --run` y `npm run build`.

## 5. Verificación de integración

- [x] 5.1 Con el stack levantado, autenticarse como administrador y crear un comerciante desde el panel.
- [x] 5.2 Verificar que el local deja de estar disponible y que un segundo intento devuelve `409`.
- [x] 5.3 Dar de baja al comerciante y verificar que el local vuelve a estar disponible.
- [x] 5.4 Verificar que un comerciante autenticado recibe `403` en las rutas administrativas.
- [x] 5.5 Validar el cambio con `openspec validate merchant-administration --strict` y registrar los resultados.

## Workflow follow-up

- Revisar y archivar después de completar la verificación.
- No implementar el login ni el panel del comerciante (CU #7).
