# Propuesta

## Why

El CU #3 pide que un visitante vea imágenes, descripción, precio y local de un producto. La búsqueda pública del CU #1 muestra un resumen, pero sus tarjetas no llevan a ningún detalle: hoy no existe una página ni un endpoint que reúna toda la información del producto ni los datos de contacto de su local.

Este cambio implementa exclusivamente el detalle público del producto y una sección de productos similares, sin feed, sin información completa del local y sin mapa.

## What Changes

- Se añade `GET /api/public/products/{id}`, sin autenticación, con todas las imágenes ordenadas, descripción, precios, categorías y datos del local.
- Se añade `GET /api/public/products/{id}/similar`, sin autenticación, con hasta seis productos disponibles que comparten categoría o palabras del nombre.
- Se amplía la información pública del local en el detalle con logo, correo, teléfono y WhatsApp.
- Se añade la página pública `/productos/:productId` con galería, información, local y similares.
- Las tarjetas de resultados de búsqueda pasan a enlazar al detalle.
- Se añaden pruebas de backend y frontend, incluyendo producto inexistente, sin imágenes y sin similares.

### Alcance

- Detalle público de un producto disponible.
- Galería de imágenes ordenadas.
- Datos de contacto del local que vende el producto.
- Productos similares por categoría o palabras del nombre.
- Navegación desde la búsqueda y estados de carga, error y no encontrado.

### Fuera de alcance

- Feed de destacados y ofertas (CU #2).
- Información completa, horarios y enlaces del local (CU #4).
- Mapa interactivo (CU #5).
- Panel de estadísticas (CU #10).
- Reseñas, favoritos, stock, carrito y compra.
- Similitud difusa con trigram o normalización de acentos.
- Endpoints de escritura.

## Capabilities

### New Capabilities

- `product-detail`: consulta pública del detalle de un producto, galería, local con contacto, productos similares y estados de no encontrado.

### Modified Capabilities

Ninguna. La búsqueda no cambia su contrato; solo sus tarjetas pasan a enlazar al detalle, lo que es una decisión de interfaz dentro de esta capability.

## Impact

- **Backend modificado:** `app/modules/public_catalog/schemas.py`, `service.py` y `router.py`; pruebas.
- **Frontend nuevo:** `features/product-detail/` (API, tipos, página, galería, carrusel de similares) y ruta `/productos/:productId`.
- **Frontend modificado:** `features/product-search/ProductCard.tsx` para enlazar al detalle; pruebas.
- **Migraciones:** ninguna.
- **Dependencias nuevas:** ninguna.
- **API:** `GET /api/public/products/{id}` y `GET /api/public/products/{id}/similar`.
- **Funcionalidades existentes:** búsqueda, CU #6, CU #7, CU #8, autenticación y health check no cambian.
- **Dependencias:** `domain-model`, `merchant-product-catalog` y `product-search`.

## Decisiones adoptadas

- Un producto pertenece a un local; el detalle muestra ese único local.
- Se muestran todas las imágenes ordenadas; la primaria se destaca en la galería.
- Sin imágenes se muestra un marcador visual.
- El local se muestra con número, nombre, logo, correo, teléfono y WhatsApp.
- Producto inexistente, eliminado, inactivo o de local inactivo → `404`.
- Similares por categoría compartida o palabras del nombre (≥3 letras), priorizando categoría, máximo seis.
- Similares en endpoint separado, con el mismo esquema que los resultados de búsqueda.
- Tarjetas de búsqueda clicables hacia `/productos/:id`.
