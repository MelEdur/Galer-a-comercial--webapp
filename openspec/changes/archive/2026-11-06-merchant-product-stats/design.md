# Diseño

## Context

Ver `proposal.md` para la motivación y `specs/product-statistics/spec.md` para los requisitos. CU #1 ya registra `ProductSearchEvent` por producto visible en la página de resultados cuando hay criterios. La tabla tiene índices por `(product_id, searched_at)` y por `searched_at`, y los eventos se conservan al eliminar lógicamente un producto. No hay endpoint de estadísticas.

## Goals / Non-Goals

**Goals:**

- Ranking simple y correcto de los productos del local propio.
- Períodos claros con límites de día local.
- Cero cambios en el registro de búsquedas.

**Non-Goals:**

- Analíticas generales, clics, ventas o visitas.
- Exportación, series temporales o gráficos avanzados.
- Purga o agregación de eventos.

## Decisions

### 1. Endpoint en el módulo de analítica

`GET /api/merchant/stats/products` en `app/modules/analytics/router.py`, con prefijo `/merchant/stats` y `Depends(require_merchant)`. El local se obtiene de `current_user.store_id`; no se acepta `store_id`.

### 2. Parámetros y períodos

- `days: Literal[7, 30, 90] | None`
- `from_date: date | None`
- `to_date: date | None`

Reglas:

- Sin parámetros → `days = 30`.
- `days` con fechas → `422`.
- Solo una fecha → `422`.
- `from_date > to_date` → `422`.
- `from_date` y `to_date` definen días locales inclusivos.

### 3. Zona horaria

Buenos Aires usa UTC-3 todo el año, sin horario de verano. Se usa un offset fijo `timezone(timedelta(hours=-3))` en lugar de `zoneinfo`, evitando depender de `tzdata` en la imagen.

- Un período predefinido de `N` días abarca desde el inicio del día local `hoy - (N-1)` hasta el final del día local de hoy.
- Un rango personalizado abarca desde las 00:00 del `from_date` hasta las 00:00 del día siguiente al `to_date`.
- Los límites se convierten a UTC para consultar `searched_at`.

### 4. Consulta del ranking

```sql
SELECT product.id, product.name, product.deleted_at,
       count(*) AS search_count, max(event.searched_at) AS last_searched_at
FROM product_search_events event
JOIN products product ON product.id = event.product_id
WHERE product.store_id = :store_id
  AND event.searched_at >= :start_utc
  AND event.searched_at < :end_utc
GROUP BY product.id, product.name, product.deleted_at
ORDER BY search_count DESC, lower(product.name) ASC, product.id ASC
LIMIT 10
```

- Incluye productos eliminados (`deleted_at` no nulo) y los marca con `is_deleted`.
- Excluye productos sin eventos por el `JOIN` y el `GROUP BY`.
- `total_searches` se obtiene con una segunda consulta `count(*)` sobre los mismos filtros de local y período, sin límite.
- Sin eventos → `items: []` y `total_searches: 0`.

### 5. Schemas

`ProductStatItem`:
- `product_id`, `name`, `search_count`, `is_deleted`, `last_searched_at`.

`ProductStatsResponse`:
- `from_date`, `to_date`, `total_searches`, `items`.

Las fechas se devuelven como `date` local; `last_searched_at` como timestamp con offset.

### 6. Errores

| Caso | Código |
|---|---|
| Sin token | `401` |
| Rol no comerciante o sin local | `403` |
| Parámetros inválidos | `422` |
| Sin datos | `200` con lista vacía |

### 7. Frontend

- Ruta protegida `/comerciante/estadisticas` con `role="merchant"`.
- Controles:
  - botones 7, 30 y 90 días;
  - fecha desde y hasta con botón "Aplicar";
  - estado del período en la URL (`days` o `from`/`to`).
- Tabla Top 10:
  - posición, nombre, marca "Eliminado", cantidad, barra CSS proporcional al máximo, última búsqueda.
  - La barra usa `width: count / maxCount * 100%`.
- Estados de carga, error y vacío.
- `useQuery` con clave que incluye el período.
- El panel del comerciante enlaza a la página; Estadísticas deja de ser "Próximamente".

### 8. Sin cambios de datos

No hay migraciones. No se añaden índices porque los existentes cubren el filtro por fecha y el join por producto. Si el volumen crece, se evaluará un índice compuesto por local y fecha.

## Risks / Trade-offs

- **Eventos como impresiones** → cuentan productos vistos en resultados, no clics; es la definición acordada.
- **Paginación** → cada página vista cuenta; un producto puede sumar varias veces si el visitante navega páginas.
- **Productos eliminados** → se muestran con marca; el nombre se conserva.
- **Offset fijo UTC-3** → correcto para Argentina; si la galería cambiara de zona, habría que ajustar.
- **Rangos amplios** → pueden recorrer muchos eventos; el volumen actual es bajo.

## Migration Plan

No hay cambios de esquema ni datos. Se despliega el backend y luego la página de estadísticas.

Rollback: retirar el endpoint y la ruta; los eventos siguen registrándose para CU #1.

## Open Questions

Ninguna que afecte al esquema o al alcance. La exportación y las series temporales quedan para cambios posteriores.
