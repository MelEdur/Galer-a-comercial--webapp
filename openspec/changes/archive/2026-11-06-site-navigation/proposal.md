# Propuesta

## Why

La navegación actual está repartida por página: cada una define su propio encabezado, la búsqueda solo existe dentro de `/buscar`, la portada es una pantalla distinta de la exploración y el cierre de sesión aparece duplicado en páginas privadas. El visitante no tiene una identidad de sitio persistente ni un acceso rápido a la búsqueda, los filtros, el mapa o su cuenta.

Este cambio centraliza la navegación en un header compartido y convierte `/` en la página principal de descubrimiento.

## What Changes

- Se crea un layout compartido con un header persistente en todas las rutas.
- El header incluye logo/texto “Galería Comercial”, búsqueda global, panel de filtros y acciones de cuenta.
- La búsqueda del header navega a `/buscar`; el panel permite categoría, precio mínimo/máximo, solo ofertas y orden.
- Las acciones de cuenta cambian según el rol: iniciar sesión, mi local, panel de administración y cerrar sesión.
- La página principal `/` muestra el botón al mapa y las secciones de exploración.
- `/explorar` redirige a `/`.
- Se elimina el estado técnico del backend de la home.
- Se quitan los botones de cierre de sesión duplicados de las páginas privadas.
- El widget del asistente se mantiene.

### Alcance

- Header compartido y responsive.
- Búsqueda y filtros globales.
- Acciones por rol y cierre de sesión centralizado.
- Home con mapa + exploración.
- Redirección de `/explorar`.
- Ajustes de pruebas existentes.

### Fuera de alcance

- Cambios de backend, endpoints o modelos.
- Nuevos filtros de búsqueda.
- Rediseño de las páginas de detalle, mapa, admin o comerciante.
- Persistencia de la sesión o cambios de autenticación.
- Cambios en el asistente.

## Capabilities

### New Capabilities

- `site-navigation`: header persistente, búsqueda y filtros globales, acciones por rol, home de descubrimiento y redirección de exploración.

### Modified Capabilities

Ninguna. El comportamiento de exploración, búsqueda y autenticación se reutiliza; solo cambia la forma de acceso y la composición de la portada.

## Impact

- **Frontend nuevo:** `app/layout/AppLayout`, `SiteHeader`, `HeaderSearch`, `AccountActions` y `ExploreContent`.
- **Frontend modificado:** `App.tsx`, `app/router.tsx`, `pages/HomePage.tsx`, `features/explore/ExplorePage.tsx`, `pages/AdminPage.tsx`, `pages/MerchantPage.tsx`, `features/admin-merchants/MerchantsPage.tsx`, `features/explore/StoreListPage.tsx` y pruebas.
- **Backend:** sin cambios.
- **Migraciones:** ninguna.
- **Dependencias nuevas:** ninguna.
- **API:** sin cambios.
- **Riesgos:** cambios en tests de rutas y logouts; el buscador del cuerpo se elimina para no duplicar controles.

## Decisiones adoptadas

- Home = exploración; `/explorar` redirige a `/`.
- Header completo en todas las rutas.
- Acción de cuenta oculta en `/login`.
- Logout vuelve a `/`.
- El header es el único punto de búsqueda y filtros; `/buscar` solo muestra los resultados.
- El botón del mapa aparece al inicio del cuerpo de la home.
- Se elimina `HealthStatus` de la home.
