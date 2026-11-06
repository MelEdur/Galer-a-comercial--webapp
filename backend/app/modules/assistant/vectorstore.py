"""Persistent ChromaDB client and knowledge collection."""

from __future__ import annotations

import logging
import threading
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class VectorStoreUnavailableError(Exception):
    """The ChromaDB store or its collection cannot be used."""


_lock = threading.Lock()
_client: Any | None = None
_collection: Any | None = None


def reset_vectorstore() -> None:
    """Drop the cached client and collection; intended for tests."""
    global _client, _collection
    with _lock:
        _client = None
        _collection = None


def get_client() -> Any:
    """Return the process-wide persistent ChromaDB client."""
    global _client

    if _client is not None:
        return _client

    with _lock:
        if _client is not None:
            return _client

        try:
            import chromadb

            _client = chromadb.PersistentClient(path=settings.chroma_path)
        except Exception as exc:
            logger.warning(
                "No se pudo abrir ChromaDB (%s)", type(exc).__name__
            )
            raise VectorStoreUnavailableError(
                "El índice del asistente no está disponible."
            ) from exc

    return _client


def get_collection() -> Any:
    """Return the knowledge collection, creating it on first use."""
    global _collection

    if _collection is not None:
        return _collection

    client = get_client()

    with _lock:
        if _collection is not None:
            return _collection

        try:
            _collection = client.get_or_create_collection(
                name=settings.assistant_collection,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception as exc:
            logger.warning(
                "No se pudo abrir la colección del asistente (%s)",
                type(exc).__name__,
            )
            raise VectorStoreUnavailableError(
                "El índice del asistente no está disponible."
            ) from exc

    return _collection
