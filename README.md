# Galería Comercial

Aplicación web para promocionar los locales comerciales de una galería y mejorar la experiencia de compra de sus visitantes. Permite descubrir productos, buscar con filtros, consultar el detalle de un producto, explorar categorías y ofertas, ubicar cada local en un mapa esquemático y conversar con un asistente virtual informativo. Los comerciantes administran su local y su catálogo desde un panel propio, y el administrador gestiona las cuentas de comerciante.

El repositorio contiene el sistema completo —backend, frontend, base de datos, datos de demostración y documentación de ingeniería— organizado como un monolito modular.

> **Datos de demostración.** La galería, sus locales, sus productos y la información institucional del asistente son ficticios y se usan únicamente con fines de demostración.

---

## Índice

1. [Descripción general](#1-descripción-general)
2. [Arquitectura](#2-arquitectura)
   - [2.1 Stack tecnológico](#21-stack-tecnológico)
   - [2.2 Estructura del repositorio](#22-estructura-del-repositorio)
   - [2.3 Arquitectura del backend](#23-arquitectura-del-backend)
   - [2.4 Arquitectura del frontend](#24-arquitectura-del-frontend)
   - [2.5 Comunicación entre frontend y backend](#25-comunicación-entre-frontend-y-backend)
   - [2.6 Flujo de una petición](#26-flujo-de-una-petición)
   - [2.7 Modelo de dominio](#27-modelo-de-dominio)
   - [2.8 Integraciones externas](#28-integraciones-externas)
3. [Instalación y ejecución desde cero](#3-instalación-y-ejecución-desde-cero)
   - [3.1 Requisitos previos](#31-requisitos-previos)
   - [3.2 Clonación del repositorio](#32-clonación-del-repositorio)
   - [3.3 Variables de entorno](#33-variables-de-entorno)
   - [3.4 Arranque con Docker](#34-arranque-con-docker)
   - [3.5 Inicialización de la base de datos](#35-inicialización-de-la-base-de-datos)
   - [3.6 Arranque local sin Docker](#36-arranque-local-sin-docker)
   - [3.7 URLs y puertos](#37-urls-y-puertos)
   - [3.8 Verificación del sistema](#38-verificación-del-sistema)
   - [3.9 Problemas comunes](#39-problemas-comunes)
4. [Casos de uso implementados](#4-casos-de-uso-implementados)
   - [4.1 Mapa de casos de uso](#41-mapa-de-casos-de-uso)
   - [4.2 CU #1 — Buscar productos](#42-cu-1--buscar-productos)
   - [4.3 CU #2 — Explorar productos, categorías y locales](#43-cu-2--explorar-productos-categorías-y-locales)
   - [4.4 CU #3 — Consultar el detalle de un producto](#44-cu-3--consultar-el-detalle-de-un-producto)
   - [4.5 CU #4 — Consultar la información de un local](#45-cu-4--consultar-la-información-de-un-local)
   - [4.6 CU #5 — Mapa de la galería](#46-cu-5--mapa-de-la-galería)
   - [4.7 CU #6 — Alta y baja de comerciantes](#47-cu-6--alta-y-baja-de-comerciantes)
   - [4.8 CU #7 — Inicio de sesión del comerciante](#48-cu-7--inicio-de-sesión-del-comerciante)
   - [4.9 CU #8 — Administrar el catálogo de productos](#49-cu-8--administrar-el-catálogo-de-productos)
   - [4.10 CU #9 — Administrar la información del local](#410-cu-9--administrar-la-información-del-local)
   - [4.11 CU #10 — Consultar estadísticas de productos](#411-cu-10--consultar-estadísticas-de-productos)
   - [4.12 CU #11 — Consultar el asistente virtual](#412-cu-11--consultar-el-asistente-virtual)
5. [Metodología de desarrollo](#5-metodología-de-desarrollo)
6. [AI Engineering](#6-ai-engineering)
   - [6.1 Rol de la IA durante el desarrollo](#61-rol-de-la-ia-durante-el-desarrollo)
   - [6.2 Prompts y estrategias](#62-prompts-y-estrategias)
   - [6.3 Metodología de iteración](#63-metodología-de-iteración)
   - [6.4 Loops de autocorrección](#64-loops-de-autocorrección)
   - [6.5 Estructuración de instrucciones](#65-estructuración-de-instrucciones)
   - [6.6 Evaluación de las respuestas generadas](#66-evaluación-de-las-respuestas-generadas)
7. [Agentes utilizados](#7-agentes-utilizados)
8. [MCP utilizados](#8-mcp-utilizados)
9. [Decisiones técnicas y metodológicas](#9-decisiones-técnicas-y-metodológicas)
10. [Procesos de corrección y validación](#10-procesos-de-corrección-y-validación)
11. [Apéndices](#12-apéndices)
    - [11.1 Resumen de endpoints](#111-resumen-de-endpoints)
    - [11.2 Credenciales de demostración](#112-credenciales-de-demostración)

---

## 1. Descripción general

**Galería Comercial** es una aplicación web full stack con tres roles:

| Rol | Capacidades |
|---|---|
| **Visitante** | Buscar productos, explorar ofertas y categorías, ver el detalle de un producto, consultar la ficha de un local, ubicar locales en el mapa y usar el asistente virtual. |
| **Comerciante** | Iniciar sesión, administrar el catálogo de su local, editar la información pública de su local y consultar estadísticas de búsqueda. |
| **Administrador** | Iniciar sesión, crear y dar de baja cuentas de comerciante y asignarles un local. |

Estado del proyecto: **11 casos de uso implementados** (los 10 casos oficiales más el asistente virtual), **17 especificaciones OpenSpec** sincronizadas, **0 cambios OpenSpec activos** y el repositorio sin divergencias respecto de `origin/main`.

El sistema **no** incluye carrito, favoritos, pagos ni checkout: su objetivo es la promoción y el descubrimiento comercial dentro de la galería.

---

## 2. Arquitectura

### 2.1 Stack tecnológico

| Capa | Tecnología | Versión declarada |
|---|---|---|
| Lenguaje backend | Python | 3.12 (imagen `python:3.12-slim`) |
| Framework backend | FastAPI | `>=0.115,<1.0` |
| ORM | SQLAlchemy 2.0 (síncrono, `Mapped` / `mapped_column`) | `>=2.0,<2.1` |
| Validación | Pydantic 2 + `pydantic-settings` | `>=2.9,<3.0` |
| Migraciones | Alembic | `>=1.13,<2.0` |
| Base de datos | PostgreSQL | 17 (`postgres:17-alpine`) |
| Driver | `psycopg` 3 | `>=3.2,<4.0` |
| Seguridad | `bcrypt`, `PyJWT` | `>=4.1,<5.0`, `>=2.8,<3.0` |
| Pruebas backend | Pytest + `httpx` | `>=8.3,<9.0`, `>=0.27,<1.0` |
| UI | React + React DOM | `^19.3.1` |
| Lenguaje frontend | TypeScript | `^5.9.3` |
| Bundler / dev server | Vite | `^8.3.5` |
| Estilos | Tailwind CSS (`@tailwindcss/vite`) | `^4.3.4` |
| Ruteo | React Router | `^7.18.5` |
| Estado de servidor | TanStack Query | `^5.105.3` |
| HTTP | Fetch API nativa | — |
| Pruebas frontend | Vitest + React Testing Library + `jsdom` | `^5.1.0`, `^16.3.3`, `^30.1.3` |
| Contenedores | Docker + Docker Compose | — |
| Asistente | Groq (chat), `sentence-transformers`, ChromaDB, LangChain mínimo | ver `backend/requirements.txt` |

Tecnologías **excluidas explícitamente** por decisión del proyecto: Axios, shadcn/ui, ESLint, Prettier y Ruff. Esa exclusión está documentada en `AGENTS.md` y en `openspec/config.yaml`, y se respeta en el código.

### 2.2 Estructura del repositorio

```text
.
├── AGENTS.md                     # Reglas del proyecto: arquitectura, roles, workflow, Git
├── README.md                     # Este documento
├── docker-compose.yml            # db + backend + frontend
├── opencode.json                 # Configuración del MCP de GitHub (sin secretos)
├── .env.example                  # Plantilla de variables de entorno
├── docker/
│   └── postgres/init/
│       └── 01-create-test-db.sql # Crea app_test en la primera inicialización
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   │       ├── 0001_domain_model.py
│   │       ├── 0002_add_user_full_name.py
│   │       └── 0003_active_merchant_uniqueness.py
│   ├── app/
│   │   ├── main.py               # App FastAPI, CORS y registro de routers
│   │   ├── core/                 # config, database, security, validation
│   │   ├── db/                   # Base declarativa, mixins, registro de modelos
│   │   └── modules/              # Módulos funcionales (ver 2.3)
│   ├── scripts/                  # Semillas y utilidades de datos
│   └── tests/                    # 15 archivos de pruebas
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── .env.example
│   └── src/
│       ├── app/                  # Router, providers y layout
│       ├── features/             # 12 features por funcionalidad
│       ├── pages/                # Páginas contenedoras
│       ├── lib/                  # http, token, useGoBack
│       └── test/                 # 15 archivos de pruebas
└── openspec/
    ├── config.yaml               # Contexto y reglas de OpenSpec
    ├── specs/                    # 17 especificaciones vigentes
    └── changes/archive/          # 16 cambios archivados
```

### 2.3 Arquitectura del backend

El backend es un **monolito modular**: cada módulo agrupa su router, sus schemas, su servicio y, cuando corresponde, sus modelos. No hay capa de repositorio separada porque los servicios usan SQLAlchemy 2.0 directamente; se prefirió evitar una abstracción que no aportaba valor en este tamaño de proyecto.

| Módulo | Responsabilidad | Rutas |
|---|---|---|
| `health` | Estado del backend y de la base | `GET /api/health` |
| `auth` | Login, identidad y dependencias de autorización | `POST /api/auth/login`, `GET /api/auth/me` |
| `merchants` | Administración de cuentas de comerciante | `/api/admin/merchants`, `/api/admin/stores` |
| `merchant_catalog` | Catálogo propio del comerciante | `/api/merchant/products`, `/api/merchant/categories` |
| `merchant_store` | Información pública del local propio | `/api/merchant/store` |
| `public_catalog` | Catálogo público: búsqueda, exploración, productos y locales | `/api/public/*` |
| `analytics` | Estadísticas de productos más buscados | `/api/merchant/stats/products` |
| `assistant` | Asistente virtual con RAG | `/api/public/assistant/chat` |
| `accounts`, `stores`, `catalog` | Modelos del dominio | — |

Piezas transversales:

- `app/core/config.py`: `Settings` con `pydantic-settings`; `DATABASE_URL` y `JWT_SECRET` son obligatorios.
- `app/core/database.py`: motor SQLAlchemy (`pool_pre_ping`) y dependencia `get_db` que cierra la sesión al terminar la petición.
- `app/core/security.py`: hash `bcrypt` y emisión/validación de JWT.
- `app/core/validation.py`: tipo de correo reutilizable.
- `app/db/registry.py`: importa todos los modelos para que Alembic y las relaciones queden registrados.
- `app/db/mixins.py`: `TimestampMixin` (`created_at`, `updated_at`).

Autorización: `get_current_user`, `require_admin` y `require_merchant` viven en `auth/dependencies.py`. Devuelven `401` sin token o con token inválido, y `403` cuando el rol no corresponde o el comerciante no tiene local asignado.

```mermaid
flowchart TB
    subgraph Cliente
        B[Navegador]
    end

    subgraph Frontend["Frontend · React + Vite :5173"]
        RT[React Router]
        TQ[TanStack Query]
        LIB[apiFetch]
    end

    subgraph Backend["Backend · FastAPI :8000"]
        MW[CORS]
        RTD[Routers]
        DEP[Dependencias de auth]
        SRV[Servicios de negocio]
        ORM[SQLAlchemy 2.0]
        SCH[Schemas Pydantic 2]
    end

    subgraph Datos
        PG[(PostgreSQL 17 :5433)]
        CH[(ChromaDB · volumen)]
        HF[(Caché de embeddings · volumen)]
    end

    subgraph Externo
        GQ[Groq API]
    end

    B --> RT --> TQ --> LIB
    LIB -->|HTTP JSON| MW --> RTD
    RTD --> DEP
    RTD --> SCH
    RTD --> SRV --> ORM --> PG
    SRV -->|RAG| CH
    SRV --> HF
    SRV -->|chat| GQ
```

### 2.4 Arquitectura del frontend

El frontend se organiza **por funcionalidad (feature-based)**. Cada feature agrupa sus componentes, su cliente de API, sus tipos TypeScript, sus query keys y sus pruebas. No se usa estado global salvo el contexto de autenticación. El layout compartido vive en `app/layout` y las páginas contenedoras en `pages/`.

| Feature / capa | Contenido |
|---|---|
| `app/layout` | `SiteHeader`, `HeaderSearch`, `AccountActions`, `AppLayout` |
| `auth` | `AuthContext`, `LoginPage`, `ProtectedRoute`, `api`, `types` |
| `explore` | `ExploreContent`, `CategoryCard`, `StoreCard`, `StoreListPage` |
| `product-search` | `SearchPage`, `ProductCard`, `api`, `format` |
| `product-detail` | `ProductDetailPage`, `ProductGallery`, `SimilarProducts` |
| `store-detail` | `StoreDetailPage`, `StoreCatalog`, `StoreHours`, `StoreLinks` |
| `store-map` | `StoreMapPage`, `MapLayout`, `StoreSlot` |
| `assistant` | `AssistantWidget`, `AssistantPanel`, `MessageList`, `ActionButton` |
| `admin-merchants` | `MerchantsPage`, `MerchantForm`, `MerchantTable` |
| `merchant-catalog` | `ProductListPage`, `ProductFormPage`, `ProductTable`, baja/restauración |
| `merchant-store` | `StoreSettingsPage`, `GeneralSection`, `ContactSection`, `HoursEditor`, `LinksEditor` |
| `product-stats` | `ProductStatsPage`, `ProductStatsTable`, `StatsPeriodSelector` |
| `health` | `HealthStatus` |

Rutas del frontend:

| Ruta | Página | Acceso |
|---|---|---|
| `/` | Inicio: CTA al mapa + exploración | Público |
| `/explorar` | Redirección a `/` | Público |
| `/buscar` | Buscador con resultados | Público |
| `/productos/:productId` | Detalle de producto | Público |
| `/locales` | Listado de locales | Público |
| `/locales/:storeId` | Ficha del local con catálogo | Público |
| `/mapa` | Mapa esquemático | Público |
| `/login` | Inicio de sesión | Público |
| `/admin` | Panel del administrador | Autenticado |
| `/admin/comerciantes` | Gestión de comerciantes | Autenticado |
| `/comerciante` | Panel del comerciante | Rol `merchant` |
| `/comerciante/local` | Información del local | Rol `merchant` |
| `/comerciante/productos` | Catálogo propio | Rol `merchant` |
| `/comerciante/productos/nuevo` | Alta de producto | Rol `merchant` |
| `/comerciante/productos/:productId/editar` | Edición de producto | Rol `merchant` |
| `/comerciante/estadisticas` | Estadísticas | Rol `merchant` |
| `*` | Página no encontrada | Público |

`ProtectedRoute` comprueba la sesión y, opcionalmente, el rol. Es una comodidad de navegación: **la autorización real siempre la aplica el backend**.

### 2.5 Comunicación entre frontend y backend

- El backend define y mantiene el contrato de la API; el frontend solo lo consume.
- Todas las peticiones pasan por `src/lib/http.ts` → `apiFetch`, que:
  - resuelve la URL base desde `VITE_API_URL` (por defecto `http://localhost:8000/api`);
  - agrega `Authorization: Bearer <token>` si hay sesión;
  - lanza `ApiError` con el código HTTP cuando la respuesta no es `2xx`;
  - devuelve `undefined` en `204`.
- El token JWT se guarda en **`sessionStorage`** (`galeria.auth.token`), no en `localStorage`: la sesión no sobrevive al cierre de la pestaña.
- El estado de servidor se cachea con TanStack Query, con query keys por recurso (por ejemplo `['public','store',id,'products',page]`).
- CORS se controla con `CORS_ORIGINS` (lista separada por comas).

### 2.6 Flujo de una petición

```mermaid
sequenceDiagram
    autonumber
    participant V as Navegador
    participant R as React + TanStack Query
    participant F as apiFetch
    participant A as FastAPI
    participant D as Dependencias
    participant S as Servicio
    participant O as SQLAlchemy
    participant P as PostgreSQL

    V->>R: interacción del usuario
    R->>F: queryFn / mutation
    F->>A: HTTP(S) + JSON (+ Bearer)
    A->>A: validación del schema Pydantic
    A->>D: get_db / require_merchant
    D-->>A: sesión + usuario autenticado
    A->>S: llamada al servicio
    S->>O: select / insert / update
    O->>P: SQL parametrizado
    P-->>O: filas
    O-->>S: entidades
    S-->>A: schema de respuesta
    A-->>F: JSON + código HTTP
    F-->>R: datos tipados o ApiError
    R-->>V: render, estados de carga/error/vacío
```

### 2.7 Modelo de dominio

Nueve tablas de dominio, creadas por la migración `0001` y ajustadas por `0002` y `0003`.

```mermaid
erDiagram
    USERS {
        bigint id PK
        string email
        string full_name
        string password_hash
        string role
        boolean is_active
        bigint store_id FK
    }
    STORES {
        bigint id PK
        smallint number UK
        string name
        text description
        string logo_url
        string email
        string phone
        string whatsapp
        string side
        smallint position
        boolean is_active
    }
    STORE_HOURS {
        bigint id PK
        bigint store_id FK
        smallint day_of_week
        time opens_at
        time closes_at
    }
    STORE_LINKS {
        bigint id PK
        bigint store_id FK
        string label
        string url
        smallint position
    }
    CATEGORIES {
        bigint id PK
        string name
    }
    PRODUCTS {
        bigint id PK
        bigint store_id FK
        string name
        text description
        numeric price
        numeric offer_price
        boolean is_featured
        boolean is_active
        timestamptz deleted_at
    }
    PRODUCT_CATEGORIES {
        bigint product_id PK
        bigint category_id PK
    }
    PRODUCT_IMAGES {
        bigint id PK
        bigint product_id FK
        string url
        string alt_text
        smallint position
        boolean is_primary
    }
    PRODUCT_SEARCH_EVENTS {
        bigint id PK
        bigint product_id FK
        string query
        timestamptz searched_at
    }

    STORES ||--o{ USERS : "asigna comerciante"
    STORES ||--o{ STORE_HOURS : "horarios"
    STORES ||--o{ STORE_LINKS : "enlaces"
    STORES ||--o{ PRODUCTS : "catálogo"
    PRODUCTS ||--o{ PRODUCT_CATEGORIES : "clasifica"
    CATEGORIES ||--o{ PRODUCT_CATEGORIES : "agrupa"
    PRODUCTS ||--o{ PRODUCT_IMAGES : "imágenes"
    PRODUCTS ||--o{ PRODUCT_SEARCH_EVENTS : "eventos"
```

Invariantes relevantes garantizadas en la base:

- `users.role ∈ {admin, merchant}`; un comerciante **debe** tener local y un administrador **no**.
- Correo único sin distinguir mayúsculas (`lower(email)`).
- Un solo comerciante **activo** por local (índice único parcial), lo que permite reasignar un local tras una baja.
- `stores.side ∈ {left, right, back}` con `position` 1–10, o `back` con `position = 1`; `(side, position)` único.
- `store_hours.day_of_week` 0–6 y `closes_at > opens_at`.
- `products.price >= 0` y `offer_price < price`.
- Una sola imagen primaria por producto (índice único parcial).
- Categorías únicas sin distinguir mayúsculas.

El local físico se modela por **lado y posición**, no por coordenadas: 10 locales a la izquierda, 10 a la derecha y 1 al fondo (21 en total, numerados de forma intercalada).

Borrado lógico: los productos usan `deleted_at`; los comerciantes usan `is_active`. En ambos casos los datos y las estadísticas se conservan.

### 2.8 Integraciones externas

| Integración | Uso | Configuración |
|---|---|---|
| **Groq API** | Chat del asistente y clasificación de intención | `GROQ_API_KEY`, `GROQ_MODEL`, `GROQ_MODEL_PREFERENCES` |
| **sentence-transformers** | Embeddings multilingües locales (`paraphrase-multilingual-MiniLM-L12-v2`) | `HF_HOME` para la caché |
| **ChromaDB** (embebido) | Índice vectorial persistente de la base de conocimiento | `CHROMA_PATH`, volumen `chroma_data` |
| **LangChain** (mínimo) | `langchain-groq`, `langchain-huggingface`, `langchain-chroma`, `langchain-text-splitters` | Solo dentro del módulo `assistant` |
| **picsum.photos** | URLs de imágenes de los datos demo | Generadas por `seed_demo.py` |
| **GitHub** | Publicación y verificación de commits | Vía MCP, con token en archivo fuera del repositorio |

No hay integraciones de pago, mensajería, analítica de terceros ni geolocalización.

---

## 3. Instalación y ejecución desde cero

### 3.1 Requisitos previos

Recomendado (todo el entorno en contenedores):

- Docker Engine 24 o superior.
- Docker Compose v2 (`docker compose`).

Alternativa sin Docker:

- Python 3.12 o superior.
- Node.js 22 o superior (el Dockerfile usa `node:22-alpine`).
- PostgreSQL 17.
- `git`.

Verificación rápida:

```bash
docker --version
docker compose version
python3 --version
node --version
```

### 3.2 Clonación del repositorio

```bash
git clone https://github.com/MelEdur/Galer-a-comercial--webapp.git
cd Galer-a-comercial--webapp
git switch main
```

### 3.3 Variables de entorno

Hay **dos** archivos de entorno, con alcances distintos:

| Archivo | Alcance | Contenido |
|---|---|---|
| `.env` (raíz) | Docker Compose y backend | Base de datos, JWT, administrador inicial y asistente |
| `frontend/.env.local` | Frontend en desarrollo local | `VITE_API_URL` |

Creación:

```bash
cp .env.example .env
```

> `.env` y `.env.*` están excluidos por `.gitignore`; solo se versionan las plantillas `.env.example` y `frontend/.env.example`.

#### Variables de la raíz

| Variable | Obligatoria | Por defecto | Descripción |
|---|---|---|---|
| `POSTGRES_USER` | No | `galeria` | Usuario de PostgreSQL. |
| `POSTGRES_PASSWORD` | No | `change-me` | Contraseña de PostgreSQL. Cambiarla fuera de demo. |
| `POSTGRES_DB` | No | `galeria` | Base principal. |
| `POSTGRES_PORT` | No | `5433` | Puerto del host para PostgreSQL. Se usa 5433 para no chocar con un PostgreSQL local en 5432. |
| `ENVIRONMENT` | No | `development` | Entorno lógico. |
| `BACKEND_PORT` | No | `8000` | Puerto del backend en el host. |
| `DATABASE_URL` | Sí, al ejecutar el backend sin Docker | `postgresql+psycopg://galeria:change-me@db:5432/galeria` | URL de SQLAlchemy. Debe coincidir con las variables `POSTGRES_*`. |
| `TEST_DATABASE_URL` | No | `postgresql+psycopg://galeria:change-me@db:5432/app_test` | Base usada por las pruebas que tocan PostgreSQL. |
| `CORS_ORIGINS` | No | `http://localhost:5173` | Orígenes permitidos, separados por comas. |
| `JWT_SECRET` | **Sí** (sin valor por defecto) | — | Secreto de firma de los tokens. Compose falla si falta. |
| `JWT_ALGORITHM` | No | `HS256` | Algoritmo de firma. |
| `JWT_EXPIRE_MINUTES` | No | `60` | Vida útil del token. |
| `ADMIN_EMAIL` | No | `admin@galeria.local` | Correo del administrador inicial; solo lo lee `create_admin`. |
| `ADMIN_PASSWORD` | No | `change-me-admin` | Contraseña del administrador inicial; solo `create_admin`. |
| `ADMIN_FULL_NAME` | No | `Administrador` | Nombre del administrador inicial. |
| `GROQ_API_KEY` | No | vacío | Clave de Groq. Sin clave el asistente no puede generar respuestas. |
| `GROQ_MODEL` | No | vacío | Modelo de chat fijo; vacío activa la selección automática. |
| `GROQ_MODEL_PREFERENCES` | No | `openai/gpt-oss-120b,openai/gpt-oss-20b,qwen/qwen3.8-27b` | Preferencias ordenadas para la selección automática. |
| `ASSISTANT_TOP_K` | No | `5` | Fragmentos recuperados por consulta. |
| `ASSISTANT_MAX_MESSAGE_CHARS` | No | `1000` | Longitud máxima de un mensaje. |
| `ASSISTANT_MAX_HISTORY_MESSAGES` | No | `10` | Mensajes de historial aceptados. |
| `ASSISTANT_RATE_LIMIT` | No | `20` | Consultas por IP y ventana. |
| `ASSISTANT_RATE_WINDOW_SECONDS` | No | `300` | Duración de la ventana de rate limit. |
| `ASSISTANT_TIMEOUT_SECONDS` | No | `20` | Timeout del proveedor de chat. |
| `CHROMA_PATH` | No | `/data/chroma` | Directorio de ChromaDB. En Compose está fijado a `/data/chroma` sobre un volumen. |
| `HF_HOME` | No | `/data/hf` | Caché del modelo de embeddings. En Compose está fijado a `/data/hf` sobre un volumen. |
| `FRONTEND_PORT` | No | `5173` | Puerto del frontend en el host. |
| `VITE_API_URL` | No | `http://localhost:8000/api` | URL base de la API que consume el navegador. |

Configuración avanzada (solo ejecutando el backend directamente, sin Compose): `Settings` también acepta `APP_NAME`, `ASSISTANT_EMBEDDING_MODEL` y `ASSISTANT_COLLECTION`, con valores por defecto. Docker Compose no las propaga, así que definirlas en `.env` no tiene efecto dentro de los contenedores.

#### Variables del frontend

| Variable | Obligatoria | Por defecto | Descripción |
|---|---|---|---|
| `VITE_API_URL` | No | `http://localhost:8000/api` | URL base de la API. Si falta, `src/lib/http.ts` usa ese valor. |

En desarrollo local:

```bash
cd frontend
cp .env.example .env.local
```

Vite solo expone variables con prefijo `VITE_`, y solo en tiempo de build/dev. **No se deben poner secretos en variables `VITE_*`**: terminan en el bundle del navegador.

#### Reglas de seguridad

- No versionar `.env` ni claves reales.
- Rotar cualquier credencial que se haya compartido por un canal inseguro.
- Usar un `JWT_SECRET` largo y aleatorio fuera de desarrollo.
- Cambiar `POSTGRES_PASSWORD`, `ADMIN_PASSWORD` y las contraseñas demo en cualquier entorno expuesto.

### 3.4 Arranque con Docker

```bash
cp .env.example .env
# editar JWT_SECRET antes de continuar
docker compose up --build
```

Servicios definidos en `docker-compose.yml`:

| Servicio | Imagen | Puerto host | Volúmenes |
|---|---|---|---|
| `db` | `postgres:17-alpine` | `5433` → 5432 | `postgres_data` + init SQL |
| `backend` | build `./backend` | `8000` | `./backend:/app`, `chroma_data`, `hf_cache` |
| `frontend` | build `./frontend` (`node:22-alpine`) | `5173` | `./frontend:/app`, `node_modules` anónimo |

Dependencias de arranque: `backend` espera a que `db` esté *healthy*; `frontend` arranca cuando el backend está iniciado. Backend y frontend corren con recarga en caliente (`uvicorn --reload`, `vite dev`).

Detener el entorno:

```bash
docker compose down
```

Eliminar también los datos (base, Chroma y caché del modelo):

```bash
docker compose down -v
```

### 3.5 Inicialización de la base de datos

Las migraciones **no** se ejecutan automáticamente al arrancar. El orden es:

```bash
# 1. Esquema
docker compose exec backend alembic upgrade head

# 2. Los 21 locales fijos
docker compose exec backend python -m scripts.seed_stores

# 3. Las 10 categorías globales
docker compose exec backend python -m scripts.seed_categories

# 4. Administrador inicial (lee ADMIN_EMAIL / ADMIN_PASSWORD)
docker compose exec backend python -m scripts.create_admin

# 5. Datos de demostración: comerciantes, locales y 420 productos
docker compose exec backend python -m scripts.seed_demo

# 6. Índice del asistente (descarga el modelo la primera vez)
docker compose exec backend python -m scripts.reindex_assistant
```

Todos los scripts de semilla son **idempotentes**:

- `seed_stores` usa `number` como clave natural.
- `seed_categories` compara nombres sin distinguir mayúsculas.
- `create_admin` no modifica una cuenta existente.
- `seed_demo` hace *upsert* por `(store_id, name)` y conserva lo existente.

Comprobación de migraciones:

```bash
docker compose exec backend alembic current
docker compose exec backend alembic check
```

Nueva migración (solo cuando cambie el modelo):

```bash
docker compose exec backend alembic revision --autogenerate -m "descripcion"
```

### 3.6 Arranque local sin Docker

#### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

export DATABASE_URL=postgresql+psycopg://galeria:change-me@localhost:5433/galeria
export JWT_SECRET=dev-only-secret-change-me

alembic upgrade head
python -m scripts.seed_stores
python -m scripts.seed_categories
python -m scripts.create_admin
python -m scripts.seed_demo
python -m scripts.reindex_assistant
uvicorn app.main:app --reload
```

El backend requiere `DATABASE_URL` y `JWT_SECRET`; sin ellos `Settings` falla al importarse y el proceso no arranca.

Si se usa el PostgreSQL de Docker desde el host, el puerto es `5433`.

#### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

#### Pruebas

```bash
# Backend
cd backend
source .venv/bin/activate
pytest -q

# Frontend
cd frontend
npm test -- --run
npm run build
```

La prueba que usa una conexión real a PostgreSQL depende de `TEST_DATABASE_URL`; si no está definida, se omite con un mensaje explícito.

### 3.7 URLs y puertos

| Recurso | URL |
|---|---|
| Frontend | <http://localhost:5173> |
| Backend | <http://localhost:8000> |
| Documentación interactiva (Swagger UI) | <http://localhost:8000/docs> |
| Esquema OpenAPI | <http://localhost:8000/openapi.json> |
| Salud | <http://localhost:8000/api/health> |
| PostgreSQL (host) | `localhost:5433` |

### 3.8 Verificación del sistema

```bash
curl http://localhost:8000/api/health
```

Con la base disponible:

```json
{"status":"ok","database":"ok"}
```

Sin base disponible, responde `503`:

```json
{"status":"degraded","database":"unavailable"}
```

Verificación funcional mínima:

1. Abrir `http://localhost:5173` y comprobar que se ven productos destacados y ofertas.
2. Abrir `/mapa` y entrar a un local.
3. Abrir un producto desde el catálogo del local y usar **Volver**.
4. Iniciar sesión como comerciante y abrir `/comerciante/productos`.
5. Iniciar sesión como administrador y abrir `/admin/comerciantes`.
6. Abrir el widget del asistente y preguntar por la dirección de la galería.

### 3.9 Problemas comunes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `JWT_SECRET is required` | Falta la variable | Definirla en `.env`. |
| El frontend sigue mostrando una versión vieja | Caché de transformación de Vite | `docker compose restart frontend` y recargar con `Ctrl+Shift+R`. |
| El asistente tarda mucho la primera vez | Descarga del modelo de embeddings (~470 MB) | Esperar; queda en el volumen `hf_cache`. |
| El asistente responde `503` | Falta `GROQ_API_KEY`, Chroma no está indexado o el proveedor falla | Revisar la variable y ejecutar `python -m scripts.reindex_assistant`. |
| Puerto 5432 ocupado | PostgreSQL local | El proyecto ya usa 5433; ajustar `POSTGRES_PORT` si hiciera falta. |
| `app_test` no existe | El volumen se creó antes del init SQL | Crear la base manualmente o recrear con `docker compose down -v`. |

---

## 4. Casos de uso implementados

Los casos de uso se describen **según el comportamiento final implementado**, no según el enunciado original. Cuando el alcance original quedó cubierto solo en parte, se indica en la sección 4.13.

### 4.1 Mapa de casos de uso

| CU | Nombre | Actor | Spec vigente | Implementación principal |
|---|---|---|---|---|
| #1 | Buscar productos | Visitante | `product-search` | `public_catalog` · `/buscar` |
| #2 | Explorar productos, categorías y locales | Visitante | `explore`, `site-navigation` | `public_catalog` · `/`, `/locales` |
| #3 | Detalle de producto | Visitante | `product-detail` | `public_catalog` · `/productos/:id` |
| #4 | Información de un local | Visitante | `store-detail` | `public_catalog` · `/locales/:id` |
| #5 | Mapa de la galería | Visitante | `store-map` | `public_catalog` · `/mapa` |
| #6 | Alta y baja de comerciantes | Administrador | `merchant-administration` | `merchants` · `/admin/comerciantes` |
| #7 | Login del comerciante | Comerciante | `merchant-portal` | `auth` · `/login`, `/comerciante` |
| #8 | Administrar catálogo | Comerciante | `merchant-product-catalog` | `merchant_catalog` · `/comerciante/productos` |
| #9 | Administrar información del local | Comerciante | `merchant-store-settings` | `merchant_store` · `/comerciante/local` |
| #10 | Estadísticas de productos | Comerciante | `product-statistics` | `analytics` · `/comerciante/estadisticas` |
| #11 | Asistente virtual | Visitante | `gallery-assistant` | `assistant` · widget global |

### 4.2 CU #1 — Buscar productos

- **Actor:** visitante.
- **Objetivo:** encontrar productos disponibles según nombre, categoría, rango de precio y ofertas.
- **Precondiciones:** existen categorías y productos; no se requiere autenticación.
- **Flujo principal:**
  1. El visitante escribe un término en el buscador del header y confirma.
  2. Navega a `/buscar` con los filtros aplicados.
  3. El frontend consulta `GET /api/public/products` con `search`, `category_id`, `min_price`, `max_price`, `has_offer`, `page`, `page_size` y `sort`.
  4. El backend devuelve una página con `items`, `total`, `page`, `page_size` y `pages`.
  5. Cada tarjeta muestra imagen, nombre, precio, oferta, categorías y local, y enlaza a `/productos/{id}`.
  6. Si hay al menos un criterio y la página devuelve resultados, se registra un evento de búsqueda por producto para CU #10.
- **Flujos alternativos:**
  - Sin criterios: se devuelve todo el catálogo disponible paginado.
  - Se cambia el orden a `price_asc` o `price_desc`.
  - Se navega entre páginas sin perder los filtros.
- **Excepciones:**
  - `min_price > max_price` o precio negativo → `422`.
  - Página o `page_size` fuera de rango → `422`.
  - Sin resultados → estado vacío; no se registran eventos.

### 4.3 CU #2 — Explorar productos, categorías y locales

- **Actor:** visitante.
- **Objetivo:** descubrir contenido sin una búsqueda previa.
- **Precondiciones:** ninguna.
- **Flujo principal:**
  1. El visitante abre `/`.
  2. Ve un encabezado con el CTA **“Ver mapa de la galería”**.
  3. Debajo, la exploración muestra productos destacados, ofertas, categorías con conteo y locales.
  4. Puede abrir un producto, una categoría (que lleva al buscador filtrado) o un local.
- **Flujos alternativos:**
  - `/explorar` redirige a `/`.
  - `/locales` lista los 21 locales activos.
  - Una categoría sin productos aparece igual, con conteo cero.
- **Excepciones:** si `GET /api/public/explore` falla, la UI muestra estado de error y permite reintentar; si no hay destacados u ofertas, muestra un mensaje de sección vacía.

### 4.4 CU #3 — Consultar el detalle de un producto

- **Actor:** visitante.
- **Objetivo:** ver imágenes, descripción, precio y el local que lo vende.
- **Precondiciones:** el producto está disponible (no eliminado, activo y de local activo).
- **Flujo principal:**
  1. El visitante abre `/productos/{id}`.
  2. El frontend consulta `GET /api/public/products/{id}`.
  3. Ve galería de imágenes, nombre, descripción, precio, oferta, categorías y datos de contacto del local.
  4. Se consulta `GET /api/public/products/{id}/similar` y se muestran hasta seis productos similares.
  5. **“Volver”** regresa a la página de origen.
- **Flujos alternativos:**
  - Llegada desde el buscador, desde el catálogo de un local o desde similares.
  - Entrada directa por URL: **“Volver”** navega a `/`.
- **Excepciones:**
  - Producto inexistente, eliminado, inactivo o de local inactivo → `404` y estado “no encontrado”.
  - Identificador no numérico → `422`.

### 4.5 CU #4 — Consultar la información de un local

- **Actor:** visitante.
- **Objetivo:** conocer los datos del local y explorar su catálogo.
- **Precondiciones:** el local está activo.
- **Flujo principal:**
  1. El visitante abre `/locales/{id}` (desde el mapa, una tarjeta o el detalle de un producto).
  2. Consulta `GET /api/public/stores/{id}`: nombre, logo, número, descripción, horarios, contacto y enlaces.
  3. Debajo de los enlaces ve la sección **Catálogo**.
  4. El catálogo consulta `GET /api/public/stores/{id}/products` con `page` y `page_size=12`.
  5. Cada tarjeta enlaza al detalle del producto y **no repite el local**.
- **Flujos alternativos:**
  - Local con más de 12 productos: paginación anterior/siguiente.
  - Datos opcionales ausentes (`logo_url`, `email`, `phone`, `whatsapp`): se muestra un estado equivalente sin romper la vista.
  - **“Volver”** regresa al origen real.
- **Excepciones:**
  - Local inexistente o inactivo → `404`.
  - Catálogo vacío → “Este local todavía no tiene productos disponibles”.
  - Entrada directa: **“Volver”** navega a `/`.

### 4.6 CU #5 — Mapa de la galería

- **Actor:** visitante.
- **Objetivo:** ubicar un local dentro de la galería.
- **Precondiciones:** existen locales activos con `side` y `position`.
- **Flujo principal:**
  1. El visitante abre `/mapa`.
  2. El frontend consulta `GET /api/public/map`.
  3. Se dibuja un plano **esquemático**: 10 locales a la izquierda, 10 a la derecha y 1 al fondo.
  4. Cada slot muestra número, logo y nombre.
  5. Al seleccionar un local se abre una ficha resumida con acceso a `/locales/{id}`.
- **Flujos alternativos:** acceder al mapa desde el CTA de la portada o desde el header.
- **Excepciones:** si no hay locales activos, el mapa se muestra vacío; un fallo de red muestra estado de error.

### 4.7 CU #6 — Alta y baja de comerciantes

- **Actor:** administrador.
- **Objetivo:** crear cuentas de comerciante con un local asignado y darlas de baja.
- **Precondiciones:** sesión con rol `admin`; existen locales.
- **Flujo principal:**
  1. El administrador inicia sesión y abre `/admin/comerciantes`.
  2. `GET /api/admin/merchants` lista las cuentas y `GET /api/admin/stores` los 21 locales con su comerciante activo o `null`.
  3. Crea una cuenta con `POST /api/admin/merchants` (correo, nombre, contraseña y local).
  4. La baja se hace con `DELETE /api/admin/merchants/{id}`, que desactiva la cuenta e idempotentemente libera el local.
- **Flujos alternativos:** un local ya ocupado no aparece disponible para una nueva asignación.
- **Excepciones:**
  - Correo duplicado → `409`.
  - Local ocupado → `409`.
  - Local inexistente → `404`.
  - Sin token → `401`; con rol `merchant` → `403`.
  - La baja **no** elimina físicamente la cuenta ni sus datos.

### 4.8 CU #7 — Inicio de sesión del comerciante

- **Actor:** comerciante.
- **Objetivo:** acceder al panel de su local.
- **Precondiciones:** cuenta activa con local asignado.
- **Flujo principal:**
  1. El comerciante abre `/login` e ingresa correo y contraseña.
  2. `POST /api/auth/login` valida `bcrypt` y devuelve un JWT.
  3. El frontend guarda el token en `sessionStorage` y consulta `GET /api/auth/me`.
  4. Según el rol, redirige a `/comerciante` o `/admin`.
  5. El panel muestra nombre, correo, número y nombre del local, y permite cerrar sesión.
- **Flujos alternativos:** un administrador que inicia sesión va a `/admin`; el header muestra las acciones correspondientes al rol.
- **Excepciones:**
  - Credenciales inválidas → `401` con mensaje uniforme (no revela si el correo existe).
  - Token vencido o inválido → `401` y vuelta al login.
  - Comerciante sin local → `403`.

### 4.9 CU #8 — Administrar el catálogo de productos

- **Actor:** comerciante.
- **Objetivo:** crear, consultar, editar, dar de baja y restaurar productos de su local.
- **Precondiciones:** sesión `merchant` con local asignado.
- **Flujo principal:**
  1. Abre `/comerciante/productos`.
  2. `GET /api/merchant/products` lista su catálogo con `search`, `status` (`active`/`deleted`/`all`), `category_id`, `page` y `page_size`.
  3. Crea un producto con `POST /api/merchant/products` (nombre, precio, al menos una categoría; descripción, oferta e imágenes opcionales).
  4. Edita con `PATCH /api/merchant/products/{id}`.
  5. Da de baja con `DELETE /api/merchant/products/{id}` (borrado lógico, `204`).
  6. Restaura con `POST /api/merchant/products/{id}/restore`.
- **Flujos alternativos:**
  - Las imágenes se envían por URL (`http`/`https`), hasta 5; la primera queda como primaria.
  - `GET /api/merchant/categories` provee las categorías globales.
- **Excepciones:**
  - Oferta mayor o igual al precio → `422`.
  - Categoría inexistente o sin categorías → `422`.
  - Producto de otro local → `404` (no se filtra su existencia).
  - Editar un producto eliminado → `409`.
  - El `store_id` nunca se acepta en el payload: se deriva del token.

### 4.10 CU #9 — Administrar la información del local

- **Actor:** comerciante.
- **Objetivo:** actualizar los datos públicos de su local.
- **Precondiciones:** sesión `merchant` con local asignado.
- **Flujo principal:**
  1. Abre `/comerciante/local`.
  2. `GET /api/merchant/store` devuelve el local con horarios y enlaces.
  3. Edita nombre, descripción, logo, correo, teléfono, WhatsApp, horarios y enlaces.
  4. Guarda con `PUT /api/merchant/store`; horarios y enlaces **reemplazan** el conjunto anterior.
  5. El backend actualiza el local y, en segundo plano, reindexa el documento del local en el asistente.
  6. El frontend vuelve al panel con los datos actualizados.
- **Flujos alternativos:** dejar campos opcionales vacíos los guarda como `null`.
- **Excepciones:**
  - `closes_at <= opens_at` → `422`.
  - Horarios duplicados (mismo día y apertura) → `422`.
  - Más de 10 enlaces o URLs repetidas → `422`.
  - URL inválida o demasiado larga → `422`.
  - Un fallo de reindexación se registra y **no** revierte el guardado.

### 4.11 CU #10 — Consultar estadísticas de productos

- **Actor:** comerciante.
- **Objetivo:** conocer los productos más buscados de su local en un período.
- **Precondiciones:** existen eventos de búsqueda registrados por CU #1.
- **Flujo principal:**
  1. Abre `/comerciante/estadisticas`.
  2. Elige un período: 7, 30 o 90 días, o un rango personalizado.
  3. `GET /api/merchant/stats/products` devuelve `from_date`, `to_date`, `total_searches` y un Top 10 con `product_id`, `name`, `search_count`, `is_deleted` y `last_searched_at`.
  4. La UI muestra la tabla con el ranking y el total.
- **Flujos alternativos:** sin argumentos se usan los últimos 30 días.
- **Excepciones:**
  - `days` distinto de 7/30/90 → `422`.
  - `days` combinado con fechas → `422`.
  - Solo una de las dos fechas → `422`.
  - `from_date > to_date` → `422`.
  - Los productos eliminados se incluyen y se marcan como tales.
  - Los límites del día se calculan en hora de Buenos Aires (UTC-3) y se convierten a UTC para filtrar.

### 4.12 CU #11 — Consultar el asistente virtual

- **Actor:** visitante.
- **Objetivo:** resolver dudas informativas sobre la galería en lenguaje natural.
- **Precondiciones:** el índice vectorial está construido y `GROQ_API_KEY` está configurada.
- **Flujo principal:**
  1. El visitante abre el widget **💬 Asistente** disponible en todas las páginas.
  2. Escribe una pregunta; el frontend envía `message` e `history` a `POST /api/public/assistant/chat`.
  3. El backend clasifica la intención (`informational`, `product_search`, `map`, `out_of_scope`).
  4. Para consultas informativas, recupera los `TOP_K` fragmentos de ChromaDB y responde **solo** con ese contexto.
  5. Devuelve `answer`, `action` y `sources`.
  6. Si la intención es de búsqueda o de mapa, devuelve una acción (`{type, label, query, href}`) y el visitante decide si navegar.
- **Flujos alternativos:**
  - Sin información suficiente: respuesta explícita de falta de datos.
  - Consulta fuera de alcance: redirección a los temas que sí cubre.
- **Excepciones:**
  - Mensaje vacío o de más de 1000 caracteres → `422`.
  - Historial de más de 10 mensajes → `422`.
  - Más de 20 consultas por IP cada 300 s → `429`.
  - Proveedor no disponible o índice ausente → `503`.
- **Límites de alcance:** no busca productos, no informa precios ni stock y no identifica qué local vende un artículo; para eso deriva al buscador.

---

## 5. Metodología de desarrollo

El proyecto se desarrolló con **OpenSpec** y un flujo **incremental por caso de uso**. La regla central, acordada al inicio y registrada en `openspec/config.yaml` y `AGENTS.md`, fue:

> Cada caso de uso o funcionalidad independiente genera su propia propuesta OpenSpec. No se implementa nada hasta que la propuesta se aprueba explícitamente. No se planifican funcionalidades no solicitadas ni se crea una propuesta global del sistema.

### 5.1 Ciclo de trabajo

```mermaid
flowchart LR
    A[Explorar / analizar el CU] --> B[Revisar specs y código existente]
    B --> C[Identificar dependencias, impactos y ambigüedades]
    C --> D[Crear cambio OpenSpec: proposal + specs + design + tasks]
    D --> E{¿Aprobación del usuario?}
    E -- No --> D
    E -- Sí --> F[Delegar backend y frontend]
    F --> G[Integrar resultados]
    G --> H[Ejecutar pruebas y validar criterios]
    H --> I{¿Cumple?}
    I -- No --> F
    I -- Sí --> J[Validar con openspec --strict]
    J --> K[Archivar el cambio y sincronizar specs]
    K --> L[Git Agent: commit y push]
    L --> M[Verificar commit remoto]
```

### 5.2 Artefactos por cambio

Cada cambio archivado contiene:

| Artefacto | Contenido |
|---|---|
| `proposal.md` | Problema, alcance, fuera de alcance, impacto, dependencias y decisiones |
| `specs/<capability>/spec.md` | Requisitos con escenarios de aceptación |
| `design.md` | Contexto, decisiones, riesgos, plan de migración y rollback |
| `tasks.md` | Checklist verificable, agrupada por backend, pruebas, frontend e integración |

Los 16 cambios archivados, en orden cronológico:

| Fecha | Cambio | Specs afectadas |
|---|---|---|
| 2026-11-03 | `bootstrap-project-foundation` | `backend-foundation`, `frontend-foundation`, `local-environment` |
| 2026-11-03 | `domain-model` | `domain-model` |
| 2026-11-03 | `admin-authentication` | `admin-authentication` |
| 2026-11-03 | `merchant-administration` | `merchant-administration` |
| 2026-11-03 | `merchant-portal` | `merchant-portal` |
| 2026-11-03 | `merchant-product-catalog` | `merchant-product-catalog` |
| 2026-11-04 | `public-product-search` | `product-search` |
| 2026-11-04 | `public-product-detail` | `product-detail` |
| 2026-11-04 | `merchant-store-settings` | `merchant-store-settings` |
| 2026-11-04 | `public-store-detail` | `store-detail` |
| 2026-11-04 | `public-explore` | `explore` |
| 2026-11-06 | `merchant-product-stats` | `product-statistics` |
| 2026-11-06 | `public-store-map` | `store-map` |
| 2026-11-06 | `gallery-assistant` | `gallery-assistant` |
| 2026-11-06 | `site-navigation` | `site-navigation` |
| 2026-11-06 | `store-catalog-and-back` | `store-detail`, `product-detail` |

Estado de las especificaciones: **17 capacidades**, **139 requisitos**, todas válidas con `openspec validate --specs --strict`.

### 5.3 División del trabajo

- El desarrollador definió el alcance, aprobó cada propuesta y validó los resultados.
- La orquestación (análisis, propuesta, integración y verificación) se hizo en una sesión principal.
- La implementación se delegó a subagentes especializados, casi siempre **backend y frontend en paralelo** cuando el contrato de API ya estaba definido.
- Las operaciones de Git se delegaron siempre a un agente dedicado, incluso después de archivar cada cambio.

### 5.4 Versionado

- Rama principal: `main`.
- Commits en **Conventional Commits**: `feat:`, `fix:`, `docs:`, `chore:`.
- Se publica después de archivar y aprobar, con alcance explícito de archivos.
- Nunca se usó `--amend`, `reset --hard`, `clean` ni force push.
- La configuración del agente Git prescribe ramas `feature/*`, `fix/*`, etc., pero en la práctica el trabajo se publicó sobre `main` con autorización explícita.

Historial (15 commits):

| Commit | Tipo | Contenido |
|---|---|---|
| `5aedc46` | chore | Bootstrap del proyecto |
| `42365a5` | feat | Modelo de dominio |
| `b540a60` | feat | Autenticación, modelo y portal del comerciante |
| `d49a5f8` | feat | Specs OpenSpec y archivado |
| `9d0219f` | feat | Archivado y sincronización |
| `0b20436` | feat | Ajustes finales de casos de uso |
| `b68eb6f` | feat | Exploración pública |
| `5335597` | feat | Estadísticas del comerciante |
| `1ec2655` | feat | Mapa público |
| `c65e06f` | chore | MCP de GitHub y agente Git |
| `31fde73` | feat | Asistente RAG |
| `4282170` | docs | Workflow de publicación |
| `925b49d` | feat | Navegación unificada y portada |
| `7607b06` | feat | Catálogo del local y “Volver” |
| `1e90ce5` | chore | Catálogo demo ampliado y conocimiento del asistente |

---

## 6. AI Engineering

Esta sección documenta cómo se incorporó la IA al proceso, con evidencia del repositorio y de los registros locales de OpenCode. Los prompts citados se recuperaron de la base de sesiones de OpenCode; los que no se citan literalmente se describen por su objetivo.

### 6.1 Rol de la IA durante el desarrollo

| Actividad | Responsable | Nivel de autonomía |
|---|---|---|
| Definir alcance y casos de uso | Desarrollador | Total |
| Aprobar propuestas | Desarrollador | Total |
| Analizar el código y redactar propuestas OpenSpec | IA (sesión principal) | Media: sin permiso de implementar |
| Implementar backend | Subagente `backend` | Media: alcance acotado por instrucción |
| Implementar frontend | Subagente `frontend` | Media: alcance acotado por instrucción |
| Ejecutar pruebas y corregir | Subagentes, supervisados | Media |
| Commit, push y verificación remota | Subagente `git` + MCP | Baja: comandos destructivos prohibidos |
| Validación final y aceptación | Desarrollador | Total |

La IA se usó para: leer el repositorio y detectar lo ya implementado, redactar propuestas y diseños, generar implementaciones completas, escribir pruebas, diagnosticar fallos a partir de la salida de tests y de errores del navegador, y preparar commits.

La IA **no** decidió el alcance funcional, no aprobó sus propias propuestas y no publicó cambios sin autorización.

### 6.2 Prompts y estrategias

#### Prompt fundacional de metodología

Se usó al inicio de la sesión principal y estableció el contrato de trabajo:

> “Quiero trabajar en este proyecto utilizando OpenSpec de manera incremental. Cada caso de uso o funcionalidad independiente que te solicite debe generar una propuesta OpenSpec propia. […] No implementes cambios hasta que apruebe explícitamente la propuesta. No planifiques funcionalidades que todavía no solicité ni generes una propuesta global de todo el sistema.”

Estrategia: convertir el proceso en una regla explícita y repetible, en lugar de confiar en que el agente la infiriera.

#### Prompts de definición de casos de uso

Cada CU se pidió con el mismo patrón:

1. Revisar `AGENTS.md`, las skills y las specs existentes.
2. Inspeccionar el código real y no asumir que algo está implementado.
3. Revisar los CU previos relacionados.
4. Identificar componentes de backend y frontend.
5. Identificar dependencias, impactos y **ambigüedades**.
6. Preparar una propuesta independiente y esperar aprobación.

Ejemplo real (CU #8):

> “Analiza exclusivamente el CU #8 y prepara una propuesta OpenSpec para su implementación. […] Un comerciante solamente puede administrar productos pertenecientes a su local asignado. No se debe confiar en el identificador del local enviado por el frontend para determinar los permisos.”

Estrategia: exigir verificación empírica del estado del código y declarar explícitamente las reglas de seguridad antes de diseñar.

#### Prompt de exploración y decisión

Antes de implementar se pedía analizar alternativas y consultar en lugar de asumir:

> “No asumas decisiones que no estén especificadas. En particular, analiza y consulta antes de decidir: cómo se autentica el administrador, dado que los casos de uso no especifican su inicio de sesión…”

Estrategia: separar el diseño de la implementación y forzar una decisión humana en los puntos ambiguos.

#### Prompt de generación de propuesta

> “Genera la propuesta”

Una vez aprobado el análisis, esta instrucción breve autorizaba la creación de `proposal.md`, `specs/`, `design.md` y `tasks.md`, sin código.

#### Prompt de implementación con delegación

> “Aprobado, comienza la implementación usando los subagentes correspondientes”

> “Implementalo, tienes permiso de realizar los comandos necesarios”

Estrategia: la aprobación habilita la ejecución y, cuando corresponde, el uso de comandos de verificación (por ejemplo, levantar contenedores o ejecutar pruebas).

#### Prompt de corrección sobre comportamiento observado

> “Si es que ya tenía una búsqueda, por ejemplo zapatillas y a través del bot realizo la búsqueda de ‘audio’, la búsqueda se queda en zapatillas.”

> “Ahora tras realizar una busqueda la página se queda en blanco.”

> “Ya vi lo que dices de los filtros duplicados, quedemonos solo con los filtros del header y quitemos la barra de busqueda y filtros del cuerpo, mostrando así solo los resultados.”

Estrategia: reportar el síntoma observable del usuario, no la causa supuesta, y dejar que el agente diagnostique.

#### Prompt de cierre

> “Archivalo”

> “Cada vez que archives un nuevo cambio llama al agente de git y haz un commit y push usando el mcp”

Estrategia: convertir la publicación en parte del protocolo, no en una decisión caso por caso.

#### Prompt de datos de demostración

> “Agrega muchos mas productos y en cuanto al archivo para el asistente inventa los datos que veas necesarios”

Seguido de preguntas estructuradas sobre cantidad por local, tratamiento de los productos existentes y datos ficticios del asistente antes de ejecutar.

### 6.3 Metodología de iteración

1. **Una funcionalidad por iteración:** cada CU produjo un cambio OpenSpec independiente, con su propia propuesta, specs, diseño y tareas.
2. **Contrato antes que código:** el backend definía endpoints y schemas; después el frontend consumía ese contrato, con frecuencia en paralelo.
3. **Instrucciones de propiedad:** cada subagente recibía la lista exacta de archivos que podía tocar y las prohibiciones explícitas (por ejemplo, “no toques `openspec/`, `frontend/`, compose ni Git”).
4. **Revisión de resultados:** el agente coordinador leía los informes, verificaba los archivos modificados y ejecutaba las suites por su cuenta antes de aceptar.
5. **Verificación funcional:** además de los tests, se comprobó el comportamiento real en el navegador en los flujos críticos.
6. **Cierre formal:** marcar tareas, validar con `--strict`, archivar, publicar y verificar el commit remoto.

### 6.4 Loops de autocorrección

Existieron **loops de corrección guiados por evidencia**, aunque no un pipeline de CI que iterara solo. El patrón fue:

```mermaid
flowchart LR
    A[Agente implementa] --> B[Ejecuta tests / build]
    B --> C{¿Falla?}
    C -- Sí --> D[Lee la salida del error]
    D --> E[Corrige]
    E --> B
    C -- No --> F[Verificación manual en navegador]
    F --> G{¿Comportamiento correcto?}
    G -- No --> D
    G -- Sí --> H[Aceptación]
```

Casos reales:

| Problema detectado | Cómo se detectó | Corrección |
|---|---|---|
| Vite servía un módulo transformado obsoleto: el catálogo no aparecía aunque el archivo fuente era correcto | Verificación con navegador automatizado y comparación del módulo servido por Vite contra el archivo del contenedor | Limpiar `node_modules/.vite` y reiniciar el contenedor del frontend |
| El asistente no actualizaba la búsqueda previa | Reporte del usuario con un caso concreto (“zapatillas” → “audio”) | Ajuste del flujo de búsqueda disparado desde el asistente |
| Filtros duplicados entre header y cuerpo | Revisión visual del usuario | Eliminar la barra y los filtros del cuerpo, dejando solo los del header |
| Pantalla en blanco tras buscar | Reporte del usuario | Corrección de la página de búsqueda y cobertura de regresión |
| El botón “Volver a la búsqueda” no respetaba el origen | Análisis de flujo del usuario | `useGoBack` con `location.key` y fallback a `/` |
| Catálogo del local no visible en el primer intento | Prueba de navegador con esperas y registro de red | Se identificó la causa en la caché de Vite, no en el código |

No hubo un agente autónomo ejecutando tests en bucle sin intervención: cada corrección se disparó por una ejecución de pruebas, un build, una verificación de navegador o un reporte del usuario, y el resultado se volvió a validar.

### 6.5 Estructuración de instrucciones

Las instrucciones se organizaron en cinco niveles, cada uno con un propósito distinto:

| Nivel | Archivo | Propósito |
|---|---|---|
| 1. Proyecto | `AGENTS.md` | Fuente de verdad: propósito, stack, arquitectura, seguridad, testing, workflow OpenSpec, agentes y reglas de Git |
| 2. OpenSpec | `openspec/config.yaml` | Contexto y reglas que toda propuesta debe respetar |
| 3. Agentes | `.opencode/agents/{backend,frontend,git}.md` | Responsabilidades, alcance, convenciones y prohibiciones por rol |
| 4. Skills | `.opencode/skills/*/SKILL.md` | Guías técnicas reutilizables (FastAPI, PostgreSQL, React/TS, OpenSpec) |
| 5. Tarea | Prompt de cada cambio | Alcance exacto, archivos permitidos, contrato y criterios de verificación |

Skills disponibles:

| Skill | Uso |
|---|---|
| `fastapi-development` | Endpoints, lógica, schemas, dependencias, pruebas |
| `postgresql-design` | Modelado, relaciones, constraints, índices, migraciones |
| `react-typescript` | Páginas, componentes, routing, formularios, estado, pruebas |
| `openspec-explore` | Exploración previa a un cambio |
| `openspec-propose` | Generación de propuesta completa |
| `openspec-apply-change` | Implementación de tareas |
| `openspec-update-change` | Revisión de artefactos de un cambio |
| `openspec-sync-specs` | Sincronización de specs delta |
| `openspec-archive-change` | Archivado |

Comandos personalizados (`/opsx-*`): `explore`, `propose`, `apply`, `update`, `sync`, `archive`. Los comandos y las skills de OpenSpec declaran `allowed-tools: Bash(openspec:*)`, lo que restringe su superficie de ejecución.

Restricciones recurrentes impuestas a los agentes:

- No implementar fuera del alcance aprobado.
- No modificar archivos de otra capa.
- No tocar `openspec/` durante la implementación.
- No ejecutar operaciones Git destructivas.
- No afirmar que una prueba pasó sin ejecutarla.
- Verificar la propiedad del recurso en el backend, nunca en el frontend.

### 6.6 Evaluación de las respuestas generadas

Criterios aplicados antes de aceptar una implementación:

| Criterio | Verificación |
|---|---|
| Cumplimiento del requerimiento | Contraste con `specs/` y con los escenarios de aceptación |
| Coherencia arquitectónica | Revisión de módulos, capas y separación backend/frontend |
| Seguridad y autorización | Pruebas de `401`/`403`, propiedad por local, ausencia de `store_id` en payloads |
| Calidad del código | Legibilidad, nombres, ausencia de duplicación, sin dependencias innecesarias |
| Contratos | Schemas Pydantic explícitos; el frontend no asume estructuras |
| Pruebas | Suites ejecutadas y reportadas; pruebas de éxito, validación y autorización |
| Regresiones | Suite completa, no solo las pruebas nuevas |
| Build | `npm run build` con comprobación de tipos |
| Especificaciones | `openspec validate --strict` y `alembic check` sin cambios inesperados |
| Comportamiento real | Navegación manual y automatizada de los flujos principales |

Un resultado se consideraba aceptable solo cuando el informe del agente coincidía con lo verificado de forma independiente por el coordinador.

---

## 7. Agentes utilizados

Los agentes son subagentes de OpenCode definidos en `.opencode/agents/`. Todos declaran `mode: subagent` y `permission.bash: ask`, es decir, cada comando de shell requiere aprobación.

### 7.1 `backend`

| Atributo | Detalle |
|---|---|
| **Responsabilidad** | Diseñar, implementar, probar y mantener el backend con Python, FastAPI y PostgreSQL |
| **Tareas** | Endpoints REST, lógica de negocio, acceso a datos, schemas, autenticación, autorización, validación, pruebas |
| **Alcance** | Solo `backend/` |
| **Herramientas** | Shell (con aprobación), lectura/escritura de archivos y skills `fastapi-development`, `postgresql-design` |
| **Restricciones** | No modifica frontend ni `openspec/`; no hace commits ni ramas; no introduce ORM, migraciones o persistencia alternativas; no cambia migraciones ya aplicadas; no expone modelos de persistencia como contrato público |
| **Colaboración** | Coordina contratos con `frontend`; reporta al coordinador |

### 7.2 `frontend`

| Atributo | Detalle |
|---|---|
| **Responsabilidad** | Diseñar, implementar, probar y mantener el frontend con React y TypeScript |
| **Tareas** | Páginas, componentes, navegación, estado de UI, formularios, integración con la API, estados de carga/error/vacío, pruebas |
| **Alcance** | Solo `frontend/` |
| **Herramientas** | Shell (con aprobación), archivos y skill `react-typescript` |
| **Restricciones** | No modifica backend ni `openspec/`; no hace Git; no introduce Axios, shadcn/ui, librerías de estado adicionales ni frameworks de estilos alternativos; no implementa lógica de negocio duplicada |
| **Colaboración** | Consume el contrato del backend; reporta endpoints faltantes o incompatibles |

### 7.3 `git`

| Atributo | Detalle |
|---|---|
| **Responsabilidad** | Gestionar el repositorio, revisar cambios y crear commits |
| **Tareas** | Estado del repo, revisión de diffs, ramas, commits, merges, conflictos, `.gitignore` |
| **Alcance** | Solo operaciones de control de versiones |
| **Herramientas** | Shell (con aprobación) |
| **Restricciones** | No modifica código de aplicación; no hace `reset --hard`, `clean`, force push ni reescritura de historia; no commitea cambios ajenos; verifica que no haya secretos |
| **Colaboración** | Recibe el alcance exacto del coordinador; reporta hash, archivos y resultado del push |

### 7.4 Coordinación

```mermaid
flowchart TB
    DEV[Desarrollador] -->|alcance y aprobaciones| ORQ[Sesión principal / coordinación]
    ORQ -->|propuesta y diseño| OPS[OpenSpec]
    ORQ -->|implementación backend| BE[backend]
    ORQ -->|implementación frontend| FE[frontend]
    BE -->|contrato de API| ORQ
    ORQ -->|contrato aprobado| FE
    ORQ -->|publicación| GIT[git]
    GIT -->|commit y push| GH[(GitHub)]
    ORQ -->|verificación| MCP[MCP GitHub]
```

Reglas de colaboración:

- Backend y frontend trabajan en paralelo solo cuando el contrato ya está definido.
- Cada subagente recibe archivos permitidos y prohibidos de forma explícita.
- El coordinador revisa los informes y vuelve a ejecutar las verificaciones.
- Ningún subagente publica por su cuenta: Git se invoca con alcance cerrado.

---

## 8. MCP utilizados

**MCP (Model Context Protocol)** es un protocolo que permite a un agente acceder a herramientas y datos externos mediante servidores estandarizados.

### 8.1 MCP configurados en el proyecto

| MCP | Ámbito | Estado | Propósito | Configuración | Uso real |
|---|---|---|---|---|---|
| `github` | Proyecto (`opencode.json`) | Usado durante el desarrollo | Consultar repositorio, commits y archivos; verificar la publicación | Servidor remoto `https://api.githubcopilot.com/mcp/`, `oauth: false`, token leído desde un archivo fuera del repositorio | Verificación de commits en `MelEdur/Galer-a-comercial--webapp` |
| `filesystem` | Proyecto (`opencode.json`) | Incorporado al final | Acceso acotado al sistema de archivos | Servidor local `npx -y @modelcontextprotocol/server-filesystem` con raíz `/home/edume/proyect/test` | Lectura y escritura dentro del repositorio |
| `codegraph` | Global (`~/.config/opencode/opencode.json`) | Usado durante el desarrollo | Grafo de símbolos del código para responder preguntas estructurales | Índice local en `.codegraph/` | Exploración de arquitectura, símbolos y relaciones |
| `engram` | Global | Usado durante el desarrollo | Memoria persistente entre sesiones | Configuración global de OpenCode | Registro y recuperación de decisiones y contexto |

### 8.2 Configuración del MCP de GitHub

El `opencode.json` del proyecto declara el servidor de GitHub así:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "github": {
        "type": "remote",
        "url": "https://api.githubcopilot.com/mcp/",
        "oauth": false,
        "headers": {
          "Authorization": "Bearer {file:~/.config/opencode/github-mcp-token}"
        }
      }
    }
  }
}
```

Puntos importantes:

- El token **no** está escrito en el archivo: se lee desde `~/.config/opencode/github-mcp-token`, con permisos restringidos y fuera del repositorio.
- Se usó token en lugar de OAuth porque el endpoint remoto no soporta registro dinámico de clientes.
- `opencode.json` se versiona; el archivo del token, no.

### 8.3 Configuración del MCP de filesystem

```json
"filesystem": {
  "type": "local",
  "command": [
    "npx",
    "-y",
    "@modelcontextprotocol/server-filesystem",
    "/home/edume/proyect/test"
  ]
}
```

- Es un servidor **local** lanzado por OpenCode.
- La raíz permitida es el directorio del proyecto, de modo que el servidor no puede salir de `/home/edume/proyect/test`.
- No requiere credenciales.

### 8.4 Permisos y restricciones

| Aspecto | Aplicación |
|---|---|
| Acceso a archivos | El MCP `filesystem` está limitado a `/home/edume/proyect/test`.  |
| Operaciones Git | El MCP de GitHub se usó para **verificar**; la escritura de historia se hizo con `git` local a través del agente Git. Nunca se usaron `push_files` ni `create_or_update_file` para reemplazar la historia. |
| Credenciales | Ningún token, clave ni contraseña se expone en el repositorio ni en este documento. |
| Alcance | El MCP de GitHub se limitó a consulta y verificación del repositorio del proyecto. |

---

## 9. Decisiones técnicas y metodológicas

| # | Decisión | Contexto | Alternativas | Justificación | Consecuencias |
|---|---|---|---|---|---|
| 1 | **Monolito modular** | Proyecto académico de alcance acotado | Microservicios, capas adicionales | Simplicidad, despliegue único, menor coste cognitivo | Un solo despliegue; módulos separados por funcionalidad |
| 2 | **SQLAlchemy 2.0 síncrono** | FastAPI permite async, pero PostgreSQL y el volumen de datos no lo exigen | Async SQLAlchemy | Menos complejidad, sin riesgo de bloquear el event loop por código síncrono mal ubicado | Endpoints `def` (ejecutados en threadpool) |
| 3 | **Sin capa de repositorio** | Servicios con consultas directas | Repositorios por entidad | Evitar una abstracción que no aportaba valor con este tamaño | Los servicios concentran lógica y consultas |
| 4 | **JWT en `sessionStorage`** | Se necesitaba sesión sin backend de sesiones | Cookies, `localStorage`, estado en memoria | Simple, sin CSRF de cookies, y la sesión no persiste al cerrar la pestaña | Hay que reautenticarse al abrir una pestaña nueva |
| 5 | **Borrado lógico de productos** | Las estadísticas deben sobrevivir a la baja | Borrado físico, archivado aparte | Conserva historia y permite restaurar | Filtros de disponibilidad en todas las consultas públicas |
| 6 | **Restauración de productos** | Pedido explícito del usuario tras la baja | Solo alta nueva | Evita recargar datos y conserva imágenes y categorías | Endpoint adicional y estado `deleted` en el catálogo propio |
| 7 | **Unicidad de comerciante activo por local** | La unicidad total impedía reasignar un local tras una baja | Eliminar la restricción | Mantiene la invariante sin bloquear la reasignación | Índice único parcial (`WHERE role='merchant' AND is_active`) |
| 8 | **Local derivado del token** | Riesgo de escalada si el cliente envía `store_id` | Validar `store_id` del payload | El backend no confía en identificadores del cliente | Ningún payload de comerciante acepta `store_id` |
| 9 | **Endpoint dedicado de productos por local** | La ficha necesitaba el catálogo del local | Reutilizar el buscador con filtro de local | Una sola consulta paginada, contrato claro, sin registrar eventos de búsqueda | `GET /api/public/stores/{id}/products` |
| 10 | **“Volver” basado en historial** | El botón fijo a `/buscar` rompía el origen real (mapa, producto, exploración) | Botón fijo, parámetro de retorno | `location.key` distingue la entrada directa; fallback a `/` | `useGoBack` compartido por local y producto |
| 11 | **Navegación unificada** | Header y buscador duplicados en varias páginas | Mantener barras por página | Un solo header persistente y una sola fuente de filtros | `/explorar` redirige a `/`; el cuerpo solo muestra resultados |
| 12 | **Asistente con alcance informativo** | Evitar respuestas inventadas sobre productos y precios | Búsqueda conversacional de productos | RAG sobre conocimiento curado y derivación al buscador | Clasificación de intención y acciones sugeridas |
| 13 | **Embeddings locales** | Coste y dependencia de un proveedor de embeddings | API de embeddings externa | Sin coste por token y sin enviar la base de conocimiento a terceros | Descarga inicial del modelo y volumen de caché |
| 14 | **ChromaDB embebido** | Simplicidad de despliegue | Servidor vectorial dedicado | Un servicio menos; volumen persistente | Pensado para un único backend |
| 15 | **Rate limit en memoria** | Suficiente para demo | Redis o almacén distribuido | Sin infraestructura adicional | No es distribuido y se reinicia con el proceso |
| 16 | **Selección automática de modelo de chat** | Los modelos disponibles en Groq cambian | Modelo fijo en código | Lista de preferencias configurable y elección de un modelo apto para chat | Si ningún modelo está disponible, el asistente falla de forma controlada |
| 17 | **Semilla determinista e idempotente** | Se necesitaban datos creíbles y reproducibles | Datos aleatorios por ejecución | Variantes derivadas de categorías; segunda ejecución sin duplicados | 420 productos, 840 imágenes, 147 ofertas |
| 18 | **Sin linters ni formateadores** | Stack excluido explícitamente | ESLint/Prettier/Ruff | Se priorizó el tipado y las pruebas | La consistencia se sostiene por convención y revisión |
| 19 | **Datos ficticios del asistente** | Se necesitaba información institucional verosímil | Dejar “no disponible” | Permite demostrar el RAG con respuestas útiles | Debe reemplazarse antes de un uso real |

---

## 10. Procesos de corrección y validación

### 10.1 Pruebas automatizadas

| Suite | Herramienta | Alcance |
|---|---|---|
| Backend | Pytest (`backend/tests/`, 15 archivos) | Configuración, seguridad, salud, dominio, auth, administración, catálogo, local, búsqueda pública, detalle, estadísticas, asistente, semillas |
| Frontend | Vitest + React Testing Library (`frontend/src/test/`, 15 archivos) | Navegación, auth, búsqueda, detalle, local, mapa, exploración, paneles, estadísticas, asistente, salud |

Comandos:

```bash
# Backend, con Docker
docker compose exec backend pytest -q

# Backend, local
cd backend && source .venv/bin/activate && pytest -q

# Frontend
cd frontend && npm test -- --run

# Comprobación de tipos y build
cd frontend && npm run build
```

Resultados registrados en la última ejecución de la sesión, sobre el commit `1e90ce5`:

| Suite | Resultado |
|---|---|
| Backend | **367 pruebas aprobadas** |
| Frontend | **143 pruebas aprobadas** (15 archivos) |
| Build del frontend | Correcto (TypeScript + Vite) |

### 10.2 Pruebas de validación y autorización

Cubiertas explícitamente en la suite:

- `401` sin token y con token inválido o vencido.
- `403` con rol incorrecto y para comerciante sin local.
- Aislamiento entre locales: un comerciante no puede leer, editar, eliminar ni restaurar productos de otro.
- `404` para productos y locales no disponibles.
- `422` para filtros, paginación y payloads inválidos.
- Ausencia de `store_id` en los contratos públicos.

### 10.3 Validaciones de especificación

```bash
openspec validate --specs --strict
openspec validate <cambio> --strict
openspec list
```

Cada cambio se archivó solo después de validar en modo estricto y de que todas las tareas estuvieran marcadas.

### 10.4 Validación de base de datos

```bash
docker compose exec backend alembic current
docker compose exec backend alembic check
```

`alembic check` se usó para confirmar que el modelo y las migraciones coincidían, sin generar migraciones inesperadas.

### 10.5 Pruebas manuales y verificación en navegador

Además de las suites, se verificaron flujos completos en un navegador real:

| Flujo | Resultado esperado |
|---|---|
| Home → mapa → local | Ficha correcta con el local seleccionado |
| Local → catálogo → producto | Detalle correcto |
| Producto → “Volver” | Regresa al local |
| Entrada directa a `/locales/1` → “Volver” | Navega a `/` |
| Buscar → filtros → paginación | Resultados coherentes sin perder filtros |
| Asistente → consulta de dirección y horario | Respuesta con datos del contexto |
| Login comerciante → catálogo | Acceso al panel propio |
| Login administrador → comerciantes | Alta y baja disponibles |

También se comprobó la consola del navegador en los flujos críticos para descartar errores de JavaScript.
---
---

## 11. Apéndices

### 11.1 Resumen de endpoints

#### Públicos

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/health` | Salud del backend y de PostgreSQL |
| `GET` | `/api/public/products` | Búsqueda paginada de productos disponibles |
| `GET` | `/api/public/categories` | Categorías globales |
| `GET` | `/api/public/explore` | Destacados, ofertas, categorías y locales |
| `GET` | `/api/public/stores` | Locales activos |
| `GET` | `/api/public/map` | Locales con lado y posición |
| `GET` | `/api/public/products/{id}` | Detalle de producto disponible |
| `GET` | `/api/public/products/{id}/similar` | Hasta seis productos similares |
| `GET` | `/api/public/stores/{id}` | Ficha pública del local |
| `GET` | `/api/public/stores/{id}/products` | Catálogo paginado del local |
| `POST` | `/api/public/assistant/chat` | Consulta al asistente |

#### Autenticación

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/auth/login` | Devuelve el token JWT |
| `GET` | `/api/auth/me` | Identidad autenticada |

#### Administrador (rol `admin`)

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/admin/merchants` | Lista de comerciantes |
| `POST` | `/api/admin/merchants` | Alta de comerciante |
| `DELETE` | `/api/admin/merchants/{id}` | Baja lógica |
| `GET` | `/api/admin/stores` | Locales con su comerciante activo |

#### Comerciante (rol `merchant`)

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/merchant/store` | Local propio |
| `PUT` | `/api/merchant/store` | Actualización completa del local |
| `GET` | `/api/merchant/products` | Catálogo propio paginado |
| `GET` | `/api/merchant/products/{id}` | Producto propio |
| `POST` | `/api/merchant/products` | Alta de producto |
| `PATCH` | `/api/merchant/products/{id}` | Edición parcial |
| `DELETE` | `/api/merchant/products/{id}` | Baja lógica |
| `POST` | `/api/merchant/products/{id}/restore` | Restauración |
| `GET` | `/api/merchant/categories` | Categorías para clasificar |
| `GET` | `/api/merchant/stats/products` | Top 10 de productos buscados |

### 11.2 Credenciales de demostración

| Rol | Usuario | Contraseña |
|---|---|---|
| Administrador | `admin@galeria.local` | `admin1234` |
| Comerciantes | `comercio01@galeria.local` … `comercio21@galeria.local` | `comercio1234` |

La cuenta de administrador se crea con `create_admin` a partir de `ADMIN_EMAIL` y `ADMIN_PASSWORD`; los valores de la tabla corresponden al entorno de demostración de este repositorio. Los comerciantes los genera `seed_demo` con la contraseña fija `comercio1234`.

Estas credenciales corresponden a los datos de demostración. No deben usarse en un entorno real.

Datos de demostración actuales:

| Dato | Cantidad |
|---|---|
| Locales | 21 |
| Comerciantes | 21 |
| Productos | 420 (20 por local) |
| Categorías | 10 |
| Imágenes de producto | 840 |
| Productos con oferta | 147 |
| Eventos de búsqueda | 65 |
| Fragmentos del índice del asistente | 44 |
---

**Repositorio:** <https://github.com/MelEdur/Galer-a-comercial--webapp>
