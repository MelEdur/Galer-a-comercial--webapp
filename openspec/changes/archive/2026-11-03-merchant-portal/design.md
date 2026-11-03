# Diseño

## Context

Ver `proposal.md` para la motivación y `specs/merchant-portal/spec.md` para los requisitos. `admin-authentication` ya expone `POST /api/auth/login` para cualquier cuenta activa, `GET /api/auth/me`, JWT y `sessionStorage`. `merchant-administration` garantiza que todo comerciante tiene local. La brecha es de experiencia y de datos del local, no de autenticación.

## Goals / Non-Goals

**Goals:**

- Completar el CU #7 reutilizando el login existente.
- Separar las rutas de administrador y comerciante sin duplicar la autenticación.
- Mostrar el local del comerciante con una sola consulta de identidad.

**Non-Goals:**

- Nuevos endpoints de negocio, `require_merchant` sin consumidor, refresh tokens o rate limiting.
- Funcionalidades de CU #8/#9/#10.

## Decisions

### 1. Ampliar `/api/auth/me` con el local

`UserRead` incorpora `store: {id, number, name} | null`. El router carga el local del usuario autenticado y devuelve el schema, no la entidad ORM. El administrador recibe `null`; el comerciante, su local.

Alternativas descartadas: `GET /api/merchant/store` (superficie nueva que se solapa con CU #9) y usar solo `store_id` (el panel no podría mostrar número ni nombre).

Se actualiza el requisito **Identidad de la sesión** de `admin-authentication`.

### 2. Redirección por rol en el frontend

`login` devuelve el `CurrentUser` además de actualizar el contexto. `LoginPage` navega a `/admin` o `/comerciante` según `user.role`. `ProtectedRoute` recibe el rol requerido y, si el usuario autenticado tiene el otro rol, redirige a su propio panel en lugar de mostrar un error.

Alternativa descartada: páginas de login separadas; duplican formulario, validación y manejo de sesión.

### 3. Panel mínimo del comerciante

`/comerciante` muestra nombre, correo, número y nombre del local, y un botón de cierre de sesión. Las secciones de CU #8/#9/#10 aparecen como "Próximamente" deshabilitadas, sin llamadas a la API. No se crea navegación ni lógica de esos casos de uso.

Alternativa descartada: panel vacío (no acredita que sea el panel de su local) y resumen con datos (amplía el alcance).

### 4. Sesión inválida

`AuthProvider` ya valida el token al montar y limpia `sessionStorage` si `/auth/me` responde `401`. Se conserva ese comportamiento y se prueba explícitamente. No se añade comprobación periódica: el panel mínimo no mantiene datos sensibles en pantalla y la siguiente petición autenticada volvería a fallar cerrando la sesión.

### 5. Sin nuevas dependencias ni migraciones

El backend y el frontend tienen todo lo necesario. El cambio es de contrato de respuesta, rutas y componentes.

### 6. Sin `require_merchant` por ahora

Ningún endpoint de este CU lo necesita: `/auth/me` sirve a ambos roles. Se añadirá cuando CU #8/#9/#10 expongan rutas propias del comerciante, evitando dependencias sin consumidor.

## Risks / Trade-offs

- **Datos del local embebidos en la sesión** → pueden quedar desactualizados si el local cambia; el frontend los refresca al recargar o volver a validar la sesión.
- **Redirección por rol** → un error en el rol por defecto podría provocar bucles; `ProtectedRoute` exige rol explícito y las rutas lo declaran.
- **Token accesible por JavaScript** → riesgo ya aceptado en `admin-authentication`; se mantiene `sessionStorage`.
- **Sin rate limiting** → el `401` uniforme evita enumeración, pero no fuerza bruta; se documenta como mejora futura.

## Migration Plan

No hay cambios de esquema. Se despliega el backend y luego el frontend; el contrato amplía un campo sin romper consumidores existentes.

Rollback: revertir el schema `UserRead` y las rutas del frontend; no hay datos que migrar.

## Open Questions

Ninguna. El rate limiting, el refresh token y `require_merchant` quedan para cambios posteriores.
