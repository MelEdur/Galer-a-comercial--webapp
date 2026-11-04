# Spec Delta

## Purpose

Define el detalle público de un producto disponible: imágenes, descripción, precios, categorías, local con datos de contacto, productos similares y navegación desde la búsqueda.

## ADDED Requirements

### Requirement: Detalle público del producto

El sistema SHALL permitir a cualquier visitante consultar el detalle de un producto disponible sin iniciar sesión.

#### Scenario: Visitante anónimo

- **WHEN** un visitante sin token solicita el detalle de un producto disponible
- **THEN** la respuesta es `200` con los datos públicos del producto

#### Scenario: Sin datos internos

- **WHEN** se devuelve el detalle
- **THEN** la respuesta no incluye `store_id`, `is_active`, `deleted_at`, cuentas ni credenciales

### Requirement: Información e imágenes del producto

El sistema SHALL devolver el nombre, la descripción, el precio, el precio de oferta, el precio efectivo, las categorías y todas las imágenes del producto ordenadas por posición.

#### Scenario: Producto con varias imágenes

- **WHEN** el producto tiene varias imágenes
- **THEN** la respuesta incluye todas, ordenadas por posición e indicando cuál es la primaria

#### Scenario: Producto con oferta

- **WHEN** el producto tiene precio de oferta
- **THEN** la respuesta incluye precio, oferta y precio efectivo

#### Scenario: Producto con categorías

- **WHEN** el producto tiene una o más categorías
- **THEN** la respuesta las incluye

### Requirement: Local que vende el producto

El sistema SHALL devolver el local del producto con su identificador, número, nombre, logo y datos de contacto.

#### Scenario: Local con contacto

- **WHEN** se consulta el detalle de un producto
- **THEN** la respuesta incluye el local con número, nombre, logo, correo, teléfono y WhatsApp cuando existan

#### Scenario: Local sin datos opcionales

- **WHEN** el local no tiene logo o algún dato de contacto
- **THEN** el detalle se devuelve igualmente y esos campos son nulos

### Requirement: Disponibilidad del detalle

El sistema SHALL devolver el detalle únicamente cuando el producto no está eliminado, está activo y su local está activo; en caso contrario SHALL responder `404`.

#### Scenario: Producto disponible

- **WHEN** el producto no está eliminado, está activo y su local está activo
- **THEN** el detalle responde `200`

#### Scenario: Producto inexistente

- **WHEN** se solicita un identificador que no existe
- **THEN** la respuesta es `404`

#### Scenario: Producto eliminado o inactivo

- **WHEN** el producto tiene fecha de eliminación o está inactivo
- **THEN** la respuesta es `404`

#### Scenario: Local inactivo

- **WHEN** el local del producto está inactivo
- **THEN** la respuesta es `404`

### Requirement: Galería sin imágenes

La interfaz del detalle SHALL mostrar un marcador visual cuando el producto no tenga imágenes.

#### Scenario: Producto sin imágenes

- **WHEN** el visitante abre el detalle de un producto sin imágenes
- **THEN** la galería muestra un marcador de "Sin imagen" y el resto de los datos sigue visible

### Requirement: Productos similares

El sistema SHALL exponer productos similares al del detalle, disponibles, excluyendo el producto actual y con un máximo de seis.

#### Scenario: Coincidencia por categoría

- **WHEN** existen otros productos disponibles que comparten una categoría
- **THEN** aparecen entre los similares, priorizados por cantidad de categorías compartidas

#### Scenario: Coincidencia por nombre

- **WHEN** existen otros productos disponibles cuyo nombre contiene una palabra significativa del nombre actual
- **THEN** aparecen entre los similares

#### Scenario: Exclusión del producto actual

- **WHEN** se calculan los similares
- **THEN** el producto consultado no aparece en la lista

#### Scenario: Límite de similares

- **WHEN** hay más de seis candidatos
- **THEN** la respuesta devuelve como máximo seis

#### Scenario: Sin similares

- **WHEN** no existen productos que cumplan los criterios
- **THEN** la respuesta es una lista vacía

#### Scenario: Producto base no disponible

- **WHEN** se solicitan similares de un producto inexistente o no disponible
- **THEN** la respuesta es `404`

### Requirement: Navegación desde la búsqueda

La interfaz de búsqueda SHALL permitir acceder al detalle desde cada resultado.

#### Scenario: Tarjeta de resultado

- **WHEN** el visitante selecciona una tarjeta de resultado
- **THEN** navega a `/productos/{id}` del producto correspondiente

### Requirement: Estados del detalle en la interfaz

La interfaz del detalle SHALL mostrar estados de carga y error, y una página de producto no encontrado cuando el backend responda `404`.

#### Scenario: Carga

- **WHEN** el detalle está pendiente
- **THEN** la interfaz muestra un estado de carga

#### Scenario: Producto no encontrado

- **WHEN** el backend responde `404`
- **THEN** la interfaz muestra un mensaje de producto no encontrado y un enlace al buscador

#### Scenario: Error de red

- **WHEN** la consulta falla por un error distinto de `404`
- **THEN** la interfaz muestra un mensaje de error sin romper la página
