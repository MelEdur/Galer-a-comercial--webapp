# Tasks

## 1. Backend

- [x] 1.1 Añadir los schemas del mapa: local con `id`, `number`, `name`, `logo_url`, `side`, `position` y respuesta `stores`.
- [x] 1.2 Implementar la consulta de locales activos ordenados por lado (`left`, `right`, `back`) y posición.
- [x] 1.3 Añadir `GET /api/public/map` al router público, sin autenticación.

## 2. Pruebas del backend

- [x] 2.1 Probar el mapa sin token y el contrato de respuesta.
- [x] 2.2 Probar que solo se incluyen locales activos.
- [x] 2.3 Probar el orden por lado y posición.
- [x] 2.4 Probar que no se exponen datos internos ni productos.
- [x] 2.5 Mantener las 317 pruebas existentes pasando.

## 3. Frontend: API y datos

- [x] 3.1 Crear tipos y cliente API para el mapa.
- [x] 3.2 Configurar la clave de TanStack Query `['public','map']`.

## 4. Frontend: página `/mapa`

- [x] 4.1 Crear la ruta pública `/mapa`.
- [x] 4.2 Implementar el esquema con columnas izquierda/derecha, pasillo central y local del fondo.
- [x] 4.3 Renderizar cada local como enlace con número, logo, nombre y etiqueta accesible.
- [x] 4.4 Enlazar cada local directamente a `/locales/{id}` y eliminar el panel de selección.
- [x] 4.5 Implementar estados de carga, error y mapa vacío.
- [x] 4.6 Asegurar navegación por teclado, foco visible y adaptación a pantallas pequeñas.

## 5. Integración

- [x] 5.1 Enlazar el mapa desde la portada.
- [x] 5.2 Verificar que el enlace a la ficha del local usa el `id` correcto.

## 6. Pruebas del frontend

- [x] 6.1 Probar que se renderizan los 21 locales con sus números.
- [x] 6.2 Probar que cada slot muestra número, logo y nombre.
- [x] 6.3 Probar la navegación de cada slot a `/locales/{id}`.
- [x] 6.4 Probar los estados de carga, error y vacío.
- [x] 6.5 Probar la navegación por teclado.
- [x] 6.6 Ejecutar `npm test -- --run` y `npm run build`.

## 7. Verificación de integración

- [x] 7.1 Con el stack levantado, abrir `/mapa` y verificar la distribución 10/10/1.
- [x] 7.2 Seleccionar locales de cada lado y del fondo.
- [x] 7.3 Verificar que la ficha del local abre correctamente.
- [x] 7.4 Verificar que un local inactivo no aparece.
- [x] 7.5 Validar el cambio con `openspec validate public-store-map --strict` y registrar los resultados.

## Workflow follow-up

- Revisar y archivar después de la verificación.
- No implementar plano gráfico real, coordenadas, pisos ni mapas externos.
