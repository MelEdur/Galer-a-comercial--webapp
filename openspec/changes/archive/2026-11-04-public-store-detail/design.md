# Diseño

## Context

Ver `proposal.md` para la motivación y `specs/store-detail/spec.md` para los requisitos. Los datos del local ya se administran en CU #9 (`stores`, `store_hours`, `store_links`). El detalle de producto ya devuelve el resumen del local con su `id`, lo que permite enlazar a la ficha. No existe endpoint público de local.

## Goals / Non-Goals

**Goals:**

- Ficha pública completa reutilizando el esquema existente.
- Horarios y enlaces tal como los administra el comerciante, sin duplicar datos.
- Navegación natural desde el detalle de producto.

**Non-Goals:**

- Búsqueda o listado de locales.
- Mapa.
- Productos del local.
- Edición o datos internos.

## Decisions

### 1. Endpoint en el módulo público existente

Se añade `GET /api/public/stores/{store_id}` al router de `public_catalog`, sin autenticación. Se reutiliza `get_db` y el patrón de schemas/servicio existente. No se crea un módulo nuevo.

### 2. Disponibilidad

Solo se devuelven locales con `is_active = true`. Un local inactivo o inexistente responde `404`, igual que el detalle de producto.

### 3. Schemas

- `PublicStoreHour`: `day_of_week`, `opens_at`, `closes_at`.
- `PublicStoreLink`: `label`, `url`, `position`.
- `PublicStoreProfile`: `id`, `number`, `name`, `description`, `logo_url`, `email`, `phone`, `whatsapp`, `hours`, `links`.

Horarios ordenados por `(day_of_week, opens_at)`; enlaces por `position`. Se cargan con `selectinload` para evitar N+1. No se exponen `is_active`, `side`, `position` ni productos.

El nombre `PublicStoreProfile` evita colisión con el `PublicStoreDetail` que ya usa el detalle de producto.

### 4. Frontend

- Ruta pública `/locales/:storeId`.
- `StoreDetailPage` con `useQuery` a `GET /public/stores/{id}`.
- Cabecera con logo o marcador "Sin logo", nombre y "Local {number}".
- Descripción si existe.
- Horarios: se agrupan por día de lunes a domingo. Si el local tiene al menos un tramo, se muestran los siete días y los que no tienen tramos indican "Cerrado". Si no tiene ningún tramo, se oculta la sección.
- Contacto: correo (`mailto:`), teléfono (`tel:`) y WhatsApp (`https://wa.me/` con solo dígitos). Se oculta si no hay ninguno.
- Enlaces: lista ordenada, abierta en pestaña nueva con `rel="noreferrer"`. Se oculta si está vacía.
- Estados: carga, error y `404` con enlace a `/buscar`.
- Sin productos ni mapa.

### 5. Integración con el detalle de producto

La sección "Local" del detalle de producto envuelve el nombre del local en un `Link` a `/locales/{product.store.id}`. No se modifica el contrato del endpoint de producto.

### 6. Sin cambios de datos

No hay migraciones ni dependencias. La información mostrada es exactamente la que el comerciante guarda en CU #9.

## Risks / Trade-offs

- **Día sin tramos** → se muestra "Cerrado"; si el comerciante no cargó horarios, puede ser inexacto, pero es la decisión de producto acordada.
- **Datos incompletos** → secciones ocultas; el visitante puede ver una ficha con poca información.
- **Logo externo** → depende de una URL accesible; si falla, el navegador muestra la imagen rota. Se usa un `onError` para caer al marcador.
- **Enlaces externos** → se abren en pestaña nueva con `noreferrer` para evitar filtrar el referente.
- **Sin listado de locales** → la ficha solo se descubre desde un producto o por URL directa; CU #2 añadirá el listado.

## Migration Plan

No hay cambios de esquema. Se despliega el backend y luego la página `/locales/:storeId`; el enlace desde el detalle de producto empieza a funcionar.

Rollback: retirar el endpoint y la ruta; no hay datos que migrar.

## Open Questions

Ninguna que afecte al esquema o al alcance. El listado público de locales y el mapa quedan para CU #2 y CU #5.
