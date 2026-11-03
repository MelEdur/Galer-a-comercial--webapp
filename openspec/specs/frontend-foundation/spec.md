# frontend-foundation Specification

## Purpose
Define el comportamiento observable de la aplicación frontend inicial: arranque, enrutado básico, consumo del estado del backend y pruebas automatizadas.

## Requirements

### Requirement: Aplicación web inicial

La aplicación frontend SHALL arrancar como una aplicación web de una sola página y SHALL renderizar una página inicial accesible desde la raíz.

#### Scenario: Carga de la página inicial

- **WHEN** un visitante accede a `/`
- **THEN** la aplicación carga y muestra la página inicial sin errores

#### Scenario: Estilos aplicados

- **WHEN** la página inicial se renderiza
- **THEN** los estilos definidos por el sistema de estilos del proyecto se aplican correctamente

### Requirement: Enrutado básico

La aplicación SHALL gestionar la navegación del lado del cliente y SHALL mostrar una página de no encontrado para rutas desconocidas.

#### Scenario: Ruta conocida

- **WHEN** un visitante accede a `/`
- **THEN** se muestra la página inicial

#### Scenario: Ruta desconocida

- **WHEN** un visitante accede a una ruta que no existe
- **THEN** se muestra una página de no encontrado

### Requirement: Estado del backend en la página inicial

La página inicial SHALL consultar el endpoint de salud del backend y SHALL mostrar los estados de carga, éxito y error de forma comprensible.

#### Scenario: Backend operativo

- **WHEN** la consulta de salud responde correctamente
- **THEN** la página muestra que el backend está operativo

#### Scenario: Consulta en curso

- **WHEN** la consulta de salud está pendiente
- **THEN** la página muestra un estado de carga

#### Scenario: Backend no disponible

- **WHEN** la consulta de salud falla o responde con error
- **THEN** la página muestra un estado de error sin bloquearse

### Requirement: Consumo de la API configurable

La aplicación SHALL consumir la API del backend usando una URL base configurable por entorno y SHALL manejar explícitamente las respuestas HTTP de error.

#### Scenario: URL base configurada

- **WHEN** la aplicación se ejecuta con una URL base de API definida
- **THEN** las peticiones se dirigen a esa URL

#### Scenario: Respuesta HTTP de error

- **WHEN** el backend responde con un código de error
- **THEN** la aplicación lo trata como un fallo y muestra el estado de error correspondiente

### Requirement: Pruebas automatizadas del frontend

La base del frontend SHALL incluir una suite de pruebas automatizadas ejecutable que cubra los estados del componente de salud.

#### Scenario: Ejecución de la suite

- **WHEN** se ejecuta la suite de pruebas del frontend
- **THEN** las pruebas de carga, éxito y error se ejecutan y finalizan correctamente

#### Scenario: Estados verificados

- **WHEN** la prueba simula una consulta pendiente, exitosa y fallida
- **THEN** se verifica que la interfaz muestra el estado correspondiente en cada caso
