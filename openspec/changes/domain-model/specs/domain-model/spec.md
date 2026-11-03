# Spec Delta

## Purpose

Define la estructura persistente del dominio de la galería comercial: locales, cuentas, catálogo, horarios, contacto, imágenes y eventos de búsqueda, junto con sus relaciones e invariantes.

## ADDED Requirements

### Requirement: Locales de la galería

El sistema SHALL representar los 21 locales fijos de la galería con un número, un lado (`left`, `right`, `back`) y una posición dentro de ese lado, y SHALL garantizar que el número y la combinación lado–posición sean únicos.

#### Scenario: Conjunto completo de locales

- **WHEN** se ejecuta la precarga de locales
- **THEN** existen 21 locales: 10 en el lado derecho, 10 en el lado izquierdo y 1 al fondo

#### Scenario: Número de local duplicado

- **WHEN** se intenta registrar un local con un número ya existente
- **THEN** la operación falla por violar la unicidad del número

#### Scenario: Posición duplicada en un lado

- **WHEN** se intenta registrar dos locales con el mismo lado y la misma posición
- **THEN** la operación falla por violar la unicidad de la posición

### Requirement: Numeración intercalada de locales

La precarga SHALL asignar números impares consecutivos del 1 al 19 a las posiciones 1 a 10 del lado derecho, números pares consecutivos del 2 al 20 a las posiciones 1 a 10 del lado izquierdo, y el número 21 al único local del fondo.

#### Scenario: Correspondencia entre posición y número

- **WHEN** finaliza la precarga
- **THEN** la posición 1 del lado derecho tiene el número 1, la posición 1 del lado izquierdo tiene el número 2, la posición 2 del lado derecho tiene el número 3 y el local del fondo tiene el número 21

#### Scenario: Ejecución repetida de la precarga

- **WHEN** la precarga se ejecuta más de una vez
- **THEN** el resultado sigue siendo exactamente 21 locales, sin duplicados

### Requirement: Información pública del local

El sistema SHALL almacenar el nombre, la descripción, el logo, el correo, el teléfono y el WhatsApp de cada local, y SHALL permitir varios enlaces externos ordenados por local.

#### Scenario: Local con datos completos

- **WHEN** existe un local con nombre, descripción, logo y datos de contacto
- **THEN** esos datos se recuperan asociados al local

#### Scenario: Varios enlaces externos

- **WHEN** un local tiene varios enlaces externos
- **THEN** se recuperan todos, ordenados según su posición

#### Scenario: Local sin datos opcionales

- **WHEN** un local no tiene descripción, logo ni datos de contacto
- **THEN** el local existe y esos campos se recuperan vacíos

### Requirement: Horarios de atención

El sistema SHALL almacenar los horarios del local como tramos por día de la semana, cada uno con hora de apertura y de cierre, SHALL permitir varios tramos para un mismo día y SHALL exigir que el cierre sea posterior a la apertura.

#### Scenario: Tramo horario válido

- **WHEN** se registra un tramo con apertura anterior al cierre
- **THEN** el tramo se almacena correctamente

#### Scenario: Cierre no posterior a la apertura

- **WHEN** se registra un tramo cuyo cierre es anterior o igual a la apertura
- **THEN** la operación falla por violar la restricción horaria

#### Scenario: Varios tramos en un día

- **WHEN** un local tiene dos tramos distintos para el mismo día
- **THEN** ambos tramos se recuperan asociados a ese día

#### Scenario: Día sin tramos

- **WHEN** un local no tiene tramos para un día de la semana
- **THEN** ese día se interpreta como cerrado

### Requirement: Cuentas de usuario

El sistema SHALL almacenar cuentas con correo único, hash de contraseña, rol (`admin` o `merchant`) y estado activo, y SHALL NOT almacenar contraseñas en texto plano.

#### Scenario: Correo duplicado

- **WHEN** se intenta registrar una cuenta con un correo ya existente, sin distinguir mayúsculas
- **THEN** la operación falla por violar la unicidad del correo

#### Scenario: Rol inválido

- **WHEN** se intenta registrar una cuenta con un rol distinto de `admin` o `merchant`
- **THEN** la operación falla por violar la restricción de rol

#### Scenario: Contraseña persistida

- **WHEN** se registra o actualiza una cuenta
- **THEN** solo se persiste el hash de la contraseña

### Requirement: Asignación de comerciantes a locales

El sistema SHALL exigir que toda cuenta con rol `merchant` tenga un local asignado, SHALL impedir que una cuenta `admin` tenga local y SHALL permitir como máximo un comerciante por local.

#### Scenario: Comerciante con local

- **WHEN** se registra un comerciante con un local existente
- **THEN** la cuenta se almacena correctamente asociada a ese local

#### Scenario: Comerciante sin local

- **WHEN** se intenta registrar un comerciante sin local
- **THEN** la operación falla por violar la restricción de asignación

