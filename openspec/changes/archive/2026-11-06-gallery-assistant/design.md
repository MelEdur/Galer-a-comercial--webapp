# Diseño

## Context

Ver `proposal.md` para la motivación y `specs/gallery-assistant/spec.md` para los requisitos. La aplicación ya tiene búsqueda, detalle, locales y mapa. No hay proveedor de IA, embeddings, Chroma ni base de conocimiento. Groq se usa como LLM porque el visitante ya dispone de una clave; Groq no ofrece embeddings, así que se generan localmente.

El proyecto de referencia `~/proyect/rag-chat` usa `langchain-huggingface`, `langchain-chroma`, `langchain-groq` y un splitter recursivo. Se reutiliza ese enfoque, adaptado a FastAPI, Chroma persistente y embeddings multilingües.

## Goals / Non-Goals

**Goals:**

- Asistente informativo sencillo y acotado.
- RAG con documentos estáticos y de locales.
- Derivaciones claras al buscador y al mapa.
- Actualización incremental del índice.
- Protección básica de un endpoint público.

**Non-Goals:**

- Buscar productos, precios o stock.
- Persistir conversaciones o analíticas.
- Streaming, agentes o tool-calling libre.
- Indexar el catálogo de productos.

## Decisions

### 1. Chat con Groq y selección de modelo

- `ChatGroq` de `langchain-groq`, temperatura 0 y máximo de tokens de salida configurable.
- `GROQ_MODEL` permite fijar un modelo.
- Si está vacío, se consulta la lista de modelos de Groq y se elige el primero disponible de `GROQ_MODEL_PREFERENCES`.
- Se excluyen modelos cuyo identificador contenga `coder`, `code`, `whisper`, `tts`, `orpheus`, `embed` o `guard`.
- Se prefieren modelos de chat/instruct (`instruct`, `chat`, `versatile`, `instant`, `gpt-oss`, `qwen`).
- Lista inicial de preferencia: `openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `qwen/qwen3.8-27b`.
- La elección se cachea durante una hora; si no hay candidatos, el endpoint responde `503`.
- Se manejan `429` y timeouts con un mensaje claro.

### 2. Embeddings locales multilingües

- `HuggingFaceEmbeddings` con `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
- El modelo se carga una vez por proceso (singleton) y se cachea en `HF_HOME`.
- Mejor recuperación en español que el `all-MiniLM-L6-v2` de `rag-chat`; el costo es una imagen Docker más grande y una primera descarga.

### 3. ChromaDB embebido

- `chromadb.PersistentClient(path=CHROMA_PATH)` y colección `gallery_assistant`.
- `CHROMA_PATH` por defecto `/data/chroma` en Docker; en local puede apuntar a `backend/.chroma`.
- Volumen Docker `chroma_data` y volumen `hf_cache` para el modelo.
- En pruebas se usa un cliente efímero o un doble de recuperación.

### 4. LangChain mínimo

- `langchain-groq`, `langchain-huggingface`, `langchain-chroma` y `langchain-text-splitters`.
- Sin agentes, sin cadenas de herramientas y sin `langchain-postgres`.
- La lógica de intención, recuperación y composición del prompt vive en el módulo del asistente.

### 5. Pipeline RAG

1. Recibir mensaje e historial.
2. Clasificar intención.
3. Si es informativa:
   - generar el embedding de la consulta;
   - recuperar los 5 documentos más similares;
   - construir el contexto con títulos y contenido;
   - responder con el LLM usando solo ese contexto;
   - devolver las fuentes usadas.
4. Si el contexto es vacío o insuficiente, responder que no hay información suficiente.
5. Si es búsqueda, mapa o fuera de alcance, no se recuperan documentos ni se generan respuestas de producto.

### 6. Clasificación de intención y acciones

Salida estructurada del clasificador:

```json
{"intent": "informational | product_search | map | out_of_scope", "search_query": "texto o null"}
```

- `product_search` → mensaje que pregunta si desea buscar y acción:
  ```json
  {"type": "search", "label": "Buscar auriculares", "query": "auriculares", "href": "/buscar?search=auriculares"}
  ```
- `map` → acción:
  ```json
  {"type": "map", "label": "Abrir mapa", "href": "/mapa"}
  ```
- El backend nunca ejecuta la búsqueda ni devuelve productos.
- El frontend muestra el botón; al confirmarlo navega.

### 7. Base de conocimiento

Documento estático: `app/modules/assistant/knowledge/galeria.md` con:
- qué es la galería;
- guía para visitantes;
- uso de la aplicación;
- categorías comerciales;
- preguntas frecuentes.

Documentos dinámicos: uno por local activo con:
- número, nombre, descripción, contacto, horarios y enlaces;
- categorías comerciales del local.

No se indexan productos, precios ni stock.

