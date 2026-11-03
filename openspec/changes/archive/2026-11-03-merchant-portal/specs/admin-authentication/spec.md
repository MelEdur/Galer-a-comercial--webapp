# Spec Delta

## MODIFIED Requirements

### Requirement: Identidad de la sesión

El sistema SHALL exponer la identidad de la cuenta autenticada con su identificador, correo, nombre completo, rol y, cuando la cuenta tenga un local asignado, los datos de ese local.

#### Scenario: Consulta de identidad

- **WHEN** una cuenta autenticada consulta su identidad
- **THEN** la respuesta incluye su identificador, correo, nombre completo y rol

#### Scenario: Token inválido o vencido

- **WHEN** se consulta la identidad con un token inválido, alterado o vencido
- **THEN** la respuesta es `401`

#### Scenario: Comerciante con local asignado

- **WHEN** una cuenta con rol `merchant` consulta su identidad
- **THEN** la respuesta incluye el identificador, número y nombre de su local

#### Scenario: Cuenta sin local

- **WHEN** una cuenta sin local asignado, como un administrador, consulta su identidad
- **THEN** la respuesta indica que no tiene local
