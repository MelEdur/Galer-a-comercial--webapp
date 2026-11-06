# Galería Comercial

Aplicación web para promover locales comerciales dentro de una galería y mejorar la experiencia de compra de los visitantes. Esta etapa incluye el esqueleto técnico, el modelo de dominio, la autenticación del administrador y la administración de comerciantes desde el backend. Todavía no incluye el catálogo, los locales públicos ni el panel del comerciante.

## Stack

- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic 2, Alembic, PostgreSQL, Pytest.
- **Frontend:** React, TypeScript, Vite, Tailwind CSS, React Router, Fetch API, TanStack Query, Vitest, React Testing Library.
- **Infraestructura:** Docker y Docker Compose.

## Estructura

```text
.
├── backend/            # API FastAPI, configuración, Alembic y pruebas
├── frontend/           # Aplicación React con Vite y pruebas
├── docker/             # Scripts de inicialización de PostgreSQL
├── docker-compose.yml
├── .env.example
└── openspec/           # Especificaciones y cambios
```

## Requisitos

- Docker y Docker Compose (recomendado para levantar todo el entorno).
- Para desarrollo sin Docker:
  - Python 3.12 o superior.
  - Node.js 22 o superior.
  - PostgreSQL 17.

## Configuración de variables de entorno

1. Copia el archivo de ejemplo:

   ```bash
   cp .env.example .env
   ```

2. Ajusta las credenciales y puertos si es necesario. `DATABASE_URL` y `TEST_DATABASE_URL` deben coincidir con `POSTGRES_USER`, `POSTGRES_PASSWORD` y `POSTGRES_DB`.

Variables principales:

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `POSTGRES_USER` | Usuario de PostgreSQL | `galeria` |
| `POSTGRES_PASSWORD` | Contraseña de PostgreSQL | `change-me` |
| `POSTGRES_DB` | Base de datos principal | `galeria` |
| `POSTGRES_PORT` | Puerto expuesto de PostgreSQL en el host | `5433` |
| `DATABASE_URL` | URL de SQLAlchemy para la aplicación | `postgresql+psycopg://galeria:change-me@db:5432/galeria` |
| `TEST_DATABASE_URL` | URL de SQLAlchemy para pruebas | `postgresql+psycopg://galeria:change-me@db:5432/app_test` |
| `BACKEND_PORT` | Puerto del backend | `8000` |
| `CORS_ORIGINS` | Orígenes permitidos, separados por comas | `http://localhost:5173` |
| `JWT_SECRET` | Secreto obligatorio usado para firmar los tokens JWT | — (sin valor por defecto) |
| `JWT_ALGORITHM` | Algoritmo de firma de los tokens | `HS256` |
| `JWT_EXPIRE_MINUTES` | Vida útil del token en minutos | `60` |
| `ADMIN_EMAIL` | Correo del administrador inicial (solo para el script) | `admin@galeria.local` |
| `ADMIN_PASSWORD` | Contraseña del administrador inicial (solo para el script) | `change-me-admin` |
| `ADMIN_FULL_NAME` | Nombre completo del administrador inicial | `Administrador` |
| `GROQ_API_KEY` | Clave de Groq usada por el asistente (solo backend) | — |
| `GROQ_MODEL` | Modelo de chat fijo; vacío lo elige automáticamente | — |
| `GROQ_MODEL_PREFERENCES` | Modelos preferidos, separados por comas y en orden | `openai/gpt-oss-120b,openai/gpt-oss-20b,qwen/qwen3.8-27b` |
| `ASSISTANT_TOP_K` | Fragmentos de conocimiento recuperados por consulta | `5` |
| `ASSISTANT_MAX_MESSAGE_CHARS` | Longitud máxima de un mensaje | `1000` |
| `ASSISTANT_MAX_HISTORY_MESSAGES` | Mensajes de historial considerados | `10` |
| `ASSISTANT_RATE_LIMIT` | Consultas permitidas por IP y ventana | `20` |
| `ASSISTANT_RATE_WINDOW_SECONDS` | Duración de la ventana de rate limit | `300` |
| `ASSISTANT_TIMEOUT_SECONDS` | Tiempo máximo de espera del proveedor | `20` |
| `CHROMA_PATH` | Directorio persistente de ChromaDB | `/data/chroma` |
| `HF_HOME` | Caché del modelo de embeddings | `/data/hf` |
| `FRONTEND_PORT` | Puerto del frontend | `5173` |
| `VITE_API_URL` | URL base de la API usada por el frontend | `http://localhost:8000/api` |

