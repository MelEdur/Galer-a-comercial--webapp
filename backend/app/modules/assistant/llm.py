"""Groq chat access and dynamic chat-model selection.

Heavy provider dependencies are imported lazily so importing the application
(and running the health checks or tests) never requires the Groq SDK or a
downloaded model.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)

MODEL_CACHE_TTL_SECONDS = 60 * 60
MAX_OUTPUT_TOKENS = 500

# Identifiers that are not meant for conversational answers.
_EXCLUDED_MODEL_HINTS = (
    "coder",
    "code",
    "whisper",
    "tts",
    "orpheus",
    "embed",
    "guard",
)

# Hints used to prefer general chat/instruct models over other modalities.
_CHAT_MODEL_HINTS = (
    "instruct",
    "chat",
    "versatile",
    "instant",
    "gpt-oss",
    "qwen",
)


class LLMUnavailableError(Exception):
    """The chat provider is not configured or cannot be reached."""


_cache_lock = threading.Lock()
_cached_model: str | None = None
_cache_expires_at = 0.0


def reset_model_cache() -> None:
    """Clear the cached model; intended for tests and configuration reloads."""
    global _cached_model, _cache_expires_at
    with _cache_lock:
        _cached_model = None
        _cache_expires_at = 0.0


def _is_excluded(model_id: str) -> bool:
    """Return whether the identifier looks like a code/audio/embedding model."""
    lowered = model_id.lower()
    return any(hint in lowered for hint in _EXCLUDED_MODEL_HINTS)


def _list_model_ids() -> list[str]:
    """Return the identifiers reported by the Groq models endpoint."""
    try:
        from groq import Groq
    except ImportError as exc:  # pragma: no cover - dependency is declared
        raise LLMUnavailableError(
            "El proveedor de chat no está disponible."
        ) from exc

    try:
        client = Groq(api_key=settings.groq_api_key)
        response = client.models.list()
    except Exception as exc:
        logger.warning(
            "No se pudo consultar la lista de modelos de Groq (%s)",
            type(exc).__name__,
        )
        raise LLMUnavailableError(
            "No se pudo consultar el proveedor de chat."
        ) from exc

    models = getattr(response, "data", None) or []
    return [
        model.id
        for model in models
        if isinstance(getattr(model, "id", None), str) and model.id
    ]


def _select_from_ids(model_ids: list[str]) -> str:
    """Pick a chat model from ``model_ids`` following the configured order."""
    available = [model_id for model_id in model_ids if not _is_excluded(model_id)]
    if not available:
        raise LLMUnavailableError(
            "No hay ningún modelo de chat disponible."
        )

    for preferred in settings.groq_model_preferences_list:
        if preferred in available:
            return preferred

    for model_id in available:
        lowered = model_id.lower()
        if any(hint in lowered for hint in _CHAT_MODEL_HINTS):
            return model_id

    return available[0]


def select_model() -> str:
    """Return the model to use, caching the automatic choice for one hour."""
    global _cached_model, _cache_expires_at

    fixed = settings.groq_model.strip()
    if fixed:
        return fixed

    now = time.monotonic()
    with _cache_lock:
        if _cached_model is not None and now < _cache_expires_at:
            return _cached_model

    model_id = _select_from_ids(_list_model_ids())

    with _cache_lock:
        _cached_model = model_id
        _cache_expires_at = now + MODEL_CACHE_TTL_SECONDS
    return model_id


def get_chat_model() -> Any:
    """Build a ``ChatGroq`` client for the selected model."""
    if not settings.groq_api_key.strip():
        raise LLMUnavailableError(
            "El asistente no tiene configurada la clave del proveedor."
        )

    try:
        from langchain_groq import ChatGroq
    except ImportError as exc:  # pragma: no cover - dependency is declared
        raise LLMUnavailableError(
            "El proveedor de chat no está disponible."
        ) from exc

    return ChatGroq(
        model=select_model(),
        api_key=settings.groq_api_key,
        temperature=0,
        max_tokens=MAX_OUTPUT_TOKENS,
        timeout=settings.assistant_timeout_seconds,
    )


def generate(messages: list[dict[str, str]]) -> str:
    """Send chat messages to Groq and return the plain text answer."""
    try:
        model = get_chat_model()
        result = model.invoke(messages)
    except LLMUnavailableError:
        raise
    except Exception as exc:
        logger.warning(
            "Fallo al invocar el proveedor de chat (%s)", type(exc).__name__
        )
        raise LLMUnavailableError(
            "El proveedor de chat no respondió."
        ) from exc

    content = getattr(result, "content", result)
    if isinstance(content, list):
        parts: list[str] = []
        for part in content:
            if isinstance(part, dict):
                parts.append(str(part.get("text", "")))
            else:
                parts.append(str(part))
        content = "".join(parts)
    return str(content).strip()
