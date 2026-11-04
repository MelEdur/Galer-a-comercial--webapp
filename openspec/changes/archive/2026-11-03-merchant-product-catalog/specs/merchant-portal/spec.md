# Spec Delta

## MODIFIED Requirements

### Requirement: Panel del comerciante

La aplicación frontend SHALL ofrecer una ruta protegida para el comerciante que muestre su identidad y los datos de su local, SHALL permitir cerrar sesión y SHALL enlazar al catálogo de productos de su local.

#### Scenario: Acceso al panel

- **WHEN** un comerciante autenticado accede a `/comerciante`
- **THEN** el panel muestra su nombre, correo, número y nombre del local

#### Scenario: Cierre de sesión

- **WHEN** el comerciante cierra sesión desde el panel
- **THEN** el token se elimina y se vuelve a la página de login

#### Scenario: Funcionalidades futuras

- **WHEN** el comerciante accede al panel
- **THEN** las secciones de información del local y estadísticas aparecen como no disponibles, sin ejecutar operaciones de esos casos de uso

#### Scenario: Acceso al catálogo

- **WHEN** el comerciante accede al panel
- **THEN** la sección de productos enlaza a la administración de su catálogo
