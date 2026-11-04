"""API tests for the merchant store settings (CU #9)."""

from datetime import time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.main import app
from app.modules.accounts.models import User
from app.modules.auth.dependencies import get_current_user
from app.modules.stores.models import Store, StoreHour, StoreLink
from tests.conftest import auth_headers, requires_database

pytestmark = requires_database

STORE_URL = "/api/merchant/store"


def _payload(**overrides) -> dict:
    data = {"name": "Local 1"}
    data.update(overrides)
    return data


def _add_hours(
    session: Session, store: Store, hours: list[tuple[int, str, str]]
) -> None:
    for day, opens, closes in hours:
        session.add(
            StoreHour(
                store_id=store.id,
                day_of_week=day,
                opens_at=time.fromisoformat(opens),
                closes_at=time.fromisoformat(closes),
            )
        )
    session.commit()


def _add_links(
    session: Session, store: Store, links: list[tuple[str, str]]
) -> None:
    for position, (label, url) in enumerate(links):
        session.add(
            StoreLink(
                store_id=store.id,
                label=label,
                url=url,
                position=position,
            )
        )
    session.commit()


def _fresh_store(session: Session, store_id: int) -> Store:
    session.expire_all()
    return session.get(Store, store_id)


# --- GET -------------------------------------------------------------------


def test_get_store_without_optional_data(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    store: Store,
) -> None:
    response = api_client.get(STORE_URL, headers=merchant_headers)

    assert response.status_code == 200
    assert response.json() == {
        "id": store.id,
        "number": 1,
        "side": "right",
        "position": 1,
        "name": "Local 1",
        "description": None,
        "logo_url": None,
        "email": None,
        "phone": None,
        "whatsapp": None,
        "hours": [],
        "links": [],
    }


