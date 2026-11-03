# Spec Delta

## MODIFIED Requirements

### Requirement: Asignación de comerciantes a locales

El sistema SHALL exigir que toda cuenta con rol `merchant` tenga un local asignado, SHALL impedir que una cuenta `admin` tenga local y SHALL permitir como máximo un comerciante activo por local.

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

- **WHEN** se intenta registrar un segundo comerciante activo para un local que ya tiene uno activo
- **THEN** la operación falla por violar la unicidad de comerciante activo por local

#### Scenario: Reasignación después de una baja

- **WHEN** el único comerciante de un local está inactivo y se registra un nuevo comerciante activo para ese local
- **THEN** la operación se completa correctamente
