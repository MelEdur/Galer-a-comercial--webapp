"""API tests for the administrative merchant management endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

import scripts.seed_stores as seed_module
from app.core.security import verify_password
from app.modules.accounts.models import User
from app.modules.stores.models import Store
from tests.conftest import requires_database

pytestmark = requires_database

MERCHANTS_URL = "/api/admin/merchants"


def _payload(**overrides) -> dict:
    data = {
        "email": "nuevo@galeria.local",
        "full_name": "Nuevo Comerciante",
        "password": "secret1234",
        "store_id": 1,
    }
    data.update(overrides)
    return data


@pytest.fixture
def seeded_stores(db_engine, clean_database, monkeypatch):
    """Seed the 21 fixed stores on the test database."""
    factory = sessionmaker(bind=db_engine, expire_on_commit=False)
    monkeypatch.setattr(seed_module, "SessionLocal", factory)
    seed_module.seed_stores()
    return factory


def test_list_merchants_empty(
    api_client: TestClient, admin_headers: dict[str, str], admin_user: User
) -> None:
    response = api_client.get(MERCHANTS_URL, headers=admin_headers)

    assert response.status_code == 200
    assert response.json() == []


def test_list_merchants_includes_store_and_hides_hash(
    api_client: TestClient,
    admin_headers: dict[str, str],
    db_session: Session,
    store: Store,
    merchant_user: User,
) -> None:
    db_session.add(
        User(
            email="ana@galeria.local",
            full_name="Ana Alvarez",
            password_hash="hash",
            role="merchant",
            is_active=False,
            store_id=store.id,
        )
    )
    db_session.commit()

    response = api_client.get(MERCHANTS_URL, headers=admin_headers)

    assert response.status_code == 200
    body = response.json()
    assert [item["full_name"] for item in body] == ["Ana Alvarez", "Comerciante Prueba"]
    first = body[0]
    assert first["email"] == "ana@galeria.local"
    assert first["is_active"] is False
    assert first["store"] == {"id": store.id, "number": store.number, "name": store.name}
    assert "created_at" in first
    assert "password_hash" not in response.text


def test_create_merchant_success(
    api_client: TestClient,
    admin_headers: dict[str, str],
    store: Store,
) -> None:
    response = api_client.post(
        MERCHANTS_URL, headers=admin_headers, json=_payload(store_id=store.id)
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "nuevo@galeria.local"
    assert body["full_name"] == "Nuevo Comerciante"
    assert body["is_active"] is True
    assert body["store"] == {"id": store.id, "number": store.number, "name": store.name}
    assert "password" not in response.text
    assert "password_hash" not in response.text


def test_created_merchant_is_active_with_hashed_password(
    api_client: TestClient,
    admin_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    response = api_client.post(
        MERCHANTS_URL, headers=admin_headers, json=_payload(store_id=store.id)
    )
    assert response.status_code == 201

    created = db_session.scalar(
        select(User).where(User.email == "nuevo@galeria.local")
    )
    assert created is not None
    assert created.role == "merchant"
    assert created.is_active is True
    assert created.store_id == store.id
    assert created.password_hash != "secret1234"
    assert verify_password("secret1234", created.password_hash) is True


def test_create_merchant_normalizes_email(
    api_client: TestClient, admin_headers: dict[str, str], store: Store, db_session
) -> None:
    response = api_client.post(
        MERCHANTS_URL,
        headers=admin_headers,
        json=_payload(email="Nuevo@Galeria.Local", store_id=store.id),
    )

    assert response.status_code == 201
    assert response.json()["email"] == "nuevo@galeria.local"


def test_create_merchant_duplicate_email(
    api_client: TestClient,
    admin_headers: dict[str, str],
    store: Store,
    merchant_user: User,
) -> None:
    response = api_client.post(
        MERCHANTS_URL,
        headers=admin_headers,
        json=_payload(email="MERCHANT@galeria.local", store_id=store.id),
    )

    assert response.status_code == 409
    assert "correo" in response.json()["detail"].lower()


def test_create_merchant_occupied_store(
    api_client: TestClient,
    admin_headers: dict[str, str],
    store: Store,
    merchant_user: User,
) -> None:
    response = api_client.post(
        MERCHANTS_URL, headers=admin_headers, json=_payload(store_id=store.id)
    )

    assert response.status_code == 409
    assert "local" in response.json()["detail"].lower()


def test_create_merchant_missing_store(
    api_client: TestClient, admin_headers: dict[str, str], store: Store
) -> None:
    response = api_client.post(
        MERCHANTS_URL, headers=admin_headers, json=_payload(store_id=9999)
    )

    assert response.status_code == 404
    assert "local" in response.json()["detail"].lower()


@pytest.mark.parametrize(
    "overrides",
    [
        {"email": "not-an-email"},
        {"full_name": ""},
        {"full_name": "   "},
        {"password": "short"},
        {"password": "a" * 73},
        {"store_id": 0},
    ],
)
def test_create_merchant_invalid_payload(
    api_client: TestClient,
    admin_headers: dict[str, str],
    store: Store,
    db_session: Session,
    overrides: dict,
) -> None:
    response = api_client.post(
        MERCHANTS_URL,
        headers=admin_headers,
        json={**_payload(store_id=store.id), **overrides},
    )

    assert response.status_code == 422
    assert (
        db_session.scalar(
            select(func.count())
            .select_from(User)
            .where(User.role == "merchant")
        )
        == 0
    )


def test_deactivate_merchant(
    api_client: TestClient,
    admin_headers: dict[str, str],
    merchant_user: User,
    db_session: Session,
) -> None:
    response = api_client.delete(
        f"{MERCHANTS_URL}/{merchant_user.id}", headers=admin_headers
    )

    assert response.status_code == 204
    db_session.refresh(merchant_user)
    assert merchant_user.is_active is False
    assert merchant_user.store_id is not None


def test_deactivate_merchant_is_idempotent(
    api_client: TestClient,
    admin_headers: dict[str, str],
    merchant_user: User,
) -> None:
    first = api_client.delete(
        f"{MERCHANTS_URL}/{merchant_user.id}", headers=admin_headers
    )
    second = api_client.delete(
        f"{MERCHANTS_URL}/{merchant_user.id}", headers=admin_headers
    )

    assert first.status_code == 204
    assert second.status_code == 204


def test_deactivate_unknown_merchant_returns_404(
    api_client: TestClient, admin_headers: dict[str, str]
) -> None:
    response = api_client.delete(f"{MERCHANTS_URL}/9999", headers=admin_headers)

    assert response.status_code == 404


def test_deactivate_admin_returns_404(
    api_client: TestClient, admin_headers: dict[str, str], admin_user: User
) -> None:
    response = api_client.delete(
        f"{MERCHANTS_URL}/{admin_user.id}", headers=admin_headers
    )

    assert response.status_code == 404


def test_store_can_be_reassigned_after_deactivation(
    api_client: TestClient,
    admin_headers: dict[str, str],
    store: Store,
    merchant_user: User,
) -> None:
    deactivated = api_client.delete(
        f"{MERCHANTS_URL}/{merchant_user.id}", headers=admin_headers
    )
    assert deactivated.status_code == 204

    response = api_client.post(
        MERCHANTS_URL,
        headers=admin_headers,
        json=_payload(email="reemplazo@galeria.local", store_id=store.id),
    )

    assert response.status_code == 201
    assert response.json()["store"]["id"] == store.id


def test_stores_endpoint_lists_21_stores(
    api_client: TestClient,
    admin_headers: dict[str, str],
    admin_user: User,
    seeded_stores,
) -> None:
    response = api_client.get("/api/admin/stores", headers=admin_headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 21
    assert [item["number"] for item in body] == list(range(1, 22))
    assert all(item["merchant"] is None for item in body)
    store = body[0]
    assert set(store) == {
        "id",
        "number",
        "name",
        "side",
        "position",
        "is_active",
        "merchant",
    }


def test_stores_endpoint_shows_active_merchant_only(
    api_client: TestClient,
    admin_headers: dict[str, str],
    db_session: Session,
    seeded_stores,
) -> None:
    target = db_session.scalar(select(Store).where(Store.number == 5))
    active = User(
        email="activo@galeria.local",
        full_name="Comerciante Activo",
        password_hash="hash",
        role="merchant",
        is_active=True,
        store_id=target.id,
    )
    db_session.add_all(
        [
            active,
            User(
                email="inactivo@galeria.local",
                full_name="Comerciante Inactivo",
                password_hash="hash",
                role="merchant",
                is_active=False,
                store_id=db_session.scalar(
                    select(Store.id).where(Store.number == 6)
                ),
            ),
        ]
    )
    db_session.commit()

    response = api_client.get("/api/admin/stores", headers=admin_headers)

    assert response.status_code == 200
    body = {item["number"]: item for item in response.json()}
    assert body[5]["merchant"] == {
        "id": active.id,
        "full_name": "Comerciante Activo",
        "email": "activo@galeria.local",
    }
    assert body[6]["merchant"] is None


@pytest.mark.parametrize(
    ("method", "url", "json"),
    [
        ("get", MERCHANTS_URL, None),
        ("post", MERCHANTS_URL, _payload()),
        ("delete", f"{MERCHANTS_URL}/1", None),
        ("get", "/api/admin/stores", None),
    ],
)
def test_merchant_gets_403(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    method: str,
    url: str,
    json: dict | None,
) -> None:
    response = api_client.request(method.upper(), url, headers=merchant_headers, json=json)

    assert response.status_code == 403


@pytest.mark.parametrize(
    ("method", "url", "json"),
    [
        ("get", MERCHANTS_URL, None),
        ("post", MERCHANTS_URL, _payload()),
        ("delete", f"{MERCHANTS_URL}/1", None),
        ("get", "/api/admin/stores", None),
    ],
)
def test_admin_routes_require_token(
    api_client: TestClient, method: str, url: str, json: dict | None
) -> None:
    response = api_client.request(method.upper(), url, json=json)

    assert response.status_code == 401
