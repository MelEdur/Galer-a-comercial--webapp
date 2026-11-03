# Spec Delta

## Purpose

Define el acceso del comerciante a su panel: inicio de sesión con su cuenta, visualización de su local, cierre de sesión y separación de rutas respecto del administrador.

## ADDED Requirements

### Requirement: Inicio de sesión del comerciante

El sistema SHALL permitir que una cuenta activa con rol `merchant` inicie sesión con su correo y contraseña y SHALL emitir un token de acceso.

#### Scenario: Credenciales válidas

- **WHEN** un comerciante activo inicia sesión con su correo y contraseña correctos
- **THEN** la respuesta es `200` e incluye un token de acceso

#### Scenario: Contraseña incorrecta

- **WHEN** un comerciante inicia sesión con una contraseña incorrecta
- **THEN** la respuesta es `401` con el mensaje uniforme de credenciales inválidas

#### Scenario: Comerciante dado de baja

- **WHEN** un comerciante inactivo intenta iniciar sesión con credenciales correctas
- **THEN** la respuesta es `401` y no se emite token

### Requirement: Panel del comerciante

La aplicación frontend SHALL ofrecer una ruta protegida para el comerciante que muestre su identidad y los datos de su local, y SHALL permitir cerrar sesión.

#### Scenario: Acceso al panel

- **WHEN** un comerciante autenticado accede a `/comerciante`
- **THEN** el panel muestra su nombre, correo, número y nombre del local

#### Scenario: Cierre de sesión

- **WHEN** el comerciante cierra sesión desde el panel
- **THEN** el token se elimina y se vuelve a la página de login

#### Scenario: Funcionalidades futuras

- **WHEN** el comerciante accede al panel
- **THEN** las secciones de productos, información del local y estadísticas aparecen como no disponibles, sin ejecutar operaciones de esos casos de uso

### Requirement: Separación de rutas por rol

La aplicación SHALL redirigir a cada cuenta autenticada al panel correspondiente a su rol y SHALL impedir el acceso a la ruta del otro rol.

#### Scenario: Redirección tras el login

- **WHEN** un comerciante inicia sesión correctamente
- **THEN** la aplicación lo redirige a `/comerciante`

#### Scenario: Administrador en el panel del comerciante

- **WHEN** un administrador autenticado intenta acceder a `/comerciante`
- **THEN** la aplicación lo redirige a `/admin`

#### Scenario: Comerciante en el panel administrativo

- **WHEN** un comerciante autenticado intenta acceder a `/admin`
- **THEN** la aplicación lo redirige a `/comerciante`

#### Scenario: Sin sesión

- **WHEN** se accede a una ruta protegida sin token
- **THEN** la aplicación redirige a `/login`

### Requirement: Sesión no válida

La aplicación SHALL descartar un token inválido o vencido y SHALL volver a la página de login.

#### Scenario: Token vencido al abrir la aplicación

- **WHEN** la aplicación encuentra un token vencido o inválido en `sessionStorage`
- **THEN** elimina el token y redirige a `/login`

#### Scenario: Identidad rechazada

- **WHEN** la consulta de identidad responde `401`
- **THEN** el frontend limpia la sesión y no muestra datos del panel

### Requirement: Errores de acceso uniformes

El sistema SHALL responder con un mensaje uniforme ante credenciales incorrectas y SHALL NOT revelar si un correo existe.

#### Scenario: Correo inexistente

- **WHEN** se intenta iniciar sesión con un correo que no existe
- **THEN** la respuesta es `401` con el mismo mensaje que una contraseña incorrecta

#### Scenario: Cuenta inactiva

- **WHEN** una cuenta inactiva intenta iniciar sesión
- **THEN** la respuesta es `401` con el mismo mensaje que credenciales inválidas

#### Scenario: Mensaje en el frontend

- **WHEN** el login devuelve `401`
- **THEN** la página muestra un mensaje genérico de credenciales inválidas
