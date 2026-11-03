# Propuesta

## Why

El CU #7 pide que el comerciante inicie sesión con sus credenciales y acceda al panel de administración de su local. El backend ya autentica cualquier cuenta activa desde `admin-authentication`, pero la experiencia sigue siendo exclusivamente administrativa: el login redirige siempre a `/admin`, el texto indica "cuenta de administrador", la ruta protegida asume rol `admin` y no existe un panel para el comerciante.

Este cambio completa el CU #7 sin reimplementar el login ni las funcionalidades del CU #6, y sin adelantar productos, información del local o estadísticas.

## What Changes

- Se amplía `GET /api/auth/me` para incluir el local asignado (`id`, `number`, `name`) cuando la cuenta es un comerciante.
- El frontend redirige tras el login según el rol: administrador a `/admin` y comerciante a `/comerciante`.
- Se neutraliza el texto del login para que sirva a ambos roles.
- `ProtectedRoute` redirige al panel propio cuando el rol no corresponde a la ruta.
- Se añade la página `/comerciante` con nombre, correo, número y nombre del local, cierre de sesión y marcadores "Próximamente" para CU #8/#9/#10.
- Se manejan credenciales incorrectas, cuentas inactivas y sesiones vencidas o inválidas.
- Se añaden pruebas de backend y frontend del acceso del comerciante y de la separación de roles.

### Alcance

- Sesión del comerciante y acceso a su panel mínimo.
- Datos del local en la identidad de la sesión.
- Separación de rutas por rol.
- Pruebas de login, sesión y redirección.

### Fuera de alcance

- Login del administrador (ya implementado).
- Alta y baja de comerciantes (CU #6, ya implementado).
- Administración de productos (CU #8), información del local (CU #9) y estadísticas (CU #10).
- Cambio o recuperación de contraseña.
- Refresh tokens, rate limiting y bloqueo por intentos.
- Nuevos roles o permisos granulares.
- Endpoints `require_merchant` sin consumidor: se añadirán con CU #8/#9/#10.

## Capabilities

### New Capabilities

- `merchant-portal`: inicio de sesión del comerciante, contexto de su local, panel mínimo y separación de rutas por rol.

### Modified Capabilities

- `admin-authentication`: el requisito **Identidad de la sesión** incorpora el local asignado cuando la cuenta lo tiene.

## Impact

- **Backend modificado:** `app/modules/auth/schemas.py` (`UserRead` con `store`), `app/modules/auth/router.py` (carga del local), pruebas de autenticación.
- **Frontend modificado:** `features/auth/` (tipos, contexto, login, ruta protegida), `app/router.tsx`, pruebas.
- **Frontend nuevo:** `pages/MerchantPage.tsx` o `features/merchant-portal/`.
- **Migraciones:** ninguna.
- **Dependencias nuevas:** ninguna.
- **API:** `GET /api/auth/me` amplía su respuesta; no se añaden endpoints.
- **Funcionalidades existentes:** el login de administrador y el panel de comerciantes del CU #6 no cambian de comportamiento.
- **Dependencias:** `admin-authentication`, `merchant-administration` y `domain-model`.

## Decisiones adoptadas

- El identificador de acceso es el correo electrónico.
- El local se obtiene ampliando `/auth/me`, sin endpoint adicional.
- Panel mínimo, sin funcionalidades de otros casos de uso.
- Redirección al panel propio según rol.
- Token en `sessionStorage` (decisión vigente de `admin-authentication`).
- Sin rate limiting; el `401` uniforme se mantiene.