def test_get_store_returns_ordered_hours_and_links(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    store.description = "Descripción"
    store.logo_url = "https://example.com/logo.png"
    store.email = "local@galeria.local"
    store.phone = "1122334455"
    store.whatsapp = "5491122334455"
    db_session.commit()
    _add_hours(
        db_session,
        store,
        [(3, "10:00", "12:00"), (0, "15:00", "19:00"), (0, "09:00", "13:00")],
    )
    _add_links(
        db_session,
        store,
        [("Instagram", "https://instagram.com/x"), ("Web", "https://x.dev")],
    )

    response = api_client.get(STORE_URL, headers=merchant_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["description"] == "Descripción"
    assert body["logo_url"] == "https://example.com/logo.png"
    assert body["email"] == "local@galeria.local"
    assert body["phone"] == "1122334455"
    assert body["whatsapp"] == "5491122334455"
    assert body["hours"] == [
        {"day_of_week": 0, "opens_at": "09:00:00", "closes_at": "13:00:00"},
        {"day_of_week": 0, "opens_at": "15:00:00", "closes_at": "19:00:00"},
        {"day_of_week": 3, "opens_at": "10:00:00", "closes_at": "12:00:00"},
    ]
    assert body["links"] == [
        {
            "label": "Instagram",
            "url": "https://instagram.com/x",
            "position": 0,
        },
        {"label": "Web", "url": "https://x.dev", "position": 1},
    ]


def test_get_store_not_found_returns_404(
    api_client: TestClient, store: Store
) -> None:
    orphan = User(
        id=9999,
        email="fantasma@galeria.local",
        full_name="Fantasma",
        password_hash="hash",
        role="merchant",
        is_active=True,
        store_id=9999,
    )
    app.dependency_overrides[get_current_user] = lambda: orphan
    try:
        response = api_client.get(STORE_URL, headers=auth_headers(orphan))
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 404


# --- General data and contact ---------------------------------------------


def test_update_general_data_and_contact(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    payload = _payload(
        name="  Local Renombrado  ",
        description="  Nueva descripción  ",
        logo_url="https://example.com/logo.png",
        email="Local@Galeria.Local",
        phone="+54 11 2233-4455",
        whatsapp="5491122334455",
        hours=[],
        links=[],
    )

    response = api_client.put(STORE_URL, headers=merchant_headers, json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Local Renombrado"
    assert body["description"] == "Nueva descripción"
    assert body["logo_url"] == "https://example.com/logo.png"
    assert body["email"] == "local@galeria.local"
    assert body["phone"] == "+54 11 2233-4455"
    assert body["whatsapp"] == "5491122334455"

    stored = _fresh_store(db_session, store.id)
    assert stored.name == "Local Renombrado"
    assert stored.description == "Nueva descripción"
    assert stored.logo_url == "https://example.com/logo.png"
    assert stored.email == "local@galeria.local"


def test_update_empty_optional_strings_become_null(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    store.description = "Algo"
    store.logo_url = "https://example.com/logo.png"
    store.email = "local@galeria.local"
    store.phone = "1122334455"
    store.whatsapp = "5491122334455"
    db_session.commit()

    response = api_client.put(
        STORE_URL,
        headers=merchant_headers,
        json=_payload(
            description="",
            logo_url="",
            email="",
            phone="",
            whatsapp="",
        ),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["description"] is None
    assert body["logo_url"] is None
    assert body["email"] is None
    assert body["phone"] is None
    assert body["whatsapp"] is None


@pytest.mark.parametrize("name", ["", "   "])
def test_update_rejects_empty_name(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
    name: str,
) -> None:
    response = api_client.put(
        STORE_URL, headers=merchant_headers, json=_payload(name=name)
    )

    assert response.status_code == 422
    assert _fresh_store(db_session, store.id).name == "Local 1"


def test_update_rejects_missing_name(
    api_client: TestClient, merchant_headers: dict[str, str]
) -> None:
    response = api_client.put(STORE_URL, headers=merchant_headers, json={})

    assert response.status_code == 422


def test_update_rejects_too_long_name(
    api_client: TestClient, merchant_headers: dict[str, str]
) -> None:
    response = api_client.put(
        STORE_URL, headers=merchant_headers, json=_payload(name="a" * 121)
    )

    assert response.status_code == 422


def test_update_rejects_too_long_description(
    api_client: TestClient, merchant_headers: dict[str, str]
) -> None:
    response = api_client.put(
        STORE_URL,
        headers=merchant_headers,
        json=_payload(description="a" * 2001),
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "logo_url",
    [
        "ftp://example.com/logo.png",
        "not-a-url",
        "https://example.com/" + "a" * 500,
    ],
)
def test_update_rejects_invalid_logo(
    api_client: TestClient, merchant_headers: dict[str, str], logo_url: str
) -> None:
    response = api_client.put(
        STORE_URL, headers=merchant_headers, json=_payload(logo_url=logo_url)
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "email", ["no-es-correo", "sin@dominio", "a b@example.com"]
)
def test_update_rejects_invalid_email(
    api_client: TestClient, merchant_headers: dict[str, str], email: str
) -> None:
    response = api_client.put(
        STORE_URL, headers=merchant_headers, json=_payload(email=email)
    )

    assert response.status_code == 422


@pytest.mark.parametrize("phone", ["123abc", "123_456", "123#456"])
def test_update_rejects_invalid_phone_characters(
    api_client: TestClient, merchant_headers: dict[str, str], phone: str
) -> None:
    response = api_client.put(
        STORE_URL, headers=merchant_headers, json=_payload(phone=phone)
    )

    assert response.status_code == 422


def test_update_rejects_too_long_phone(
    api_client: TestClient, merchant_headers: dict[str, str]
) -> None:
    response = api_client.put(
        STORE_URL, headers=merchant_headers, json=_payload(phone="1" * 31)
    )

    assert response.status_code == 422


# --- Hours -----------------------------------------------------------------


def test_update_accepts_several_intervals_per_day(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    response = api_client.put(
        STORE_URL,
        headers=merchant_headers,
        json=_payload(
            hours=[
                {"day_of_week": 0, "opens_at": "15:00", "closes_at": "19:00"},
                {"day_of_week": 0, "opens_at": "09:00", "closes_at": "13:00"},
            ]
        ),
    )

    assert response.status_code == 200
    assert response.json()["hours"] == [
        {"day_of_week": 0, "opens_at": "09:00:00", "closes_at": "13:00:00"},
        {"day_of_week": 0, "opens_at": "15:00:00", "closes_at": "19:00:00"},
    ]


def test_update_allows_closed_days(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    response = api_client.put(
        STORE_URL,
        headers=merchant_headers,
        json=_payload(
            hours=[
                {"day_of_week": 5, "opens_at": "10:00", "closes_at": "14:00"}
            ]
        ),
    )

    assert response.status_code == 200
    hours = response.json()["hours"]
    assert [hour["day_of_week"] for hour in hours] == [5]


@pytest.mark.parametrize(
    ("opens_at", "closes_at"),
    [("10:00", "10:00"), ("12:00", "09:00")],
)
def test_update_rejects_invalid_interval(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
    opens_at: str,
    closes_at: str,
) -> None:
    _add_hours(db_session, store, [(0, "09:00", "13:00")])

    response = api_client.put(
        STORE_URL,
        headers=merchant_headers,
        json=_payload(
            hours=[
                {
                    "day_of_week": 1,
                    "opens_at": opens_at,
                    "closes_at": closes_at,
                }
            ]
        ),
    )

    assert response.status_code == 422
    session = db_session
    session.expire_all()
    assert session.scalar(
        select(StoreHour).where(StoreHour.store_id == store.id)
    ).day_of_week == 0


@pytest.mark.parametrize("day", [-1, 7])
def test_update_rejects_day_out_of_range(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    day: int,
) -> None:
    response = api_client.put(
        STORE_URL,
        headers=merchant_headers,
        json=_payload(
            hours=[
                {"day_of_week": day, "opens_at": "09:00", "closes_at": "13:00"}
            ]
        ),
    )

    assert response.status_code == 422


def test_update_rejects_duplicate_intervals(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    _add_hours(db_session, store, [(0, "09:00", "13:00")])

    response = api_client.put(
        STORE_URL,
        headers=merchant_headers,
        json=_payload(
            hours=[
                {"day_of_week": 0, "opens_at": "09:00", "closes_at": "13:00"},
                {"day_of_week": 0, "opens_at": "09:00", "closes_at": "17:00"},
            ]
        ),
    )

    assert response.status_code == 422
    db_session.expire_all()
    stored = db_session.scalars(
        select(StoreHour).where(StoreHour.store_id == store.id)
    ).all()
    assert len(stored) == 1


def test_update_replaces_all_hours(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    _add_hours(db_session, store, [(0, "09:00", "13:00"), (2, "10:00", "18:00")])

    response = api_client.put(
        STORE_URL,
        headers=merchant_headers,
        json=_payload(
            hours=[
                {"day_of_week": 1, "opens_at": "08:00", "closes_at": "12:00"}
            ]
        ),
    )

    assert response.status_code == 200
    assert response.json()["hours"] == [
        {"day_of_week": 1, "opens_at": "08:00:00", "closes_at": "12:00:00"}
    ]


def test_update_empty_hours_removes_previous(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    _add_hours(db_session, store, [(0, "09:00", "13:00")])

    response = api_client.put(
        STORE_URL, headers=merchant_headers, json=_payload(hours=[])
    )

    assert response.status_code == 200
    assert response.json()["hours"] == []


# --- Links -----------------------------------------------------------------


def test_update_links_keeps_order(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    response = api_client.put(
        STORE_URL,
        headers=merchant_headers,
        json=_payload(
            links=[
                {"label": "Instagram", "url": "https://instagram.com/x"},
                {"label": "Sitio", "url": "https://example.com"},
                {"label": "Facebook", "url": "https://facebook.com/x"},
            ]
        ),
    )

    assert response.status_code == 200
    links = response.json()["links"]
    assert [link["position"] for link in links] == [0, 1, 2]
    assert [link["label"] for link in links] == ["Instagram", "Sitio", "Facebook"]
    assert links[1]["url"].startswith("https://example.com")


@pytest.mark.parametrize(
    "url",
    ["ftp://example.com", "no-es-url", "https://example.com/" + "a" * 500],
)
def test_update_rejects_invalid_link_url(
    api_client: TestClient, merchant_headers: dict[str, str], url: str
) -> None:
    response = api_client.put(
        STORE_URL,
        headers=merchant_headers,
        json=_payload(links=[{"label": "Web", "url": url}]),
    )

    assert response.status_code == 422


def test_update_rejects_duplicate_link_urls(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    _add_links(db_session, store, [("Web", "https://old.example.com")])

    response = api_client.put(
        STORE_URL,
        headers=merchant_headers,
        json=_payload(
            links=[
                {"label": "A", "url": "https://example.com"},
                {"label": "B", "url": "https://example.com"},
            ]
        ),
    )

    assert response.status_code == 422
    db_session.expire_all()
    stored = db_session.scalars(
        select(StoreLink).where(StoreLink.store_id == store.id)
    ).all()
    assert [link.url for link in stored] == ["https://old.example.com"]


def test_update_rejects_more_than_ten_links(
    api_client: TestClient, merchant_headers: dict[str, str]
) -> None:
    links = [
        {"label": f"Enlace {index}", "url": f"https://example.com/{index}"}
        for index in range(11)
    ]

    response = api_client.put(
        STORE_URL, headers=merchant_headers, json=_payload(links=links)
    )

    assert response.status_code == 422


def test_update_empty_links_removes_previous(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    _add_links(db_session, store, [("Web", "https://example.com")])

    response = api_client.put(
        STORE_URL, headers=merchant_headers, json=_payload(links=[])
    )

    assert response.status_code == 200
    assert response.json()["links"] == []


def test_update_replaces_all_links(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    _add_links(
        db_session,
        store,
        [("Viejo", "https://old.example.com"), ("Otro", "https://other.example.com")],
    )

    response = api_client.put(
        STORE_URL,
        headers=merchant_headers,
        json=_payload(links=[{"label": "Nuevo", "url": "https://new.example.com"}]),
    )

    assert response.status_code == 200
    assert response.json()["links"] == [
        {"label": "Nuevo", "url": "https://new.example.com/", "position": 0}
    ]


# --- Forbidden fields ------------------------------------------------------


@pytest.mark.parametrize(
    "overrides",
    [
        {"store_id": 2},
        {"number": 2},
        {"side": "left"},
        {"position": 2},
        {"is_active": False},
        {"unknown": "value"},
    ],
)
def test_update_rejects_foreign_or_unknown_fields(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
    overrides: dict,
) -> None:
    response = api_client.put(
        STORE_URL,
        headers=merchant_headers,
        json=_payload(**overrides),
    )

    assert response.status_code == 422
    assert _fresh_store(db_session, store.id).name == "Local 1"


# --- Authorization ---------------------------------------------------------


@pytest.mark.parametrize("method", ["get", "put"])
def test_store_requires_token(
    api_client: TestClient, method: str
) -> None:
    response = api_client.request(
        method.upper(), STORE_URL, json=_payload()
    )

    assert response.status_code == 401


@pytest.mark.parametrize("method", ["get", "put"])
def test_store_forbids_admin(
    api_client: TestClient,
    admin_headers: dict[str, str],
    method: str,
) -> None:
    response = api_client.request(
        method.upper(), STORE_URL, headers=admin_headers, json=_payload()
    )

    assert response.status_code == 403


@pytest.mark.parametrize("method", ["get", "put"])
def test_store_forbids_merchant_without_store(
    api_client: TestClient, method: str
) -> None:
    orphan = User(
        id=999,
        email="sinlocal@galeria.local",
        full_name="Sin Local",
        password_hash="hash",
        role="merchant",
        is_active=True,
        store_id=None,
    )
    app.dependency_overrides[get_current_user] = lambda: orphan
    try:
        response = api_client.request(
            method.upper(),
            STORE_URL,
            headers=auth_headers(orphan),
            json=_payload(),
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 403