#### Scenario: Administrador con local

- **WHEN** se intenta asignar un local a una cuenta administradora
- **THEN** la operación falla por violar la restricción de asignación

#### Scenario: Segundo comerciante en el mismo local

- **WHEN** se intenta registrar un segundo comerciante para un local que ya tiene uno
- **THEN** la operación falla por violar la unicidad de comerciante por local

### Requirement: Catálogo de productos

El sistema SHALL asociar cada producto a un único local, SHALL almacenar nombre, descripción, precio en pesos argentinos, indicador de destacado y precio de oferta opcional, y SHALL exigir que el precio no sea negativo y que la oferta sea menor que el precio.

#### Scenario: Producto válido

- **WHEN** se registra un producto con precio mayor o igual a cero
- **THEN** el producto se almacena asociado a su local

#### Scenario: Precio negativo

- **WHEN** se intenta registrar un producto con precio negativo
- **THEN** la operación falla por violar la restricción de precio

#### Scenario: Oferta no menor que el precio

- **WHEN** se intenta registrar un producto cuya oferta es mayor o igual que su precio
- **THEN** la operación falla por violar la restricción de oferta

#### Scenario: Producto sin oferta

- **WHEN** se registra un producto sin precio de oferta
- **THEN** el producto se almacena y se recupera sin oferta

### Requirement: Categorización de productos

El sistema SHALL mantener un catálogo global de categorías con nombre único sin distinguir mayúsculas, SHALL permitir que un producto pertenezca a varias categorías y SHALL impedir eliminar una categoría asociada a productos.

#### Scenario: Nombre de categoría duplicado

- **WHEN** se intenta registrar una categoría cuyo nombre coincide con otra sin distinguir mayúsculas
- **THEN** la operación falla por violar la unicidad del nombre

#### Scenario: Producto con varias categorías

- **WHEN** un producto se asocia a dos categorías distintas
- **THEN** ambas asociaciones se recuperan para el producto

#### Scenario: Categoría en uso

- **WHEN** se intenta eliminar una categoría asociada a uno o más productos
- **THEN** la operación falla por integridad referencial

### Requirement: Imágenes de producto

El sistema SHALL almacenar varias imágenes por producto, con un orden definido y como máximo una imagen primaria por producto.

#### Scenario: Varias imágenes ordenadas

- **WHEN** un producto tiene varias imágenes con distinta posición
- **THEN** se recuperan todas en el orden definido

#### Scenario: Segunda imagen primaria

- **WHEN** se intenta marcar una segunda imagen como primaria para el mismo producto
- **THEN** la operación falla por violar la unicidad de imagen primaria

### Requirement: Registro de búsquedas para estadísticas

El sistema SHALL registrar un evento por cada producto devuelto en una búsqueda, con el término consultado y la fecha del evento, y SHALL conservar esos eventos como histórico para calcular los productos más buscados en un lapso de tiempo.

#### Scenario: Búsqueda con resultados

- **WHEN** una búsqueda devuelve varios productos
- **THEN** se registra un evento por cada producto devuelto, con el término y la fecha de la búsqueda

#### Scenario: Conteo por producto y rango de fechas

- **WHEN** se consultan los eventos de un producto dentro de un rango de fechas
- **THEN** se obtiene la cantidad de búsquedas que incluyeron ese producto en el rango

#### Scenario: Producto desactivado

- **WHEN** un producto se marca como inactivo o se borra lógicamente
- **THEN** sus eventos de búsqueda anteriores se conservan

### Requirement: Integridad referencial y borrado

El sistema SHALL impedir eliminar un local que tenga productos o comerciantes asociados, SHALL aplicar borrado lógico a los productos y SHALL desactivar las cuentas en lugar de eliminarlas.

#### Scenario: Borrado de local con productos

- **WHEN** se intenta eliminar un local que tiene productos asociados
- **THEN** la operación falla por integridad referencial

#### Scenario: Borrado de local con comerciante

- **WHEN** se intenta eliminar un local que tiene un comerciante asignado
- **THEN** la operación falla por integridad referencial

#### Scenario: Borrado lógico de producto

- **WHEN** un producto se marca como borrado
- **THEN** el producto deja de considerarse activo pero sus datos e imágenes permanecen almacenados

### Requirement: Migración del esquema

El esquema SHALL crearse mediante una migración versionada y reversible, y el backend SHALL NOT crear ni modificar tablas al arrancar.

#### Scenario: Aplicación de la migración

- **WHEN** se ejecuta la migración inicial sobre una base vacía
- **THEN** se crean las nueve tablas del dominio con sus restricciones e índices

#### Scenario: Reversión de la migración

- **WHEN** se revierte la migración inicial
- **THEN** las tablas del dominio se eliminan y la base queda sin ellas

#### Scenario: Arranque sin creación automática

- **WHEN** el backend arranca contra una base sin el esquema aplicado
- **THEN** no crea tablas automáticamente
