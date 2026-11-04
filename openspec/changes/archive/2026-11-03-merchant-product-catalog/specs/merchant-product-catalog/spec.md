# Spec Delta

## Purpose

Define la administración del catálogo propio del comerciante: consulta paginada y filtrada, alta, edición, baja lógica, restauración, categorías globales e imágenes por URL, con control de propiedad por local.

## ADDED Requirements

### Requirement: Catálogo propio del comerciante

El sistema SHALL exponer al comerciante autenticado un listado paginado de los productos de su local, con búsqueda por nombre, filtro por estado y filtro por categoría.

#### Scenario: Listado de productos vigentes

- **WHEN** un comerciante consulta su catálogo sin filtros
- **THEN** recibe solo los productos vigentes de su local, ordenados por nombre

#### Scenario: Búsqueda por nombre

- **WHEN** el comerciante busca por un texto
- **THEN** el resultado incluye los productos cuyo nombre contiene ese texto sin distinguir mayúsculas

#### Scenario: Filtro por estado

- **WHEN** el comerciante filtra por estado `active`, `deleted` o `all`
- **THEN** recibe los productos vigentes, los eliminados o ambos, respectivamente

#### Scenario: Filtro por categoría

- **WHEN** el comerciante filtra por una categoría
- **THEN** recibe solo los productos de su local asociados a esa categoría

#### Scenario: Paginación

- **WHEN** el comerciante solicita una página con tamaño dentro del rango permitido
- **THEN** la respuesta incluye los elementos de la página, el total, la página, el tamaño y la cantidad de páginas

### Requirement: Alta de producto

El sistema SHALL permitir al comerciante crear un producto asociado automáticamente a su local, con nombre, precio y al menos una categoría, y con descripción, precio de oferta e imágenes opcionales.

#### Scenario: Alta correcta

- **WHEN** el comerciante envía nombre, precio y una categoría existente
- **THEN** la respuesta es `201`, el producto queda asociado a su local y aparece en su catálogo

#### Scenario: Local derivado de la sesión

- **WHEN** el comerciante crea un producto
- **THEN** el local se toma de su cuenta autenticada y no del cuerpo de la petición

#### Scenario: Intento de enviar el local

- **WHEN** el cuerpo de la petición incluye `store_id` o cualquier campo no permitido
- **THEN** la respuesta es `422` y no se crea el producto

#### Scenario: Datos inválidos

- **WHEN** falta el nombre, el precio o la categoría, o los valores no respetan los límites
- **THEN** la respuesta es `422` y no se crea el producto

### Requirement: Edición de producto

El sistema SHALL permitir al comerciante modificar parcialmente un producto vigente de su local, incluyendo nombre, descripción, precios, categorías e imágenes.

#### Scenario: Edición correcta

- **WHEN** el comerciante modifica un campo de un producto vigente de su local
- **THEN** la respuesta es `200` con el producto actualizado

#### Scenario: Reemplazo de categorías e imágenes

- **WHEN** la edición incluye `category_ids` o `images`
- **THEN** el conjunto enviado reemplaza al anterior

#### Scenario: Producto eliminado

- **WHEN** el comerciante intenta modificar un producto eliminado
- **THEN** la respuesta es `409` y el producto no cambia

#### Scenario: Producto de otro local

- **WHEN** el comerciante intenta modificar un producto de otro local
- **THEN** la respuesta es `404`

### Requirement: Baja lógica de producto

El sistema SHALL dar de baja un producto de forma lógica, idempotente y sin eliminar sus datos ni sus imágenes.

#### Scenario: Baja correcta

- **WHEN** el comerciante da de baja un producto vigente de su local
- **THEN** la respuesta es `204` y el producto deja de aparecer entre los vigentes

#### Scenario: Baja repetida

- **WHEN** el comerciante da de baja un producto ya eliminado
- **THEN** la respuesta es `204` y no se producen cambios adicionales

#### Scenario: Datos conservados

