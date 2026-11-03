# Tasks

## 1. Base de modelos y registro de metadata

- [x] 1.1 Crear el mixin de marcas de tiempo (`created_at`, `updated_at`) y el registro de modelos que expone la metadata a Alembic; verificar que `Base.metadata` contiene todas las tablas tras importar el registro.
- [x] 1.2 Ajustar `backend/app/db/base.py` y `backend/alembic/env.py` si es necesario para que la metadata registrada sea la única fuente del esquema; verificar que el backend sigue arrancando sin crear tablas.

## 2. Modelos de cuentas

- [x] 2.1 Implementar `User` con correo único, hash de contraseña, rol `admin`/`merchant`, estado activo y local asignado; verificar la restricción de rol y la asignación obligatoria para comerciantes.
- [x] 2.2 Añadir el índice único parcial que impide más de un comerciante por local; verificar que un segundo comerciante para el mismo local es rechazado.

## 3. Modelos de locales

- [x] 3.1 Implementar `Store` con número único, lado, posición, datos de contacto y logo; verificar las restricciones de lado/posición y la unicidad de número.
- [x] 3.2 Implementar `StoreHour` con día, apertura y cierre; verificar que el cierre posterior a la apertura y que se admiten varios tramos por día.
- [x] 3.3 Implementar `StoreLink` con etiqueta, URL y orden; verificar la unicidad de URL por local y el orden de recuperación.

## 4. Modelos de catálogo

- [x] 4.1 Implementar `Category` con nombre único sin distinguir mayúsculas; verificar que un nombre duplicado es rechazado.
- [x] 4.2 Implementar `Product` con local, nombre, descripción, precio, oferta, destacado, estado y borrado lógico; verificar las restricciones de precio y de oferta.
- [x] 4.3 Implementar `ProductCategory` con clave primaria compuesta; verificar que un producto admite varias categorías y que una categoría en uso no se elimina.
- [x] 4.4 Implementar `ProductImage` con URL, orden y primaria; verificar que solo existe una imagen primaria por producto.

## 5. Modelos de analítica

- [x] 5.1 Implementar `ProductSearchEvent` con producto, término y fecha; verificar el registro por producto y los índices de consulta por producto y por rango de fechas.

## 6. Migración inicial

- [x] 6.1 Generar la revisión `0001_domain_model` con Alembic y revisar que incluya tablas, claves foráneas, restricciones e índices acordados.
- [x] 6.2 Verificar `alembic upgrade head` sobre una base vacía y `alembic downgrade base`; comprobar que no quedan diferencias pendientes con `alembic check` o autogenerate vacío.

## 7. Semilla de locales

- [x] 7.1 Crear `backend/scripts/seed_stores.py` idempotente que precargue los 21 locales con la numeración intercalada acordada; verificar una primera ejecución y una segunda sin duplicados.
- [x] 7.2 Documentar en el `README.md` el comando de precarga y su carácter idempotente.

## 8. Pruebas e integración

- [x] 8.1 Configurar fixtures de base de datos para pruebas con aislamiento por transacción sobre `app_test`; verificar que las pruebas no afectan datos de desarrollo.
- [x] 8.2 Escribir pruebas de restricciones e invariantes: unicidad de local, numeración de la semilla, asignación de comerciantes, precio y oferta, categorías, imágenes primarias y horarios.
- [x] 8.3 Escribir pruebas del registro de búsquedas: un evento por producto devuelto, conteo por rango de fechas y conservación tras el borrado lógico.
- [x] 8.4 Ejecutar la suite completa del backend y confirmar que `GET /api/health` sigue respondiendo correctamente.
- [x] 8.5 Validar el cambio con `openspec validate domain-model --strict` y registrar los resultados.

## Workflow follow-up

- Revisar la propuesta y las verificaciones antes de archivar.
- Sincronizar la spec principal al archivar.
- No se requieren tareas de frontend: este cambio no modifica contratos ni interfaz.
