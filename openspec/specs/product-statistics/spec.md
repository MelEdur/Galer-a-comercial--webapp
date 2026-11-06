# product-statistics Specification

## Purpose
Define las estadísticas de productos más buscados del local propio: acceso del comerciante, períodos, conteos, productos eliminados, ranking y presentación en el panel.

## Requirements

### Requirement: Acceso a las estadísticas del local

El sistema SHALL permitir consultar las estadísticas únicamente a cuentas activas con rol `merchant` y SHALL limitar los datos a los productos de su local.

#### Scenario: Comerciante autorizado

- **WHEN** un comerciante activo consulta sus estadísticas
- **THEN** recibe únicamente datos de los productos de su local

#### Scenario: Administrador

- **WHEN** una cuenta con rol `admin` accede a las estadísticas del comerciante
- **THEN** la respuesta es `403`

#### Scenario: Sin autenticación

- **WHEN** se accede sin token
- **THEN** la respuesta es `401`

#### Scenario: Comerciante sin local

- **WHEN** una cuenta de comerciante no tiene local asignado
- **THEN** la respuesta es `403`

#### Scenario: Local derivado de la sesión

- **WHEN** se consultan las estadísticas
- **THEN** el local se obtiene de la cuenta autenticada y no de un identificador enviado por el cliente

### Requirement: Fuente de las estadísticas

El sistema SHALL calcular las estadísticas a partir de los eventos de búsqueda registrados por CU #1, contando un evento por cada producto visible en la página devuelta cuando la búsqueda tiene criterios.

#### Scenario: Búsqueda con criterios

- **WHEN** una búsqueda con criterios devuelve productos
- **THEN** cada producto de la página tiene un evento asociado

#### Scenario: Exploración sin búsqueda

- **WHEN** el visitante explora sin criterios
- **THEN** no se generan eventos que afecten las estadísticas

#### Scenario: Consultar estadísticas no registra búsquedas

- **WHEN** el comerciante consulta sus estadísticas
- **THEN** no se crean nuevos eventos de búsqueda

### Requirement: Período de consulta

El sistema SHALL admitir períodos predefinidos de 7, 30 y 90 días, y un rango personalizado con fecha desde y hasta, interpretados en la zona horaria de Buenos Aires.

#### Scenario: Período predefinido

- **WHEN** el comerciante solicita 7, 30 o 90 días
- **THEN** se incluyen los eventos del período correspondiente hasta el día actual

#### Scenario: Rango personalizado

- **WHEN** el comerciante envía fecha desde y hasta
- **THEN** se incluyen los eventos de ambos días inclusive

#### Scenario: Período por defecto

- **WHEN** no se envía período
- **THEN** se usan los últimos 30 días

#### Scenario: Rango inválido

- **WHEN** la fecha desde es posterior a la hasta o falta uno de los extremos
- **THEN** la respuesta es `422`

#### Scenario: Parámetros excluyentes

- **WHEN** se envían días y fechas a la vez
- **THEN** la respuesta es `422`

#### Scenario: Límite del día local

- **WHEN** un evento ocurre cerca de la medianoche de Buenos Aires
- **THEN** se asigna al día local correspondiente y no al día UTC

### Requirement: Ranking de productos más buscados

El sistema SHALL devolver hasta diez productos con al menos una búsqueda en el período, ordenados por cantidad descendente y nombre ascendente, con el conteo y la última búsqueda de cada uno.

#### Scenario: Conteo por producto

- **WHEN** un producto recibió varias búsquedas en el período
- **THEN** la respuesta incluye la cantidad total de eventos de ese producto

#### Scenario: Orden del ranking

- **WHEN** hay productos con distintas cantidades
- **THEN** se ordenan de mayor a menor cantidad

#### Scenario: Empate

- **WHEN** dos productos tienen la misma cantidad
- **THEN** se ordenan por nombre ascendente

#### Scenario: Límite

- **WHEN** hay más de diez productos con búsquedas
- **THEN** se devuelven como máximo diez

#### Scenario: Productos sin búsquedas

- **WHEN** un producto del local no tuvo búsquedas en el período
- **THEN** no aparece en el ranking

#### Scenario: Total del período

- **WHEN** se devuelve el ranking
- **THEN** la respuesta incluye el total de eventos del local en el período, no solo los del Top 10

### Requirement: Productos eliminados en el ranking

El sistema SHALL incluir los productos eliminados lógicamente que tuvieron búsquedas en el período y SHALL marcarlos como eliminados.

#### Scenario: Producto eliminado con búsquedas

- **WHEN** un producto fue eliminado después de recibir búsquedas
- **THEN** aparece en el ranking con la marca de eliminado y su conteo histórico

#### Scenario: Producto de otro local

- **WHEN** un producto con búsquedas pertenece a otro local
- **THEN** no aparece en el ranking del comerciante

### Requirement: Presentación de estadísticas en el panel

La interfaz SHALL ofrecer una ruta protegida con selector de período, tabla del Top 10, conteos, última búsqueda y barras proporcionales, y SHALL enlazarla desde el panel del comerciante.

#### Scenario: Acceso desde el panel

- **WHEN** el comerciante accede a su panel
- **THEN** la sección de estadísticas enlaza a la página de estadísticas

#### Scenario: Selección de período

- **WHEN** el comerciante elige 7, 30 o 90 días, o un rango personalizado
- **THEN** la tabla se actualiza con los datos del período

#### Scenario: Visualización del ranking

- **WHEN** hay resultados
- **THEN** se muestran posición, nombre, cantidad, barra proporcional y última búsqueda

#### Scenario: Producto eliminado

- **WHEN** un producto del ranking está eliminado
- **THEN** la interfaz muestra una marca visible

#### Scenario: Sin búsquedas

- **WHEN** no hay eventos en el período
- **THEN** la interfaz muestra un estado vacío explicativo

#### Scenario: Error de consulta

- **WHEN** la consulta falla
- **THEN** la interfaz muestra un mensaje de error sin romper la página

### Requirement: Autorización en la interfaz de estadísticas

La interfaz SHALL redirigir o denegar el acceso a la página de estadísticas cuando la sesión no sea de un comerciante.

#### Scenario: Sesión no válida

- **WHEN** no hay sesión válida
- **THEN** la interfaz redirige al login

#### Scenario: Rol no autorizado

- **WHEN** una cuenta sin rol comerciante accede a la ruta
- **THEN** la interfaz redirige a su panel o muestra acceso denegado sin exponer datos