Chunking:
- estático: 500 caracteres, 50 de solapamiento, cortando por encabezados y párrafos;
- locales: un único chunk por documento.

Metadatos: `source_type` (`static` o `store`), `source_id`, `title`, `store_id`, `updated_at`.
IDs deterministas: `static:<archivo>:<índice>` y `store:<id>:0`.

### 8. Ingesta y actualización

`scripts/reindex_assistant.py`:
- sin argumentos: reconstruye documentos estáticos y de todos los locales;
- `--store-id N`: actualiza solo ese local;
- realiza upsert por IDs deterministas y elimina fragmentos obsoletos del mismo origen.

Actualización automática:
- el router de CU #9 añade una `BackgroundTask` después de un guardado exitoso;
- la tarea abre su propia sesión, carga el local y actualiza su documento;
- cualquier error se registra y no revierte el guardado.

### 9. Endpoint

`POST /api/public/assistant/chat`:

```json
{
  "message": "¿Cómo encuentro un local?",
  "history": [
    {"role": "user", "content": "Hola"},
    {"role": "assistant", "content": "¡Hola! ¿En qué puedo ayudarte?"}
  ]
}
```

Respuesta:

```json
{
  "answer": "Puedes usar el mapa...",
  "action": null,
  "sources": [{"title": "Guía de la galería", "type": "static"}]
}
```

Validaciones:
- mensaje 1–1000 caracteres;
- historial máximo 10 mensajes;
- roles `user` y `assistant`;
- `422` por validación, `429` por rate limit, `503` por proveedor no disponible.

### 10. Historial y rate limit

- El frontend mantiene los mensajes y envía los últimos 10.
- Sin estado en el servidor ni base de datos de conversaciones.
- Rate limit en memoria por IP: por defecto 20 consultas cada 300 segundos.
- Se documenta que no es distribuido y que se reinicia con el proceso.

### 11. Frontend

- `AssistantWidget` montado dentro del router; visible solo en rutas públicas.
- Botón flotante que abre un panel tipo diálogo.
- Lista de mensajes, entrada, estado de carga y error.
- Acción sugerida como botón; al pulsarlo navega a `href`.
- Historial en estado del componente; se limpia al recargar.
- Sin streaming.
- Accesibilidad: `role="dialog"`, `aria-live="polite"`, cierre con Escape y foco visible.

### 12. Configuración

Variables nuevas:
- `GROQ_API_KEY` (obligatoria para el asistente).
- `GROQ_MODEL` (opcional).
- `GROQ_MODEL_PREFERENCES` (lista separada por comas).
- `ASSISTANT_TOP_K=5`.
- `ASSISTANT_MAX_MESSAGE_CHARS=1000`.
- `ASSISTANT_MAX_HISTORY_MESSAGES=10`.
- `ASSISTANT_RATE_LIMIT=20`.
- `ASSISTANT_RATE_WINDOW_SECONDS=300`.
- `ASSISTANT_TIMEOUT_SECONDS=20`.
- `CHROMA_PATH` y `HF_HOME`.

### 13. Errores

| Caso | Código |
|---|---|
| Mensaje o historial inválido | `422` |
| Rate limit | `429` |
| Groq sin clave, sin modelo o error | `503` |
| Chroma o embeddings no disponibles | `503` |
| Sin contexto suficiente | `200` con respuesta informativa |

## Risks / Trade-offs

- **Modelos gratuitos de Groq** → cambian y tienen límites; selección dinámica, caché y manejo de `429`.
- **Embeddings locales pesados** → PyTorch y descarga inicial; volumen `hf_cache` y primera indexación documentada.
- **Chroma embebido** → no apto para varios workers; el proyecto usa un solo backend.
- **Reindexación en segundo plano** → puede fallar o quedar desactualizada; se registra y existe el CLI.
- **Alucinaciones** → se mitigan con contexto obligatorio, temperatura 0, prompt y respuesta de falta de información.
- **Contenido pendiente** → dirección, horarios generales y contacto de administración dependen del Markdown que aporte el usuario.
- **Sin streaming** → respuestas percibidas como lentas; se acepta para la primera versión.
- **Clave compartida por chat** → debe rotarse; `.env` está ignorado.

## Migration Plan

No hay migraciones de base de datos. Pasos:

1. Añadir dependencias y variables de entorno.
2. Añadir volúmenes `chroma_data` y `hf_cache` a Compose.
3. Reconstruir el backend.
4. Ejecutar la reindexación inicial.
5. Verificar una consulta informativa, una derivación al buscador y una al mapa.

Rollback: retirar el router y el widget; el resto de la aplicación no depende del asistente.

## Open Questions

- Falta el contenido real de la galería (dirección, horarios generales y contacto de administración) para `galeria.md`.
- La lista de modelos gratuitos de Groq puede variar; la preferencia es configurable.
- El modelo de embeddings se descarga en el primer uso; conviene documentar el tiempo.
