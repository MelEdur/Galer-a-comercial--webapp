# site-navigation Specification

## Purpose
Define la navegación del sitio: header persistente, búsqueda y filtros globales, acciones de cuenta por rol, página principal de descubrimiento con acceso al mapa y composición de la exploración.

## Requirements

### Requirement: Header persistente

La aplicación SHALL mostrar un header compartido en todas las rutas, incluidas las públicas, las privadas y la página no encontrada.

#### Scenario: Rutas públicas

- **WHEN** el visitante navega a la home, búsqueda, mapa, locales o detalle
- **THEN** el header permanece visible con la misma estructura

#### Scenario: Rutas privadas

- **WHEN** el usuario accede a `/admin` o `/comerciante`
- **THEN** el header permanece visible

#### Scenario: Página no encontrada

- **WHEN** el visitante accede a una ruta inexistente
- **THEN** el header también se muestra sobre la página 404

### Requirement: Identidad del sitio

El header SHALL mostrar el texto “Galería Comercial” como enlace a la página principal.

#### Scenario: Volver al inicio

- **WHEN** el visitante selecciona “Galería Comercial”
- **THEN** navega a `/`

### Requirement: Búsqueda global

El header SHALL ofrecer un campo de búsqueda por texto y SHALL navegar al buscador al enviarlo.

#### Scenario: Enviar búsqueda

- **WHEN** el visitante escribe un término y envía el formulario
- **THEN** navega a `/buscar?search={término}`

#### Scenario: Sin término

- **WHEN** el visitante envía la búsqueda vacía
- **THEN** navega a `/buscar` sin filtro de texto

### Requirement: Filtros globales

El header SHALL permitir mostrar un panel de filtros con categoría, precio mínimo, precio máximo, solo ofertas y orden, y SHALL aplicar los filtros en la URL del buscador.

#### Scenario: Aplicar filtros

- **WHEN** el visitante completa el panel y selecciona “Aplicar”
- **THEN** navega a `/buscar` con los parámetros correspondientes

#### Scenario: Sincronización con el buscador

- **WHEN** el visitante está en `/buscar` y la URL cambia
- **THEN** el campo de búsqueda y el panel del header reflejan los valores de la URL

#### Scenario: Cerrar el panel

- **WHEN** el visitante presiona Escape, hace clic fuera o aplica los filtros
- **THEN** el panel se cierra

#### Scenario: Sin controles duplicados en el buscador

- **WHEN** el visitante está en `/buscar`
- **THEN** el header contiene la búsqueda y los filtros, y la página muestra solo los resultados

### Requirement: Acciones de cuenta

El header SHALL mostrar acciones diferentes según la sesión y el rol.

#### Scenario: Visitante sin sesión

- **WHEN** no hay sesión y el visitante no está en `/login`
- **THEN** el header muestra “Iniciar sesión” hacia `/login`

#### Scenario: Comerciante

- **WHEN** la sesión es de rol `merchant`
- **THEN** el header muestra “Mi local” hacia `/comerciante`

#### Scenario: Administrador

- **WHEN** la sesión es de rol `admin`
- **THEN** el header muestra “Panel de administración” hacia `/admin`

#### Scenario: Página de login

- **WHEN** el visitante está en `/login`
- **THEN** el header no muestra la acción de cuenta

### Requirement: Cierre de sesión centralizado

El header SHALL mostrar “Cerrar sesión” cuando hay una sesión activa y SHALL limpiar la sesión al usarlo.

#### Scenario: Cerrar sesión

- **WHEN** el usuario autenticado selecciona “Cerrar sesión”
- **THEN** la sesión se elimina y vuelve a `/`

#### Scenario: Sin duplicados

- **WHEN** el usuario está en el panel de administración o del comerciante
- **THEN** el cierre de sesión solo aparece en el header, no repetido en la página

### Requirement: Página principal de descubrimiento

La ruta `/` SHALL ser la página principal y SHALL mostrar, al inicio del cuerpo, un acceso al mapa de la galería seguido de las secciones de exploración.

#### Scenario: Acceso al mapa

- **WHEN** el visitante abre `/`
- **THEN** ve un botón destacado hacia `/mapa`

#### Scenario: Secciones de exploración

- **WHEN** el visitante abre `/`
- **THEN** ve destacados, ofertas, categorías y locales

#### Scenario: Sin estado técnico

- **WHEN** el visitante abre `/`
- **THEN** no se muestra el estado técnico del backend

### Requirement: Redirección de exploración

La antigua ruta `/explorar` SHALL redirigir a `/` para evitar contenido duplicado.

#### Scenario: Ruta antigua

- **WHEN** el visitante accede a `/explorar`
- **THEN** la aplicación lo redirige a `/`

### Requirement: Asistente virtual

El widget del asistente SHALL mantenerse disponible en las páginas públicas y SHALL seguir oculto en las rutas privadas y de login.

#### Scenario: Página pública

- **WHEN** el visitante navega por una página pública
- **THEN** el botón del asistente sigue visible

#### Scenario: Página privada

- **WHEN** el visitante accede a `/admin`, `/comerciante` o `/login`
- **THEN** el botón del asistente no se muestra

### Requirement: Adaptación y accesibilidad

El header SHALL adaptarse a pantallas pequeñas y SHALL ser operable con teclado.

#### Scenario: Pantalla pequeña

- **WHEN** el header se muestra en un ancho reducido
- **THEN** la búsqueda y las acciones siguen siendo accesibles sin desbordarse

#### Scenario: Teclado

- **WHEN** el visitante recorre el header con el teclado
- **THEN** el logo, la búsqueda, los filtros y las acciones son enfocables y activables
