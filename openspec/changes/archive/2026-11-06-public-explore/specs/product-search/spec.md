# Spec Delta

## ADDED Requirements

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
