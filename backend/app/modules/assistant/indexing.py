"""Knowledge indexing for the assistant (CU #11).

Reindexing replaces the affected sources by their deterministic metadata, so
running it repeatedly is idempotent and removes obsolete fragments.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import SessionLocal
from app.modules.assistant import knowledge
from app.modules.assistant.embeddings import get_embeddings
from app.modules.assistant.vectorstore import get_collection
from app.modules.catalog.models import Product, ProductCategory
from app.modules.stores.models import Store

logger = logging.getLogger(__name__)

_STORE_OPTIONS = (
    selectinload(Store.hours),
    selectinload(Store.links),
    selectinload(Store.products)
    .selectinload(Product.product_categories)
    .selectinload(ProductCategory.category),
)


@dataclass(frozen=True)
class IndexResult:
    """Summary of a full reindex run."""

    static_chunks: int
    stores_indexed: int
    store_chunks: int

    @property
    def total_chunks(self) -> int:
        return self.static_chunks + self.store_chunks


def _add_chunks(collection: Any, chunks: Iterable[knowledge.KnowledgeChunk]) -> int:
    """Embed and store ``chunks``; return how many were written."""
    items = list(chunks)
    if not items:
        return 0

    embeddings = get_embeddings()
    vectors = embeddings.embed_documents([item.text for item in items])
    collection.add(
        ids=[item.id for item in items],
        embeddings=vectors,
        documents=[item.text for item in items],
        metadatas=[item.metadata for item in items],
    )
    return len(items)


def _load_store(session: Session, store_id: int) -> Store | None:
    """Load a store with every relationship needed to describe it."""
    return session.scalars(
        select(Store)
        .where(Store.id == store_id)
        .options(*_STORE_OPTIONS)
    ).first()


def reindex_all() -> IndexResult:
    """Rebuild the static guide and every active store document."""
    static = knowledge.static_chunks()

    with SessionLocal() as session:
        stores = list(
            session.scalars(
                select(Store)
                .where(Store.is_active.is_(True))
                .order_by(Store.number)
                .options(*_STORE_OPTIONS)
            ).all()
        )
        store_chunks = [knowledge.store_chunk(store) for store in stores]

    collection = get_collection()
    # Remove every previous document so stores that disappeared or became
    # inactive do not linger in the index.
    collection.delete(where={"source_type": "static"})
    collection.delete(where={"source_type": "store"})

    _add_chunks(collection, static)
    _add_chunks(collection, store_chunks)

    return IndexResult(
        static_chunks=len(static),
        stores_indexed=len(stores),
        store_chunks=len(store_chunks),
    )


def reindex_store(store_id: int) -> bool:
    """Replace the knowledge document of one store.

    Returns ``True`` when a document was indexed and ``False`` when the store
    does not exist or is inactive (its stale document is removed either way).
    """
    with SessionLocal() as session:
        store = _load_store(session, store_id)
        chunk = (
            knowledge.store_chunk(store)
            if store is not None and store.is_active
            else None
        )

    collection = get_collection()
    collection.delete(where={"store_id": store_id})
    if chunk is None:
        return False

    _add_chunks(collection, [chunk])
    return True


def reindex_store_safely(store_id: int) -> None:
    """Best-effort reindex used after saving a store; never raises."""
    try:
        reindex_store(store_id)
    except Exception as exc:  # noqa: BLE001 - background task must not fail
        logger.warning(
            "No se pudo reindexar el local %s (%s)",
            store_id,
            type(exc).__name__,
        )
