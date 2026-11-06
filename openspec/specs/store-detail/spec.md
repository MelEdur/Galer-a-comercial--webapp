# store-detail Specification

## Purpose
Define la ficha pública de un local de la galería: datos generales, horarios, medios de contacto, enlaces externos, comportamiento ante datos incompletos y acceso desde el detalle de producto.

## Requirements

### Requirement: Ficha pública del local

El sistema SHALL permitir a cualquier visitante consultar la información de un local activo sin iniciar sesión.

#### Scenario: Visitante anónimo

- **WHEN** un visitante sin token solicita la ficha de un local activo
- **THEN** la respuesta es `200` con los datos públicos del local

#### Scenario: Sin datos internos

- **WHEN** se devuelve la ficha
- **THEN** la respuesta no incluye estado interno, cuentas, credenciales ni productos

### Requirement: Datos generales del local

El sistema SHALL devolver el número, nombre, descripción y logo del local.

#### Scenario: Local con descripción y logo

- **WHEN** el local tiene descripción y logo
- **THEN** la respuesta incluye ambos datos

#### Scenario: Local sin descripción o logo

- **WHEN** el local no tiene descripción o logo
- **THEN** la respuesta los devuelve como nulos sin fallar

### Requirement: Horarios del local

El sistema SHALL devolver los tramos horarios del local ordenados por día y apertura, y SHALL permitir varios tramos por día.

#### Scenario: Varios tramos en un día

- **WHEN** el local tiene dos tramos para el mismo día
- **THEN** ambos se devuelven ordenados por apertura

#### Scenario: Día sin tramos

- **WHEN** un día no tiene tramos horarios
- **THEN** la interfaz lo muestra como "Cerrado"

#### Scenario: Local sin horarios

- **WHEN** el local no tiene ningún tramo horario
- **THEN** la interfaz oculta la sección de horarios

### Requirement: Medios de contacto

El sistema SHALL devolver el correo, teléfono y WhatsApp del local y SHALL permitir contactar mediante ellos desde la interfaz.

#### Scenario: Contacto completo

- **WHEN** el local tiene correo, teléfono y WhatsApp
- **THEN** la ficha ofrece enlaces `mailto:`, `tel:` y WhatsApp

#### Scenario: Contacto parcial

- **WHEN** el local solo tiene alguno de los medios de contacto
- **THEN** se muestran únicamente los disponibles

#### Scenario: Sin contacto

- **WHEN** el local no tiene ningún medio de contacto
- **THEN** la interfaz oculta la sección de contacto

### Requirement: Enlaces externos

El sistema SHALL devolver los enlaces externos del local ordenados y SHALL mostrarlos como enlaces seguros.

#### Scenario: Varios enlaces

- **WHEN** el local tiene varios enlaces
- **THEN** se devuelven y muestran en el orden definido por el comerciante

#### Scenario: Apertura segura

- **WHEN** el visitante abre un enlace externo
- **THEN** se abre en una pestaña nueva con `rel="noreferrer"`

#### Scenario: Sin enlaces

- **WHEN** el local no tiene enlaces
- **THEN** la interfaz oculta la sección de enlaces

### Requirement: Disponibilidad de la ficha

El sistema SHALL devolver la ficha únicamente de locales activos y SHALL responder `404` cuando el local no exista o esté inactivo.

#### Scenario: Local activo

- **WHEN** el local está activo
- **THEN** la ficha responde `200`

#### Scenario: Local inactivo

- **WHEN** el local está inactivo
- **THEN** la respuesta es `404`

#### Scenario: Local inexistente

- **WHEN** el identificador no corresponde a ningún local
- **THEN** la respuesta es `404`

### Requirement: Datos incompletos en la ficha

La interfaz SHALL ocultar las secciones sin datos y SHALL mostrar un marcador cuando el local no tenga logo.

#### Scenario: Sin logo

- **WHEN** el local no tiene logo
- **THEN** la ficha muestra un marcador visual en lugar de una imagen rota

#### Scenario: Secciones vacías

- **WHEN** faltan horarios, contacto o enlaces
- **THEN** las secciones correspondientes no se muestran

### Requirement: Navegación desde el detalle de producto

La interfaz del detalle de producto SHALL enlazar el local que vende el producto con su ficha pública.

#### Scenario: Acceso desde un producto

- **WHEN** el visitante selecciona el local en el detalle de un producto
- **THEN** navega a `/locales/{id}` del local correspondiente

### Requirement: Estados de la ficha en la interfaz

La interfaz SHALL mostrar estados de carga y error, y una página de local no encontrado cuando el backend responda `404`.

#### Scenario: Carga

- **WHEN** la ficha está pendiente
- **THEN** la interfaz muestra un estado de carga

#### Scenario: Local no encontrado

- **WHEN** el backend responde `404`
- **THEN** la interfaz muestra un mensaje de local no encontrado y un enlace al buscador

#### Scenario: Error de red

- **WHEN** la consulta falla por un error distinto de `404`
- **THEN** la interfaz muestra un mensaje de error sin romper la página

### Requirement: Catálogo del local

La ficha pública del local SHALL mostrar, debajo de sus enlaces, un catálogo paginado con los productos disponibles de ese local.

#### Scenario: Catálogo con productos

- **WHEN** el visitante abre la ficha de un local con productos disponibles
- **THEN** ve una sección “Catálogo” debajo de los enlaces con las tarjetas de sus productos

#### Scenario: Producto del catálogo

- **WHEN** se muestra un producto del catálogo
- **THEN** la tarjeta incluye imagen, nombre, precio, oferta y categorías, y enlaza a `/productos/{id}`

#### Scenario: Sin línea de local

- **WHEN** el producto se muestra dentro del catálogo del local
- **THEN** la tarjeta no repite el número ni el nombre del local

#### Scenario: Paginación

- **WHEN** el local tiene más productos que el tamaño de página
- **THEN** la sección muestra controles de página anterior y siguiente

#### Scenario: Catálogo vacío

- **WHEN** el local no tiene productos disponibles
- **THEN** la sección muestra un mensaje de catálogo vacío

### Requirement: API del catálogo del local

El sistema SHALL exponer los productos disponibles de un local activo mediante un endpoint público paginado.

#### Scenario: Consulta correcta

- **WHEN** se solicitan los productos de un local activo
- **THEN** la respuesta incluye una página de productos del local con el total y la cantidad de páginas

#### Scenario: Solo productos disponibles

- **WHEN** un producto está eliminado, inactivo o pertenece a otro local
- **THEN** no aparece en el catálogo de ese local

#### Scenario: Local inexistente o inactivo

- **WHEN** se solicitan productos de un local inexistente o inactivo
- **THEN** la respuesta es `404`

#### Scenario: Sin eventos de búsqueda

- **WHEN** se consulta el catálogo de un local
- **THEN** no se registran eventos de búsqueda

### Requirement: Volver al origen en la ficha del local

La ficha del local SHALL ofrecer un botón “Volver” que regrese a la página de origen y, si no existe historial interno, a la página principal.

#### Scenario: Origen interno

- **WHEN** el visitante llega desde el mapa, un producto u otra página interna y selecciona “Volver”
- **THEN** regresa a esa página de origen

#### Scenario: Entrada directa

- **WHEN** el visitante abre la ficha directamente por URL y selecciona “Volver”
- **THEN** navega a `/`

#### Scenario: Etiqueta accesible

- **WHEN** el botón se muestra
- **THEN** su texto es “Volver” y es operable con teclado
