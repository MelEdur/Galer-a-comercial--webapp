# Spec Delta

## ADDED Requirements

### Requirement: Volver al origen en el detalle de producto

El detalle público de producto SHALL ofrecer un botón “Volver” que regrese a la página de origen y, si no existe historial interno, a la página principal.

#### Scenario: Origen interno

- **WHEN** el visitante llega desde el buscador, el catálogo de un local u otra página interna y selecciona “Volver”
- **THEN** regresa a esa página de origen

#### Scenario: Entrada directa

- **WHEN** el visitante abre el detalle directamente por URL y selecciona “Volver”
- **THEN** navega a `/`

#### Scenario: Etiqueta accesible

- **WHEN** el botón se muestra
- **THEN** su texto es “Volver” y es operable con teclado
