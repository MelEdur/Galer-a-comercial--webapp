# Spec Delta

## MODIFIED Requirements

### Requirement: Cuentas de usuario

El sistema SHALL almacenar cuentas con correo único, nombre completo, hash de contraseña, rol (`admin` o `merchant`) y estado activo, y SHALL NOT almacenar contraseñas en texto plano.

#### Scenario: Correo duplicado

- **WHEN** se intenta registrar una cuenta con un correo ya existente, sin distinguir mayúsculas
- **THEN** la operación falla por violar la unicidad del correo

#### Scenario: Rol inválido

- **WHEN** se intenta registrar una cuenta con un rol distinto de `admin` o `merchant`
- **THEN** la operación falla por violar la restricción de rol

#### Scenario: Contraseña persistida

- **WHEN** se registra o actualiza una cuenta
- **THEN** solo se persiste el hash de la contraseña

#### Scenario: Nombre completo obligatorio

- **WHEN** se intenta registrar una cuenta sin nombre completo
- **THEN** la operación falla por validación
