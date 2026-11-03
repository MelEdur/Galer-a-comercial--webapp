# Spec Delta

## Purpose

Define la administración de cuentas de comerciante por parte del administrador: consulta, alta con local asignado, baja lógica y disponibilidad de locales.

## ADDED Requirements

### Requirement: Listado de comerciantes

El sistema SHALL exponer al administrador un listado de las cuentas con rol `merchant`, incluyendo su correo, nombre completo, estado y el local asignado.

#### Scenario: Listado con comerciantes

- **WHEN** un administrador autenticado consulta el listado de comerciantes
- **THEN** la respuesta incluye cada comerciante con su correo, nombre completo, estado y local asignado

#### Scenario: Comerciante sin datos sensibles

- **WHEN** se consulta el listado de comerciantes
- **THEN** ninguna entrada incluye la contraseña ni su hash

#### Scenario: Listado vacío

- **WHEN** no existen cuentas de comerciante
- **THEN** la respuesta es una lista vacía

### Requirement: Alta de comerciante

El sistema SHALL permitir al administrador crear una cuenta de comerciante con correo, nombre completo, contraseña inicial y local, asignando el rol `merchant` y el estado activo.

#### Scenario: Alta correcta

- **WHEN** el administrador envía un correo nuevo, un nombre, una contraseña válida y un local libre
- **THEN** la respuesta es `201` con la cuenta creada, sin contraseña ni hash, y el local queda asignado

#### Scenario: Rol fijado por el sistema

- **WHEN** el administrador crea un comerciante
- **THEN** la cuenta resultante tiene rol `merchant` y estado activo

#### Scenario: Datos inválidos

- **WHEN** el administrador envía un correo inválido, un nombre vacío o una contraseña fuera del rango permitido
- **THEN** la respuesta es `422` y no se crea la cuenta

### Requirement: Validación del alta

El sistema SHALL rechazar el alta cuando el correo ya esté registrado o el local ya tenga un comerciante activo, y SHALL rechazar el alta cuando el local no exista.

#### Scenario: Correo duplicado

- **WHEN** el administrador intenta crear un comerciante con un correo ya registrado, sin distinguir mayúsculas
- **THEN** la respuesta es `409` y no se crea la cuenta

#### Scenario: Local ocupado

- **WHEN** el administrador intenta crear un comerciante para un local que ya tiene un comerciante activo
- **THEN** la respuesta es `409` y no se crea la cuenta

#### Scenario: Local inexistente

- **WHEN** el administrador intenta crear un comerciante para un local que no existe
- **THEN** la respuesta es `404` y no se crea la cuenta

### Requirement: Baja de comerciante

El sistema SHALL dar de baja a un comerciante de forma lógica, marcándolo como inactivo y liberando su local para un nuevo comerciante, sin eliminar la cuenta.

#### Scenario: Baja correcta

- **WHEN** el administrador da de baja a un comerciante activo
- **THEN** la respuesta es `204`, la cuenta queda inactiva y conserva su local como histórico

#### Scenario: Local liberado tras la baja

- **WHEN** un comerciante fue dado de baja
- **THEN** su local puede asignarse a un nuevo comerciante activo

#### Scenario: Baja repetida

- **WHEN** el administrador da de baja a un comerciante que ya está inactivo
- **THEN** la respuesta es `204` y no se producen cambios adicionales

#### Scenario: Identificador inexistente o no comerciante

- **WHEN** el administrador intenta dar de baja un identificador que no existe o que no corresponde a un comerciante
- **THEN** la respuesta es `404`

### Requirement: Disponibilidad de locales

El sistema SHALL exponer al administrador los 21 locales con su número, nombre y el comerciante activo asignado, o `null` cuando esté libre.

#### Scenario: Local libre

- **WHEN** un local no tiene comerciante activo
- **THEN** la respuesta lo indica como disponible y con comerciante `null`

#### Scenario: Local ocupado

- **WHEN** un local tiene un comerciante activo
- **THEN** la respuesta incluye una referencia al comerciante asignado

#### Scenario: Conjunto completo

- **WHEN** el administrador consulta los locales
- **THEN** la respuesta incluye los 21 locales ordenados por número

### Requirement: Autorización de la administración de comerciantes

El sistema SHALL permitir las operaciones de administración de comerciantes únicamente a cuentas con rol `admin`.

#### Scenario: Administrador autorizado

- **WHEN** un administrador autenticado accede a cualquier operación de comerciantes
- **THEN** la operación se ejecuta según las reglas del caso de uso

#### Scenario: Comerciante no autorizado

- **WHEN** un comerciante autenticado accede a cualquier operación de administración de comerciantes
- **THEN** la respuesta es `403`

#### Scenario: Sin autenticación

- **WHEN** se accede a una operación de administración de comerciantes sin token
- **THEN** la respuesta es `401`

### Requirement: Panel de administración de comerciantes

La aplicación frontend SHALL ofrecer una ruta administrativa protegida con el listado de comerciantes, un formulario de alta con selector de locales disponibles y una acción de baja con confirmación.

#### Scenario: Visualización del panel

- **WHEN** un administrador autenticado accede a la ruta de comerciantes
- **THEN** ve el listado con correo, nombre, local y estado de cada comerciante

#### Scenario: Alta desde el panel

- **WHEN** el administrador completa el formulario con datos válidos y un local disponible
- **THEN** el comerciante aparece en el listado y el local deja de estar disponible

#### Scenario: Error de local ocupado

- **WHEN** el alta devuelve `409`
- **THEN** el panel muestra un mensaje comprensible y conserva los datos del formulario

#### Scenario: Confirmación de baja

- **WHEN** el administrador solicita la baja de un comerciante
- **THEN** el panel pide confirmación antes de ejecutar la operación

#### Scenario: Sesión no autorizada

- **WHEN** la sesión no es válida o el rol no es administrador
- **THEN** el panel redirige al login o muestra un mensaje de acceso denegado, sin exponer datos
