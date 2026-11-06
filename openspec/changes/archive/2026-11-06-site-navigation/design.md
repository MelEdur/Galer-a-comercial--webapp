# Diseño

## Context

Ver `proposal.md` y `specs/site-navigation/spec.md`. Hoy `App` monta las rutas directamente y cada página define su propio encabezado. La portada es distinta de `/explorar`, la búsqueda solo está en `/buscar` y el cierre de sesión está repetido en tres páginas.

## Goals / Non-Goals

**Goals:**

- Un header único y persistente.
- Búsqueda y filtros accesibles desde cualquier página.
- Acciones de cuenta coherentes con el rol.
- Home única de descubrimiento.

**Non-Goals:**

- Cambios de backend, API o base de datos.
- Nuevos filtros o nueva lógica de búsqueda.
- Rediseñar detalle, mapa o paneles.

## Decisions

### 1. Layout con rutas anidadas

- `AppLayout` renderiza `SiteHeader` y `<Outlet />`.
- `AppRoutes` envuelve todas las rutas en `<Route element={<AppLayout />}>`.
- La ruta 404 también queda dentro del layout.
- `AssistantWidget` sigue en `App`, fuera del layout de rutas, para conservar su estado al navegar.

### 2. Header

`SiteHeader` contiene:

- enlace “Galería Comercial” a `/`;
- `HeaderSearch`;
- `AccountActions`.

Diseño sticky, fondo blanco, borde inferior y `z-index` menor que el widget del asistente.

En móvil:
- logo y acciones visibles;
- búsqueda en una fila propia;
- panel de filtros desplegable y scroll interno si hace falta.

### 3. Búsqueda y filtros del header

`HeaderSearch`:

- input controlado;
- submit → `/buscar?search=...`;
- botón “Filtros” con indicador cuando hay filtros activos;
- panel con categoría, precio mínimo, precio máximo, solo ofertas y orden;
- “Aplicar” navega a `/buscar` con los parámetros;
- cierra con Escape, clic fuera o al aplicar;
- en `/buscar`, inicializa y sincroniza desde la URL;
- usa `listPublicCategories` con TanStack Query.

La URL es la única fuente de verdad para los filtros. El header es el único punto de búsqueda y filtros; `SearchPage` solo lee los parámetros y renderiza los resultados, sin barra ni filtros propios.

### 4. Acciones de cuenta

`AccountActions` usa `useAuth`:

- sin sesión: enlace “Iniciar sesión” a `/login`, oculto en `/login`;
- `merchant`: enlace “Mi local” a `/comerciante`;
- `admin`: enlace “Panel de administración” a `/admin`;
- con sesión: botón “Cerrar sesión” que ejecuta `logout()` y navega a `/`.

### 5. Home y exploración

- Se extrae `ExploreContent` de `ExplorePage` con las secciones de destacados, ofertas, categorías y locales.
- `HomePage` muestra:
  - hero breve;
  - CTA “Ver mapa de la galería”;
  - `ExploreContent`.
- `HealthStatus` deja de mostrarse en la home.
- `/explorar` pasa a `<Navigate to="/" replace />`.
- `ExplorePage` puede eliminarse o quedar como wrapper sin ruta; se prefiere eliminar el código muerto y adaptar sus pruebas a `ExploreContent`/`HomePage`.
- Los enlaces internos a `/explorar` se cambian a `/`.

### 6. Páginas privadas

- Se quitan los botones “Cerrar sesión” de `AdminPage`, `MerchantPage` y `MerchantsPage`.
- Se conservan títulos y datos de usuario.
- El header centraliza la acción.

### 7. Pruebas

- `SiteHeader` con y sin sesión, por rol y en `/login`.
- Búsqueda con submit y filtros aplicados.
- Sincronización con la URL del buscador.
- Logout limpia sesión y navega a `/`.
- Home muestra mapa y secciones; no muestra `HealthStatus`.
- `/explorar` redirige a `/`.
- Header presente en rutas privadas y 404.
- Widget del asistente visible/oculto según ruta.
- Ajustar pruebas de `AdminPage`, `MerchantPage`, `MerchantsPage`, `StoreListPage` y exploración.

## Risks / Trade-offs

- **Un solo control de filtros** → el header; la página de búsqueda queda como resultados puros y no puede desincronizarse.
- **Header en rutas privadas** → carga la consulta de categorías; TanStack Query la cachea.
- **Cambio de rutas** → tests y enlaces internos deben actualizarse.
- **Responsive** → el panel de filtros puede ocupar mucho espacio; se usa desplegable con scroll.
- **Sin cambios de backend** → riesgo bajo.

## Migration Plan

No hay datos ni esquema. Se despliega el frontend; `/explorar` redirige y los enlaces internos se actualizan.

Rollback: restaurar el router anterior y las páginas con sus headers.

## Open Questions

Ninguna que afecte al alcance. El contenido de la home y los filtros reutilizan las funcionalidades existentes.
