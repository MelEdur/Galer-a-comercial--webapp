"""Lazy singleton for the multilingual sentence-transformers embeddings."""

from __future__ import annotations

import logging
import os
import threading
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingUnavailableError(Exception):
    """The local embedding model cannot be loaded."""


_lock = threading.Lock()
_embeddings: Any | None = None


def reset_embeddings() -> None:
    """Drop the cached model; intended for tests."""
    global _embeddings
    with _lock:
        _embeddings = None


def get_embeddings() -> Any:
    """Return the process-wide ``HuggingFaceEmbeddings`` instance."""
    global _embeddings

    if _embeddings is not None:
        return _embeddings

    with _lock:
        if _embeddings is not None:
            return _embeddings

        if settings.hf_home:
            os.environ.setdefault("HF_HOME", settings.hf_home)

        try:
            from langchain_huggingface import HuggingFaceEmbeddings

            _embeddings = HuggingFaceEmbeddings(
                model_name=settings.assistant_embedding_model
            )
        except Exception as exc:
            logger.warning(
                "No se pudieron cargar los embeddings locales (%s)",
                type(exc).__name__,
            )
            raise EmbeddingUnavailableError(
                "Los embeddings del asistente no están disponibles."
            ) from exc

    return _embeddings
