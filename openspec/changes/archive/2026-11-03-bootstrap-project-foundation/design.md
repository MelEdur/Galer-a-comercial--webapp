# Diseño

## Context

El repositorio solo contiene documentación, configuración de OpenSpec y skills; no hay código de aplicación ni especificaciones previas. El diseño parte de un proyecto vacío y debe dejar una base ejecutable, sin lógica de negocio. Ver `proposal.md` para la motivación y `specs/` para los requisitos.

Restricciones relevantes:

- Monolito modular con backend y frontend separados.
- Stack fijado: FastAPI, SQLAlchemy 2.0, Pydantic 2, Alembic, PostgreSQL y Pytest; React, TypeScript, Vite, Tailwind CSS, React Router, Fetch API, TanStack Query, Vitest y React Testing Library.
- Docker y Docker Compose como entorno local.
- Sin autenticación, usuarios, productos, locales ni mapa en esta etapa.

## Goals / Non-Goals

**Goals:**

- Dejar un esqueleto mínimo que arranque con un solo comando y sea verificable.
- Separar claramente configuración, acceso a datos y módulo de salud en el backend.
- Mantener el frontend simple, con una única feature de diagnóstico.
- Evitar capas, abstracciones y dependencias que aún no estén justificadas.

**Non-Goals:**

- Diseñar el modelo de datos de negocio.
- Definir autenticación, autorización o roles.
- Preparar un despliegue productivo con Nginx, TLS o CI/CD.
- Añadir linting o formateo mientras esas herramientas estén excluidas.

## Decisions

### 1. Monorepo con `backend/` y `frontend/` en la raíz

Se usa una única raíz con dos aplicaciones independientes. Es la opción más directa para un monolito modular y evita introducir un nivel `apps/` que todavía no aporta valor. Cada aplicación mantiene su propio manifiesto de dependencias y su propio Dockerfile.

Alternativa considerada: `apps/backend` y `apps/frontend`. Se descarta por añadir profundidad sin beneficio actual.

### 2. SQLAlchemy síncrono con `Session` por request y `psycopg` 3

La base usa `create_engine`, `sessionmaker` y una dependencia `get_db()` que entrega una sesión y la cierra al finalizar. Los endpoints que accedan a base de datos serán síncronos (`def`), ejecutados por FastAPI en su pool de hilos. Se usa `psycopg` 3 por ser el driver moderno compatible con SQLAlchemy 2.0.

Alternativa considerada: `AsyncSession` con `asyncpg`. Se descarta porque añade complejidad de ciclo de vida y pruebas sin una necesidad de concurrencia todavía demostrada.

No se usa `Base.metadata.create_all()`: el esquema es responsabilidad exclusiva de Alembic.

### 3. Configuración tipada con `pydantic-settings`

`Settings` centraliza las variables de entorno y valida al arranque. `DATABASE_URL` es obligatoria; si falta, la aplicación falla con un error de validación claro. Las variables de CORS y entorno tienen valores por defecto solo para desarrollo.

Alternativa considerada: leer `os.environ` directamente. Se descarta por perder tipado, valores por defecto y validación temprana.

### 4. Endpoint de salud con verificación de base de datos

`GET /api/health` ejecuta una consulta mínima (`SELECT 1`) con la sesión del request:

- Éxito: `200 {"status": "ok", "database": "ok"}`.
- Fallo: `503 {"status": "degraded", "database": "unavailable"}`.

El fallo se captura y se registra sin exponer credenciales, trazas ni detalles de conexión. Se usa un esquema Pydantic explícito para la respuesta.

Alternativa considerada: separar liveness y readiness en dos endpoints. Se descarta para no añadir superficie en esta etapa; el único endpoint solicitado ya cubre la verificación de backend y base.

### 5. Alembic sin migración inicial y sin ejecución automática

`alembic/env.py` toma la URL desde la configuración, expone `Base.metadata` como `target_metadata` y deja `versions/` vacío. No se crea una revisión vacía porque no hay tablas; la primera migración llegará con la primera entidad de negocio. La aplicación no ejecuta migraciones al arrancar: se aplican explícitamente.