El archivo `.env` está excluido del control de versiones. No se deben commitear credenciales reales.

## Arranque con Docker

```bash
cp .env.example .env
docker compose up --build
```

Servicios:

- PostgreSQL: `localhost:5433` (se usa 5433 para no chocar con un PostgreSQL local en 5432).
- Backend: `http://localhost:8000`.
- Frontend: `http://localhost:5173`.

Verificación:

```bash
curl http://localhost:8000/api/health
```

Respuesta esperada con la base disponible:

```json
{"status":"ok","database":"ok"}
```

Si la base de datos no está disponible, el endpoint responde `503`:

```json
{"status":"degraded","database":"unavailable"}
```

Para detener el entorno:

```bash
docker compose down
```

Para eliminar también los datos y recrear la base de pruebas:

```bash
docker compose down -v
```

## Migraciones

Alembic contiene la revisión inicial `0001` que crea las nueve tablas del dominio con sus restricciones e índices. La revisión `0002` añade `users.full_name` y la `0003` limita la unicidad de comerciante por local a las cuentas activas. Las migraciones se aplican de forma explícita:

```bash
docker compose exec backend alembic upgrade head
docker compose exec backend alembic current
```

Para crear una migración cuando exista un modelo:

```bash
docker compose exec backend alembic revision --autogenerate -m "descripcion"
```

No se ejecutan migraciones automáticamente al arrancar el backend.

## Datos iniciales

Después de aplicar las migraciones, la precarga de los 21 locales se ejecuta una sola vez:

```bash
cd backend
python -m scripts.seed_stores
```

Con Docker:

```bash
docker compose exec backend python -m scripts.seed_stores
```

El script es idempotente: usa el número de local como clave natural y no inserta duplicados si se ejecuta más de una vez. Al finalizar imprime cuántos locales creó y cuántos ya existían.

### Categorías iniciales

Después de aplicar las migraciones, precarga las diez categorías globales del catálogo:

```bash
cd backend
python -m scripts.seed_categories
```

Con Docker:

```bash
docker compose exec backend python -m scripts.seed_categories
```

El script compara los nombres sin distinguir mayúsculas, por lo que es idempotente: una segunda ejecución no crea duplicados. Imprime cuántas categorías creó y cuántas ya existían.

### Administrador inicial

Después de aplicar las migraciones y definir `JWT_SECRET`, crea el administrador inicial:

```bash
cd backend
python -m scripts.create_admin
```

Con Docker:

```bash
docker compose exec backend python -m scripts.create_admin
```

El script lee `ADMIN_EMAIL`, `ADMIN_PASSWORD` y `ADMIN_FULL_NAME` (por defecto `Administrador`). Si falta el correo o la contraseña termina con un error claro sin crear nada. Es idempotente: si el correo ya existe no modifica la cuenta ni la contraseña.

### Datos de demostración

Para poblar la galería con comerciantes, información de locales y productos:

```bash
docker compose exec backend python -m scripts.seed_demo
```

El script requiere que existan los locales y las categorías. Crea un comerciante por local, completa nombre, descripción, logo, contacto, horarios y enlaces de los 21 locales, y agrega tres productos por local. Es idempotente: una segunda ejecución actualiza los datos demo sin duplicar comerciantes ni productos.

Credenciales de los comerciantes demo:

- Correos: `comercio01@galeria.local` … `comercio21@galeria.local`.
- Contraseña: `comercio1234`.
- El administrador sigue siendo `admin@galeria.local`.

## Autenticación y administración

- `POST /api/auth/login` recibe `{"email": "...", "password": "..."}` y responde `{"access_token": "...", "token_type": "bearer"}`. Ante credenciales inválidas responde siempre `401` con el mismo mensaje.
- `GET /api/auth/me` devuelve la identidad autenticada (sin contraseña ni hash). Los comerciantes incluyen su local como `store` (`id`, `number`, `name`); el administrador recibe `store: null`.
- Las rutas `/api/admin/*` requieren un token con rol `admin`: sin token responden `401` y con rol `merchant` responden `403`.
- `GET /api/admin/merchants`, `POST /api/admin/merchants` y `DELETE /api/admin/merchants/{id}` gestionan las cuentas de comerciante.
- `GET /api/admin/stores` devuelve los 21 locales con su comerciante activo o `null`.

