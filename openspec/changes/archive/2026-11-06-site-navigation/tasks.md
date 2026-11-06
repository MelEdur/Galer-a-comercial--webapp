# Tasks

## 1. Layout y header

- [x] 1.1 Crear `app/layout/AppLayout.tsx` con `SiteHeader` y `<Outlet />`.
- [x] 1.2 Crear `SiteHeader` con logo/texto a `/`, búsqueda, filtros y acciones de cuenta.
- [x] 1.3 Anidar todas las rutas dentro del layout, incluida la 404, en `app/router.tsx`.
- [x] 1.4 Ajustar `App.tsx` para mantener el widget del asistente fuera del layout de rutas.

## 2. Búsqueda y filtros globales

- [x] 2.1 Crear `HeaderSearch` con input, submit a `/buscar` y botón de filtros.
- [x] 2.2 Implementar el panel con categoría, precio mínimo/máximo, solo ofertas y orden.
- [x] 2.3 Sincronizar el header con la URL cuando el visitante está en `/buscar`.
- [x] 2.4 Implementar cierre con Escape, clic fuera y al aplicar; accesibilidad del panel.
- [x] 2.5 Quitar la barra de búsqueda y los filtros del cuerpo de `/buscar`; dejar solo resultados y paginación.

## 3. Cuenta y roles

- [x] 3.1 Crear `AccountActions` con los estados visitante, comerciante y administrador.
- [x] 3.2 Ocultar la acción de cuenta en `/login`.
- [x] 3.3 Implementar logout centralizado con vuelta a `/`.
- [x] 3.4 Quitar los botones de logout de `AdminPage`, `MerchantPage` y `MerchantsPage`.

## 4. Home y exploración

- [x] 4.1 Extraer `ExploreContent` de `ExplorePage`.
- [x] 4.2 Reescribir `HomePage` con hero, CTA al mapa y `ExploreContent`.
- [x] 4.3 Quitar `HealthStatus` de la home.
- [x] 4.4 Redirigir `/explorar` a `/` y actualizar enlaces internos.
- [x] 4.5 Eliminar el código muerto de `ExplorePage` si ya no tiene ruta.

## 5. Pruebas

- [x] 5.1 Probar header en rutas públicas, privadas y 404.
- [x] 5.2 Probar logo, búsqueda y filtros del header.
- [x] 5.3 Probar acciones de cuenta por rol, login y logout.
- [x] 5.4 Probar home con mapa y exploración, sin `HealthStatus`.
- [x] 5.5 Probar la redirección de `/explorar`.
- [x] 5.6 Ajustar las pruebas existentes afectadas por los logouts, la ruta de exploración y la eliminación de filtros del cuerpo.
- [x] 5.7 Probar que el widget del asistente sigue visible/oculto correctamente.
- [x] 5.8 Ejecutar `npm test -- --run` y `npm run build`.

## 6. Verificación de integración

- [x] 6.1 Verificar manualmente el header en home, búsqueda, mapa, locales, admin y comerciante.
- [x] 6.2 Verificar búsqueda y filtros desde una página distinta de `/buscar`.
- [x] 6.3 Verificar acciones de comerciante y administrador con las cuentas demo.
- [x] 6.4 Validar el cambio con `openspec validate site-navigation --strict`.

## Workflow follow-up

- Revisar y archivar después de la verificación.
- No modificar backend, API ni base de datos.
