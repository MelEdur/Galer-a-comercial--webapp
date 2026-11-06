"""Tests for the public assistant (CU #11).

Every provider is replaced by an in-memory double: no Groq call is made and no
embedding model is downloaded.
"""

from __future__ import annotations

import json
from datetime import time
from decimal import Decimal
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.modules.assistant import (
    embeddings,
    indexing,
    intent,
    knowledge,
    llm,
    router,
    vectorstore,
)
from app.modules.assistant.schemas import ChatMessage, ChatRequest
from app.modules.assistant.service import NO_INFO_ANSWER
from app.modules.catalog.models import Category, Product, ProductCategory
from app.modules.stores.models import Store, StoreHour, StoreLink
from tests.conftest import requires_database

CHAT_URL = "/api/public/assistant/chat"


# --- Doubles ---------------------------------------------------------------


class FakeLLM:
    """Return queued responses and record the prompts it received."""

    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.calls: list[list[dict[str, str]]] = []

    def __call__(self, messages: list[dict[str, str]]) -> str:
        self.calls.append(messages)
        if not self.responses:
            raise AssertionError("El LLM falso no tiene más respuestas.")
        return self.responses.pop(0)


class FakeEmbeddings:
    """Deterministic two-dimensional embeddings."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[1.0, 0.0] for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        return [1.0, 0.0]


class FakeCollection:
    """Minimal in-memory Chroma collection with the used operations."""

    def __init__(
        self,
        documents: list[str] | None = None,
        metadatas: list[dict[str, Any]] | None = None,
    ) -> None:
        self.items: dict[str, dict[str, Any]] = {}
        self.query_documents = documents or []
        self.query_metadatas = metadatas or []

    def add(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None:
        for item_id, embedding, document, metadata in zip(
            ids, embeddings, documents, metadatas
        ):
            self.items[item_id] = {
                "embedding": embedding,
                "document": document,
                "metadata": metadata,
            }

    def delete(
        self,
        where: dict[str, Any] | None = None,
        ids: list[str] | None = None,
    ) -> None:
        if ids is not None:
            for item_id in ids:
                self.items.pop(item_id, None)
            return
        if where is None:
            self.items.clear()
            return
        for item_id, item in list(self.items.items()):
            metadata = item["metadata"]
            if all(metadata.get(key) == value for key, value in where.items()):
                del self.items[item_id]

    def query(
        self,
        query_embeddings: list[list[float]],
        n_results: int,
        include: list[str] | None = None,
    ) -> dict[str, Any]:
        documents = self.query_documents[:n_results]
        metadatas = self.query_metadatas[:n_results]
        return {
            "documents": [documents],
            "metadatas": [metadatas],
            "distances": [[0.1] * len(documents)],
        }


@pytest.fixture(autouse=True)
def _reset_state() -> Any:
    """Reset caches and rate-limit counters before every test."""
    llm.reset_model_cache()
    router.reset_rate_limit()
    embeddings.reset_embeddings()
    vectorstore.reset_vectorstore()
    yield
    llm.reset_model_cache()
    router.reset_rate_limit()
    embeddings.reset_embeddings()
    vectorstore.reset_vectorstore()


def _install_llm(monkeypatch: pytest.MonkeyPatch, responses: list[str]) -> FakeLLM:
    fake = FakeLLM(responses)
    monkeypatch.setattr(llm, "generate", fake)
    return fake


def _install_retrieval(
    monkeypatch: pytest.MonkeyPatch,
    documents: list[str] | None = None,
    metadatas: list[dict[str, Any]] | None = None,
) -> FakeCollection:
    collection = FakeCollection(documents, metadatas)
    monkeypatch.setattr(embeddings, "get_embeddings", lambda: FakeEmbeddings())
    monkeypatch.setattr(vectorstore, "get_collection", lambda: collection)
    return collection


def _intent_json(name: str, query: str | None = None) -> str:
    return json.dumps({"intent": name, "search_query": query})


# --- Endpoint contract -----------------------------------------------------


def test_chat_contract_informational_with_sources(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _install_llm(
        monkeypatch,
        [_intent_json("informational"), "La galería tiene 21 locales."],
    )
    _install_retrieval(
        monkeypatch,
        documents=["La galería reúne 21 locales en dos lados y un fondo."],
        metadatas=[
            {
                "source_type": "static",
                "source_id": "galeria",
                "title": "Guía de la galería",
            }
        ],
    )

    response = client.post(
        CHAT_URL,
        json={"message": "¿Cuántos locales hay?", "history": []},
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": "La galería tiene 21 locales.",
        "action": None,
        "sources": [{"title": "Guía de la galería", "type": "static"}],
    }


def test_chat_accepts_history(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = _install_llm(
        monkeypatch,
        [_intent_json("informational"), "Respuesta con historial."],
    )
    _install_retrieval(
        monkeypatch,
        documents=["Contenido"],
        metadatas=[{"source_type": "static", "title": "Guía de la galería"}],
    )
    history = [
        {"role": "user", "content": "Hola"},
        {"role": "assistant", "content": "¡Hola!"},
    ]

    response = client.post(
        CHAT_URL,
        json={"message": "¿Y los locales?", "history": history},
    )

    assert response.status_code == 200
    assert "Visitante: Hola" in fake.calls[-1][-1]["content"]


def test_chat_without_context_reports_no_information(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _install_llm(monkeypatch, [_intent_json("informational")])
    _install_retrieval(monkeypatch, documents=[], metadatas=[])

    response = client.post(
        CHAT_URL, json={"message": "¿Tienen clases de piano?"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == NO_INFO_ANSWER
    assert body["action"] is None
    assert body["sources"] == []


def test_chat_product_search_offers_search_action(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _install_llm(
        monkeypatch, [_intent_json("product_search", "auriculares")]
    )

    response = client.post(
        CHAT_URL, json={"message": "¿Dónde compro auriculares?"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["action"] == {
        "type": "search",
        "label": "Buscar auriculares",
        "query": "auriculares",
        "href": "/buscar?search=auriculares",
    }
    assert body["sources"] == []
    assert "price" not in body


def test_chat_product_search_quotes_the_query(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _install_llm(
        monkeypatch, [_intent_json("product_search", "zapatillas running")]
    )

    response = client.post(
        CHAT_URL, json={"message": "Busco zapatillas para correr"}
    )

    assert response.status_code == 200
    assert (
        response.json()["action"]["href"]
        == "/buscar?search=zapatillas+running"
    )


def test_chat_map_offers_map_action(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _install_llm(monkeypatch, [_intent_json("map")])

    response = client.post(
        CHAT_URL, json={"message": "¿Dónde está el local 21?"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["action"] == {
        "type": "map",
        "label": "Abrir mapa",
        "query": None,
        "href": "/mapa",
    }
    assert body["sources"] == []


def test_chat_out_of_scope_explains_capabilities(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _install_llm(monkeypatch, [_intent_json("out_of_scope")])

    response = client.post(
        CHAT_URL, json={"message": "¿Quién ganó el partido?"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["action"] is None
    assert "galería" in body["answer"]
    assert body["sources"] == []


def test_intent_falls_back_to_informational_on_invalid_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_llm(monkeypatch, ["esto no es JSON"])

    classified = intent.classify("Hola", [])

    assert classified.name == intent.INFORMATIONAL


# --- Validation and limits -------------------------------------------------


@pytest.mark.parametrize(
    "payload",
    [
        {"message": "a" * 1001},
        {"message": ""},
        {"message": "   "},
        {"message": "Hola", "history": [{"role": "user", "content": "a"} ] * 11},
        {"message": "Hola", "history": [{"role": "system", "content": "a"}]},
        {"message": "Hola", "history": [{"role": "user", "content": ""}]},
    ],
)
def test_chat_rejects_invalid_payloads(
    client: TestClient, payload: dict[str, Any]
) -> None:
    response = client.post(CHAT_URL, json=payload)

    assert response.status_code == 422


def test_chat_accepts_ten_history_messages(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _install_llm(monkeypatch, [_intent_json("informational")])
    _install_retrieval(monkeypatch, documents=[], metadatas=[])
    history = [
        {"role": "user" if index % 2 == 0 else "assistant", "content": "hola"}
        for index in range(10)
    ]

    response = client.post(
        CHAT_URL, json={"message": "Hola", "history": history}
    )

    assert response.status_code == 200


def test_chat_rate_limit_returns_429(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "assistant_rate_limit", 2)
    _install_llm(
        monkeypatch, [_intent_json("informational") for _ in range(2)]
    )
    _install_retrieval(monkeypatch, documents=[], metadatas=[])

    assert client.post(CHAT_URL, json={"message": "Hola"}).status_code == 200
    assert client.post(CHAT_URL, json={"message": "Hola"}).status_code == 200
    response = client.post(CHAT_URL, json={"message": "Hola"})

    assert response.status_code == 429
    assert "demasiadas" in response.json()["detail"].lower()


def test_chat_returns_503_when_llm_is_unavailable(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _raise(messages: list[dict[str, str]]) -> str:
        raise llm.LLMUnavailableError("sin clave")

    monkeypatch.setattr(llm, "generate", _raise)

    response = client.post(CHAT_URL, json={"message": "Hola"})

    assert response.status_code == 503
    assert "no está disponible" in response.json()["detail"]
    assert "sin clave" not in response.text


def test_chat_returns_503_when_embeddings_are_unavailable(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _install_llm(monkeypatch, [_intent_json("informational")])

    def _raise() -> Any:
        raise embeddings.EmbeddingUnavailableError("modelo ausente")

    monkeypatch.setattr(embeddings, "get_embeddings", _raise)

    response = client.post(CHAT_URL, json={"message": "¿Qué es la galería?"})

    assert response.status_code == 503
    assert "modelo ausente" not in response.text


# --- Model selection -------------------------------------------------------


def test_select_model_uses_preference_order(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        llm,
        "_list_model_ids",
        lambda: [
            "qwen/qwen3.8-27b",
            "openai/gpt-oss-20b",
            "openai/gpt-oss-120b",
        ],
    )

    assert llm.select_model() == "openai/gpt-oss-120b"


def test_select_model_falls_back_to_an_available_chat_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        llm, "_list_model_ids", lambda: ["llama-3.3-70b-versatile"]
    )

    assert llm.select_model() == "llama-3.3-70b-versatile"


def test_select_model_excludes_code_audio_and_guard_models(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        llm,
        "_list_model_ids",
        lambda: [
            "meta-llama/llama-4-maverick-coder",
            "whisper-large-v3",
            "playai-tts",
            "text-embedding-3-small",
            "llama-guard-4-12b",
        ],
    )

    with pytest.raises(llm.LLMUnavailableError):
        llm.select_model()


def test_select_model_without_models_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(llm, "_list_model_ids", lambda: [])

    with pytest.raises(llm.LLMUnavailableError):
        llm.select_model()


def test_select_model_prefers_the_fixed_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "groq_model", "fixed/chat-model")

    def _unexpected() -> list[str]:
        raise AssertionError("No debe consultar modelos con GROQ_MODEL fijo.")

    monkeypatch.setattr(llm, "_list_model_ids", _unexpected)

    assert llm.select_model() == "fixed/chat-model"


def test_get_chat_model_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "groq_api_key", "")

    with pytest.raises(llm.LLMUnavailableError):
        llm.get_chat_model()


# --- Knowledge documents ---------------------------------------------------


def test_static_chunks_have_deterministic_ids_and_metadata() -> None:
    chunks = knowledge.static_chunks()

    assert len(chunks) > 1
    assert chunks[0].id == "static:galeria:0"
    assert [chunk.id for chunk in chunks] == [
        f"static:galeria:{index}" for index in range(len(chunks))
    ]
    for chunk in chunks:
        assert chunk.metadata["source_type"] == "static"
        assert chunk.metadata["source_id"] == "galeria"
        assert chunk.metadata["title"] == "Guía de la galería"
        assert "updated_at" in chunk.metadata


def _store_with_catalog() -> Store:
    item = Store(
        id=7,
        number=7,
        name="Tecno Local",
        description="Accesorios y pequeños dispositivos.",
        logo_url=None,
        email="local7@galeria.local",
        phone="1122334455",
        whatsapp="5491122334455",
        side="right",
        position=4,
    )
    item.hours = [
        StoreHour(day_of_week=0, opens_at=time(9, 0), closes_at=time(13, 0))
    ]
    item.links = [
        StoreLink(label="Web", url="https://local7.example.com", position=0)
    ]
    product = Product(
        id=1,
        store_id=7,
        name="Auriculares Bluetooth",
        description="Auriculares inalámbricos.",
        price=Decimal("25999.00"),
        offer_price=Decimal("19999.00"),
        is_active=True,
        deleted_at=None,
    )
    product.product_categories = [
        ProductCategory(
            product_id=1, category_id=1, category=Category(id=1, name="Tecnología")
        )
    ]
    item.products = [product]
    return item


def test_store_chunk_includes_public_data_without_products() -> None:
    chunk = knowledge.store_chunk(_store_with_catalog())

    assert chunk.id == "store:7:0"
    assert chunk.metadata == {
        "source_type": "store",
        "source_id": "store:7",
        "title": "Local 7 — Tecno Local",
        "store_id": 7,
        "updated_at": "",
    }
    assert "Local 7" in chunk.text
    assert "Ubicación en el mapa: lado derecho, posición 4." in chunk.text
    assert "Accesorios y pequeños dispositivos." in chunk.text
    assert "Tecnología" in chunk.text
    assert "1122334455" in chunk.text
    assert "Lunes: 09:00 a 13:00" in chunk.text
    assert "https://local7.example.com" in chunk.text
    # Products, prices and stock are never indexed.
    assert "Auriculares" not in chunk.text
    assert "25999" not in chunk.text
    assert "19999" not in chunk.text
    assert "stock" not in chunk.text.lower()


def test_store_chunk_reports_missing_data_without_inventing_it() -> None:
    item = Store(
        id=8,
        number=8,
        name="Local Vacío",
        description=None,
        side="left",
        position=4,
    )
    item.hours = []
    item.links = []
    item.products = []

    text = knowledge.store_chunk(item).text

    assert "no publica datos de contacto" in text
    assert "no publica horarios" in text
    assert "no publica enlaces" in text


# --- Indexing --------------------------------------------------------------


@pytest.fixture
def fake_index(monkeypatch: pytest.MonkeyPatch, db_engine: Any) -> FakeCollection:
    """Bind indexing to the test database and in-memory providers."""
    factory = sessionmaker(bind=db_engine, expire_on_commit=False)
    monkeypatch.setattr(indexing, "SessionLocal", factory)
    collection = FakeCollection()
    monkeypatch.setattr(indexing, "get_embeddings", lambda: FakeEmbeddings())
    monkeypatch.setattr(indexing, "get_collection", lambda: collection)
    return collection


@pytest.mark.usefixtures("clean_database")
@requires_database
def test_reindex_store_is_idempotent(
    db_session: Any, store: Store, fake_index: FakeCollection
) -> None:
    assert indexing.reindex_store(store.id) is True
    first_ids = set(fake_index.items)
    assert first_ids == {f"store:{store.id}:0"}

    assert indexing.reindex_store(store.id) is True

    assert set(fake_index.items) == first_ids


@pytest.mark.usefixtures("clean_database")
@requires_database
def test_reindex_store_keeps_static_documents(
    db_session: Any, store: Store, fake_index: FakeCollection
) -> None:
    fake_index.items["static:galeria:0"] = {
        "embedding": [1.0, 0.0],
        "document": "guía",
        "metadata": {"source_type": "static", "source_id": "galeria"},
    }

    indexing.reindex_store(store.id)

    assert "static:galeria:0" in fake_index.items
    assert f"store:{store.id}:0" in fake_index.items


@pytest.mark.usefixtures("clean_database")
@requires_database
def test_reindex_store_removes_inactive_store_document(
    db_session: Any, store: Store, fake_index: FakeCollection
) -> None:
    indexing.reindex_store(store.id)
    store.is_active = False
    db_session.commit()

    assert indexing.reindex_store(store.id) is False
    assert fake_index.items == {}


@pytest.mark.usefixtures("clean_database")
@requires_database
def test_reindex_all_indexes_static_and_stores(
    db_session: Any, store: Store, fake_index: FakeCollection
) -> None:
    result = indexing.reindex_all()

    assert result.static_chunks > 1
    assert result.stores_indexed == 1
    assert result.store_chunks == 1
    assert f"store:{store.id}:0" in fake_index.items
    assert "static:galeria:0" in fake_index.items


@pytest.mark.usefixtures("clean_database")
@requires_database
def test_reindex_store_safely_swallows_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _raise(store_id: int) -> bool:
        raise RuntimeError("índice roto")

    monkeypatch.setattr(indexing, "reindex_store", _raise)

    indexing.reindex_store_safely(1)


# --- Merchant store hook (CU #9) -------------------------------------------


@requires_database
def test_saving_store_enqueues_reindex(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    store: Store,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[int] = []
    monkeypatch.setattr(
        indexing, "reindex_store_safely", lambda store_id: calls.append(store_id)
    )

    response = api_client.put(
        "/api/merchant/store",
        headers=merchant_headers,
        json={"name": "Local Renombrado"},
    )

    assert response.status_code == 200
    assert calls == [store.id]


@requires_database
def test_saving_store_succeeds_when_reindex_fails(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    store: Store,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _raise(store_id: int) -> bool:
        raise RuntimeError("índice roto")

    monkeypatch.setattr(indexing, "reindex_store", _raise)

    response = api_client.put(
        "/api/merchant/store",
        headers=merchant_headers,
        json={"name": "Local Renombrado"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Local Renombrado"


# --- Direct service signatures --------------------------------------------


def test_chat_request_rejects_more_than_ten_history_messages() -> None:
    history = [
        ChatMessage(role="user", content="hola") for _ in range(10)
    ]

    request = ChatRequest(message="hola", history=history)
    assert len(request.history) == 10

    with pytest.raises(ValueError):
        ChatRequest(
            message="hola",
            history=history + [ChatMessage(role="user", content="hola")],
        )
