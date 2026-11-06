# Spec Delta

## Purpose

Define el asistente virtual público de la galería: consultas informativas con RAG, límites de alcance, derivaciones al buscador y al mapa, base de conocimiento, actualización del índice y widget de conversación.

## ADDED Requirements

### Requirement: Asistente público

El sistema SHALL ofrecer un asistente virtual accesible para visitantes sin autenticación.

#### Scenario: Visitante anónimo

- **WHEN** un visitante sin sesión envía una consulta al asistente
- **THEN** la respuesta es `200` con una contestación informativa o una acción sugerida

#### Scenario: Sin datos internos

- **WHEN** el asistente responde
- **THEN** no expone credenciales, claves, configuración interna ni datos de cuentas

### Requirement: Respuestas basadas en la base de conocimiento

El asistente SHALL responder en español usando exclusivamente información recuperada de la base de conocimiento y SHALL reconocer cuando no dispone de información suficiente.

#### Scenario: Consulta informativa con contexto

- **WHEN** la consulta se relaciona con información presente en la base
- **THEN** la respuesta se fundamenta en los documentos recuperados e incluye las fuentes usadas

#### Scenario: Consulta sin contexto suficiente

- **WHEN** no se recuperan documentos relevantes o el contexto no alcanza
- **THEN** el asistente indica que no tiene información suficiente y no inventa datos

#### Scenario: Tono y idioma

- **WHEN** el asistente responde
- **THEN** lo hace en español, con un tono claro y cordial

### Requirement: Alcance informativo del asistente

El asistente SHALL NOT buscar productos, consultar precios, verificar stock ni identificar locales que vendan un producto específico.

#### Scenario: Consulta de producto

- **WHEN** el visitante pregunta dónde comprar un producto, su precio o su disponibilidad
- **THEN** el asistente no responde con datos de productos y ofrece derivar al buscador

#### Scenario: Consulta de precio o stock

- **WHEN** la consulta pide un precio, stock o disponibilidad concreta
- **THEN** el asistente explica que esa información se consulta en el buscador o en la ficha del producto

#### Scenario: Sin datos de productos indexados

- **WHEN** se construye la base de conocimiento
- **THEN** no se indexan productos individuales, precios ni stock

### Requirement: Derivación al buscador

El asistente SHALL ofrecer una acción de búsqueda cuando la consulta requiera buscar productos, y SHALL preguntar antes de abrirla.

#### Scenario: Oferta de búsqueda

- **WHEN** la consulta requiere buscar un producto
- **THEN** la respuesta incluye una acción `search` con el término propuesto y un mensaje que pregunta si desea abrir el buscador

#### Scenario: Confirmación en el frontend

- **WHEN** el visitante confirma la acción
- **THEN** el frontend navega a `/buscar?search={término}`

#### Scenario: Sin ejecución automática

- **WHEN** el asistente detecta una consulta de producto
- **THEN** no ejecuta la búsqueda ni devuelve resultados de productos por sí mismo

### Requirement: Derivación al mapa

El asistente SHALL ofrecer una acción para abrir el mapa cuando la consulta requiera ubicar un local.

#### Scenario: Oferta de mapa

- **WHEN** la consulta pide cómo llegar o dónde se ubica un local
- **THEN** la respuesta incluye una acción `map` con destino `/mapa`

#### Scenario: Confirmación

- **WHEN** el visitante confirma la acción del mapa
- **THEN** el frontend navega a `/mapa`

### Requirement: Consultas fuera de alcance

El asistente SHALL explicar qué tipos de consultas puede resolver cuando la pregunta está fuera de su alcance.

#### Scenario: Consulta no soportada

- **WHEN** la consulta no es informativa, de búsqueda ni de ubicación
- **THEN** el asistente describe brevemente sus capacidades y no inventa una respuesta

### Requirement: Contexto de la conversación

El sistema SHALL aceptar un historial de conversación enviado por el cliente, limitado a los últimos diez mensajes, y SHALL usarlo para mantener el hilo.

#### Scenario: Continuidad

