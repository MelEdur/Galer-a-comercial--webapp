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

## Autenticación y administración

- `POST /api/auth/login` recibe `{"email": "...", "password": "..."}` y responde `{"access_token": "...", "token_type": "bearer"}`. Ante credenciales inválidas responde siempre `401` con el mismo mensaje.
- `GET /api/auth/me` devuelve la identidad autenticada (sin contraseña ni hash). Los comerciantes incluyen su local como `store` (`id`, `number`, `name`); el administrador recibe `store: null`.
- Las rutas `/api/admin/*` requieren un token con rol `admin`: sin token responden `401` y con rol `merchant` responden `403`.
- `GET /api/admin/merchants`, `POST /api/admin/merchants` y `DELETE /api/admin/merchants/{id}` gestionan las cuentas de comerciante.
- `GET /api/admin/stores` devuelve los 21 locales con su comerciante activo o `null`.

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
