"""API tests for the merchant product statistics (CU #10)."""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.main import app
from app.modules.accounts.models import User
from app.modules.analytics.models import ProductSearchEvent
from app.modules.analytics.service import BUENOS_AIRES
from app.modules.auth.dependencies import get_current_user
from app.modules.catalog.models import Product
from app.modules.stores.models import Store
from tests.conftest import auth_headers, requires_database

pytestmark = requires_database

STATS_URL = "/api/merchant/stats/products"
UTC = timezone.utc


def _add_product(
    session: Session,
    store: Store,
    *,
    name: str = "Producto",
    deleted: bool = False,
) -> Product:
    product = Product(
        store_id=store.id,
        name=name,
        price=Decimal("10.00"),
        is_active=not deleted,
        deleted_at=datetime.now(UTC) if deleted else None,
    )
    session.add(product)
    session.commit()
    return product


def _add_event(
    session: Session, product: Product, searched_at: datetime
) -> ProductSearchEvent:
    event = ProductSearchEvent(product_id=product.id, searched_at=searched_at)
    session.add(event)
    session.commit()
    return event


def _event_count(session: Session) -> int:
    return (
        session.scalar(select(func.count()).select_from(ProductSearchEvent)) or 0
    )


def _local_today() -> date:
    return datetime.now(BUENOS_AIRES).date()


@pytest.fixture
def other_store(db_session: Session, store: Store) -> Store:
    item = Store(number=2, name="Local 2", side="left", position=1)
    db_session.add(item)
    db_session.commit()
    return item


# --- Authorization ---------------------------------------------------------


def test_stats_require_token(api_client: TestClient) -> None:
    response = api_client.get(STATS_URL)

    assert response.status_code == 401


def test_stats_forbid_admin(
    api_client: TestClient, admin_headers: dict[str, str]
) -> None:
    response = api_client.get(STATS_URL, headers=admin_headers)

    assert response.status_code == 403