- **WHEN** el visitante envía un mensaje con historial previo
- **THEN** el asistente considera ese historial para interpretar la consulta

#### Scenario: Límite de historial

- **WHEN** el historial supera diez mensajes
- **THEN** el backend usa solo los últimos diez

#### Scenario: Sin persistencia en servidor

- **WHEN** finaliza una petición
- **THEN** el backend no almacena la conversación

### Requirement: Base de conocimiento

El sistema SHALL construir la base de conocimiento a partir de un documento Markdown estático y de documentos descriptivos por local, sin incluir productos individuales.

#### Scenario: Documento estático

- **WHEN** se indexa la base
- **THEN** se incluye el contenido de `knowledge/galeria.md`

#### Scenario: Documentos de locales

- **WHEN** se indexa la base
- **THEN** cada local activo aporta un documento con número, nombre, descripción, contacto, horarios, enlaces y categorías comerciales

#### Scenario: Sin productos

- **WHEN** se indexa un local
- **THEN** no se incluyen sus productos, precios ni stock

### Requirement: Actualización del índice

El sistema SHALL permitir reindexar toda la base o un local, y SHALL actualizar el documento del local al guardarlo desde CU #9 sin bloquear el guardado.

#### Scenario: Reindexación completa

- **WHEN** se ejecuta el comando de reindexación
- **THEN** se actualizan los documentos estáticos y de todos los locales

#### Scenario: Reindexación de un local

- **WHEN** se ejecuta el comando con un identificador de local
- **THEN** solo se actualiza el documento de ese local

#### Scenario: Guardado de un local

- **WHEN** el comerciante guarda la información de su local
- **THEN** el guardado responde correctamente y la reindexación se intenta en segundo plano

#### Scenario: Fallo de reindexación

- **WHEN** la reindexación falla después de guardar
- **THEN** el guardado no se revierte y el fallo queda registrado

### Requirement: Selección del modelo de chat

El sistema SHALL usar Groq y SHALL seleccionar un modelo destinado a chat, excluyendo modelos de generación de código, audio o embeddings.

#### Scenario: Modelo preferido

- **WHEN** hay un modelo de la lista de preferencia disponible
- **THEN** se usa ese modelo

#### Scenario: Exclusión de modelos de código

- **WHEN** se evalúan modelos disponibles
- **THEN** se descartan los identificadores de modelos de código

#### Scenario: Sin modelos disponibles

- **WHEN** no hay ningún modelo de chat disponible
- **THEN** el asistente responde `503` con un mensaje claro

### Requirement: Límites y protección del endpoint

El sistema SHALL limitar la longitud del mensaje, el historial, el uso por IP y el tiempo de espera del proveedor.

#### Scenario: Mensaje demasiado largo

- **WHEN** el mensaje supera los 1000 caracteres
- **THEN** la respuesta es `422`

#### Scenario: Rate limit

- **WHEN** un visitante supera el límite de consultas por ventana
- **THEN** la respuesta es `429`

#### Scenario: Proveedor no disponible

- **WHEN** Groq falla, expira el tiempo de espera o no hay clave configurada
- **THEN** la respuesta es `503` con un mensaje comprensible

### Requirement: Widget del asistente en el frontend

La interfaz SHALL mostrar un widget flotante en las páginas públicas, con conversación, entrada, estado de carga, errores y botones de acción.

#### Scenario: Abrir y cerrar

- **WHEN** el visitante usa el botón flotante
- **THEN** el panel del asistente se abre o se cierra

#### Scenario: Enviar mensaje

- **WHEN** el visitante envía una consulta
- **THEN** se muestra su mensaje, un estado de carga y luego la respuesta

#### Scenario: Acción sugerida

- **WHEN** la respuesta incluye una acción `search` o `map`
- **THEN** el widget muestra un botón que navega al destino al confirmarlo

#### Scenario: Rutas privadas

- **WHEN** el visitante está en `/admin`, `/comerciante` o `/login`
- **THEN** el widget no se muestra

#### Scenario: Error

- **WHEN** la consulta falla
- **THEN** el widget muestra un mensaje de error sin perder la conversación
