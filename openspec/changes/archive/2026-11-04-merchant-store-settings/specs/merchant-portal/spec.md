# Spec Delta

## MODIFIED Requirements

### Requirement: Panel del comerciante

La aplicación frontend SHALL ofrecer una ruta protegida para el comerciante que muestre su identidad y los datos de su local, SHALL permitir cerrar sesión y SHALL enlazar al catálogo de productos y a la administración de la información de su local.

#### Scenario: Acceso al panel

- **WHEN** un comerciante autenticado accede a `/comerciante`
- **THEN** el panel muestra su nombre, correo, número y nombre del local

#### Scenario: Cierre de sesión

- **WHEN** el comerciante cierra sesión desde el panel
- **THEN** el token se elimina y se vuelve a la página de login

#### Scenario: Funcionalidades futuras

- **WHEN** el comerciante accede al panel
- **THEN** la sección de estadísticas aparece como no disponible, sin ejecutar operaciones de ese caso de uso

#### Scenario: Acceso al catálogo

- **WHEN** el comerciante accede al panel
- **THEN** la sección de productos enlaza a la administración de su catálogo

#### Scenario: Acceso a la información del local

- **WHEN** el comerciante accede al panel
- **THEN** la sección de información del local enlaza a la administración de los datos de su local
