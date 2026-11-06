# Tasks

## 1. Backend

- [x] 1.1 Añadir `ProductStatItem` y `ProductStatsResponse` a `app/modules/analytics/schemas.py`.
- [x] 1.2 Implementar el cálculo del período: presets 7/30/90, rango personalizado, validaciones y conversión a UTC-3.
- [x] 1.3 Implementar la consulta del Top 10 por local, conteo, última búsqueda, productos eliminados y orden con empates.
- [x] 1.4 Implementar `total_searches` del período para el local.
- [x] 1.5 Añadir `GET /api/merchant/stats/products` al router de analítica y registrarlo en `app/main.py`.

## 2. Pruebas del backend

- [x] 2.1 Probar `401` sin token, `403` para administrador y `403` para comerciante sin local.
- [x] 2.2 Probar que solo se incluyen productos del local autenticado.
- [x] 2.3 Probar conteo por producto, orden descendente y empate por nombre.
- [x] 2.4 Probar límite de 10 y exclusión de productos sin búsquedas.
- [x] 2.5 Probar productos eliminados incluidos y marcados.
- [x] 2.6 Probar presets 7/30/90, rango personalizado y período por defecto de 30 días.
- [x] 2.7 Probar exclusión de eventos fuera del período y límites de día local.
- [x] 2.8 Probar `422` por fechas inválidas, fecha única y mezcla de días con fechas.
- [x] 2.9 Probar `total_searches` y lista vacía sin eventos.
- [x] 2.10 Probar que consultar estadísticas no crea eventos.
- [x] 2.11 Mantener las 292 pruebas existentes pasando.

## 3. Frontend: API y tipos

- [x] 3.1 Crear tipos y cliente API para estadísticas.
- [x] 3.2 Configurar las claves de TanStack Query por período.

## 4. Frontend: página de estadísticas

- [x] 4.1 Crear la ruta protegida `/comerciante/estadisticas`.
- [x] 4.2 Implementar el selector de 7, 30 y 90 días y el rango personalizado con validación.
- [x] 4.3 Implementar la tabla Top 10 con posición, nombre, marca de eliminado, conteo, barra proporcional y última búsqueda.
- [x] 4.4 Implementar estados de carga, error y vacío.
- [x] 4.5 Enlazar Estadísticas desde el panel del comerciante y retirar el marcador "Próximamente".

## 5. Pruebas del frontend

- [x] 5.1 Probar carga del ranking y orden.
- [x] 5.2 Probar cambio de preset y rango personalizado.
- [x] 5.3 Probar marca de producto eliminado.
- [x] 5.4 Probar estado vacío y error.
- [x] 5.5 Probar el enlace desde el panel.
- [x] 5.6 Ejecutar `npm test -- --run` y `npm run build`.

## 6. Verificación de integración

- [x] 6.1 Generar búsquedas reales para productos de un local.
- [x] 6.2 Verificar el ranking, los conteos y el total del período.
- [x] 6.3 Verificar que otro comerciante no ve esos datos.
- [x] 6.4 Verificar productos eliminados y límites de fecha.
- [x] 6.5 Validar el cambio con `openspec validate merchant-product-stats --strict` y registrar los resultados.

## Workflow follow-up

- Revisar y archivar después de la verificación.
- No implementar analíticas generales, clics, ventas ni exportación.