## Catálogo del comerciante

Las rutas `/api/merchant/*` requieren un token con rol `merchant` y un local asignado: sin token responden `401`, con rol `admin` responden `403` y un comerciante sin local responde `403`. El local se deriva siempre de la cuenta autenticada; ningún payload acepta `store_id`.

- `GET /api/merchant/products` lista el catálogo propio. Query: `search` (nombre, sin distinguir mayúsculas), `status` (`active` por defecto, `deleted` o `all`), `category_id`, `page` (desde 1) y `page_size` (1–100, por defecto 20). Responde `{items, total, page, page_size, pages}`.
- `GET /api/merchant/products/{id}` devuelve un producto propio, incluido uno eliminado; un producto de otro local responde `404`.
- `POST /api/merchant/products` crea un producto (`201`) con `name`, `price`, `category_ids` (al menos una) y, opcionalmente, `description`, `offer_price` e `images` (máximo 5 `{url, alt_text?}` en `http`/`https`). La primera imagen queda como primaria.
- `PATCH /api/merchant/products/{id}` actualiza parcialmente; `category_ids` e `images`, si se envían, reemplazan el conjunto anterior. Un producto eliminado responde `409`.
- `DELETE /api/merchant/products/{id}` da de baja lógica de forma idempotente (`204`) y conserva sus datos e imágenes.
- `POST /api/merchant/products/{id}/restore` restaura un producto eliminado propio y devuelve el producto (`200`); restaurar uno vigente no produce cambios y un producto de otro local responde `404`.
- `GET /api/merchant/categories` devuelve las categorías globales `{id, name}` ordenadas por nombre.

Los datos inválidos, las categorías inexistentes y una oferta que no sea menor que el precio responden `422`; los productos inexistentes o de otro local responden `404`.

## Búsqueda pública

Las rutas `/api/public/*` no requieren autenticación. Solo exponen productos disponibles: no eliminados, activos y de locales activos. Cada resultado incluye `id`, `name`, `description`, `price`, `offer_price`, `effective_price` (`coalesce(offer_price, price)`), `categories` (`{id, name}`), `primary_image` (`{url, alt_text}` o `null`) y `store` (`{id, number, name}`); nunca expone `store_id`, `is_active` ni `deleted_at`.

- `GET /api/public/products` busca productos disponibles. Query: `search` (nombre, coincidencia parcial sin distinguir mayúsculas, comodines literales), `category_id`, `min_price` y `max_price` (inclusivos sobre el precio efectivo, no negativos), `has_offer` (solo productos con precio de oferta), `page` (desde 1), `page_size` (1–100, por defecto 20) y `sort` (`name` por defecto, `price_asc` o `price_desc`). Los filtros se combinan con AND. Responde `{items, total, page, page_size, pages}`.
- `GET /api/public/categories` devuelve todas las categorías globales `{id, name}` ordenadas por nombre.
- `GET /api/public/explore` devuelve la portada de descubrimiento: `featured` (hasta 8 productos, primero las ofertas recientes y luego novedades sin repetir), `offers` (hasta 8 productos con precio de oferta), `categories` (`{id, name, product_count}` de productos disponibles, incluidas las de conteo cero) y `stores` (hasta 6 locales activos ordenados por número).
- `GET /api/public/stores` devuelve todos los locales activos `{id, number, name, description, logo_url}` ordenados por número, sin paginación.
- Un rango con `min_price > max_price` o un precio negativo responde `422`. Sin criterios se devuelve todo el catálogo disponible paginado.
- Cuando la consulta incluye al menos un criterio (incluido `has_offer=true`) y la página devuelve productos, se registra un evento de búsqueda por producto de la página para las estadísticas de CU #10; la exploración sin criterios, la exploración pública (`/explore`) y las páginas vacías no registran eventos.

## Detalle público

