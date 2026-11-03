# Propuesta

## Why

El CU #6 requiere que solo un administrador pueda crear y dar de baja comerciantes, pero el sistema no tiene autenticación de ningún tipo: no existen cuentas administradoras, ni login, ni forma de autorizar una petición. Sin esta base, el panel de administración quedaría expuesto o habría que inventar un mecanismo de acceso improvisado dentro del CU #6.

Este cambio implementa la autenticación mínima del administrador como prerrequisito aislado, reutilizable después por el CU #7 para el login del comerciante.

## What Changes

- Se añade `full_name` a `users` mediante una migración reversible.
- Se configura el secreto y la expiración de los tokens JWT por variables de entorno.
- Se implementa `POST /api/auth/login` con correo y contraseña.
- Se implementa `GET /api/auth/me` para recuperar la identidad y el rol de la sesión actual.
- Se añade la dependencia de autorización `require_admin`, que responde 401 sin token y 403 cuando el rol no es administrador.
- Se implementa el hash de contraseñas con `bcrypt`; nunca se almacenan ni se devuelven contraseñas en claro.
- Se añade un script idempotente para crear el administrador inicial desde variables de entorno.
- Se añade al frontend la página de inicio de sesión, el contexto de autenticación y una ruta protegida.
- El token se conserva en `sessionStorage` y se elimina al cerrar sesión.

### Alcance

- Autenticación de administradores por correo y contraseña.
- Autorización por rol para rutas administrativas.
- Alta del administrador inicial.
- Sesión del frontend y protección de rutas.
- Pruebas de backend y frontend del flujo de autenticación.

### Fuera de alcance

- Login del comerciante y su panel (CU #7).
- Recuperación o cambio de contraseña, verificación por correo y envío de emails.
- Registro público de usuarios.
- Refresh tokens, revocación de tokens y cierre de sesión del lado del servidor.
- Permisos granulares más allá de `admin` y `merchant`.
- Gestión de comerciantes (CU #6).

## Capabilities

### New Capabilities

- `admin-authentication`: inicio de sesión del administrador, identidad de la sesión, protección por rol, alta del administrador inicial y manejo seguro de credenciales.

### Modified Capabilities

- `domain-model`: el requisito **Cuentas de usuario** incorpora el nombre completo como dato obligatorio de la cuenta.

## Impact

- **Backend nuevo:** `app/modules/auth/` (seguridad, schemas, servicio, router), `app/core/security.py`, `app/scripts/create_admin.py` o `scripts/create_admin.py`.
- **Backend modificado:** `app/core/config.py` (JWT y expiración), `app/main.py` (router de autenticación), `app/modules/accounts/models.py` (`full_name`), `app/db/registry.py` si aplica.
- **Migración:** nueva revisión que añade `users.full_name`.
- **Dependencias nuevas:** `bcrypt`, `PyJWT` y `email-validator` (validación de correo en Pydantic).
- **Frontend nuevo:** `features/auth/` (API, tipos, contexto), página de login, componente de ruta protegida y pruebas.
- **Frontend modificado:** `app/router.tsx`, `app/providers.tsx`, `lib/http.ts`.
- **Variables de entorno:** `JWT_SECRET`, `JWT_EXPIRE_MINUTES`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `ADMIN_FULL_NAME`.
- **API:** se añaden `POST /api/auth/login` y `GET /api/auth/me`.
- **Funcionalidades existentes:** el health check y las rutas públicas no cambian.
- **Dependencias futuras:** el CU #6 consume `require_admin`; el CU #7 podrá reutilizar el login.

## Decisiones adoptadas

- Cambio independiente y previo a CU #6.
- `full_name` obligatorio, añadido en esta migración (la tabla `users` está vacía).
- JWT firmado con HS256; expiración configurable.
- Contraseñas con `bcrypt` y límite de 72 bytes.
- Token en `sessionStorage`, no en cookies.
- Administrador inicial creado por script idempotente desde variables de entorno.
- El login responde igual para credenciales inválidas, sin revelar si el correo existe.
