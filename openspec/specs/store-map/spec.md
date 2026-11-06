# store-map Specification

## Purpose
Define el mapa público esquemático de la galería: ubicación de los locales según lado y posición, identificación por número, selección con ficha resumida y navegación a la ficha del local.

## Requirements

### Requirement: Mapa público sin autenticación

El sistema SHALL permitir a cualquier visitante consultar el mapa de la galería sin iniciar sesión.

#### Scenario: Visitante anónimo

- **WHEN** un visitante sin token consulta el mapa
- **THEN** la respuesta incluye los locales activos con su ubicación

#### Scenario: Sin datos internos

- **WHEN** se devuelven los datos del mapa
- **THEN** la respuesta no incluye cuentas, credenciales, productos ni datos de administración

### Requirement: Datos de ubicación de los locales

El sistema SHALL devolver cada local activo con su identificador, número, nombre, logo, lado y posición.

#### Scenario: Local con ubicación

- **WHEN** se consulta el mapa
- **THEN** cada local incluye `side` (`left`, `right`, `back`) y `position`

#### Scenario: Orden de los datos

- **WHEN** se devuelve la lista de locales
- **THEN** están ordenados por lado y posición

#### Scenario: Local inactivo

- **WHEN** un local está inactivo
- **THEN** no aparece en el mapa

### Requirement: Representación esquemática

La interfaz SHALL representar la galería como un esquema con 10 locales a la izquierda, 10 a la derecha, un pasillo central y el local del fondo.

#### Scenario: Columnas laterales

- **WHEN** el visitante abre el mapa
- **THEN** ve dos columnas con las posiciones 1 a 10 de cada lado

#### Scenario: Local del fondo

- **WHEN** el visitante abre el mapa
- **THEN** ve el local del fondo separado de las columnas

#### Scenario: Sin orientación inventada

- **WHEN** se muestra el mapa
- **THEN** no se indica entrada ni sentido de circulación no definidos en los datos

#### Scenario: Sin coordenadas

- **WHEN** se renderiza el mapa
- **THEN** las posiciones se derivan de `side` y `position`, sin coordenadas inventadas

### Requirement: Identificación de locales

La interfaz SHALL mostrar en cada slot el número, el logo y el nombre del local.

#### Scenario: Número, logo y nombre visibles

- **WHEN** el visitante observa un slot
- **THEN** ve el número, el logo y el nombre del local

#### Scenario: Local sin logo

- **WHEN** un local no tiene logo
- **THEN** el slot muestra un marcador y mantiene visibles su número y nombre

### Requirement: Navegación a la ficha del local

La interfaz SHALL hacer que cada local del mapa enlace directamente a su ficha pública.

#### Scenario: Clic en un local

- **WHEN** el visitante selecciona un slot
- **THEN** navega a `/locales/{id}` del local correspondiente

#### Scenario: Enlace accesible

- **WHEN** el visitante enfoca un local con el teclado y lo activa
- **THEN** navega a la ficha del local

### Requirement: Accesibilidad y adaptación

La interfaz SHALL permitir navegar y abrir los locales con teclado y SHALL adaptarse a pantallas pequeñas.

#### Scenario: Navegación por teclado

- **WHEN** el visitante recorre el mapa con el teclado
- **THEN** cada local es un enlace enfocable y activable

#### Scenario: Etiqueta accesible

- **WHEN** un lector de pantalla enfoca un local
- **THEN** anuncia su número y nombre

#### Scenario: Pantalla pequeña

- **WHEN** el mapa se muestra en un ancho reducido
- **THEN** el esquema sigue siendo legible y operable

### Requirement: Estados de la interfaz del mapa

La interfaz SHALL mostrar estados de carga y error, y SHALL manejar un mapa sin locales.

#### Scenario: Carga

- **WHEN** los datos del mapa están pendientes
- **THEN** la interfaz muestra un estado de carga

#### Scenario: Error

- **WHEN** la consulta falla
- **THEN** la interfaz muestra un mensaje de error sin romper la página

#### Scenario: Mapa vacío

- **WHEN** no hay locales activos
- **THEN** la interfaz muestra un estado vacío
