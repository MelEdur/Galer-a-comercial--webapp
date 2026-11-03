# Propuesta

## Why

El proyecto todavía no tiene código de aplicación: solo cuenta con instrucciones, configuración de OpenSpec y skills. Sin una base ejecutable y verificable no es posible empezar a desarrollar funcionalidades de negocio de forma incremental, ni comprobar que el stack decidido (FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL, React, Vite y Docker) funciona en conjunto.

Esta propuesta establece un esqueleto mínimo, reproducible y probado que servirá de punto de partida para las siguientes propuestas funcionales.

## What Changes

- Se crea la estructura monorepo con `backend/` y `frontend/` en la raíz.
- Se inicializa una aplicación FastAPI con configuración tipada por variables de entorno.
- Se configura SQLAlchemy 2.0 con sesión síncrona por request y conexión a PostgreSQL mediante `psycopg` 3.
- Se configura Alembic sobre la metadata de SQLAlchemy, sin migraciones de negocio iniciales.
- Se añade el endpoint `GET /api/health`, que verifica el estado del backend y de la base de datos.
- Se inicializa una aplicación React + TypeScript con Vite, Tailwind CSS, React Router y TanStack Query.
- Se añade una página inicial mínima que muestra el estado del backend y una página 404.
- Se configuran Pytest en backend y Vitest + React Testing Library en frontend.
- Se añaden Dockerfiles para backend y frontend, y un `docker-compose.yml` con PostgreSQL, backend y frontend.
- Se documentan las variables de entorno en `.env.example` y los comandos de arranque en `README.md`.

### Alcance

- Dejar el proyecto ejecutable con `docker compose up --build`.
- Verificar la integración backend–base de datos mediante el endpoint de salud.
- Verificar la integración frontend–backend mediante la página inicial.
- Ejecutar las suites de pruebas de ambos lados.

### Fuera de alcance

- Usuarios, autenticación, autorización y roles.
- Productos, locales, categorías, búsqueda, mapa interactivo o cualquier funcionalidad de negocio.
- CRUDs, datos semilla y migraciones de negocio.
- CI/CD, despliegue productivo, TLS, Nginx y observabilidad avanzada.
- Axios, shadcn/ui, ESLint, Prettier y Ruff.
- Versionado de API, internacionalización y gestión avanzada de estado global.

## Capabilities

### New Capabilities

- `backend-foundation`: estructura modular del backend, configuración por entorno, conexión a PostgreSQL, migraciones con Alembic, endpoint de salud y pruebas con Pytest.
- `frontend-foundation`: aplicación React con Vite y Tailwind, enrutado básico, cliente HTTP con Fetch y TanStack Query, vista de estado del backend y pruebas con Vitest.
- `local-environment`: Dockerfiles, Docker Compose con PostgreSQL, backend y frontend, persistencia, healthchecks y variables de entorno documentadas.

### Modified Capabilities

Ninguna. No existen especificaciones previas en `openspec/specs/`.

## Impact

- **Código nuevo:** `backend/`, `frontend/`, `docker/`, `docker-compose.yml`, `README.md`, `.env.example`, `.gitignore`.
- **Dependencias nuevas:** FastAPI, Uvicorn, SQLAlchemy 2.0, `psycopg` 3, Pydantic 2, `pydantic-settings`, Alembic, Pytest y `httpx` en backend; React, React Router, TanStack Query, Tailwind CSS, Vitest y React Testing Library en frontend.
- **API:** se introduce únicamente `GET /api/health`.
- **Base de datos:** se configura la conexión y Alembic, pero no se crean tablas de negocio.
- **Funcionalidades existentes:** no hay código ni especificaciones previas que puedan verse afectados.
- **Dependencias futuras:** las próximas propuestas de negocio se apoyarán en estas tres capacidades.

## Decisiones adoptadas

- Monorepo con `backend/` y `frontend/` en la raíz.
- SQLAlchemy síncrono con `Session` por request y `psycopg` 3.
- Docker Compose levanta PostgreSQL 17, backend y frontend.
- Un único endpoint `GET /api/health` que verifica la base de datos (200/503).
- Página inicial mínima que muestra el estado del backend.
- Python 3.12, Node 22 LTS, PostgreSQL 17 y Tailwind CSS 4.
- `pip` + `requirements*.txt` en backend y `npm` en frontend.
- Base de pruebas `app_test` creada por script de inicialización en el mismo contenedor PostgreSQL.
