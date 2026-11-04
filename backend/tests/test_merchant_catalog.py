"""API tests for the merchant product catalog (CU #8)."""

from datetime import datetime, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.main import app
from app.modules.accounts.models import User
from app.modules.auth.dependencies import get_current_user
from app.modules.catalog.models import Category, Product, ProductCategory, ProductImage
from app.modules.stores.models import Store
from tests.conftest import auth_headers, requires_database

pytestmark = requires_database

PRODUCTS_URL = "/api/merchant/products"
CATEGORIES_URL = "/api/merchant/categories"


def _add_product(
    session: Session,
    store: Store,
    *,
    name: str = "Producto",
    price: str = "10.00",
    offer_price: str | None = None,
    categories: tuple[Category, ...] = (),
    image_urls: tuple[str, ...] = (),
    deleted: bool = False,
) -> Product:
    product = Product(
        store_id=store.id,
        name=name,
        price=Decimal(price),
        offer_price=Decimal(offer_price) if offer_price is not None else None,
        is_active=not deleted,
        deleted_at=datetime.now(timezone.utc) if deleted else None,
    )
    for category in categories:
        product.product_categories.append(ProductCategory(category=category))
    for position, url in enumerate(image_urls):
        product.images.append(
            ProductImage(
                url=url,
                position=position,
                is_primary=position == 0,
            )
        )
    session.add(product)
    session.commit()
    return product


def _payload(categories: list[Category], **overrides) -> dict:
    data = {
        "name": "Producto de prueba",
        "price": "10.00",
        "category_ids": [categories[0].id],
    }
    data.update(overrides)
    return data


@pytest.fixture
def categories(db_session: Session) -> list[Category]:
    items = [
        Category(name="Indumentaria"),
        Category(name="Calzado"),
        Category(name="Accesorios"),
    ]
    db_session.add_all(items)
    db_session.commit()
    return items


@pytest.fixture
def other_store(db_session: Session, store: Store) -> Store:
    item = Store(number=2, name="Local 2", side="left", position=1)
    db_session.add(item)
    db_session.commit()
    return item


@pytest.fixture
def other_merchant(db_session: Session, other_store: Store) -> User:
    user = User(
        email="otro@galeria.local",
        full_name="Otro Comerciante",
        password_hash="hash",
        role="merchant",
        is_active=True,
        store_id=other_store.id,
    )
    db_session.add(user)
    db_session.commit()
    return user


# --- Listing ---------------------------------------------------------------


def test_list_products_empty(
    api_client: TestClient, merchant_headers: dict[str, str]
) -> None:
    response = api_client.get(PRODUCTS_URL, headers=merchant_headers)

    assert response.status_code == 200
    assert response.json() == {
        "items": [],
        "total": 0,
        "page": 1,
        "page_size": 20,
        "pages": 0,
    }


def test_list_returns_only_own_store_ordered_by_name(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
    other_store: Store,
) -> None:
    _add_product(db_session, store, name="Zapato")
    _add_product(db_session, store, name="camisa")
    _add_product(db_session, other_store, name="Ajeno")

    response = api_client.get(PRODUCTS_URL, headers=merchant_headers)

    assert response.status_code == 200
    body = response.json()
    assert [item["name"] for item in body["items"]] == ["camisa", "Zapato"]
    assert body["total"] == 2