- **WHEN** un producto fue dado de baja
- **THEN** sus datos e imágenes permanecen almacenados y visibles al filtrar por eliminados

### Requirement: Restauración de producto

El sistema SHALL permitir al comerciante restaurar un producto eliminado de su local, devolviéndolo al estado vigente sin perder sus datos, categorías ni imágenes.

#### Scenario: Restauración correcta

- **WHEN** el comerciante restaura un producto eliminado de su local
- **THEN** la respuesta es `200`, el producto vuelve a aparecer entre los vigentes y conserva sus datos, categorías e imágenes

#### Scenario: Restauración repetida

- **WHEN** el comerciante restaura un producto que ya está vigente
- **THEN** la respuesta es `200` y no se producen cambios adicionales

#### Scenario: Producto de otro local

- **WHEN** el comerciante intenta restaurar un producto de otro local
- **THEN** la respuesta es `404`

#### Scenario: Sin autenticación

- **WHEN** se intenta restaurar un producto sin token
- **THEN** la respuesta es `401`

### Requirement: Propiedad y autorización del catálogo

El sistema SHALL permitir las operaciones del catálogo únicamente a cuentas activas con rol `merchant`, SHALL limitar cada operación a los productos del local de la cuenta y SHALL tratar los productos de otro local como inexistentes.

#### Scenario: Comerciante autenticado

- **WHEN** un comerciante activo opera sobre sus propios productos
- **THEN** la operación se ejecuta según las reglas del catálogo

#### Scenario: Producto de otro local

- **WHEN** un comerciante consulta, modifica o elimina un producto de otro local
- **THEN** la respuesta es `404`

#### Scenario: Rol no autorizado

- **WHEN** una cuenta con rol `admin` accede a las rutas del catálogo del comerciante
- **THEN** la respuesta es `403`

#### Scenario: Sin autenticación

- **WHEN** se accede a una ruta del catálogo sin token
- **THEN** la respuesta es `401`

### Requirement: Categorías del catálogo

El sistema SHALL exponer las categorías globales en modo de solo lectura y SHALL precargar diez categorías iniciales de forma idempotente.

#### Scenario: Listado de categorías

- **WHEN** el comerciante consulta las categorías
- **THEN** recibe todas las categorías ordenadas por nombre

#### Scenario: Semilla inicial

- **WHEN** se ejecuta la precarga de categorías
- **THEN** existen las diez categorías acordadas y una segunda ejecución no crea duplicados

#### Scenario: Categoría inexistente en el alta

- **WHEN** el comerciante envía un identificador de categoría que no existe
- **THEN** la respuesta es `422` y no se crea ni modifica el producto

### Requirement: Imágenes del producto

El sistema SHALL permitir hasta cinco imágenes por producto mediante URLs ordenadas, SHALL marcar la primera como primaria y SHALL NOT admitir subida de archivos.

#### Scenario: Producto con imágenes

- **WHEN** el comerciante envía dos URLs de imagen al crear o editar
- **THEN** ambas se almacenan en orden y la primera queda como primaria

#### Scenario: Límite de imágenes

- **WHEN** el comerciante envía más de cinco imágenes
- **THEN** la respuesta es `422` y no se guarda el producto

#### Scenario: URL inválida

- **WHEN** una imagen no usa un esquema `http` o `https` o excede la longitud permitida
- **THEN** la respuesta es `422`

### Requirement: Precios del producto

El sistema SHALL validar que el precio no sea negativo y que el precio de oferta, cuando exista, sea no negativo y estrictamente menor que el precio.

#### Scenario: Precio válido

- **WHEN** el comerciante envía un precio mayor o igual a cero con dos decimales
- **THEN** el precio se almacena correctamente

#### Scenario: Oferta inválida

- **WHEN** el comerciante envía una oferta mayor o igual que el precio
- **THEN** la respuesta es `422` y no se guarda el cambio

#### Scenario: Sin oferta

- **WHEN** el comerciante no envía precio de oferta
- **THEN** el producto se guarda sin oferta
