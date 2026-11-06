# Spec Delta

## Purpose

Define la portada pública de exploración de la galería: productos destacados, ofertas, categorías con conteo y locales, además del listado público de locales.

## ADDED Requirements

### Requirement: Exploración pública sin autenticación

El sistema SHALL permitir a cualquier visitante explorar productos, categorías y locales sin iniciar sesión.

#### Scenario: Visitante anónimo

- **WHEN** un visitante sin token consulta la exploración
- **THEN** la respuesta es `200` con las secciones de descubrimiento

#### Scenario: Sin datos internos

- **WHEN** se devuelven productos o locales
- **THEN** la respuesta no incluye cuentas, credenciales, estado interno ni datos de administración

### Requirement: Productos destacados

El sistema SHALL devolver hasta ocho productos destacados, compuestos por ofertas recientes primero y luego novedades, sin repetir productos.

#### Scenario: Ofertas primero

- **WHEN** existen productos con precio de oferta
- **THEN** aparecen primero en destacados, ordenados por fecha de creación descendente

#### Scenario: Completar con novedades

- **WHEN** las ofertas no alcanzan el límite
- **THEN** se completan con los productos disponibles más recientes que no estén ya incluidos

#### Scenario: Sin repeticiones

- **WHEN** un producto con oferta también es reciente
- **THEN** aparece una sola vez en destacados

#### Scenario: Límite

- **WHEN** hay más de ocho productos candidatos
- **THEN** se devuelven como máximo ocho

### Requirement: Ofertas de la galería

El sistema SHALL devolver hasta ocho productos disponibles con precio de oferta, ordenados por fecha de creación descendente.

#### Scenario: Productos con oferta

- **WHEN** existen productos con precio de oferta
- **THEN** se devuelven en la sección de ofertas

#### Scenario: Sin ofertas

- **WHEN** no hay productos con oferta
- **THEN** la sección se devuelve vacía

#### Scenario: Solo ofertas disponibles

- **WHEN** un producto con oferta está eliminado, inactivo o su local está inactivo
- **THEN** no aparece en la sección

### Requirement: Categorías con conteo

El sistema SHALL devolver todas las categorías con la cantidad de productos disponibles asociados a cada una.

#### Scenario: Conteo correcto

- **WHEN** una categoría tiene productos disponibles
- **THEN** la respuesta incluye la cantidad correspondiente

#### Scenario: Categoría vacía

- **WHEN** una categoría no tiene productos disponibles
- **THEN** se devuelve con conteo cero

#### Scenario: Productos no disponibles

- **WHEN** un producto está eliminado, inactivo o su local está inactivo
- **THEN** no se cuenta en la categoría

### Requirement: Locales en la portada

El sistema SHALL devolver hasta seis locales activos, ordenados por número, con su información básica.

#### Scenario: Selección de locales

- **WHEN** existen locales activos
- **THEN** se devuelven hasta seis ordenados por número

#### Scenario: Local inactivo

- **WHEN** un local está inactivo
- **THEN** no aparece en la selección

### Requirement: Listado público de locales

El sistema SHALL exponer un listado público de todos los locales activos ordenados por número, con identificador, número, nombre, descripción y logo.

#### Scenario: Listado completo

- **WHEN** un visitante consulta el listado de locales
- **THEN** recibe todos los locales activos ordenados por número

#### Scenario: Sin datos internos

- **WHEN** se devuelve el listado
- **THEN** no incluye estado interno, cuentas, productos ni datos de administración

### Requirement: Navegación de la exploración

La interfaz de exploración SHALL permitir acceder al detalle de productos y locales, y al buscador filtrado por categoría u ofertas.

#### Scenario: Producto destacado

- **WHEN** el visitante selecciona un producto
- **THEN** navega a `/productos/{id}`

#### Scenario: Local

- **WHEN** el visitante selecciona un local
- **THEN** navega a `/locales/{id}`

#### Scenario: Categoría

- **WHEN** el visitante selecciona una categoría
- **THEN** navega al buscador filtrado por esa categoría

#### Scenario: Todas las ofertas

- **WHEN** el visitante selecciona "Ver todas las ofertas"
- **THEN** navega al buscador con `has_offer=true`

#### Scenario: Todos los productos

- **WHEN** el visitante selecciona "Ver todos los productos"
- **THEN** navega al buscador sin filtros

#### Scenario: Todos los locales

- **WHEN** el visitante selecciona "Ver todos los locales"
- **THEN** navega a `/locales`

### Requirement: Estados de la exploración

La interfaz SHALL mostrar estados de carga y error, y SHALL manejar secciones vacías sin romper la página.

#### Scenario: Carga

- **WHEN** la exploración está pendiente
- **THEN** la interfaz muestra un estado de carga

#### Scenario: Error

- **WHEN** la consulta falla
- **THEN** la interfaz muestra un mensaje de error sin romper la página

#### Scenario: Sección vacía

- **WHEN** no hay ofertas o locales
- **THEN** la sección correspondiente no se muestra o indica que está vacía
