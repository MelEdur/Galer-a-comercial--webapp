# Spec Delta

## Purpose

Define el comportamiento observable de la base del backend: configuración por entorno, acceso a datos, migraciones versionadas, salud del servicio y pruebas automatizadas.

## ADDED Requirements

### Requirement: Estructura modular del backend

El backend SHALL organizarse por módulos funcionales y, en esta etapa, SHALL exponer únicamente el módulo de salud, sin rutas de negocio.

#### Scenario: Arranque sin rutas de negocio

- **WHEN** se inicia el backend
- **THEN** la API expone `GET /api/health` y no expone rutas de usuarios, productos, locales ni otras funcionalidades de negocio

#### Scenario: Organización por módulos

- **WHEN** se inspecciona el código del backend
- **THEN** la configuración, el acceso a datos y el módulo de salud están separados en ubicaciones claramente identificables

### Requirement: Configuración por variables de entorno

La aplicación SHALL obtener su configuración de variables de entorno y SHALL rechazar el arranque con un mensaje claro cuando falte la URL de conexión a la base de datos.

#### Scenario: Configuración completa

- **WHEN** las variables de entorno requeridas están definidas
- **THEN** el backend arranca correctamente

#### Scenario: Falta la URL de base de datos

- **WHEN** se inicia el backend sin la variable de conexión a la base de datos
- **THEN** el arranque falla con un error de validación que identifica la variable faltante

### Requirement: Conexión a la base de datos

El backend SHALL abrir una sesión de base de datos por request, cerrarla al finalizar y SHALL NOT crear ni modificar tablas automáticamente al arrancar.

#### Scenario: Consulta a la base de datos

- **WHEN** se ejecuta una consulta simple contra PostgreSQL durante una petición
- **THEN** la consulta se completa correctamente y la sesión se cierra al terminar la petición

#### Scenario: Sin creación automática de esquema

- **WHEN** el backend arranca contra una base de datos vacía
- **THEN** no se crean tablas automáticamente

### Requirement: Migraciones versionadas

Los cambios de esquema SHALL gestionarse mediante migraciones versionadas que puedan aplicarse de forma explícita y repetible.

#### Scenario: Aplicación de migraciones

- **WHEN** se ejecuta la aplicación de migraciones sobre una base actualizada
- **THEN** el comando termina correctamente y no deja migraciones pendientes

#### Scenario: Migraciones no automáticas

- **WHEN** el backend arranca
- **THEN** no aplica migraciones de esquema de forma automática

### Requirement: Endpoint de salud

El sistema SHALL exponer `GET /api/health` para informar el estado del backend y de su conexión a la base de datos.

#### Scenario: Servicio y base disponibles

- **WHEN** se solicita `GET /api/health` con la base de datos disponible
- **THEN** responde `200` con un cuerpo JSON que indica estado `ok` y base de datos `ok`

#### Scenario: Base de datos no disponible

- **WHEN** se solicita `GET /api/health` y la base de datos no responde
- **THEN** responde `503` con un cuerpo JSON que indica estado `degraded` y base de datos `unavailable`

#### Scenario: Error sin detalles internos

- **WHEN** la verificación de la base de datos falla
- **THEN** la respuesta no incluye stack traces, credenciales ni detalles internos de conexión

### Requirement: Pruebas automatizadas del backend

La base del backend SHALL incluir una suite de pruebas automatizadas ejecutable que cubra la configuración, la conexión a la base de datos y el endpoint de salud.

#### Scenario: Ejecución de la suite

- **WHEN** se ejecuta la suite de pruebas del backend
- **THEN** las pruebas de configuración, base de datos y salud se ejecutan y finalizan correctamente

#### Scenario: Cobertura de fallo de base de datos

- **WHEN** la suite simula una base de datos no disponible
- **THEN** existe una prueba que verifica la respuesta `503` del endpoint de salud
