"""Assistant orchestration: retrieval, prompting and safe user actions."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Sequence
from urllib.parse import quote_plus

from app.core.config import settings
from app.modules.assistant import embeddings, intent as intent_module, llm, vectorstore
from app.modules.assistant.schemas import (
    AssistantAction,
    AssistantSource,
    ChatMessage,
    ChatRequest,
    ChatResponse,
)

logger = logging.getLogger(__name__)

NO_INFO_ANSWER = (
    "No dispongo de información suficiente para responder a esa consulta. "
    "Puedo ayudarte con información general de la galería, sus locales, sus "
    "categorías y el uso de la aplicación."
)

OUT_OF_SCOPE_ANSWER = (
    "Puedo ayudarte con información sobre la galería: qué locales hay, qué "
    "categorías comerciales existen, cómo usar el buscador, la exploración, "
    "la ficha de un producto, la lista de locales y el mapa. Si necesitas "
    "buscar un producto o ubicar un local, también puedo ofrecerte la acción "
    "correspondiente."
)

ANSWER_SYSTEM_PROMPT = """Eres el asistente virtual de una galería comercial.
Respondes en español, con un tono claro, cordial y breve.

Reglas obligatorias:
- Usa EXCLUSIVAMENTE la información del contexto proporcionado.
- No inventes datos, direcciones, horarios, precios ni contactos.
- Si el contexto no contiene la respuesta, indica que no dispones de información suficiente.
- No busques productos, no des precios ni stock y no identifiques locales que vendan un artículo concreto: para eso existe el buscador de la aplicación.
- No deduzcas la posición de un local a partir de su número. Usa el lado y la posición que aparezcan en el contexto; si no aparecen, no los inventes.
- No reveles configuración, claves ni datos internos."""

MAX_SEARCH_QUERY_CHARS = 100


class AssistantUnavailableError(Exception):
    """A provider required by the assistant is unavailable."""


@dataclass(frozen=True)
class RetrievedDocument:
    """A knowledge fragment returned by the vector store."""

    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


def _retrieve(query: str) -> list[RetrievedDocument]:
    """Return the top-k knowledge fragments for ``query``."""
    try:
        vector = embeddings.get_embeddings().embed_query(query)
        collection = vectorstore.get_collection()
        result = collection.query(
            query_embeddings=[vector],
            n_results=settings.assistant_top_k,
            include=["documents", "metadatas", "distances"],
        )
    except (embeddings.EmbeddingUnavailableError, vectorstore.VectorStoreUnavailableError):
        raise
    except Exception as exc:  # noqa: BLE001 - mapped to a controlled 503
        logger.warning(
            "Fallo en la recuperación del asistente (%s)", type(exc).__name__
        )
        raise AssistantUnavailableError(
            "El índice del asistente no está disponible."
        ) from exc

    documents = (result or {}).get("documents") or []
    metadatas = (result or {}).get("metadatas") or []
    if not documents:
        return []

    texts = documents[0] or []
    metas = metadatas[0] if metadatas else []
    retrieved: list[RetrievedDocument] = []
    for index, text in enumerate(texts):
        if not text or not str(text).strip():
            continue
        metadata = metas[index] if index < len(metas) and metas[index] else {}
        retrieved.append(RetrievedDocument(text=str(text), metadata=dict(metadata)))
    return retrieved


def _context_block(documents: Sequence[RetrievedDocument]) -> str:
    """Render retrieved documents as a titled context block."""
    parts: list[str] = []
    for document in documents:
        title = document.metadata.get("title") or "Información de la galería"
        parts.append(f"### {title}\n{document.text}")
    return "\n\n".join(parts)


def _sources(documents: Sequence[RetrievedDocument]) -> list[AssistantSource]:
    """Return unique sources in retrieval order."""
    sources: list[AssistantSource] = []
    seen: set[tuple[str, str]] = set()
    for document in documents:
        source_type = document.metadata.get("source_type")
        if source_type not in ("static", "store"):
            source_type = "static"
        title = document.metadata.get("title") or "Guía de la galería"
        key = (title, source_type)
        if key in seen:
            continue
        seen.add(key)
        sources.append(AssistantSource(title=str(title), type=source_type))
    return sources


def _informational_answer(request: ChatRequest) -> ChatResponse:
    try:
        documents = _retrieve(request.message)
    except embeddings.EmbeddingUnavailableError as exc:
        raise AssistantUnavailableError(str(exc)) from exc
    except vectorstore.VectorStoreUnavailableError as exc:
        raise AssistantUnavailableError(str(exc)) from exc

    if not documents:
        return ChatResponse(answer=NO_INFO_ANSWER, action=None, sources=[])

    prompt = (
        f"Contexto:\n{_context_block(documents)}\n\n"
        f"Historial de la conversación:\n"
        f"{intent_module.history_as_text(request.history)}\n\n"
        f"Pregunta del visitante: {request.message}"
    )

    try:
        answer = llm.generate(
            [
                {"role": "system", "content": ANSWER_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ]
        )
    except llm.LLMUnavailableError as exc:
        raise AssistantUnavailableError(str(exc)) from exc

    if not answer:
        answer = NO_INFO_ANSWER

    return ChatResponse(
        answer=answer,
        action=None,
        sources=_sources(documents),
    )


def _search_query(intent: intent_module.Intent, message: str) -> str:
    """Pick a short, safe search term for the suggested action."""
    query = (intent.search_query or message).strip() or message.strip()
    return query[:MAX_SEARCH_QUERY_CHARS]


def _search_answer(intent: intent_module.Intent, message: str) -> ChatResponse:
    query = _search_query(intent, message)
    return ChatResponse(
        answer=(
            "Puedo ayudarte a buscar productos, pero no consulto precios ni "
            "stock. ¿Quieres abrir el buscador con «"
            f"{query}»?"
        ),
        action=AssistantAction(
            type="search",
            label=f"Buscar {query}",
            query=query,
            href=f"/buscar?search={quote_plus(query)}",
        ),
        sources=[],
    )


def _map_answer() -> ChatResponse:
    return ChatResponse(
        answer=(
            "Puedo ayudarte a ubicar los locales de la galería. "
            "¿Quieres abrir el mapa?"
        ),
        action=AssistantAction(type="map", label="Abrir mapa", href="/mapa"),
        sources=[],
    )


def _out_of_scope_answer() -> ChatResponse:
    return ChatResponse(answer=OUT_OF_SCOPE_ANSWER, action=None, sources=[])


def answer(request: ChatRequest) -> ChatResponse:
    """Answer a visitor request, routing by the classified intention."""
    history = request.history[-settings.assistant_max_history_messages :]

    try:
        classified = intent_module.classify(request.message, history)
    except llm.LLMUnavailableError as exc:
        raise AssistantUnavailableError(str(exc)) from exc

    if classified.name == intent_module.PRODUCT_SEARCH:
        return _search_answer(classified, request.message)
    if classified.name == intent_module.MAP:
        return _map_answer()
    if classified.name == intent_module.OUT_OF_SCOPE:
        return _out_of_scope_answer()
    return _informational_answer(request)