Alternativa considerada: crear una revisión base vacía para validar la cadena. Se descarta por añadir ruido sin cambios de esquema.

### 6. Frontend con Vite, Router y TanStack Query; URL de API por entorno

La aplicación monta `QueryClientProvider`, define `/` y una ruta 404, y centraliza las peticiones en un cliente `fetch` con URL base `VITE_API_URL`. La página inicial usa una query de salud y muestra estados de carga, éxito y error. El backend habilita CORS para el origen del frontend en desarrollo.

Alternativa considerada: proxy de Vite hacia el backend. Se descarta para que el contrato sea explícito mediante `VITE_API_URL` y funcione igual con el frontend en Docker o en local.

### 7. Docker Compose orientado a desarrollo

Tres servicios:

- `db`: PostgreSQL 17 con volumen nombrado y healthcheck `pg_isready`.
- `backend`: imagen Python 3.12, depende de `db` saludable, puerto `8000`, recarga en desarrollo.
- `frontend`: imagen Node 22, servidor Vite en `5173`, depende de `backend`.

El backend se monta como volumen para recarga; el frontend monta el código y preserva `node_modules` con un volumen anónimo. El healthcheck del backend usa la librería estándar de Python para no instalar `curl`.

Alternativa considerada: levantar solo la base de datos y ejecutar el resto en local. Se descarta porque el objetivo es un entorno completo reproducible con un comando.

### 8. Base de pruebas dedicada en el mismo contenedor

El script `docker/postgres/init/01-create-test-db.sql` crea `app_test` al inicializar el volumen. Las pruebas de backend usan `TEST_DATABASE_URL`, fixtures de sesión y override de `get_db`. La prueba del endpoint de salud con base disponible usa la base de pruebas; el escenario de fallo se simula con un override que lanza un error.

Alternativa considerada: contenedor PostgreSQL exclusivo para pruebas. Se descarta para mantener el entorno local simple.

### 9. Variables de entorno centralizadas y secretos fuera del repositorio

`.env.example` en la raíz documenta las variables de Compose con placeholders. `frontend/.env.example` documenta `VITE_API_URL` para ejecución local. El `.env` real se ignora. Las credenciales solo se pasan por entorno.

## Risks / Trade-offs

- **El health check depende de la base de datos** → el backend se reporta no saludable si PostgreSQL falla. Es el comportamiento deseado como readiness, pero impide distinguir un fallo de aplicación de un fallo de base. Mitigación: el cuerpo JSON separa `status` y `database`.
- **El script de inicialización solo se ejecuta con un volumen nuevo** → un volumen existente puede no tener `app_test`. Mitigación: documentar `docker compose down -v` para recrear el entorno y usar una URL de pruebas explícita.
- **Sesión síncrona en endpoints** → si en el futuro aparecen cargas de alta concurrencia, habrá que evaluar `AsyncSession`. Mitigación: aislar el acceso a datos en `core/database.py` para facilitar el cambio.
- **CORS mal configurado** → el frontend no podría llamar al backend. Mitigación: valor por defecto `http://localhost:5173` y variable `CORS_ORIGINS`.
- **Mount de `node_modules` en Docker** → un volumen anónimo mal configurado puede ocultar dependencias. Mitigación: declarar el volumen anónimo sobre `/app/node_modules`.
- **Sin migración inicial** → no se valida una migración real hasta la primera entidad. Mitigación: la suite y la tarea de verificación comprueban `alembic upgrade head` y `alembic current`.

## Migration Plan

Proyecto greenfield: no hay datos ni esquema que migrar.

1. Crear la estructura y la configuración.
2. Levantar el entorno con `docker compose up --build`.
3. Verificar salud, frontend, pruebas y migraciones.
4. Para reiniciar desde cero: `docker compose down -v`.

No se requiere rollback de datos. Si algo falla, basta con eliminar los contenedores y el volumen de desarrollo.

## Open Questions

Ninguna que afecte a las especificaciones, al enfoque o al desglose de tareas. La build de producción del frontend y el pipeline de CI/CD se resolverán en una propuesta posterior.