def test_stats_forbid_merchant_without_store(
    api_client: TestClient,
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
        response = api_client.get(STATS_URL, headers=auth_headers(orphan))
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 403


# --- Store isolation -------------------------------------------------------


def test_stats_only_include_authenticated_store_products(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
    other_store: Store,
) -> None:
    own = _add_product(db_session, store, name="Propio")
    foreign = _add_product(db_session, other_store, name="Ajeno")
    now = datetime.now(UTC)
    _add_event(db_session, own, now)
    _add_event(db_session, foreign, now)

    response = api_client.get(STATS_URL, headers=merchant_headers)

    assert response.status_code == 200
    body = response.json()
    assert [item["product_id"] for item in body["items"]] == [own.id]
    assert body["total_searches"] == 1


# --- Ranking ---------------------------------------------------------------


def test_stats_count_and_descending_order(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    low = _add_product(db_session, store, name="Bajo")
    high = _add_product(db_session, store, name="Alto")
    middle = _add_product(db_session, store, name="Medio")
    now = datetime.now(UTC)
    for _ in range(3):
        _add_event(db_session, high, now)
    for _ in range(2):
        _add_event(db_session, middle, now)
    _add_event(db_session, low, now)

    response = api_client.get(STATS_URL, headers=merchant_headers)

    assert response.status_code == 200
    body = response.json()
    assert [(item["name"], item["search_count"]) for item in body["items"]] == [
        ("Alto", 3),
        ("Medio", 2),
        ("Bajo", 1),
    ]
    assert body["total_searches"] == 6


def test_stats_ties_are_ordered_by_name(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    zeta = _add_product(db_session, store, name="Zeta")
    alpha = _add_product(db_session, store, name="alfa")
    now = datetime.now(UTC)
    for _ in range(2):
        _add_event(db_session, zeta, now)
    for _ in range(2):
        _add_event(db_session, alpha, now)

    response = api_client.get(STATS_URL, headers=merchant_headers)

    assert response.status_code == 200
    assert [item["name"] for item in response.json()["items"]] == ["alfa", "Zeta"]


def test_stats_limit_top_ten_but_total_counts_all(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    now = datetime.now(UTC)
    for index in range(12):
        product = _add_product(db_session, store, name=f"Producto {index:02d}")
        _add_event(db_session, product, now)

    response = api_client.get(STATS_URL, headers=merchant_headers)

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 10
    assert body["total_searches"] == 12
    assert [item["name"] for item in body["items"]] == [
        f"Producto {index:02d}" for index in range(10)
    ]


def test_stats_exclude_products_without_searches(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    searched = _add_product(db_session, store, name="Buscado")
    _add_product(db_session, store, name="Sin búsquedas")
    _add_event(db_session, searched, datetime.now(UTC))

    response = api_client.get(STATS_URL, headers=merchant_headers)

    assert response.status_code == 200
    assert [item["name"] for item in response.json()["items"]] == ["Buscado"]


def test_stats_include_deleted_products_marked(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    deleted = _add_product(db_session, store, name="Eliminado", deleted=True)
    now = datetime.now(UTC)
    _add_event(db_session, deleted, now)
    _add_event(db_session, deleted, now)

    response = api_client.get(STATS_URL, headers=merchant_headers)

    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["product_id"] == deleted.id
    assert item["name"] == "Eliminado"
    assert item["is_deleted"] is True
    assert item["search_count"] == 2


# --- Periods ---------------------------------------------------------------


@pytest.mark.parametrize(
    ("days", "expected_names"),
    [
        (7, ["Reciente"]),
        (30, ["Reciente", "Medio"]),
        (90, ["Reciente", "Medio", "Antiguo"]),
    ],
)
def test_stats_presets(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
    days: int,
    expected_names: list[str],
) -> None:
    now = datetime.now(UTC)
    recent = _add_product(db_session, store, name="Reciente")
    middle = _add_product(db_session, store, name="Medio")
    old = _add_product(db_session, store, name="Antiguo")
    _add_event(db_session, recent, now - timedelta(days=1))
    _add_event(db_session, middle, now - timedelta(days=20))
    _add_event(db_session, old, now - timedelta(days=60))

    response = api_client.get(
        STATS_URL, headers=merchant_headers, params={"days": days}
    )

    assert response.status_code == 200
    names = [item["name"] for item in response.json()["items"]]
    assert sorted(names) == sorted(expected_names)


def test_stats_default_period_is_thirty_days(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    now = datetime.now(UTC)
    inside = _add_product(db_session, store, name="Dentro")
    outside = _add_product(db_session, store, name="Fuera")
    _add_event(db_session, inside, now - timedelta(days=20))
    _add_event(db_session, outside, now - timedelta(days=40))

    response = api_client.get(STATS_URL, headers=merchant_headers)

    assert response.status_code == 200
    body = response.json()
    assert [item["name"] for item in body["items"]] == ["Dentro"]
    assert body["to_date"] == _local_today().isoformat()
    assert body["from_date"] == (
        _local_today() - timedelta(days=29)
    ).isoformat()


def test_stats_custom_range_and_local_day_boundaries(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    product = _add_product(db_session, store, name="Medianoche")
    # Local day 2026-10-02 is 03:00Z on 2026-10-02 through 03:00Z on 2026-10-03.
    _add_event(db_session, product, datetime(2026, 10, 2, 2, 59, tzinfo=UTC))
    _add_event(db_session, product, datetime(2026, 10, 2, 3, 0, tzinfo=UTC))
    _add_event(db_session, product, datetime(2026, 10, 3, 2, 59, tzinfo=UTC))
    _add_event(db_session, product, datetime(2026, 10, 3, 3, 0, tzinfo=UTC))

    response = api_client.get(
        STATS_URL,
        headers=merchant_headers,
        params={"from_date": "2026-10-02", "to_date": "2026-10-02"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["from_date"] == "2026-10-02"
    assert body["to_date"] == "2026-10-02"
    assert body["total_searches"] == 2
    assert body["items"][0]["search_count"] == 2
    assert body["items"][0]["last_searched_at"] == "2026-10-02T23:59:00-03:00"


def test_stats_last_searched_at_uses_buenos_aires_offset(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    product = _add_product(db_session, store, name="Remera")
    _add_event(db_session, product, datetime(2026, 10, 31, 21, 12, tzinfo=UTC))

    response = api_client.get(
        STATS_URL,
        headers=merchant_headers,
        params={"from_date": "2026-10-31", "to_date": "2026-10-31"},
    )

    assert response.status_code == 200
    assert (
        response.json()["items"][0]["last_searched_at"]
        == "2026-10-31T18:12:00-03:00"
    )


# --- Empty results ---------------------------------------------------------


def test_stats_without_events_returns_empty_list(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    _add_product(db_session, store, name="Sin eventos")

    response = api_client.get(STATS_URL, headers=merchant_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total_searches"] == 0


def test_stats_does_not_create_events(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    product = _add_product(db_session, store, name="Producto")
    _add_event(db_session, product, datetime.now(UTC))
    before = _event_count(db_session)

    response = api_client.get(STATS_URL, headers=merchant_headers)

    assert response.status_code == 200
    db_session.expire_all()
    assert _event_count(db_session) == before


# --- Validation ------------------------------------------------------------


@pytest.mark.parametrize(
    "params",
    [
        {"from_date": "2026-10-10", "to_date": "2026-10-01"},
        {"from_date": "2026-10-01"},
        {"to_date": "2026-10-01"},
        {"days": 7, "from_date": "2026-10-01", "to_date": "2026-10-10"},
        {"days": 7, "from_date": "2026-10-01"},
        {"days": 10},
        {"from_date": "no-es-fecha"},
        {"to_date": "no-es-fecha"},
    ],
)
def test_stats_reject_invalid_period_arguments(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    params: dict,
) -> None:
    response = api_client.get(
        STATS_URL, headers=merchant_headers, params=params
    )

    assert response.status_code == 422
