"""API tests for login, session identity and admin authorization."""

from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_access_token
from app.modules.accounts.models import User
from app.modules.stores.models import Store
from tests.conftest import auth_headers, requires_database

pytestmark = requires_database

INVALID_CREDENTIALS = "Credenciales inválidas"


def _expired_token(subject: int, role: str) -> str:
    past = datetime.now(timezone.utc) - timedelta(hours=1)
    return jwt.encode(
        {
            "sub": str(subject),
            "role": role,
            "iat": past - timedelta(minutes=5),
            "exp": past,
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def test_login_returns_token_for_valid_credentials(
    api_client: TestClient, admin_user: User
) -> None:
    response = api_client.post(
        "/api/auth/login",
        json={"email": "ADMIN@galeria.local", "password": "admin1234"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]

    payload = decode_access_token(body["access_token"])
    assert payload["sub"] == str(admin_user.id)
    assert payload["role"] == "admin"

    assert "password" not in response.text
    assert "password_hash" not in response.text


@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("admin@galeria.local", "wrong-password"),
        ("unknown@galeria.local", "admin1234"),
    ],
)
def test_login_rejects_invalid_credentials_with_uniform_message(
    api_client: TestClient,
    admin_user: User,
    email: str,
    password: str,
) -> None:
    response = api_client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )

    assert response.status_code == 401
    assert response.json() == {"detail": INVALID_CREDENTIALS}


def test_login_rejects_inactive_account(
    api_client: TestClient, admin_user: User, db_session: Session
) -> None:
    admin_user.is_active = False
    db_session.commit()

    response = api_client.post(
        "/api/auth/login",
        json={"email": "admin@galeria.local", "password": "admin1234"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": INVALID_CREDENTIALS}


def test_login_rejects_invalid_payload(api_client: TestClient) -> None:
    response = api_client.post(
        "/api/auth/login", json={"email": "not-an-email", "password": "x"}
    )

    assert response.status_code == 422


def test_login_rejects_password_over_72_characters(api_client: TestClient) -> None:
    response = api_client.post(
        "/api/auth/login",
        json={"email": "admin@galeria.local", "password": "a" * 73},
    )

    assert response.status_code == 422


def test_me_returns_authenticated_identity(
    api_client: TestClient, admin_headers: dict[str, str], admin_user: User
) -> None:
    response = api_client.get("/api/auth/me", headers=admin_headers)

    assert response.status_code == 200
    assert response.json() == {
        "id": admin_user.id,
        "email": "admin@galeria.local",
        "full_name": "Administrador",
        "role": "admin",
        "is_active": True,
        "store_id": None,
        "store": None,
    }
    assert "password_hash" not in response.text


def test_me_returns_store_for_merchant(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    merchant_user: User,
    store: Store,
) -> None:
    response = api_client.get("/api/auth/me", headers=merchant_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == merchant_user.id
    assert body["role"] == "merchant"
    assert body["store_id"] == store.id
    assert body["store"] == {
        "id": store.id,
        "number": store.number,
        "name": store.name,
    }
    assert "password_hash" not in response.text


def test_merchant_login_returns_token(
    api_client: TestClient, merchant_user: User
) -> None:
    response = api_client.post(
        "/api/auth/login",
        json={"email": "merchant@galeria.local", "password": "merchant1234"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]

    payload = decode_access_token(body["access_token"])
    assert payload["sub"] == str(merchant_user.id)
    assert payload["role"] == "merchant"

    assert "password_hash" not in response.text


@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("merchant@galeria.local", "wrong-password"),
        ("unknown-merchant@galeria.local", "merchant1234"),
    ],
)
def test_merchant_login_rejects_invalid_credentials(
    api_client: TestClient,
    merchant_user: User,
    email: str,
    password: str,
) -> None:
    response = api_client.post(
        "/api/auth/login", json={"email": email, "password": password}
    )

    assert response.status_code == 401
    assert response.json() == {"detail": INVALID_CREDENTIALS}
    assert "access_token" not in response.json()


def test_merchant_login_rejects_inactive_account(
    api_client: TestClient, merchant_user: User, db_session: Session
) -> None:
    merchant_user.is_active = False
    db_session.commit()

    response = api_client.post(
        "/api/auth/login",
        json={"email": "merchant@galeria.local", "password": "merchant1234"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": INVALID_CREDENTIALS}
    assert "access_token" not in response.json()


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"Authorization": "Bearer not-a-token"},
        {"Authorization": "Basic abc"},
    ],
)
def test_me_rejects_missing_or_invalid_token(
    api_client: TestClient, headers: dict[str, str]
) -> None:
    response = api_client.get("/api/auth/me", headers=headers)

    assert response.status_code == 401


def test_me_rejects_expired_token(
    api_client: TestClient, admin_user: User
) -> None:
    token = _expired_token(admin_user.id, admin_user.role)

    response = api_client.get(
        "/api/auth/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401


def test_me_rejects_token_for_inactive_account(
    api_client: TestClient, merchant_user: User, db_session: Session
) -> None:
    headers = auth_headers(merchant_user)
    merchant_user.is_active = False
    db_session.commit()

    response = api_client.get("/api/auth/me", headers=headers)

    assert response.status_code == 401


def test_admin_can_access_admin_route(
    api_client: TestClient, admin_headers: dict[str, str]
) -> None:
    response = api_client.get("/api/admin/merchants", headers=admin_headers)

    assert response.status_code == 200


def test_merchant_gets_403_on_admin_route(
    api_client: TestClient, merchant_headers: dict[str, str]
) -> None:
    response = api_client.get("/api/admin/merchants", headers=merchant_headers)

    assert response.status_code == 403


def test_admin_route_requires_token(api_client: TestClient) -> None:
    response = api_client.get("/api/admin/merchants")

    assert response.status_code == 401
