# Tasks

## 1. Backend: schemas y consulta

- [x] 1.1 Crear `app/modules/merchant_store/` con `__init__.py`, schemas, servicio y router; registrar el router bajo `/api`.
- [x] 1.2 Implementar `StoreRead`, `StoreUpdate`, `StoreHourRead` y `StoreLinkRead` con `extra="forbid"`, límites y validaciones.
- [x] 1.3 Implementar `GET /api/merchant/store` con local derivado del token, horarios y enlaces ordenados.

## 2. Backend: actualización

- [x] 2.1 Implementar la actualización de datos generales y contacto, recortando cadenas y guardando nulos.
- [x] 2.2 Implementar la validación y el reemplazo atómico de horarios, rechazando duplicados y cierres inválidos.
- [x] 2.3 Implementar la validación y el reemplazo atómico de enlaces, con máximo diez y URLs únicas.
- [x] 2.4 Implementar `PUT /api/merchant/store`, traduciendo errores a `422` y devolviendo el local actualizado.
- [x] 2.5 Asegurar que `store_id`, `number`, `side`, `position` e `is_active` no se aceptan en el payload.

## 3. Pruebas del backend

- [x] 3.1 Probar consulta correcta, con y sin datos opcionales.
- [x] 3.2 Probar actualización de nombre, descripción, logo y contacto.
- [x] 3.3 Probar nombre vacío, longitudes, logo inválido y correo inválido.
- [x] 3.4 Probar varios tramos por día, día cerrado, cierre inválido, día fuera de rango y duplicados.
- [x] 3.5 Probar enlaces válidos, orden, URL inválida, URL repetida, más de diez y lista vacía.
- [x] 3.6 Probar que el reemplazo de horarios y enlaces no deja datos parciales si falla.
- [x] 3.7 Probar autorización: `401` sin token, `403` admin, `403` sin local.
- [x] 3.8 Probar rechazo de `store_id` y campos desconocidos con `422`.
- [x] 3.9 Mantener las 225 pruebas existentes pasando.

## 4. Frontend: API y tipos

- [x] 4.1 Crear tipos y cliente API para consultar y actualizar el local.
- [x] 4.2 Configurar las claves de TanStack Query para el local.

## 5. Frontend: página de administración

- [x] 5.1 Crear la ruta protegida `/comerciante/local`.
- [x] 5.2 Implementar la carga de datos y el estado de carga/error.
- [x] 5.3 Implementar la sección de datos generales con vista previa del logo.
- [x] 5.4 Implementar la sección de contacto.
- [x] 5.5 Implementar el editor de horarios por día con varios tramos.
- [x] 5.6 Implementar el editor de enlaces con agregar/quitar y límite de diez.
- [x] 5.7 Mostrar número, lado y posición como solo lectura.
- [x] 5.8 Implementar guardado, confirmación y errores `422` sin perder datos.
- [x] 5.9 Tras guardar, refrescar la identidad de la sesión y navegar al panel con los datos actualizados.

## 6. Frontend: panel y pruebas

- [x] 6.1 Enlazar la información del local desde el panel y dejar Estadísticas como "Próximamente".
- [x] 6.2 Probar carga, edición, guardado y confirmación.
- [x] 6.3 Probar agregar/quitar horarios y enlaces.
- [x] 6.4 Probar errores de validación y de sesión.
- [x] 6.5 Ejecutar `npm test -- --run` y `npm run build`.
- [x] 6.6 Probar que al guardar se vuelve al panel y que la sesión se refresca con el local actualizado.

## 7. Verificación de integración

- [x] 7.1 Con el stack levantado, guardar datos generales, contacto, horarios y enlaces.
- [x] 7.2 Recargar y verificar la persistencia.
- [x] 7.3 Verificar que el detalle público muestra el logo y contacto actualizados.
- [x] 7.4 Verificar `403` para administrador y `401` sin token.
- [x] 7.5 Validar el cambio con `openspec validate merchant-store-settings --strict` y registrar los resultados.

## Workflow follow-up

- Revisar y archivar después de la verificación.
- No implementar CU #4, CU #5 ni CU #10.
