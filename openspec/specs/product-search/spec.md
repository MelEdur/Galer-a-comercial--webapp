# product-search Specification

## Purpose
Define la búsqueda pública de productos disponibles en la galería, con filtros combinables por nombre, categoría y precio, información del local, orden, paginación y registro de eventos.

## Requirements

### Requirement: Búsqueda pública sin autenticación

El sistema SHALL permitir a cualquier visitante consultar los productos disponibles sin iniciar sesión.

#### Scenario: Visitante anónimo

- **WHEN** un visitante sin token consulta la búsqueda de productos
- **THEN** la respuesta es `200` con los resultados disponibles

#### Scenario: Sin datos sensibles

- **WHEN** se devuelven productos
- **THEN** la respuesta no incluye credenciales, datos internos ni información de cuentas

### Requirement: Búsqueda por nombre

El sistema SHALL buscar productos por coincidencia parcial en el nombre, sin distinguir mayúsculas y tratando los comodines como texto literal.

#### Scenario: Coincidencia parcial

- **WHEN** el visitante busca `reme`
- **THEN** se incluyen productos cuyo nombre contiene `reme`, como `Remera`

#### Scenario: Sin distinción de mayúsculas

- **WHEN** el visitante busca `REMERA` o `remera`
- **THEN** el resultado es el mismo

#### Scenario: Comodines literales

- **WHEN** el término contiene `%` o `_`
- **THEN** esos caracteres se buscan literalmente y no como comodines

### Requirement: Filtro por categoría

El sistema SHALL permitir filtrar los productos por una categoría global.

#### Scenario: Productos de una categoría

- **WHEN** el visitante filtra por una categoría
- **THEN** recibe solo productos asociados a esa categoría

#### Scenario: Categoría sin productos

- **WHEN** el visitante filtra por una categoría sin productos disponibles
- **THEN** la respuesta es una lista vacía con total cero

### Requirement: Filtro por precio

El sistema SHALL permitir filtrar por precio mínimo, máximo o ambos, de forma inclusiva y sobre el precio efectivo del producto.

#### Scenario: Solo precio mínimo

- **WHEN** el visitante indica un precio mínimo
- **THEN** se incluyen productos cuyo precio efectivo es mayor o igual a ese valor

#### Scenario: Solo precio máximo

- **WHEN** el visitante indica un precio máximo
- **THEN** se incluyen productos cuyo precio efectivo es menor o igual a ese valor

#### Scenario: Rango completo

- **WHEN** el visitante indica mínimo y máximo
- **THEN** se incluyen productos cuyo precio efectivo está dentro del rango inclusive

#### Scenario: Precio efectivo con oferta

- **WHEN** un producto tiene precio de oferta
- **THEN** el filtro y el orden por precio usan el precio de oferta

#### Scenario: Rango inválido

- **WHEN** el precio mínimo es mayor que el máximo
- **THEN** la respuesta es `422`

#### Scenario: Precio negativo

- **WHEN** se envía un precio negativo
- **THEN** la respuesta es `422`

### Requirement: Combinación de filtros

El sistema SHALL combinar los filtros de nombre, categoría y precio con conjunción: todos los criterios enviados deben cumplirse.

#### Scenario: Nombre y categoría

- **WHEN** el visitante envía nombre y categoría
- **THEN** solo recibe productos que cumplen ambos criterios

#### Scenario: Todos los filtros

- **WHEN** el visitante envía nombre, categoría y rango de precio
- **THEN** solo recibe productos que cumplen los tres criterios

### Requirement: Disponibilidad de productos

El sistema SHALL devolver únicamente productos no eliminados, activos y pertenecientes a locales activos.

#### Scenario: Producto disponible

- **WHEN** un producto no está eliminado, está activo y su local está activo
- **THEN** puede aparecer en los resultados

#### Scenario: Producto eliminado

- **WHEN** un producto tiene fecha de eliminación
- **THEN** no aparece en la búsqueda pública

#### Scenario: Producto inactivo

