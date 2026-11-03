# Tasks

## 1. Estructura raíz y configuración compartida

- [x] 1.1 Crear `.gitignore`, `.env.example` y `docker/postgres/init/01-create-test-db.sql`; verificar que los archivos existen y que `.env` está excluido.
- [x] 1.2 Crear el `README.md` con las secciones de requisitos, arranque, variables de entorno y pruebas; verificar que los comandos documentados coinciden con los archivos creados.

## 2. Backend

- [x] 2.1 Crear `backend/requirements.txt` y `backend/requirements-dev.txt` con las dependencias acordadas; verificar la instalación en un entorno limpio.
- [x] 2.2 Implementar `app/core/config.py`, `app/core/database.py` y `app/db/base.py`; verificar que la aplicación importa y arranca con las variables requeridas.
- [x] 2.3 Implementar `app/main.py` y el módulo `app/modules/health/` con `GET /api/health`; verificar respuesta `200` con base disponible y `503` sin base.
- [x] 2.4 Configurar Pytest con `backend/pytest.ini`, `tests/conftest.py`, `tests/test_health.py` y `tests/test_database.py`; verificar que `pytest` finaliza correctamente.
- [x] 2.5 Configurar `backend/alembic.ini` y `backend/alembic/env.py` sobre la metadata de SQLAlchemy; verificar que `alembic upgrade head` y `alembic current` finalizan correctamente.
- [x] 2.6 Crear `backend/Dockerfile`; verificar que la imagen se construye y que el contenedor responde en `/api/health`.
- [x] 2.7 Documentar en el `README.md` los comandos de backend, migraciones y pruebas; verificar que las instrucciones se ejecutan tal como están escritas.

## 3. Frontend

- [x] 3.1 Inicializar `frontend/` con Vite, React, TypeScript, `package.json`, `tsconfig` y `vite.config.ts`; verificar que `npm run build` finaliza correctamente.
- [x] 3.2 Configurar Tailwind CSS 4 con `@tailwindcss/vite` y `src/index.css`; verificar que los estilos se aplican en la página inicial.
- [x] 3.3 Implementar `providers.tsx`, `router.tsx`, `HomePage.tsx` y `NotFoundPage.tsx`; verificar que `/` y una ruta desconocida renderizan la página correspondiente.
- [x] 3.4 Implementar `lib/http.ts` y la feature `features/health/` con TanStack Query; verificar los estados de carga, éxito y error contra el backend.
- [x] 3.5 Configurar Vitest, React Testing Library y `src/test/setup.ts`; verificar que `npm test` ejecuta las pruebas de estados del componente de salud.
- [x] 3.6 Crear `frontend/Dockerfile`; verificar que la imagen se construye y que el servidor Vite responde en el puerto configurado.
- [x] 3.7 Documentar en el `README.md` los comandos de frontend y pruebas; verificar que las instrucciones se ejecutan tal como están escritas.

## 4. Integración y verificación

- [x] 4.1 Crear `docker-compose.yml` con los servicios `db`, `backend` y `frontend`, healthchecks, volumen persistente y variables de entorno; verificar con `docker compose config`.
- [x] 4.2 Levantar el entorno con `docker compose up --build`; verificar que `GET /api/health` responde `200` y que el frontend carga en `http://localhost:5173`.
- [x] 4.3 Detener el servicio de base de datos y verificar que `/api/health` responde `503` y que la página inicial muestra el estado de error.
- [x] 4.4 Ejecutar las suites completas (`pytest` y `npm test`) y validar el cambio con `openspec validate bootstrap-project-foundation --strict`; registrar los resultados.
- [x] 4.5 Revisar el `README.md` completo y verificar que el arranque desde cero (`docker compose down -v` y `docker compose up --build`) funciona según lo documentado.

## Workflow follow-up

- Archivar el cambio después de que la revisión y las verificaciones sean aprobadas.
- Verificar el resultado archivado y sincronizar las especificaciones principales.
