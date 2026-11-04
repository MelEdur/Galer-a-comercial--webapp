# merchant-store-settings Specification

## Purpose
Define la consulta y actualización del local propio por parte del comerciante: datos generales, contacto, horarios semanales y enlaces externos, con validaciones y control de propiedad.

## Requirements

### Requirement: Consulta del local propio

El sistema SHALL permitir al comerciante autenticado consultar la información de su local asignado, incluyendo número, lado, posición, nombre, descripción, logo, contacto, horarios y enlaces.

#### Scenario: Consulta correcta

- **WHEN** un comerciante autenticado consulta su local
- **THEN** la respuesta incluye sus datos generales, contacto, horarios y enlaces

#### Scenario: Local derivado de la sesión

- **WHEN** el comerciante consulta su local
- **THEN** el local se obtiene de su cuenta autenticada y no de un identificador enviado por el cliente

#### Scenario: Datos incompletos

- **WHEN** el local no tiene logo, descripción, contacto, horarios o enlaces
- **THEN** la consulta responde correctamente con esos campos vacíos o nulos

### Requirement: Actualización de datos generales

El sistema SHALL permitir al comerciante actualizar el nombre, la descripción y el logo de su local.

#### Scenario: Guardado correcto

- **WHEN** el comerciante envía un nombre válido y los datos generales
- **THEN** la respuesta es `200` y los cambios quedan persistidos

#### Scenario: Nombre obligatorio

- **WHEN** el comerciante envía un nombre vacío o ausente
- **THEN** la respuesta es `422` y no se guarda ningún cambio

#### Scenario: Límites de longitud

- **WHEN** el nombre supera 120 caracteres o la descripción supera 2000
- **THEN** la respuesta es `422`

#### Scenario: Logo por URL

- **WHEN** el comerciante envía una URL de logo `http` o `https` de hasta 500 caracteres
- **THEN** el logo se guarda

#### Scenario: Logo inválido

- **WHEN** la URL del logo no usa `http` o `https` o excede 500 caracteres
- **THEN** la respuesta es `422`

### Requirement: Actualización de medios de contacto

El sistema SHALL permitir al comerciante actualizar el correo, el teléfono y el WhatsApp de su local, y SHALL validar el correo y los límites de longitud.

#### Scenario: Contacto válido

- **WHEN** el comerciante envía un correo válido, teléfono y WhatsApp dentro de los límites
- **THEN** los datos se guardan

#### Scenario: Correo inválido

- **WHEN** el comerciante envía un correo con formato inválido
- **THEN** la respuesta es `422`

#### Scenario: Contacto opcional

- **WHEN** el comerciante deja vacío alguno de los medios de contacto
- **THEN** el local se guarda con ese campo nulo

### Requirement: Horarios de atención

El sistema SHALL permitir definir varios tramos horarios por día de la semana y SHALL reemplazar el conjunto completo en cada guardado.

#### Scenario: Varios tramos por día

- **WHEN** el comerciante envía dos tramos distintos para el mismo día
- **THEN** ambos se guardan y se recuperan ordenados por día y apertura

#### Scenario: Día cerrado

- **WHEN** el comerciante no envía tramos para un día
- **THEN** ese día queda sin horario definido

#### Scenario: Cierre inválido

- **WHEN** un tramo tiene cierre anterior o igual a la apertura
- **THEN** la respuesta es `422`

#### Scenario: Día inválido

- **WHEN** un tramo usa un día fuera del rango 0 a 6
- **THEN** la respuesta es `422`

#### Scenario: Reemplazo completo

- **WHEN** el comerciante guarda un nuevo conjunto de horarios
- **THEN** los tramos anteriores se reemplazan por el conjunto enviado

### Requirement: Enlaces externos

El sistema SHALL permitir gestionar una lista ordenada de enlaces externos con etiqueta y URL, con un máximo de diez y sin URLs repetidas.

#### Scenario: Varios enlaces

- **WHEN** el comerciante envía varios enlaces válidos
- **THEN** se guardan en el orden enviado y se recuperan en ese orden

#### Scenario: URL inválida

- **WHEN** un enlace no usa `http` o `https` o excede 500 caracteres
- **THEN** la respuesta es `422`

#### Scenario: URL repetida

- **WHEN** el comerciante envía dos enlaces con la misma URL
- **THEN** la respuesta es `422`

#### Scenario: Límite de enlaces

- **WHEN** el comerciante envía más de diez enlaces
- **THEN** la respuesta es `422`

#### Scenario: Sin enlaces

- **WHEN** el comerciante envía una lista vacía
- **THEN** se eliminan los enlaces anteriores

### Requirement: Propiedad y autorización del local

El sistema SHALL permitir la consulta y actualización únicamente a cuentas activas con rol `merchant`, SHALL limitar la operación a su local y SHALL rechazar cualquier identificador de local enviado por el cliente.

#### Scenario: Comerciante autorizado

- **WHEN** un comerciante activo consulta o actualiza su local
- **THEN** la operación se ejecuta solo sobre su local

#### Scenario: Administrador

- **WHEN** una cuenta con rol `admin` accede a las rutas del local del comerciante
- **THEN** la respuesta es `403`

#### Scenario: Sin autenticación

- **WHEN** se accede sin token
- **THEN** la respuesta es `401`

#### Scenario: Comerciante sin local

- **WHEN** una cuenta de comerciante no tiene local asignado
- **THEN** la respuesta es `403`

#### Scenario: Intento de enviar otro local

- **WHEN** el cuerpo incluye `store_id` o cualquier campo no permitido
- **THEN** la respuesta es `422` y no se modifica ningún local

### Requirement: Formulario de administración del local

La aplicación frontend SHALL ofrecer una ruta protegida para consultar y guardar la información del local, con secciones de datos generales, contacto, horarios y enlaces.

#### Scenario: Carga de datos actuales

- **WHEN** el comerciante accede a la página de su local
- **THEN** el formulario muestra los datos actuales, incluidos horarios y enlaces

#### Scenario: Guardado exitoso

- **WHEN** el comerciante guarda cambios válidos
- **THEN** la interfaz vuelve al panel del comerciante con los datos actualizados

#### Scenario: Datos del panel actualizados

- **WHEN** el comerciante regresa al panel después de guardar
- **THEN** la sesión se refresca y el panel muestra el nombre y los datos actualizados del local

#### Scenario: Error de validación

- **WHEN** el backend responde `422`
- **THEN** la interfaz muestra los errores sin perder los datos ingresados

#### Scenario: Campos de solo lectura

- **WHEN** el formulario muestra el número, lado y posición del local
- **THEN** esos campos no son editables

#### Scenario: Acceso desde el panel

- **WHEN** el comerciante accede al panel
- **THEN** la sección de información del local enlaza a su administración

#### Scenario: Sesión no autorizada

- **WHEN** la sesión no es válida o el rol no es comerciante
- **THEN** la interfaz redirige al login o muestra acceso denegado sin exponer datos
