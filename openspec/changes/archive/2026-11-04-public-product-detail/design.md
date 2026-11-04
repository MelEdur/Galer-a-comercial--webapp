# Diseño

## Context

Ver `proposal.md` para la motivación y `specs/product-detail/spec.md` para los requisitos. El módulo `public_catalog` ya expone búsqueda y categorías, y `Product` tiene imágenes ordenadas y un local con logo y contacto. Las tarjetas de búsqueda no navegan.

## Goals / Non-Goals

**Goals:**

- Detalle público completo con galería y datos del local.
- Similares útiles y acotados por categoría y nombre.
- Reutilizar el esquema y los patrones de búsqueda.

**Non-Goals:**

- Información completa del local, feed, mapa o estadísticas.
- Similitud difusa con trigram.
- Escritura o autenticación.

## Decisions

### 1. Endpoint de detalle

`GET /api/public/products/{product_id}` reutiliza las condiciones de disponibilidad de la búsqueda:

- `Product.deleted_at IS NULL`
- `Product.is_active IS TRUE`
- `Store.is_active IS TRUE`

Carga con `selectinload` las imágenes, categorías y local. Si no cumple, `404`.

### 2. Schemas

- `PublicImageDetail`: `id`, `url`, `alt_text`, `position`, `is_primary`.
- `PublicStoreDetail`: `id`, `number`, `name`, `logo_url`, `email`, `phone`, `whatsapp`.
- `PublicProductDetail`: datos actuales del producto, `images` (todas, ordenadas) y `store` detallado.
- `PublicSimilarProducts`: `{items: list[PublicProduct]}` reutilizando el schema de la búsqueda (imagen primaria y local resumido).

Las imágenes se ordenan por `position` y, en empate, por `id`.

### 3. Similares

`GET /api/public/products/{product_id}/similar`:

1. Verifica que el producto base esté disponible; si no, `404`.
2. Extrae palabras significativas del nombre: secuencias de letras de al menos 3 caracteres, en minúsculas y sin duplicados.
3. Busca candidatos disponibles, excluyendo el producto actual, que cumplan al menos una condición:
   - comparten alguna categoría con el producto base;
   - el nombre contiene alguna palabra significativa (`ILIKE` con comodines escapados).
4. Recupera hasta 50 candidatos y los puntúa en memoria:
   - cantidad de categorías compartidas (descendente);
   - cantidad de palabras coincidentes (descendente);
   - nombre ascendente y `id`.
5. Devuelve como máximo 6.

Se puntúa en memoria porque el conjunto es pequeño y permite un orden claro sin SQL complejo. Si el producto no tiene categorías ni palabras significativas, la lista es vacía.

Alternativa descartada: `pg_trgm` y similitud por umbral; requiere extensión y migración, y queda para una mejora posterior.

### 4. Local con contacto

El detalle incluye `logo_url`, `email`, `phone` y `whatsapp`, todos opcionales. Los enlaces externos, horarios y el resto de la información quedan para CU #4.

### 5. Frontend

- Ruta pública `/productos/:productId`.
- `ProductDetailPage` con dos consultas: detalle y similares. La de similares solo se habilita cuando el detalle cargó.
- Galería: imagen principal con estado local, miniaturas para cambiar, marcador "Sin imagen" si no hay.
- Información: nombre, descripción, precio/oferta/precio efectivo y categorías.
- Local: número, nombre, logo y contacto.
- Contacto: correo con `mailto:`, teléfono con `tel:` y WhatsApp con enlace `wa.me` usando solo dígitos.
- Similares: carrusel horizontal con las tarjetas existentes; se oculta si la lista está vacía.
- `ProductCard` se envuelve en un `Link` a `/productos/{id}` conservando el diseño y la accesibilidad; se reutiliza en la búsqueda y en los similares.
- Estados: carga, error y `404` con enlace a `/buscar`.

### 6. Errores

| Caso | Código |
|---|---|
| Producto inexistente, eliminado, inactivo o de local inactivo | `404` |
| Identificador no numérico | `422` |
| Error interno | `500` sin detalles |

### 7. Rendimiento

- `selectinload` para imágenes, categorías y local.
- Similares con una consulta acotada a 50 candidatos y puntuación en memoria.
- Sin N+1 en la serialización.

## Risks / Trade-offs

- **Similitud por palabras** → puede incluir productos de rubros distintos si comparten una palabra genérica; se mitiga priorizando categorías y limitando a seis.
- **Carga de hasta 50 candidatos** → aceptable con el catálogo actual; se puede mover la puntuación a SQL si crece.
- **Contacto del local en el detalle** → se solapa parcialmente con CU #4, pero se limita a logo y contacto, sin horarios ni enlaces.
- **Galería con URLs externas** → depende de que las URLs sean válidas; el backend ya valida `http/https` al crear el producto.

## Migration Plan

No hay cambios de esquema ni datos. Se despliega el backend y luego la página de detalle; las tarjetas de búsqueda empiezan a enlazar.

Rollback: retirar los endpoints y la ruta; no hay datos que migrar.

## Open Questions

Ninguna que afecte al esquema o al alcance. La similitud difusa y la información completa del local quedan para cambios posteriores.
