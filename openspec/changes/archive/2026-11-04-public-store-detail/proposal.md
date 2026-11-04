# Propuesta

## Why

El CU #4 pide que un visitante consulte la información pública de un local: nombre, logo, número, horarios, contacto y enlaces. El CU #9 ya permite al comerciante administrar todos esos datos, y el detalle de producto muestra un resumen del local, pero no existe una ficha pública del local ni un endpoint para consultarla.

Este cambio implementa exclusivamente la consulta pública de un local, sin búsqueda, feed, mapa ni administración.

## What Changes

- Se añade `GET /api/public/stores/{store_id}`, sin autenticación.
- La respuesta incluye número, nombre, descripción, logo, contacto, horarios y enlaces del local.
- Se añade la página pública `/locales/:storeId` con logo, datos generales, horarios agrupados por día, contacto y enlaces externos.
- Los días sin tramos horarios se muestran como "Cerrado".
- Las secciones sin datos se ocultan y el logo ausente se reemplaza por un marcador.
- El local mostrado en el detalle de producto enlaza a su ficha pública.
- Se añaden pruebas de backend y frontend, incluyendo local inactivo, local inexistente y datos incompletos.

### Alcance

- Ficha pública de un local activo.
- Horarios, contacto y enlaces administrados por CU #9.
- Navegación desde el detalle de producto.
- Estados de carga, error y local no encontrado.

### Fuera de alcance

- Búsqueda o exploración de locales (CU #1 y CU #2).
- Mapa interactivo (CU #5).
- Administración de la información del local (CU #9).
- Productos del local, reseñas, favoritos o carrito.
- Horarios especiales, feriados o excepciones.
- Edición de cualquier dato.

## Capabilities

### New Capabilities

- `store-detail`: consulta pública de la información de un local, horarios, contacto, enlaces, datos incompletos y navegación desde el detalle de producto.

### Modified Capabilities

Ninguna. La ficha del local es una capability nueva y no cambia el contrato de búsqueda, detalle de producto ni administración del local.

## Impact

- **Backend nuevo:** schemas, servicio y router público de locales dentro de `app/modules/public_catalog/` o un módulo `public_stores`; pruebas.
- **Backend modificado:** `app/main.py` para registrar el router si se crea uno nuevo.
- **Frontend nuevo:** `features/store-detail/` (API, tipos, página, horarios, contacto, enlaces) y ruta `/locales/:storeId`.
- **Frontend modificado:** `app/router.tsx` y la sección de local del detalle de producto para enlazar a la ficha.
- **Migraciones:** ninguna; `stores`, `store_hours` y `store_links` ya existen.
- **Dependencias nuevas:** ninguna.
- **API:** `GET /api/public/stores/{store_id}`.
- **Funcionalidades existentes:** búsqueda, detalle de producto, CU #6, #7, #8, #9, autenticación y health check no cambian de comportamiento.
- **Dependencias:** `domain-model`, `merchant-store-settings` y `product-detail`.

## Decisiones adoptadas

- Identificador público: id interno del local; el número se muestra en la ficha.
- La descripción del local se incluye.
- Los días sin tramos muestran "Cerrado".
- Las secciones sin datos se ocultan; sin logo se muestra un marcador.
- El acceso principal es desde el detalle de producto, además de la URL directa.
- Solo se exponen locales activos; el resto responde `404`.
- No se incluyen productos ni ubicación en el mapa.
