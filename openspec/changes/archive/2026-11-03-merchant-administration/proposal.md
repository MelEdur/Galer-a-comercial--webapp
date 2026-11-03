# Propuesta

## Why

El CU #6 pide un panel donde el administrador cree y dé de baja comerciantes asignándoles un local. Hoy el modelo soporta las cuentas y los 21 locales, pero no existe ningún endpoint, servicio ni pantalla para administrarlos, y la restricción de unicidad vigente impediría reasignar el local de un comerciante dado de baja.

Este cambio implementa exclusivamente el CU #6 sobre la autenticación de administrador ya existente.

## What Changes

- Se implementa el alta de comerciantes con correo, nombre completo, contraseña inicial y local.
- Se implementa la baja lógica de comerciantes, liberando el local para un reemplazo.
- Se implementa el listado de comerciantes con su local y estado.
- Se implementa un endpoint administrativo con los 21 locales y el comerciante activo de cada uno.
- Se ajusta el índice único de comerciante por local para que solo considere cuentas activas mediante una migración reversible.
- Se añade al frontend la ruta protegida de administración con listado, formulario de alta y confirmación de baja.
- Se restringen todas las operaciones al rol `admin`.
- Se añaden pruebas de reglas de negocio, autorización y frontend.

### Alcance

- Backend: schemas, servicio, router y migración del CU #6.
- Frontend: panel de administración de comerciantes.
- Pruebas de alta, duplicados, local ocupado, baja, reasignación y autorización.

### Fuera de alcance

- Login del comerciante y su panel (CU #7).
- Edición de datos del comerciante, reactivación, cambio de contraseña o reasignación manual de local.
- Búsqueda, paginación o filtros del listado (solo 21 locales y pocos comerciantes).
- Gestión de locales (CU #9).
- Notificaciones por correo al comerciante creado.

## Capabilities

### New Capabilities

- `merchant-administration`: alta, baja y consulta de comerciantes por parte del administrador, disponibilidad de locales y panel de administración.

### Modified Capabilities

- `domain-model`: el requisito **Asignación de comerciantes a locales** pasa a limitar a un comerciante **activo** por local, conservando el local en la cuenta inactiva.

## Impact

- **Backend nuevo:** `app/modules/accounts/{schemas,service,router}.py` (o `app/modules/merchants/`), consultas de locales en `app/modules/stores/`.
- **Backend modificado:** `app/main.py` (router administrativo), `app/modules/accounts/models.py` (índice único), `app/db/registry.py` si aplica.
- **Migración:** nueva revisión que reemplaza `uq_users_store_merchant` por una variante que incluye `is_active`.
- **Dependencias nuevas:** ninguna.
- **Frontend nuevo:** `features/admin-merchants/` con API, tipos, página, formulario, tabla y pruebas.
- **Frontend modificado:** `app/router.tsx` (ruta protegida `/admin/comerciantes`).
- **API:** `GET/POST /api/admin/merchants`, `DELETE /api/admin/merchants/{id}` y `GET /api/admin/stores`.
- **Dependencias:** requiere `admin-authentication` implementado y archivado; reutiliza `require_admin`.
- **Funcionalidades existentes:** catálogo, locales y health check no cambian.
- **Dependencias futuras:** CU #7 usará las cuentas creadas aquí; CU #8 y #9 se apoyarán en el local asignado.

## Decisiones adoptadas

- Alta con `email`, `full_name`, contraseña inicial y `store_id`; rol fijado en `merchant`.
- Baja lógica e idempotente; el comerciante inactivo conserva su local como histórico.
- Unicidad de comerciante por local solo entre cuentas activas.
- Endpoint administrativo de locales con el comerciante activo o `null`.
- Sin paginación ni búsqueda por el tamaño actual del dominio.
- Errores de negocio con `409` (correo duplicado o local ocupado) y `404` (local o comerciante inexistente).
- La respuesta nunca incluye `password_hash`.
