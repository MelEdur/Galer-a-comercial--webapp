# Tasks

## 1. Dependencias y configuración

- [x] 1.1 Añadir `bcrypt`, `PyJWT` y `email-validator` a `backend/requirements.txt`; verificar la instalación en un entorno limpio.
- [x] 1.2 Incorporar `jwt_secret`, `jwt_algorithm` y `jwt_expire_minutes` a `Settings`; verificar que el arranque falla con un mensaje claro si falta `JWT_SECRET`.
- [x] 1.3 Actualizar `.env.example`, `.env` local y `docker-compose.yml` con las variables nuevas; verificar que el contenedor arranca con ellas.

## 2. Modelo y migración

- [x] 2.1 Añadir `full_name` a `User` y crear la revisión `0002` que agrega `users.full_name` NOT NULL; verificar `upgrade` y `downgrade`.
- [x] 2.2 Confirmar que `alembic check` no detecta diferencias entre modelos y esquema.

## 3. Seguridad y autenticación

- [x] 3.1 Implementar el hash y la verificación de contraseñas con `bcrypt`, incluyendo el límite de 72 bytes; verificar con pruebas unitarias.
- [x] 3.2 Implementar la emisión y decodificación de JWT con expiración configurable; verificar token válido, alterado y vencido.
- [x] 3.3 Implementar `POST /api/auth/login` y `GET /api/auth/me`; verificar `200`, `401` uniforme y ausencia de datos sensibles.
- [x] 3.4 Implementar la dependencia `require_admin`; verificar `401` sin token y `403` con rol comerciante.

## 4. Administrador inicial

- [x] 4.1 Crear `backend/scripts/create_admin.py` idempotente con variables de entorno; verificar creación y ejecución repetida.
- [x] 4.2 Documentar en el `README.md` las variables y el comando de creación del administrador.

## 5. Pruebas del backend

- [x] 5.1 Probar login válido, contraseña incorrecta, correo inexistente, cuenta inactiva, token inválido y token vencido.
- [x] 5.2 Probar `require_admin` con administrador, comerciante y sin token.
- [x] 5.3 Probar el script del administrador: creación, idempotencia y variables faltantes.
- [x] 5.4 Ejecutar la suite completa del backend y confirmar que los cambios no rompen el health check.

## 6. Frontend

- [x] 6.1 Implementar el cliente de autenticación, los tipos y el contexto con token en `sessionStorage`; verificar persistencia y limpieza.
- [x] 6.2 Extender `lib/http.ts` para adjuntar el token y tratar `401`; verificar que las peticiones autenticadas incluyen la cabecera.
- [x] 6.3 Implementar la página de login con estados de carga y error; verificar credenciales válidas e inválidas.
- [x] 6.4 Implementar `ProtectedRoute` y la ruta administrativa; verificar la redirección sin sesión y el acceso con sesión.
- [x] 6.5 Añadir pruebas de login, redirección y cierre de sesión; ejecutar `npm test -- --run` y `npm run build`.

## 7. Verificación de integración

- [x] 7.1 Levantar el stack y crear el administrador inicial; verificar login manual y consulta de identidad.
- [x] 7.2 Verificar que un comerciante recibe `403` en una ruta administrativa (con datos de prueba).
- [x] 7.3 Validar el cambio con `openspec validate admin-authentication --strict` y registrar los resultados.

## Workflow follow-up

- Revisar y archivar antes de implementar `merchant-administration`, que depende de esta capability.
- No implementar el login del comerciante ni su panel.
