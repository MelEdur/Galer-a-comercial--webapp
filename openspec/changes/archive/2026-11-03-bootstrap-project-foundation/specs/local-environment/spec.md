# Spec Delta

## Purpose

Define el comportamiento del entorno local reproducible: arranque conjunto de base de datos, backend y frontend, persistencia, dependencias de arranque, configuración segura y verificación de extremo a extremo.

## ADDED Requirements

### Requirement: Entorno local reproducible

El proyecto SHALL poder iniciarse con un único comando de Docker Compose que levante PostgreSQL, backend y frontend.

#### Scenario: Arranque completo

- **WHEN** se ejecuta `docker compose up --build`
- **THEN** los servicios de base de datos, backend y frontend se inician correctamente

#### Scenario: Salud del backend accesible

- **WHEN** el entorno está iniciado
- **THEN** `GET http://localhost:8000/api/health` responde `200`

#### Scenario: Frontend accesible

- **WHEN** el entorno está iniciado
- **THEN** `http://localhost:5173` carga la página inicial

### Requirement: Persistencia de la base de datos

Los datos de PostgreSQL SHALL conservarse en un volumen persistente entre reinicios del servicio.

#### Scenario: Persistencia tras reinicio

- **WHEN** se detiene y vuelve a iniciar el servicio de base de datos
- **THEN** los datos almacenados previamente siguen disponibles

### Requirement: Dependencias de arranque

El backend SHALL esperar a que la base de datos esté saludable antes de iniciarse.

#### Scenario: Base de datos no lista

- **WHEN** el entorno se inicia y la base de datos todavía no está saludable
- **THEN** el backend no se inicia hasta que la base de datos reporte un estado saludable

### Requirement: Configuración segura

La configuración sensible SHALL proporcionarse mediante variables de entorno y SHALL NOT versionarse en el repositorio.

#### Scenario: Variables documentadas

- **WHEN** se revisa el repositorio
- **THEN** existe un archivo de ejemplo con las variables requeridas y valores placeholder

#### Scenario: Secretos fuera del repositorio

- **WHEN** se revisa el repositorio
- **THEN** el archivo de variables de entorno real está excluido del control de versiones

### Requirement: Verificación de extremo a extremo

El entorno local SHALL permitir comprobar la integración completa entre frontend, backend y base de datos.

#### Scenario: Integración visible

- **WHEN** el entorno está iniciado y el backend responde correctamente
- **THEN** la página inicial muestra que el backend está operativo

#### Scenario: Fallo visible de la base de datos

- **WHEN** el servicio de base de datos se detiene
- **THEN** el endpoint de salud responde `503` y la página inicial muestra un estado de error
