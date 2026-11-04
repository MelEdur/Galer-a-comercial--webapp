# Diseño

## Context

Ver `proposal.md` para la motivación y `specs/merchant-store-settings/spec.md` para los requisitos. `stores` ya contiene los datos generales, `store_hours` los tramos y `store_links` los enlaces. `require_merchant` existe desde CU #8 y el local se obtiene de `current_user.store_id`. El panel muestra la información del local como "Próximamente".

## Goals / Non-Goals

**Goals:**

- Un único formulario para consultar y guardar todo el local.
- Validación estricta y coherente con el esquema.
- Reemplazo atómico de horarios y enlaces.

**Non-Goals:**

- Consulta pública del local, mapa o estadísticas.
- Subida de archivos.
- Horarios nocturnos, excepciones o feriados.
- Edición de número, lado, posición o estado.

## Decisions

### 1. Endpoints

- `GET /api/merchant/store` → local propio con horarios y enlaces.
- `PUT /api/merchant/store` → actualización completa y devolución del local actualizado.

Router con prefijo `/merchant`, protegido con `require_merchant`. El local se obtiene por `current_user.store_id`; no se acepta `store_id` en el payload.

### 2. Schemas

`StoreRead`:
- `id`, `number`, `side`, `position` (solo lectura);
- `name`, `description`, `logo_url`, `email`, `phone`, `whatsapp`;
- `hours`: lista de `{day_of_week, opens_at, closes_at}` ordenada;
- `links`: lista de `{label, url, position}` ordenada.

`StoreUpdate`:
- `name` obligatorio (1–120, recortado);
- `description` opcional (≤2000);
- `logo_url` opcional (`HttpUrl`, ≤500);
- `email` opcional (`EmailAddress`, ≤320);
- `phone` y `whatsapp` opcionales (≤30, caracteres permitidos);
- `hours`: lista de tramos, por defecto vacía;
- `links`: lista de enlaces, máximo 10, por defecto vacía.

Todos con `extra="forbid"`.

### 3. Horarios

- `day_of_week` entre 0 (lunes) y 6 (domingo).
- `opens_at` y `closes_at` como `time`; `closes_at` estrictamente posterior.
- Sin cruzar medianoche: un tramo que termine al día siguiente no está soportado por el CHECK actual.
- Se admiten varios tramos por día y días sin tramos.
- Duplicados exactos (mismo día y apertura) se rechazan con `422` antes de tocar la base.

### 4. Enlaces

- `label` 1–60, `url` http/https ≤500.
- Máximo 10 y sin URLs repetidas (comparación exacta tras recortar).
- El orden del array define `position`.
- Lista vacía elimina todos los enlaces.

### 5. Reemplazo atómico

En una sola transacción:

1. Actualizar los campos del local.
2. `store.hours.clear()` + `flush()` y agregar los nuevos.
3. `store.links.clear()` + `flush()` y agregar los nuevos.
4. `commit()`.

El `flush` intermedio evita conflictos con la unicidad `(store_id, day_of_week, opens_at)` y `(store_id, url)`. Si algo falla, la transacción no deja cambios parciales.

### 6. Validaciones

| Campo | Regla |
|---|---|
| `name` | 1–120, no solo espacios |
| `description` | ≤2000 |
| `logo_url` | `http`/`https`, ≤500 |
| `email` | formato válido, ≤320 |
| `phone` / `whatsapp` | ≤30, dígitos, espacios, `+`, `-`, `(` y `)` |
| `hours` | día 0–6, cierre > apertura, sin duplicados |
| `links` | ≤10, etiqueta 1–60, URL válida, sin repetidas |

Los errores devuelven `422` con detalle. El frontend también valida antes de enviar, pero el backend es la autoridad.

### 7. Frontend

- Ruta protegida `/comerciante/local` con `role="merchant"`.
- `StoreSettingsPage` carga `GET /merchant/store` y guarda con `PUT`.
- Secciones:
  - **Datos generales:** nombre, descripción, logo (URL + vista previa).
  - **Contacto:** email, teléfono, WhatsApp.
  - **Horarios:** grilla por día; agregar y quitar tramos; `input type="time"`.
  - **Enlaces:** filas etiqueta + URL; agregar y quitar; máximo 10.
- Número, lado y posición visibles como texto de solo lectura.
- Estado de carga, guardado, confirmación y errores.
- Se invalida `['merchant','store']` tras guardar.
- Tras un guardado exitoso se refresca la identidad de la sesión (`GET /auth/me`) y se navega a `/comerciante`; así el panel muestra el nombre y los datos actualizados del local.
- El panel enlaza a la página; solo Estadísticas queda como "Próximamente".

### 8. Errores

| Caso | Código |
|---|---|
| Sin token | `401` |
| Rol no comerciante o sin local | `403` |
| Local no encontrado | `404` |
| Datos inválidos, `store_id` o campos desconocidos | `422` |

## Risks / Trade-offs

- **Reemplazo completo de horarios y enlaces** → un cliente desactualizado puede sobrescribir cambios; hay un solo comerciante por local y no se implementa bloqueo optimista.
- **Sin horarios nocturnos** → limitación conocida; se resolverá si el negocio lo requiere.
- **URL de logo externa** → depende de un recurso accesible; no se almacenan archivos.
- **Validación de teléfonos permisiva** → acepta formatos habituales sin normalizar; se documenta.
- **Datos incompletos** → permitidos por decisión de producto; las vistas públicas deben manejar nulos.

## Migration Plan

No hay cambios de esquema. Se despliega el backend y luego la página `/comerciante/local`.

Rollback: retirar los endpoints y la ruta; los datos guardados permanecen y no afectan a otras funcionalidades.

## Open Questions

Ninguna que afecte al esquema o al alcance. La consulta pública del local y el mapa quedan para CU #4 y CU #5.
