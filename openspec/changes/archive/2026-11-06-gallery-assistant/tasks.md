# Tasks

## 1. Dependencias, configuración e infraestructura

- [x] 1.1 Añadir `langchain-groq`, `langchain-huggingface`, `langchain-chroma`, `langchain-text-splitters`, `chromadb` y `sentence-transformers` a `backend/requirements.txt`.
- [x] 1.2 Añadir las variables del asistente a `Settings` y a `.env.example`: Groq, modelo y preferencias, top-k, límites, Chroma y HF.
- [x] 1.3 Añadir los volúmenes `chroma_data` y `hf_cache` y las variables `CHROMA_PATH`/`HF_HOME` al backend en `docker-compose.yml`.
- [x] 1.4 Añadir `.chroma/` y rutas locales de caché a `.gitignore`.

## 2. Módulo del asistente

- [x] 2.1 Crear `app/modules/assistant/` con `__init__.py`, `schemas.py`, `service.py`, `retrieval.py`, `intent.py`, `indexing.py` y `router.py`.
- [x] 2.2 Implementar los schemas de mensaje, historial, acción, fuentes y respuesta.
- [x] 2.3 Implementar la selección del modelo de chat de Groq con preferencias, exclusión de modelos de código/audio/embeddings, caché y error `503`.
- [x] 2.4 Registrar el router público en `app/main.py`.

## 3. Embeddings, Chroma e ingesta

- [x] 3.1 Implementar el singleton de embeddings multilingües y el cliente Chroma persistente.
- [x] 3.2 Crear la colección `gallery_assistant` con los metadatos definidos.
- [x] 3.3 Implementar la carga y el chunking del Markdown estático.
- [x] 3.4 Generar documentos por local activo con datos generales, contacto, horarios, enlaces y categorías, sin productos.
- [x] 3.5 Implementar el upsert idempotente por IDs deterministas y la eliminación de fragmentos obsoletos por origen.
- [x] 3.6 Crear `scripts/reindex_assistant.py` con reindexación completa y `--store-id`.

## 4. RAG y comportamiento

- [x] 4.1 Implementar la clasificación de intención con salida estructurada: informativa, búsqueda, mapa o fuera de alcance.
- [x] 4.2 Implementar la recuperación top-k y la construcción de contexto con fuentes.
- [x] 4.3 Implementar la respuesta informativa con prompt en español, temperatura 0 y respuesta de falta de información.
- [x] 4.4 Implementar la acción `search` con confirmación y sin ejecutar búsquedas.
- [x] 4.5 Implementar la acción `map`.
- [x] 4.6 Implementar el manejo de consultas fuera de alcance y la descripción de capacidades.
- [x] 4.7 Implementar el endpoint `POST /api/public/assistant/chat` con validación de mensaje e historial.

## 5. Límites y actualización automática

- [x] 5.1 Implementar el rate limit por IP en memoria y los límites de longitud, historial y timeout.
- [x] 5.2 Implementar el manejo de `429`, errores de Groq, errores de Chroma/embeddings y `503`.
- [x] 5.3 Añadir la `BackgroundTask` de reindexación del local después de guardar en CU #9, con manejo de errores que no revierta el guardado.
- [x] 5.4 Verificar que un fallo de reindexación no afecta la respuesta de guardado.

## 6. Pruebas del backend

- [x] 6.1 Probar el endpoint público y el contrato de respuesta.
- [x] 6.2 Probar consulta informativa con contexto y fuentes.
- [x] 6.3 Probar falta de contexto y respuesta sin invención.
- [x] 6.4 Probar consulta de producto: acción `search`, sin datos de productos y sin ejecución.
- [x] 6.5 Probar consulta de ubicación: acción `map`.
- [x] 6.6 Probar consulta fuera de alcance.
- [x] 6.7 Probar historial limitado a 10 mensajes y mensaje de más de 1000 caracteres.
- [x] 6.8 Probar rate limit `429` y errores del proveedor `503`.
- [x] 6.9 Probar selección de modelo de chat, exclusión de modelos de código y ausencia de modelos.
- [x] 6.10 Probar ingesta: documento estático, documentos de local, ausencia de productos, upsert idempotente y reindexación por local.
- [x] 6.11 Probar que guardar un local no falla si la reindexación falla.
- [x] 6.12 Usar dobles de LLM/embeddings y Chroma efímero; no llamar a Groq en tests.
- [x] 6.13 Mantener las pruebas existentes pasando.

## 7. Frontend

- [x] 7.1 Crear `features/assistant/` con tipos, cliente API, widget, panel, lista de mensajes y botón de acción.
- [x] 7.2 Montar el widget en las rutas públicas y ocultarlo en `/admin`, `/comerciante` y `/login`.
- [x] 7.3 Implementar apertura/cierre, envío, estado de carga y errores.
- [x] 7.4 Mantener el historial en el estado del componente y enviar los últimos 10 mensajes.
- [x] 7.5 Implementar las acciones `search` y `map` con navegación al confirmar.
- [x] 7.6 Implementar accesibilidad: diálogo, `aria-live`, foco y Escape.

## 8. Pruebas del frontend

- [x] 8.1 Probar abrir/cerrar el widget.
- [x] 8.2 Probar el envío y la visualización de la respuesta.
- [x] 8.3 Probar la acción de búsqueda y la navegación a `/buscar?search=...`.
- [x] 8.4 Probar la acción de mapa y la navegación a `/mapa`.
- [x] 8.5 Probar carga, error y conservación de la conversación.
- [x] 8.6 Probar que el widget no aparece en rutas privadas.
- [x] 8.7 Ejecutar `npm test -- --run` y `npm run build`.

## 9. Integración y verificación

- [x] 9.1 Ejecutar la reindexación inicial y verificar Chroma persistente.
- [x] 9.2 Probar una consulta informativa real con Groq.
- [x] 9.3 Probar una consulta de producto y confirmar que solo ofrece el buscador.
- [x] 9.4 Probar una consulta de ubicación y confirmar la acción del mapa.
- [x] 9.5 Guardar un local desde CU #9 y verificar la reindexación en segundo plano.
- [x] 9.6 Verificar el rate limit y el mensaje ante fallos del proveedor.
- [x] 9.7 Validar el cambio con `openspec validate gallery-assistant --strict` y registrar los resultados.

## Workflow follow-up

- Revisar y archivar después de la verificación.
- No indexar productos, precios ni stock.
- No implementar streaming, analíticas ni persistencia de conversaciones.
