# Tasks

## 1. Backend: identidad con local

- [x] 1.1 Añadir `StoreSummary` y el campo `store` a `UserRead`; verificar que el administrador recibe `null`.
- [x] 1.2 Cargar el local del usuario autenticado en `GET /api/auth/me` y devolver el schema actualizado.
- [x] 1.3 Verificar que las respuestas siguen sin incluir `password_hash` ni datos sensibles.

## 2. Pruebas del backend

- [x] 2.1 Probar `/auth/me` de un comerciante con local: incluye `id`, `number` y `name`.
- [x] 2.2 Probar `/auth/me` de un administrador: `store` es `null`.
- [x] 2.3 Probar login de comerciante válido, contraseña incorrecta, correo inexistente y cuenta inactiva.
- [x] 2.4 Probar token inválido y vencido; confirmar `401`.
- [x] 2.5 Ejecutar la suite completa y confirmar que el login y el panel del CU #6 siguen funcionando.

## 3. Frontend: sesión y redirección

- [x] 3.1 Actualizar `CurrentUser` con `store` y hacer que `login` devuelva el usuario autenticado.
- [x] 3.2 Neutralizar el texto de `LoginPage` y redirigir según el rol a `/admin` o `/comerciante`.
- [x] 3.3 Extender `ProtectedRoute` para redirigir al panel propio cuando el rol no corresponde a la ruta.
- [x] 3.4 Manejar `401` de `/auth/me` limpiando la sesión y volviendo a `/login`.

## 4. Frontend: panel del comerciante

- [x] 4.1 Crear la página `/comerciante` con nombre, correo, número y nombre del local, y cierre de sesión.
- [x] 4.2 Añadir marcadores "Próximamente" para productos, información del local y estadísticas, sin lógica ni llamadas a la API.
- [x] 4.3 Registrar la ruta protegida con rol `merchant` y enlazarla desde el login.

## 5. Pruebas del frontend

- [x] 5.1 Probar login de comerciante: redirige a `/comerciante` y muestra su local.
- [x] 5.2 Probar que un administrador en `/comerciante` es redirigido a `/admin` y un comerciante en `/admin` a `/comerciante`.
- [x] 5.3 Probar sesión inválida o vencida: se limpia `sessionStorage` y se redirige a `/login`.
- [x] 5.4 Probar error `401` de credenciales: mensaje genérico y sin datos del panel.
- [x] 5.5 Ejecutar `npm test -- --run` y `npm run build`.

## 6. Verificación de integración

- [x] 6.1 Con el stack levantado, iniciar sesión como comerciante y verificar el panel con su local.
- [x] 6.2 Verificar la redirección cruzada entre `/admin` y `/comerciante`.
- [x] 6.3 Verificar que un comerciante inactivo no puede iniciar sesión.
- [x] 6.4 Verificar que el flujo del administrador y el CU #6 siguen funcionando.
- [x] 6.5 Validar el cambio con `openspec validate merchant-portal --strict` y registrar los resultados.

## Workflow follow-up

- Revisar y archivar después de la verificación.
- No implementar productos, edición del local ni estadísticas.