- **WHEN** un producto está marcado como inactivo
- **THEN** no aparece en la búsqueda pública

#### Scenario: Local inactivo

- **WHEN** el local de un producto está inactivo
- **THEN** sus productos no aparecen en la búsqueda pública

### Requirement: Resultado con local y datos del producto

El sistema SHALL devolver cada producto con su nombre, descripción, precio, precio de oferta, precio efectivo, categorías, imagen primaria y el local que lo ofrece.

#### Scenario: Producto con local

- **WHEN** se devuelve un producto
- **THEN** la respuesta incluye el identificador, número y nombre de su local

#### Scenario: Producto con oferta

- **WHEN** el producto tiene precio de oferta
- **THEN** la respuesta incluye precio, oferta y precio efectivo

#### Scenario: Producto con varias imágenes

- **WHEN** el producto tiene varias imágenes
- **THEN** la respuesta incluye la imagen primaria

#### Scenario: Mismo nombre en dos locales

- **WHEN** dos locales ofrecen productos con el mismo nombre
- **THEN** aparecen como dos resultados independientes, cada uno con su local

### Requirement: Orden y paginación

El sistema SHALL paginar los resultados y SHALL permitir ordenarlos por nombre o por precio efectivo.

#### Scenario: Orden por nombre

- **WHEN** el visitante no indica orden
- **THEN** los resultados se ordenan por nombre ascendente

#### Scenario: Orden por precio

- **WHEN** el visitante elige precio ascendente o descendente
- **THEN** los resultados se ordenan por precio efectivo en ese sentido

#### Scenario: Paginación

- **WHEN** el visitante solicita una página con tamaño dentro del rango permitido
- **THEN** la respuesta incluye los elementos, el total, la página, el tamaño y la cantidad de páginas

#### Scenario: Tamaño fuera de rango

- **WHEN** el tamaño de página es menor que uno o mayor que cien
- **THEN** la respuesta es `422`

### Requirement: Búsqueda sin criterios

El sistema SHALL devolver todos los productos disponibles paginados cuando no se envíe ningún criterio de búsqueda.

#### Scenario: Exploración inicial

- **WHEN** el visitante abre el buscador sin filtros
- **THEN** recibe la primera página de todos los productos disponibles

### Requirement: Categorías públicas

El sistema SHALL exponer las categorías globales al visitante para alimentar los filtros de búsqueda.

#### Scenario: Listado de categorías

- **WHEN** el visitante consulta las categorías
- **THEN** recibe todas las categorías ordenadas por nombre

### Requirement: Registro de eventos de búsqueda

El sistema SHALL registrar un evento por cada producto devuelto en la página cuando la consulta tenga al menos un criterio, con el término y la fecha.

#### Scenario: Búsqueda con resultados

- **WHEN** una búsqueda con criterios devuelve productos
- **THEN** se registra un evento por cada producto de la página

#### Scenario: Búsqueda sin criterios

- **WHEN** el visitante explora sin filtros
- **THEN** no se registran eventos

#### Scenario: Búsqueda sin resultados

- **WHEN** una búsqueda no devuelve productos
- **THEN** no se registran eventos

#### Scenario: Eventos históricos

- **WHEN** un producto se elimina o desactiva después de una búsqueda
- **THEN** sus eventos anteriores se conservan

### Requirement: Filtro por ofertas

El sistema SHALL permitir filtrar la búsqueda pública para devolver únicamente productos con precio de oferta mediante el parámetro `has_offer`.

#### Scenario: Solo productos con oferta

- **WHEN** el visitante envía `has_offer=true`
- **THEN** la búsqueda devuelve únicamente productos con precio de oferta

#### Scenario: Sin el filtro

- **WHEN** el visitante no envía `has_offer` o envía `false`
- **THEN** la búsqueda mantiene su comportamiento actual y no filtra por oferta

#### Scenario: Combinación con otros filtros

- **WHEN** el visitante combina `has_offer=true` con categoría o precio
- **THEN** se aplican todos los criterios con conjunción