- `GET /api/public/products/{id}` devuelve el detalle de un producto disponible: `id`, `name`, `description`, `price`, `offer_price`, `effective_price`, `categories`, `images` y `store`. Cada imagen incluye `id`, `url`, `alt_text`, `position` e `is_primary`, ordenadas por `position` y luego `id`. El local incluye `id`, `number`, `name`, `logo_url`, `email`, `phone` y `whatsapp` (los opcionales pueden ser `null`). No expone `store_id`, `is_active`, `deleted_at`, cuentas ni credenciales.
- `GET /api/public/products/{id}/similar` devuelve `{items}` con hasta seis productos disponibles similares, usando el mismo esquema que la búsqueda (`primary_image` y `store` resumido). Se priorizan las categorías compartidas, luego las palabras del nombre (secuencias de letras de al menos 3 caracteres) y el nombre; el producto consultado nunca aparece.
- Producto inexistente, eliminado, inactivo o de local inactivo responde `404` en ambos endpoints; un identificador no numérico responde `422`.

## Asistente virtual

`POST /api/public/assistant/chat` es público y no requiere autenticación. Responde consultas informativas en español sobre la galería, sus locales, sus categorías y el uso de la aplicación. No busca productos, precios ni stock: cuando la consulta lo requiere ofrece abrir el buscador o el mapa, pero nunca ejecuta la búsqueda.

```json
{
  "message": "¿Cómo encuentro un local?",
  "history": [
    {"role": "user", "content": "Hola"},
    {"role": "assistant", "content": "¡Hola! ¿En qué puedo ayudarte?"}
  ]
}
```

Respuesta:

```json
{
  "answer": "Puedes consultar la lista de locales o abrir el mapa de la galería.",
  "action": null,
  "sources": [{"title": "Guía de la galería", "type": "static"}]
}
```

- `action` es `null` o `{type: "search"|"map", label, query, href}`. El frontend muestra un botón y navega solo cuando el visitante lo confirma.
- Límites: mensaje de 1–1000 caracteres, historial de hasta 10 mensajes, 20 consultas por IP cada 300 segundos y 20 segundos de espera del proveedor. Un mensaje u historial inválido responde `422`, el rate limit `429` y un proveedor no disponible `503`.
- El rate limit es en memoria por proceso: no es distribuido y se reinicia al reiniciar el backend.
- No se persisten conversaciones ni se registran analíticas del asistente.

La base de conocimiento combina `app/modules/assistant/knowledge/galeria.md` con un documento por local activo (datos públicos y categorías comerciales, sin productos ni precios). Se usa Groq para el chat y embeddings multilingües locales (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`) con ChromaDB persistente en `chroma_data`.

La primera ejecución descarga el modelo de embeddings y puede tardar varios minutos. Para construir o reconstruir el índice:

```bash
docker compose exec backend python -m scripts.reindex_assistant
docker compose exec backend python -m scripts.reindex_assistant --store-id 5
```

Guardar el local desde el panel del comerciante (CU #9) reindexa ese local en segundo plano; un fallo de indexación se registra y nunca revierte el guardado. El CLI sigue siendo la vía para reconstruir todo el índice.

## Pruebas

### Backend

Con Docker:

```bash
docker compose exec backend pytest -q
```

En local:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
export DATABASE_URL=postgresql+psycopg://galeria:change-me@localhost:5433/galeria
pytest -q
```

La prueba de conexión real usa `TEST_DATABASE_URL`. Si no está definida, se omite con un mensaje claro.

### Frontend

Con Docker:

```bash
docker compose exec frontend npm test -- --run
```

En local:

```bash
cd frontend
npm install
npm run dev
```

Pruebas y build:

```bash
npm test -- --run
npm run build
```

## Desarrollo local sin Docker

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
export DATABASE_URL=postgresql+psycopg://galeria:change-me@localhost:5433/galeria
export JWT_SECRET=dev-only-secret-change-me-in-production
uvicorn app.main:app --reload
```

Si quieres usar la base de datos de Docker desde el host, el puerto es `5433`.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

`frontend/.env.example` contiene `VITE_API_URL=http://localhost:8000/api`.

## Endpoint de salud

`GET /api/health` comprueba el backend y ejecuta `SELECT 1` contra PostgreSQL.

- `200`: backend y base de datos operativos.
- `503`: backend operativo, base de datos no disponible.

No expone credenciales, trazas ni detalles internos de conexión.
