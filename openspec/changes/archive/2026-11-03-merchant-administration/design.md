# Diseño

## Context

Ver `proposal.md` para la motivación y `specs/merchant-administration/spec.md` para los requisitos. El cambio depende de `admin-authentication` (JWT, `require_admin`, bcrypt y `users.full_name`). El dominio ya tiene `users` y 21 `stores`; no hay endpoints de negocio.

## Goals / Non-Goals

**Goals:**

- Implementar el CU #6 de punta a punta con reglas en el servicio y respaldo en la base.
- Resolver la reasignación de locales tras una baja sin romper el histórico.
- Mantener el panel simple y sin estado global innecesario.

**Non-Goals:**

- Edición de comerciantes, reactivación o cambio de contraseña.
- Paginación, búsqueda o filtros.
- Notificaciones por correo.
- Login o panel del comerciante.

## Decisions

### 1. Unicidad solo entre comerciantes activos

La revisión `0003` elimina el índice `uq_users_store_merchant` y lo vuelve a crear como:

```sql
CREATE UNIQUE INDEX uq_users_store_merchant
ON users (store_id)
WHERE role = 'merchant' AND is_active;
```

El comerciante inactivo conserva `store_id` (histórico) y el local queda libre para un reemplazo.

Alternativas descartadas: `store_id = NULL` al dar de baja (pierde el histórico y exige relajar el CHECK); mantener el índice actual (impide reasignar sin borrado físico).

### 2. API administrativa

- `GET /api/admin/merchants` → lista ordenada por nombre.
- `POST /api/admin/merchants` → `201` con `MerchantRead`.
- `DELETE /api/admin/merchants/{merchant_id}` → `204`, idempotente.
- `GET /api/admin/stores` → 21 locales ordenados por número, con `merchant` activo o `null`.

Todas las rutas usan `Depends(require_admin)`.

`MerchantRead`: `id`, `email`, `full_name`, `is_active`, `created_at`, `store` (`id`, `number`, `name`) o `null`.
`MerchantCreate`: `email` (`EmailStr`), `full_name` (1–120), `password` (8–72), `store_id`.
`StoreAdminRead`: `id`, `number`, `name`, `side`, `position`, `is_active`, `merchant` (`id`, `full_name`, `email`) o `null`.

### 3. Reglas en el servicio y respaldo en la base

El servicio normaliza el correo a minúsculas, valida el local, verifica que no haya comerciante activo y crea la cuenta con `hash_password`. Ante una carrera, el índice único y el índice de correo producen `IntegrityError`, que se traduce a `409` con un mensaje específico. El router no contiene reglas de negocio.

Alternativa descartada: confiar solo en comprobaciones previas (vulnerable a concurrencia).

### 4. Baja lógica idempotente

`DELETE` busca una cuenta con rol `merchant`; si no existe responde `404`. Si existe, fija `is_active = False` y confirma. Repetir la operación devuelve `204`. No se modifican `email`, `full_name` ni `store_id`.

### 5. Consulta de disponibilidad

Una sola consulta con `outerjoin` a comerciantes activos devuelve los 21 locales y su comerciante. Se evita N+1. Como el conjunto es fijo y pequeño, no hay paginación.

### 6. Panel con TanStack Query

- `useQuery(['admin','merchants'])` y `useQuery(['admin','stores'])`.
- Alta con `useMutation`; al éxito invalida ambas consultas.
- Baja con `useMutation` y confirmación explícita; invalida ambas consultas.
- El selector solo muestra locales sin comerciante activo.
- Errores `409`, `403` y `401` se muestran en el formulario o en la página.
- La ruta `/admin/comerciantes` se envuelve en `ProtectedRoute` de `admin-authentication`.

### 7. Sin cambios de infraestructura

No se añaden dependencias ni variables de entorno. El backend ya tiene `bcrypt` y `require_admin` desde el cambio A.

## Risks / Trade-offs

- **Carrera al asignar el mismo local** → el índice único parcial la resuelve y se traduce a `409`.
- **Listado crece con muchos comerciantes** → hoy son pocos; se añadirá paginación cuando el volumen lo justifique.
- **Comerciante inactivo conserva el local** → puede confundir si se listan inactivos; el panel muestra el estado y el endpoint de locales solo considera activos.
- **Sin edición ni reactivación** → si se requiere, será un cambio posterior.
- **Dependencia estricta de `admin-authentication`** → no se puede implementar ni probar el CU #6 sin ese cambio.

## Migration Plan

1. Aplicar `admin-authentication`.
2. Crear la revisión `0003` con el nuevo índice.
3. `alembic upgrade head` y `alembic check`.
4. Verificar alta, baja y reasignación.
5. Rollback: se recrea el índice original; fallará si existen dos comerciantes del mismo local (uno inactivo y uno activo), por lo que el rollback requiere resolver esos datos.

## Open Questions

Ninguna que afecte al alcance o al esquema. La reactivación y la edición de comerciantes quedan para cambios posteriores.
