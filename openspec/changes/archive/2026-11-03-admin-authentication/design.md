# Diseño

## Context

Ver `proposal.md` para la motivación y `specs/admin-authentication/spec.md` para los requisitos. La tabla `users` existe con `email`, `password_hash`, `role`, `is_active` y `store_id`, pero no tiene nombre completo y no hay ninguna capa de autenticación. El backend usa SQLAlchemy 2.0 síncrono y el frontend React con Fetch y TanStack Query.

Restricciones:

- Stack fijo; solo se añaden dependencias justificadas de seguridad y validación.
- No se implementa el login del comerciante (CU #7).
- El token debe vivir en `sessionStorage` (decisión del usuario).

## Goals / Non-Goals

**Goals:**

- Autenticar administradores y exponer una dependencia de autorización simple.
- Reutilizar el mismo login para el CU #7 sin reescribirlo.
- Mantener el flujo comprensible y verificable con pruebas.

**Non-Goals:**

- Refresh tokens, revocación, recuperación de contraseña o verificación por correo.
- Sesiones del lado del servidor o cookies.
- Permisos por recurso más allá del rol.

## Decisions

### 1. JWT con HS256

`POST /api/auth/login` valida credenciales y emite un JWT con `sub` (id), `role`, `iat` y `exp`. La firma usa `JWT_SECRET` y el algoritmo configurable (por defecto HS256). `require_admin` decodifica el token, carga la cuenta y exige `is_active` y `role == "admin"`.

Alternativas descartadas: sesiones en base de datos (más estado y limpieza), HTTP Basic (reenvía credenciales en cada petición y no diferencia roles con comodidad).

### 2. Token en `sessionStorage`

El frontend guarda el token en `sessionStorage` bajo una clave única y lo adjunta como `Authorization: Bearer`. Al cerrar sesión se elimina. Se descarta `localStorage` para no persistir el token entre pestañas ni sesiones del navegador. Se documenta el riesgo de XSS inherente a cualquier almacenamiento accesible por JavaScript.

Alternativa descartada: cookie `httpOnly` (más resistente a XSS, pero exige manejo CSRF y no fue la opción elegida).

### 3. `bcrypt` para contraseñas

Se usa el paquete `bcrypt` con salt por contraseña. Se valida un mínimo de 8 caracteres y un máximo de 72 bytes, límite del algoritmo. El hash nunca se serializa en respuestas.

Alternativas descartadas: `argon2-cffi` (válido, pero se eligió bcrypt), `hashlib.scrypt` (sin dependencias, pero con más código propio).

### 4. `full_name` en esta migración

`users` está vacía, así que la migración añade `full_name varchar(120) NOT NULL` directamente, sin backfill. Se actualiza también el modelo y el requisito de `domain-model`.

### 5. Respuesta uniforme ante credenciales inválidas

Correo inexistente, contraseña incorrecta y cuenta inactiva devuelven el mismo `401` con un mensaje genérico. Así no se filtra qué correos existen.

### 6. Administrador inicial por script

`python -m scripts.create_admin` lee `ADMIN_EMAIL`, `ADMIN_PASSWORD` y `ADMIN_FULL_NAME`. Si el correo ya existe, no modifica nada. No se versionan credenciales; `.env.example` solo contiene placeholders.

### 7. Configuración

`Settings` incorpora `jwt_secret` (obligatorio), `jwt_algorithm` y `jwt_expire_minutes` (60 por defecto). Un secreto ausente impide el arranque, igual que `DATABASE_URL`.

### 8. Autorización en el frontend

`AuthProvider` expone el token, el usuario y las acciones de login/logout. `ProtectedRoute` redirige a `/login` si no hay token y `GET /api/auth/me` falla. El backend sigue siendo la autoridad final: la protección de rutas es solo de experiencia de usuario.

## Risks / Trade-offs

- **Token accesible por JavaScript** → expiración corta y ausencia de datos sensibles en el token; se documenta y se acepta.
- **Sin refresh token** → al vencer, el usuario debe volver a iniciar sesión; aceptable para un panel administrativo.
- **`JWT_SECRET` obligatorio** → hay que actualizar `.env`, `.env.example` y Compose; se documenta en el README.
- **bcrypt y 72 bytes** → validación explícita de longitud para evitar truncamientos silenciosos.
- **Script de administrador** → si se ejecuta con credenciales débiles, la seguridad depende del operador; se recomienda una contraseña fuerte.

## Migration Plan

1. Añadir dependencias y configuración.
2. Crear la revisión `0002` que añade `users.full_name`.
3. Aplicar la migración y ejecutar el script del administrador.
4. Verificar login, `/auth/me` y `403` con un comerciante.
5. Rollback: la migración elimina la columna; las cuentas creadas dejarían de ser válidas, pero no hay datos productivos.

## Open Questions

Ninguna que afecte al diseño. La recuperación de contraseña y el refresh token se resolverán en cambios posteriores si el producto los requiere.
