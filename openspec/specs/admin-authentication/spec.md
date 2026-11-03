# admin-authentication Specification

## Purpose
Define el acceso del administrador al sistema: inicio de sesión con credenciales, identidad de la sesión, protección de rutas por rol y creación segura del administrador inicial.

## Requirements

### Requirement: Inicio de sesión

El sistema SHALL permitir iniciar sesión con correo y contraseña y SHALL responder con un token de acceso cuando las credenciales pertenecen a una cuenta activa.

#### Scenario: Credenciales válidas

- **WHEN** una cuenta activa inicia sesión con su correo y contraseña correctos
- **THEN** la respuesta es `200` e incluye un token de acceso y su tipo

#### Scenario: Contraseña incorrecta

- **WHEN** se inicia sesión con una contraseña incorrecta
- **THEN** la respuesta es `401` y no revela si el correo existe

#### Scenario: Correo inexistente

- **WHEN** se inicia sesión con un correo que no corresponde a ninguna cuenta
- **THEN** la respuesta es `401` con el mismo mensaje que una contraseña incorrecta

#### Scenario: Cuenta inactiva

- **WHEN** una cuenta desactivada intenta iniciar sesión con credenciales correctas
- **THEN** la respuesta es `401` y no se emite token

### Requirement: Identidad de la sesión

El sistema SHALL exponer la identidad de la cuenta autenticada con su identificador, correo, nombre completo, rol y, cuando la cuenta tenga un local asignado, los datos de ese local.

#### Scenario: Consulta de identidad

- **WHEN** una cuenta autenticada consulta su identidad
- **THEN** la respuesta incluye su identificador, correo, nombre completo y rol

#### Scenario: Token inválido o vencido

- **WHEN** se consulta la identidad con un token inválido, alterado o vencido
- **THEN** la respuesta es `401`

#### Scenario: Comerciante con local asignado

- **WHEN** una cuenta con rol `merchant` consulta su identidad
- **THEN** la respuesta incluye el identificador, número y nombre de su local

#### Scenario: Cuenta sin local

- **WHEN** una cuenta sin local asignado, como un administrador, consulta su identidad
- **THEN** la respuesta indica que no tiene local

### Requirement: Autorización por rol

El sistema SHALL proteger las rutas administrativas y SHALL permitir el acceso únicamente a cuentas con rol `admin`.

#### Scenario: Administrador autorizado

- **WHEN** un administrador autenticado accede a una ruta administrativa
- **THEN** la operación se ejecuta correctamente

#### Scenario: Comerciante en ruta administrativa

- **WHEN** un comerciante autenticado accede a una ruta administrativa
- **THEN** la respuesta es `403`

#### Scenario: Petición sin token

- **WHEN** se accede a una ruta administrativa sin token de acceso
- **THEN** la respuesta es `401`

### Requirement: Manejo de contraseñas

El sistema SHALL almacenar únicamente el hash de la contraseña y SHALL NOT devolver la contraseña ni su hash en ninguna respuesta.

#### Scenario: Contraseña almacenada como hash

- **WHEN** se crea o actualiza una cuenta con contraseña
- **THEN** solo se persiste un hash `bcrypt` con salt

#### Scenario: Contraseña fuera de las respuestas

- **WHEN** se consulta cualquier respuesta de autenticación o de cuenta
- **THEN** la respuesta no incluye la contraseña ni el hash

#### Scenario: Contraseña demasiado larga

- **WHEN** se intenta registrar una contraseña de más de 72 bytes
- **THEN** la operación se rechaza por validación

### Requirement: Administrador inicial

El sistema SHALL permitir crear el administrador inicial mediante un script idempotente que tome las credenciales de variables de entorno.

#### Scenario: Creación del administrador

- **WHEN** se ejecuta el script con correo, contraseña y nombre completo definidos en el entorno
- **THEN** se crea una cuenta activa con rol `admin` y contraseña hasheada

#### Scenario: Ejecución repetida

- **WHEN** el script se ejecuta nuevamente con el mismo correo
- **THEN** no se duplica la cuenta ni se modifica la contraseña existente

#### Scenario: Variables faltantes

- **WHEN** el script se ejecuta sin correo o sin contraseña
- **THEN** termina con un error claro y no crea ninguna cuenta

### Requirement: Sesión del frontend

La aplicación frontend SHALL ofrecer una página de inicio de sesión, SHALL conservar el token en `sessionStorage` y SHALL redirigir a la página de login cuando no haya sesión válida.

#### Scenario: Inicio de sesión exitoso

- **WHEN** el formulario de login envía credenciales válidas
- **THEN** el token se guarda en `sessionStorage` y se accede a la ruta administrativa

#### Scenario: Ruta protegida sin sesión

- **WHEN** se intenta acceder a una ruta administrativa sin token
- **THEN** la aplicación redirige a la página de login

#### Scenario: Cierre de sesión

- **WHEN** el usuario cierra sesión
- **THEN** el token se elimina de `sessionStorage` y se vuelve a la página de login

#### Scenario: Error de credenciales

- **WHEN** el login devuelve `401`
- **THEN** la página muestra un mensaje de credenciales inválidas sin revelar detalles internos
