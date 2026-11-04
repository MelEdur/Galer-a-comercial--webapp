# Propuesta

## Why

El CU #9 pide que el comerciante consulte y modifique la información pública de su local: nombre, logo, descripción, contacto, horarios y enlaces. El modelo ya contiene todos esos datos, pero no existe ningún endpoint ni pantalla que permita gestionarlos: el panel del comerciante muestra "Información del local" como funcionalidad no disponible.

Este cambio implementa únicamente la administración del local propio, sin consulta pública del local ni mapa.

## What Changes

- Se añade `GET /api/merchant/store` para consultar el local del comerciante autenticado.
- Se añade `PUT /api/merchant/store` para actualizar nombre, descripción, logo, contacto, horarios y enlaces.
- El local se deriva siempre de `current_user.store_id`; ningún payload acepta `store_id`.
- Se validan longitudes, correo, URL del logo, teléfonos, tramos horarios y enlaces.
- Horarios y enlaces se reemplazan completos en cada guardado.
- Se añade la página protegida `/comerciante/local` con formulario por secciones.
- Se enlaza la información del local desde el panel del comerciante.
- Se añaden pruebas de backend y frontend, incluyendo autorización y aislamiento.

### Alcance

- Consulta y edición del local propio.
- Datos generales, contacto, horarios semanales y enlaces externos.
- Validaciones de backend y frontend.
- Persistencia y recarga de los cambios.

### Fuera de alcance

- Consulta pública de la información del local (CU #4) y mapa (CU #5).
- Subida de archivos o almacenamiento de imágenes: el logo es una URL.
- Horarios que cruzan medianoche, excepciones, feriados o cierres temporales.
- Edición de número, lado, posición o estado del local.
- Productos, categorías, estadísticas y cuentas.
- Redes sociales como campos fijos: se cubren con enlaces externos.

## Capabilities

### New Capabilities

- `merchant-store-settings`: consulta y actualización del local propio, con datos generales, contacto, horarios y enlaces, validaciones y control de propiedad.

### Modified Capabilities

- `merchant-portal`: el panel del comerciante deja de mostrar la información del local como no disponible y enlaza a su administración.

## Impact

- **Backend nuevo:** `app/modules/merchant_store/` (schemas, servicio, router) y pruebas.
- **Backend modificado:** `app/main.py` para registrar el router.
- **Frontend nuevo:** `features/merchant-store/` (API, tipos, página, formulario, editor de horarios, editor de enlaces) y ruta `/comerciante/local`.
- **Frontend modificado:** `app/router.tsx` y `pages/MerchantPage.tsx`.
- **Migraciones:** ninguna; `stores`, `store_hours` y `store_links` ya existen.
- **Dependencias nuevas:** ninguna.
- **API:** `GET /api/merchant/store` y `PUT /api/merchant/store`.
- **Funcionalidades existentes:** CU #6, #7, #8, búsqueda, detalle público y health check no cambian.
- **Dependencias:** `domain-model`, `admin-authentication`, `merchant-administration` y `merchant-portal`.

## Decisiones adoptadas

- Logo mediante URL http/https, sin subida de archivos.
- Horarios como tramos semanales; el conjunto se reemplaza al guardar.
- Contacto limitado a email, teléfono y WhatsApp.
- Enlaces genéricos de etiqueta + URL, máximo diez.
- Solo el nombre es obligatorio; el resto puede quedar nulo.
- Un único formulario y un único `PUT` para guardar todo.
- Número, lado, posición y estado son de solo lectura.
- Tramo horario dentro del mismo día: el cierre debe ser posterior a la apertura.
