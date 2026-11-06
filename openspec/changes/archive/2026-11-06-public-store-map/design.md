# Diseño

## Context

Ver `proposal.md` para la motivación y `specs/store-map/spec.md` para los requisitos. Los 21 locales ya tienen `side` (`left`, `right`, `back`) y `position` (1–10, o 1 al fondo) con restricciones de base de datos. No hay imagen, coordenadas ni pisos. La ficha pública de cada local ya existe en `/locales/:id`.

## Goals / Non-Goals

**Goals:**

- Representar fielmente los 21 espacios sin inventar ubicaciones.
- Acceso directo a la ficha existente desde cada local.
- Sin dependencias ni cambios de esquema.

**Non-Goals:**

- Plano gráfico real con imagen y coordenadas.
- Pisos, sectores, búsqueda o productos en el mapa.
- Geolocalización o mapas externos.

## Decisions

### 1. Endpoint público

`GET /api/public/map` en el router público existente, sin autenticación:

```json
{
  "stores": [
    {
      "id": 1,
      "number": 2,
      "name": "Café Central",
      "logo_url": "https://...",
      "side": "left",
      "position": 1
    }
  ]
}
```

- Solo locales activos.
- Orden: lado (`left`, `right`, `back`) y posición ascendente, con un `CASE` en SQL o ordenamiento explícito.
- No incluye `is_active`, descripción, contacto, productos ni cuentas.

### 2. Esquema con CSS

- Contenedor con tres zonas: columna izquierda, pasillo central y columna derecha.
- El local del fondo se muestra en una fila superior separada, rotulada "Fondo".
- Cada slot es un enlace que muestra el número, el logo y el nombre del local.
- Los locales se agrupan en el frontend por `side` y se ordenan por `position`.
- No se dibuja entrada ni flecha de circulación.
- No se usan coordenadas: la posición visual deriva de `side`/`position`.
- Slots con tamaño mínimo y `overflow-x-auto` en pantallas muy estrechas; el esquema conserva la legibilidad.

### 3. Navegación directa

- Cada slot es un `Link` a `/locales/{id}`.
- No hay estado de selección ni panel de detalle.
- El logo se muestra en pequeño; si falta o falla, se usa un marcador.
- El número y el nombre permanecen visibles; el nombre se recorta si no cabe.
- Al hacer clic o activar el enlace con teclado se abre la ficha del local.

### 4. Accesibilidad

- Cada slot es un enlace con `aria-label` "Local {number}: {name}".
- Foco visible con las clases existentes.
- El orden del DOM sigue el orden visual.
- Los encabezados de lado y fondo estructuran las regiones.

### 5. Frontend

- Ruta pública `/mapa`.
- `features/store-map/` con tipos, API, query keys, página, esquema y slots enlazados.
- Enlace "Mapa de la galería" desde la portada.
- Estados de carga, error y vacío.
- Reutiliza los estilos Tailwind del proyecto; sin librerías de mapas.

### 6. Sin cambios de datos

No hay migraciones ni dependencias. Si en el futuro se incorpora un plano real, se añadirán imagen y coordenadas en un cambio aparte.

## Risks / Trade-offs

- **Esquema, no plano real** → no muestra la forma física exacta de la galería; se documenta como representación esquemática.
- **Sin orientación** → el visitante no ve dónde está la entrada; no se inventa.
- **Slots más densos** → incluir logo y nombre reduce el espacio; se usan tamaños compactos y truncado del nombre.
- **Pantallas pequeñas** → el esquema puede requerir desplazamiento horizontal; se prioriza no deformar los slots.
- **Locales inactivos** → no aparecen; si se desactiva uno, el mapa queda con menos slots.

## Migration Plan

No hay cambios de esquema ni datos. Se despliega el backend y luego la ruta `/mapa`.

Rollback: retirar el endpoint y la ruta; no hay datos que migrar.

## Open Questions

Ninguna que afecte al esquema o al alcance. El plano gráfico real y las coordenadas quedan pendientes de un recurso y un cambio posterior.