def test_search_is_case_insensitive_and_escapes_wildcards(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    _add_product(db_session, store, name="Camisa")
    _add_product(db_session, store, name="CAMPERA")
    _add_product(db_session, store, name="50% off")
    _add_product(db_session, store, name="a_b")

    by_text = api_client.get(
        PRODUCTS_URL, headers=merchant_headers, params={"search": "cAm"}
    )
    assert [item["name"] for item in by_text.json()["items"]] == [
        "Camisa",
        "CAMPERA",
    ]

    by_percent = api_client.get(
        PRODUCTS_URL, headers=merchant_headers, params={"search": "%"}
    )
    assert [item["name"] for item in by_percent.json()["items"]] == ["50% off"]

    by_underscore = api_client.get(
        PRODUCTS_URL, headers=merchant_headers, params={"search": "_"}
    )
    assert [item["name"] for item in by_underscore.json()["items"]] == ["a_b"]


def test_status_filters_active_deleted_and_all(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    _add_product(db_session, store, name="Vigente")
    _add_product(db_session, store, name="Eliminado", deleted=True)

    default = api_client.get(PRODUCTS_URL, headers=merchant_headers)
    assert [item["name"] for item in default.json()["items"]] == ["Vigente"]

    deleted = api_client.get(
        PRODUCTS_URL, headers=merchant_headers, params={"status": "deleted"}
    )
    assert [item["name"] for item in deleted.json()["items"]] == ["Eliminado"]

    every = api_client.get(
        PRODUCTS_URL, headers=merchant_headers, params={"status": "all"}
    )
    assert [item["name"] for item in every.json()["items"]] == [
        "Eliminado",
        "Vigente",
    ]

    invalid = api_client.get(
        PRODUCTS_URL, headers=merchant_headers, params={"status": "unknown"}
    )
    assert invalid.status_code == 422


def test_filter_by_category(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
    categories: list[Category],
) -> None:
    indumentaria, calzado, _ = categories
    _add_product(db_session, store, name="Remera", categories=(indumentaria,))
    _add_product(db_session, store, name="Zapatilla", categories=(calzado,))
    _add_product(
        db_session, store, name="Ambos", categories=(indumentaria, calzado)
    )

    response = api_client.get(
        PRODUCTS_URL,
        headers=merchant_headers,
        params={"category_id": calzado.id},
    )

    assert [item["name"] for item in response.json()["items"]] == [
        "Ambos",
        "Zapatilla",
    ]


def test_pagination_returns_page_metadata(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    for letter in "ABCDE":
        _add_product(db_session, store, name=f"Producto {letter}")

    response = api_client.get(
        PRODUCTS_URL,
        headers=merchant_headers,
        params={"page": 2, "page_size": 2},
    )

    body = response.json()
    assert [item["name"] for item in body["items"]] == [
        "Producto C",
        "Producto D",
    ]
    assert body["total"] == 5
    assert body["page"] == 2
    assert body["page_size"] == 2
    assert body["pages"] == 3


@pytest.mark.parametrize("params", [{"page": 0}, {"page_size": 0}, {"page_size": 101}])
def test_pagination_rejects_out_of_range_values(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    params: dict,
) -> None:
    response = api_client.get(PRODUCTS_URL, headers=merchant_headers, params=params)

    assert response.status_code == 422


# --- Create ----------------------------------------------------------------


def test_create_product_success(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    merchant_user: User,
    db_session: Session,
    categories: list[Category],
) -> None:
    indumentaria, calzado, _ = categories
    response = api_client.post(
        PRODUCTS_URL,
        headers=merchant_headers,
        json={
            "name": "  Camisa azul  ",
            "description": "Algodón",
            "price": "10.50",
            "offer_price": "8.00",
            "category_ids": [indumentaria.id, calzado.id],
            "images": [
                {"url": "https://example.com/uno.jpg", "alt_text": "Frente"},
                {"url": "https://example.com/dos.jpg"},
            ],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Camisa azul"
    assert body["description"] == "Algodón"
    assert Decimal(body["price"]) == Decimal("10.50")
    assert Decimal(body["offer_price"]) == Decimal("8.00")
    assert {category["name"] for category in body["categories"]} == {
        "Indumentaria",
        "Calzado",
    }
    assert [image["position"] for image in body["images"]] == [0, 1]
    assert [image["is_primary"] for image in body["images"]] == [True, False]
    assert body["is_active"] is True
    assert body["deleted_at"] is None
    assert "store_id" not in body
    assert "password_hash" not in response.text

    created = db_session.scalar(
        select(Product).where(Product.name == "Camisa azul")
    )
    assert created is not None
    assert created.store_id == merchant_user.store_id


def test_create_minimal_product_without_offer_or_images(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    categories: list[Category],
) -> None:
    response = api_client.post(
        PRODUCTS_URL,
        headers=merchant_headers,
        json={
            "name": "Mínimo",
            "price": "5",
            "category_ids": [categories[0].id],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["offer_price"] is None
    assert body["description"] is None
    assert body["images"] == []


def test_create_product_rejects_store_id(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    categories: list[Category],
) -> None:
    response = api_client.post(
        PRODUCTS_URL,
        headers=merchant_headers,
        json=_payload(categories, store_id=1),
    )

    assert response.status_code == 422
    assert db_session.scalar(select(func.count()).select_from(Product)) == 0


@pytest.mark.parametrize("field", ["is_featured", "is_active"])
def test_create_product_rejects_internal_fields(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    categories: list[Category],
    field: str,
) -> None:
    response = api_client.post(
        PRODUCTS_URL,
        headers=merchant_headers,
        json=_payload(categories, **{field: True}),
    )

    assert response.status_code == 422
    assert db_session.scalar(select(func.count()).select_from(Product)) == 0


@pytest.mark.parametrize(
    "overrides",
    [
        {"name": ""},
        {"name": "   "},
        {"name": "x" * 161},
        {"price": "-1.00"},
        {"price": "10.999"},
        {"description": "x" * 2001},
        {"offer_price": "10.00"},
        {"offer_price": "11.00"},
        {"category_ids": []},
        {
            "images": [
                {"url": f"https://example.com/{index}.jpg"} for index in range(6)
            ]
        },
        {"images": [{"url": "ftp://example.com/image.jpg"}]},
        {"images": [{"url": "not-a-url"}]},
        {"images": [{"url": "https://example.com/" + "a" * 490 + ".jpg"}]},
        {"images": [{"url": "https://example.com/a.jpg", "alt_text": "x" * 201}]},
    ],
)
def test_create_product_invalid_payload(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    categories: list[Category],
    overrides: dict,
) -> None:
    payload = _payload(categories)
    response = api_client.post(
        PRODUCTS_URL, headers=merchant_headers, json={**payload, **overrides}
    )

    assert response.status_code == 422
    assert db_session.scalar(select(func.count()).select_from(Product)) == 0


def test_create_product_missing_price(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    categories: list[Category],
) -> None:
    payload = _payload(categories)
    payload.pop("price")

    response = api_client.post(
        PRODUCTS_URL, headers=merchant_headers, json=payload
    )

    assert response.status_code == 422


def test_create_product_unknown_category(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    categories: list[Category],
) -> None:
    response = api_client.post(
        PRODUCTS_URL,
        headers=merchant_headers,
        json=_payload(categories, category_ids=[categories[0].id, 9999]),
    )

    assert response.status_code == 422
    assert "categor" in response.json()["detail"].lower()
    assert db_session.scalar(select(func.count()).select_from(Product)) == 0


# --- Detail and update -----------------------------------------------------


def test_get_own_product_includes_deleted(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
    categories: list[Category],
) -> None:
    product = _add_product(
        db_session,
        store,
        name="Eliminado",
        categories=(categories[0],),
        image_urls=("https://example.com/a.jpg",),
        deleted=True,
    )

    response = api_client.get(
        f"{PRODUCTS_URL}/{product.id}", headers=merchant_headers
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Eliminado"
    assert body["deleted_at"] is not None
    assert body["categories"] == [
        {"id": categories[0].id, "name": categories[0].name}
    ]
    assert body["images"][0]["is_primary"] is True


def test_get_other_store_product_returns_404(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    other_store: Store,
) -> None:
    product = _add_product(db_session, other_store, name="Ajeno")

    response = api_client.get(
        f"{PRODUCTS_URL}/{product.id}", headers=merchant_headers
    )

    assert response.status_code == 404


def test_get_unknown_product_returns_404(
    api_client: TestClient, merchant_headers: dict[str, str]
) -> None:
    response = api_client.get(f"{PRODUCTS_URL}/9999", headers=merchant_headers)

    assert response.status_code == 404


def test_update_partial_fields(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
    categories: list[Category],
) -> None:
    product = _add_product(
        db_session, store, name="Original", price="10.00", offer_price="8.00"
    )

    response = api_client.patch(
        f"{PRODUCTS_URL}/{product.id}",
        headers=merchant_headers,
        json={"name": "Actualizado", "offer_price": None},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Actualizado"
    assert Decimal(body["price"]) == Decimal("10.00")
    assert body["offer_price"] is None


def test_update_replaces_categories_and_images(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
    categories: list[Category],
) -> None:
    indumentaria, calzado, accesorios = categories
    product = _add_product(
        db_session,
        store,
        categories=(indumentaria,),
        image_urls=(
            "https://example.com/uno.jpg",
            "https://example.com/dos.jpg",
        ),
    )

    response = api_client.patch(
        f"{PRODUCTS_URL}/{product.id}",
        headers=merchant_headers,
        json={
            "category_ids": [calzado.id, accesorios.id],
            "images": [{"url": "https://example.com/nueva.jpg"}],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert {category["name"] for category in body["categories"]} == {
        "Calzado",
        "Accesorios",
    }
    assert len(body["images"]) == 1
    assert body["images"][0]["url"] == "https://example.com/nueva.jpg"
    assert body["images"][0]["position"] == 0
    assert body["images"][0]["is_primary"] is True


def test_update_offer_against_stored_price_returns_422(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    product = _add_product(db_session, store, price="10.00", offer_price="8.00")

    response = api_client.patch(
        f"{PRODUCTS_URL}/{product.id}",
        headers=merchant_headers,
        json={"offer_price": "10.00"},
    )

    assert response.status_code == 422
    db_session.refresh(product)
    assert product.offer_price == Decimal("8.00")


def test_update_deleted_product_returns_409(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    product = _add_product(db_session, store, name="Eliminado", deleted=True)

    response = api_client.patch(
        f"{PRODUCTS_URL}/{product.id}",
        headers=merchant_headers,
        json={"name": "No permitido"},
    )

    assert response.status_code == 409
    db_session.refresh(product)
    assert product.name == "Eliminado"


def test_update_unknown_category_returns_422(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    product = _add_product(db_session, store)

    response = api_client.patch(
        f"{PRODUCTS_URL}/{product.id}",
        headers=merchant_headers,
        json={"category_ids": [9999]},
    )

    assert response.status_code == 422


def test_update_other_store_product_returns_404(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    other_store: Store,
) -> None:
    product = _add_product(db_session, other_store, name="Ajeno")

    response = api_client.patch(
        f"{PRODUCTS_URL}/{product.id}",
        headers=merchant_headers,
        json={"name": "Hackeado"},
    )

    assert response.status_code == 404
    db_session.refresh(product)
    assert product.name == "Ajeno"


# --- Delete ----------------------------------------------------------------


def test_delete_is_idempotent_and_moves_between_filters(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    product = _add_product(
        db_session,
        store,
        name="Producto",
        image_urls=("https://example.com/a.jpg",),
    )

    first = api_client.delete(
        f"{PRODUCTS_URL}/{product.id}", headers=merchant_headers
    )
    second = api_client.delete(
        f"{PRODUCTS_URL}/{product.id}", headers=merchant_headers
    )

    assert first.status_code == 204
    assert second.status_code == 204

    db_session.refresh(product)
    assert product.deleted_at is not None
    assert product.is_active is False

    active = api_client.get(PRODUCTS_URL, headers=merchant_headers)
    assert active.json()["total"] == 0

    deleted = api_client.get(
        PRODUCTS_URL, headers=merchant_headers, params={"status": "deleted"}
    )
    assert deleted.json()["total"] == 1

    detail = api_client.get(
        f"{PRODUCTS_URL}/{product.id}", headers=merchant_headers
    )
    assert detail.status_code == 200
    assert len(detail.json()["images"]) == 1


def test_delete_other_store_product_returns_404(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    other_store: Store,
) -> None:
    product = _add_product(db_session, other_store, name="Ajeno")

    response = api_client.delete(
        f"{PRODUCTS_URL}/{product.id}", headers=merchant_headers
    )

    assert response.status_code == 404
    db_session.refresh(product)
    assert product.deleted_at is None


def test_delete_unknown_product_returns_404(
    api_client: TestClient, merchant_headers: dict[str, str]
) -> None:
    response = api_client.delete(f"{PRODUCTS_URL}/9999", headers=merchant_headers)

    assert response.status_code == 404


# --- Restore ---------------------------------------------------------------


def test_restore_deleted_product_brings_it_back_with_relations(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
    categories: list[Category],
) -> None:
    product = _add_product(
        db_session,
        store,
        name="Restaurable",
        price="10.00",
        offer_price="8.00",
        categories=(categories[0], categories[1]),
        image_urls=(
            "https://example.com/a.jpg",
            "https://example.com/b.jpg",
        ),
        deleted=True,
    )

    response = api_client.post(
        f"{PRODUCTS_URL}/{product.id}/restore", headers=merchant_headers
    )

    assert response.status_code == 200
    body = response.json()
    assert body["deleted_at"] is None
    assert body["is_active"] is True
    assert {category["name"] for category in body["categories"]} == {
        "Indumentaria",
        "Calzado",
    }
    assert [image["url"] for image in body["images"]] == [
        "https://example.com/a.jpg",
        "https://example.com/b.jpg",
    ]
    assert body["images"][0]["is_primary"] is True

    db_session.refresh(product)
    assert product.deleted_at is None
    assert product.is_active is True
    assert product.offer_price == Decimal("8.00")

    active = api_client.get(
        PRODUCTS_URL, headers=merchant_headers, params={"status": "active"}
    )
    assert [item["id"] for item in active.json()["items"]] == [product.id]

    deleted = api_client.get(
        PRODUCTS_URL, headers=merchant_headers, params={"status": "deleted"}
    )
    assert deleted.json()["total"] == 0


def test_restore_active_product_is_idempotent(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    store: Store,
) -> None:
    product = _add_product(db_session, store, name="Vigente")
    db_session.refresh(product)
    updated_at = product.updated_at

    response = api_client.post(
        f"{PRODUCTS_URL}/{product.id}/restore", headers=merchant_headers
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Vigente"
    assert body["deleted_at"] is None
    assert body["is_active"] is True

    db_session.refresh(product)
    assert product.updated_at == updated_at
    assert product.deleted_at is None


def test_restore_other_store_product_returns_404(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    db_session: Session,
    other_store: Store,
) -> None:
    product = _add_product(db_session, other_store, name="Ajeno", deleted=True)

    response = api_client.post(
        f"{PRODUCTS_URL}/{product.id}/restore", headers=merchant_headers
    )

    assert response.status_code == 404
    db_session.refresh(product)
    assert product.deleted_at is not None


def test_restore_unknown_product_returns_404(
    api_client: TestClient, merchant_headers: dict[str, str]
) -> None:
    response = api_client.post(
        f"{PRODUCTS_URL}/9999/restore", headers=merchant_headers
    )

    assert response.status_code == 404


# --- Categories ------------------------------------------------------------


def test_categories_are_ordered(
    api_client: TestClient,
    merchant_headers: dict[str, str],
    categories: list[Category],
) -> None:
    response = api_client.get(CATEGORIES_URL, headers=merchant_headers)

    assert response.status_code == 200
    assert response.json() == [
        {"id": categories[2].id, "name": "Accesorios"},
        {"id": categories[1].id, "name": "Calzado"},
        {"id": categories[0].id, "name": "Indumentaria"},
    ]


# --- Authorization ---------------------------------------------------------


@pytest.mark.parametrize(
    ("method", "url"),
    [
        ("get", PRODUCTS_URL),
        ("post", PRODUCTS_URL),
        ("get", f"{PRODUCTS_URL}/1"),
        ("patch", f"{PRODUCTS_URL}/1"),
        ("delete", f"{PRODUCTS_URL}/1"),
        ("post", f"{PRODUCTS_URL}/1/restore"),
        ("get", CATEGORIES_URL),
    ],
)
def test_catalog_requires_token(
    api_client: TestClient, method: str, url: str
) -> None:
    response = api_client.request(method.upper(), url)

    assert response.status_code == 401


@pytest.mark.parametrize(
    ("method", "url"),
    [
        ("get", PRODUCTS_URL),
        ("post", PRODUCTS_URL),
        ("get", f"{PRODUCTS_URL}/1"),
        ("patch", f"{PRODUCTS_URL}/1"),
        ("delete", f"{PRODUCTS_URL}/1"),
        ("post", f"{PRODUCTS_URL}/1/restore"),
        ("get", CATEGORIES_URL),
    ],
)
def test_catalog_forbids_admin(
    api_client: TestClient,
    admin_headers: dict[str, str],
    method: str,
    url: str,
) -> None:
    response = api_client.request(method.upper(), url, headers=admin_headers)

    assert response.status_code == 403


def test_merchant_without_store_gets_403(api_client: TestClient) -> None:
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
        response = api_client.get(
            PRODUCTS_URL, headers=auth_headers(orphan)
        )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 403
