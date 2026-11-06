# Propuesta

## Why

El CU #11 pide un asistente virtual informativo para visitantes: consultas en lenguaje natural sobre la galería, sus locales, categorías y el uso de la aplicación. La aplicación ya resuelve búsqueda, detalle, locales y mapa, pero no ofrece orientación conversacional ni una base de conocimiento consultable.

El asistente debe ser una guía informativa con RAG, no un buscador alternativo. Cuando la consulta requiera productos, precios, stock o locales que vendan algo, debe ofrecer abrir el buscador existente; cuando requiera ubicación, ofrecer el mapa.

## What Changes

- Se añade `POST /api/public/assistant/chat`, público, con respuesta informativa y acciones sugeridas.
- Se crea el módulo `app/modules/assistant/` con recuperación, generación, clasificación de intención e indexación.
- Se usa Groq para el chat, seleccionando automáticamente un modelo de chat disponible y evitando modelos de código.
- Se usan embeddings multilingües locales con `sentence-transformers` y ChromaDB embebido con volumen persistente.
- Se crea `knowledge/galeria.md` como fuente estática de ingesta y se generan documentos por local desde la base.
- Se añade un script de reindexación completa y por local.
- Se dispara una reindexación best-effort del local al guardarlo desde CU #9, sin bloquear el guardado.
- Se añade un widget flotante de chat en las páginas públicas.
- Se añaden límites de mensaje, historial, rate limit y manejo de errores.
- Se documentan variables de entorno, volúmenes y el procedimiento de ingesta.

### Alcance

- Asistente informativo con RAG en español.
- Base de conocimiento estática y documentos dinámicos de locales.
- Clasificación de intención y derivación al buscador o al mapa.
- Widget público con historial en cliente.
- Actualización del conocimiento por CLI y al guardar un local.
- Pruebas de backend y frontend con proveedores simulados.

### Fuera de alcance

- Buscar productos, precios, stock o disponibilidad desde el asistente.
- Reemplazar el buscador, el feed, el detalle o el mapa.
- Compras, reservas o modificación de datos.
- Autenticación de visitantes o persistencia de conversaciones en base.
- Analíticas de uso del asistente.
- Streaming de respuestas.
- Indexar productos individuales ni precios.
- Aprendizaje o fine-tuning de modelos.

## Capabilities

### New Capabilities

- `gallery-assistant`: asistente público informativo con RAG, límites de alcance, derivaciones al buscador y al mapa, base de conocimiento e índice vectorial.

### Modified Capabilities

Ninguna. La reindexación al guardar un local es un efecto no bloqueante implementado en el nuevo módulo; el contrato de CU #9 (guardar el local) no cambia y el guardado sigue siendo exitoso aunque la indexación falle.

## Impact

- **Backend nuevo:** `app/modules/assistant/` (router, schemas, servicio, recuperación, intención, indexación y conocimiento), `scripts/reindex_assistant.py`.
- **Backend modificado:** `app/core/config.py` (Groq, assistant, Chroma), `app/main.py` (router), `app/modules/merchant_store/service.py` (hook best-effort).
- **Frontend nuevo:** `features/assistant/` (widget, panel, mensajes, acciones) y montaje en `App`.
- **Frontend modificado:** `App.tsx` o el layout público para mostrar el widget fuera de rutas privadas.
- **Dependencias nuevas:** `langchain-groq`, `langchain-huggingface`, `langchain-chroma`, `langchain-text-splitters`, `chromadb`, `sentence-transformers`.
- **Infraestructura:** volúmenes `chroma_data` y `hf_cache`; variables `GROQ_API_KEY`, `GROQ_MODEL`, `GROQ_MODEL_PREFERENCES`, `CHROMA_PATH`, `HF_HOME` y límites del asistente.
- **Sin migraciones de base de datos.**
- **Funcionalidades existentes:** búsqueda, exploración, detalle, locales, mapa, CU #6-#10, autenticación y health check no cambian de comportamiento.
- **Dependencias:** `product-search`, `product-detail`, `store-detail`, `store-map` y `merchant-store-settings`.

## Decisiones adoptadas

- Proveedor de chat: Groq con `GROQ_API_KEY`; la clave vive solo en el backend.
- Selección automática de un modelo de chat disponible; se excluyen modelos de código (`coder`, `code`), audio (`whisper`, `tts`, `orpheus`) y embeddings.
- Lista de preferencia configurable con modelos de chat disponibles: `openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `qwen/qwen3.8-27b`; si ninguno está disponible, se usa otro modelo de chat válido o se responde `503`.
- Embeddings locales multilingües: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
- ChromaDB embebido con `PersistentClient` y volumen Docker.
- LangChain mínimo: chat, embeddings, splitter y Chroma; sin agentes ni cadenas complejas.
- Historial de conversación en el cliente, máximo 10 mensajes.
- Derivaciones con acción estructurada y confirmación en el frontend.
- Reindexación automática best-effort al guardar un local; CLI para reindexar todo o un local.
- Límites: 1000 caracteres por mensaje, 10 mensajes de historial, top-5 documentos, rate limit por IP y timeout del proveedor.
- No se indexan productos, precios ni stock.

## Nota de seguridad

La clave de Groq compartida por chat debe considerarse expuesta. Se configura en `.env` (ignorado por Git) y se recomienda rotarla después de las pruebas. No se versiona ni se envía al frontend.
