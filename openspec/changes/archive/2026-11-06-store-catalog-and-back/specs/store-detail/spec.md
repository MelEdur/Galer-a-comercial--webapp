# Spec Delta

## ADDED Requirements

### Requirement: Catálogo del local

La ficha pública del local SHALL mostrar, debajo de sus enlaces, un catálogo paginado con los productos disponibles de ese local.

#### Scenario: Catálogo con productos

- **WHEN** el visitante abre la ficha de un local con productos disponibles
- **THEN** ve una sección “Catálogo” debajo de los enlaces con las tarjetas de sus productos

#### Scenario: Producto del catálogo

- **WHEN** se muestra un producto del catálogo
- **THEN** la tarjeta incluye imagen, nombre, precio, oferta y categorías, y enlaza a `/productos/{id}`

#### Scenario: Sin línea de local

- **WHEN** el producto se muestra dentro del catálogo del local
- **THEN** la tarjeta no repite el número ni el nombre del local

#### Scenario: Paginación

- **WHEN** el local tiene más productos que el tamaño de página
- **THEN** la sección muestra controles de página anterior y siguiente

#### Scenario: Catálogo vacío

- **WHEN** el local no tiene productos disponibles
- **THEN** la sección muestra un mensaje de catálogo vacío

### Requirement: API del catálogo del local

El sistema SHALL exponer los productos disponibles de un local activo mediante un endpoint público paginado.

#### Scenario: Consulta correcta

- **WHEN** se solicitan los productos de un local activo
- **THEN** la respuesta incluye una página de productos del local con el total y la cantidad de páginas

#### Scenario: Solo productos disponibles

- **WHEN** un producto está eliminado, inactivo o pertenece a otro local
- **THEN** no aparece en el catálogo de ese local

#### Scenario: Local inexistente o inactivo

- **WHEN** se solicitan productos de un local inexistente o inactivo
- **THEN** la respuesta es `404`

#### Scenario: Sin eventos de búsqueda

- **WHEN** se consulta el catálogo de un local
- **THEN** no se registran eventos de búsqueda

### Requirement: Volver al origen en la ficha del local

La ficha del local SHALL ofrecer un botón “Volver” que regrese a la página de origen y, si no existe historial interno, a la página principal.

#### Scenario: Origen interno

- **WHEN** el visitante llega desde el mapa, un producto u otra página interna y selecciona “Volver”
- **THEN** regresa a esa página de origen

#### Scenario: Entrada directa

- **WHEN** el visitante abre la ficha directamente por URL y selecciona “Volver”
- **THEN** navega a `/`

#### Scenario: Etiqueta accesible

- **WHEN** el botón se muestra
- **THEN** su texto es “Volver” y es operable con teclado
