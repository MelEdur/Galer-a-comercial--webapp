"""API tests for the public product search (CU #1)."""

from datetime import datetime, time, timedelta, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.analytics.models import ProductSearchEvent
from app.modules.catalog.models import Category, Product, ProductCategory, ProductImage
from app.modules.stores.models import Store, StoreHour, StoreLink
from tests.conftest import requires_database

pytestmark = requires_database

PRODUCTS_URL = "/api/public/products"
CATEGORIES_URL = "/api/public/categories"
STORES_URL = "/api/public/stores"


def _add_product(
    session: Session,
    store: Store,
    *,
    name: str = "Producto",
    description: str | None = None,
    price: str = "10.00",
    offer_price: str | None = None,
    categories: tuple[Category, ...] = (),
    image_urls: tuple[str, ...] = (),
    is_active: bool = True,
    deleted: bool = False,
    created_at: datetime | None = None,
) -> Product:
    product = Product(
        store_id=store.id,
        name=name,
        description=description,
        price=Decimal(price),
        offer_price=Decimal(offer_price) if offer_price is not None else None,
        is_active=is_active and not deleted,
        deleted_at=datetime.now(timezone.utc) if deleted else None,
        **({"created_at": created_at} if created_at is not None else {}),
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


def _event_count(session: Session) -> int:
    return session.scalar(select(func.count()).select_from(ProductSearchEvent)) or 0


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
def inactive_store(db_session: Session, store: Store, other_store: Store) -> Store:
    item = Store(
        number=3, name="Local 3", side="left", position=2, is_active=False
    )
    db_session.add(item)
    db_session.commit()
    return item


# --- Contract --------------------------------------------------------------


def test_public_search_without_token_returns_expected_contract(
    api_client: TestClient,
    db_session: Session,
    store: Store,
    categories: list[Category],
) -> None:
    _add_product(
        db_session,
        store,
        name="Remera",
        description="Algodón",
        price="1500.00",
        offer_price="1200.00",
        categories=(categories[0],),
        image_urls=("https://example.com/remera.jpg",),
    )

    response = api_client.get(PRODUCTS_URL)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["page"] == 1
    assert body["page_size"] == 20
    assert body["pages"] == 1

    item = body["items"][0]
    assert set(item) == {
        "id",
        "name",
        "description",
        "price",
        "offer_price",
        "effective_price",
        "categories",
        "primary_image",
        "store",
    }
    assert item["name"] == "Remera"
    assert item["description"] == "Algodón"
    assert item["price"] == "1500.00"
    assert item["offer_price"] == "1200.00"
    assert item["effective_price"] == "1200.00"
    assert item["categories"] == [
        {"id": categories[0].id, "name": categories[0].name}
    ]
    assert item["primary_image"] == {
        "url": "https://example.com/remera.jpg",
        "alt_text": None,
    }
    assert item["store"] == {"id": store.id, "number": 1, "name": "Local 1"}
    assert "store_id" not in item
    assert "is_active" not in item
    assert "deleted_at" not in item
    assert "password" not in response.text.lower()


def test_primary_image_uses_lowest_position_when_no_flag(
    api_client: TestClient,
    db_session: Session,
    store: Store,
) -> None:
    product = Product(
        store_id=store.id,
        name="Con imágenes",
        price=Decimal("10.00"),
        is_active=True,
    )
    product.images.append(
        ProductImage(url="https://example.com/b.jpg", position=1, is_primary=False)
    )
    product.images.append(
        ProductImage(url="https://example.com/a.jpg", position=0, is_primary=False)
    )
    db_session.add(product)
    db_session.commit()

    response = api_client.get(PRODUCTS_URL)

    assert response.status_code == 200
    assert response.json()["items"][0]["primary_image"]["url"] == (
        "https://example.com/a.jpg"
    )


def test_product_without_images_has_null_primary_image(
    api_client: TestClient, db_session: Session, store: Store
) -> None:
    _add_product(db_session, store, name="Sin imagen")

    response = api_client.get(PRODUCTS_URL)

    assert response.json()["items"][0]["primary_image"] is None


# --- Name search -----------------------------------------------------------


def test_search_is_partial_and_case_insensitive(
    api_client: TestClient, db_session: Session, store: Store
) -> None:
    _add_product(db_session, store, name="Camisa")
    _add_product(db_session, store, name="CAMPERA")
    _add_product(db_session, store, name="Pantalón")

    response = api_client.get(PRODUCTS_URL, params={"search": "cAm"})

    assert response.status_code == 200
    assert [item["name"] for item in response.json()["items"]] == [
        "Camisa",
        "CAMPERA",
    ]


def test_search_treats_wildcards_as_literal_characters(
    api_client: TestClient, db_session: Session, store: Store
) -> None:
    _add_product(db_session, store, name="50% off")
    _add_product(db_session, store, name="a_b")
    _add_product(db_session, store, name="aXb")

    by_percent = api_client.get(PRODUCTS_URL, params={"search": "%"})
    assert [item["name"] for item in by_percent.json()["items"]] == ["50% off"]

    by_underscore = api_client.get(PRODUCTS_URL, params={"search": "_"})
    assert [item["name"] for item in by_underscore.json()["items"]] == ["a_b"]


def test_empty_search_is_treated_as_no_criteria(
    api_client: TestClient, db_session: Session, store: Store
) -> None:
    _add_product(db_session, store, name="Uno")
    _add_product(db_session, store, name="Dos")

    response = api_client.get(PRODUCTS_URL, params={"search": "   "})

    assert response.status_code == 200
    assert response.json()["total"] == 2


# --- Category filter -------------------------------------------------------


def test_filter_by_category_with_and_without_results(
    api_client: TestClient,
    db_session: Session,
    store: Store,
    categories: list[Category],
) -> None:
    indumentaria, calzado, accesorios = categories
    _add_product(db_session, store, name="Remera", categories=(indumentaria,))
    _add_product(db_session, store, name="Zapatilla", categories=(calzado,))

    with_results = api_client.get(
        PRODUCTS_URL, params={"category_id": calzado.id}
    )
    assert [item["name"] for item in with_results.json()["items"]] == [
        "Zapatilla"
    ]

    without_results = api_client.get(
        PRODUCTS_URL, params={"category_id": accesorios.id}
    )
    assert without_results.json()["items"] == []
    assert without_results.json()["total"] == 0


# --- Price filters ---------------------------------------------------------


def test_filter_by_min_price_inclusive(
    api_client: TestClient, db_session: Session, store: Store
) -> None:
    _add_product(db_session, store, name="Barato", price="5.00")
    _add_product(db_session, store, name="Medio", price="10.00")
    _add_product(db_session, store, name="Caro", price="20.00")

    response = api_client.get(PRODUCTS_URL, params={"min_price": "10.00"})

    assert [item["name"] for item in response.json()["items"]] == [
        "Caro",
        "Medio",
    ]


def test_filter_by_max_price_inclusive(
    api_client: TestClient, db_session: Session, store: Store
) -> None:
    _add_product(db_session, store, name="Barato", price="5.00")
    _add_product(db_session, store, name="Medio", price="10.00")
    _add_product(db_session, store, name="Caro", price="20.00")

    response = api_client.get(PRODUCTS_URL, params={"max_price": "10.00"})

    assert [item["name"] for item in response.json()["items"]] == [
        "Barato",
        "Medio",
    ]


def test_filter_by_price_range(
    api_client: TestClient, db_session: Session, store: Store
) -> None:
    _add_product(db_session, store, name="Barato", price="5.00")
    _add_product(db_session, store, name="Medio", price="10.00")
    _add_product(db_session, store, name="Caro", price="20.00")

    response = api_client.get(
        PRODUCTS_URL, params={"min_price": "7.00", "max_price": "15.00"}
    )

    assert [item["name"] for item in response.json()["items"]] == ["Medio"]


def test_price_filter_uses_effective_offer_price(
    api_client: TestClient, db_session: Session, store: Store
) -> None:
    _add_product(
        db_session,
        store,
        name="Oferta",
        price="20.00",
        offer_price="8.00",
    )

    within = api_client.get(PRODUCTS_URL, params={"max_price": "10.00"})
    assert within.json()["total"] == 1
    assert within.json()["items"][0]["effective_price"] == "8.00"

    excluded = api_client.get(PRODUCTS_URL, params={"min_price": "15.00"})
    assert excluded.json()["total"] == 0


def test_invalid_price_range_returns_422(
    api_client: TestClient,
) -> None:
    response = api_client.get(
        PRODUCTS_URL, params={"min_price": "20.00", "max_price": "10.00"}
    )

    assert response.status_code == 422


@pytest.mark.parametrize("field", ["min_price", "max_price"])
def test_negative_price_returns_422(
    api_client: TestClient, field: str
) -> None:
    response = api_client.get(PRODUCTS_URL, params={field: "-1.00"})

    assert response.status_code == 422


# --- Combined filters ------------------------------------------------------


def test_combines_name_category_and_price_filters(
    api_client: TestClient,
    db_session: Session,
    store: Store,
    categories: list[Category],
) -> None:
    indumentaria, calzado, _ = categories
    _add_product(
        db_session,
        store,
        name="Remera Azul",
        price="100.00",
        categories=(indumentaria,),
    )
    _add_product(
        db_session,
        store,
        name="Remera Roja",
        price="300.00",
        categories=(indumentaria,),
    )
    _add_product(
        db_session,
        store,
        name="Remera Verde",
        price="150.00",
        categories=(calzado,),
    )
    _add_product(
        db_session,
        store,
        name="Pantalón Azul",
        price="120.00",
        categories=(indumentaria,),
    )

    response = api_client.get(
        PRODUCTS_URL,
        params={
            "search": "remera",
            "category_id": indumentaria.id,
            "min_price": "50.00",
            "max_price": "200.00",
        },
    )

    assert [item["name"] for item in response.json()["items"]] == [
        "Remera Azul"
    ]


# --- Availability ----------------------------------------------------------


def test_only_available_products_are_returned(
    api_client: TestClient,
    db_session: Session,
    store: Store,
    other_store: Store,
    inactive_store: Store,
) -> None:
    _add_product(db_session, store, name="Disponible")
    _add_product(db_session, store, name="Eliminado", deleted=True)
    _add_product(db_session, store, name="Inactivo", is_active=False)
    _add_product(db_session, inactive_store, name="Local inactivo")
    _add_product(db_session, other_store, name="Otro local activo")

    response = api_client.get(PRODUCTS_URL)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert {item["name"] for item in body["items"]} == {
        "Disponible",
        "Otro local activo",
    }


# --- Ordering --------------------------------------------------------------


def test_order_by_name_is_case_insensitive(
    api_client: TestClient, db_session: Session, store: Store
) -> None:
    _add_product(db_session, store, name="Zapato")
    _add_product(db_session, store, name="camisa")

    response = api_client.get(PRODUCTS_URL)

    assert [item["name"] for item in response.json()["items"]] == [
        "camisa",
        "Zapato",
    ]


@pytest.mark.parametrize(
    ("sort", "expected"),
    [
        ("price_asc", ["Barato", "Medio", "Caro"]),
        ("price_desc", ["Caro", "Medio", "Barato"]),
    ],
)
def test_order_by_effective_price(
    api_client: TestClient,
    db_session: Session,
    store: Store,
    sort: str,
    expected: list[str],
) -> None:
    _add_product(db_session, store, name="Medio", price="10.00")
    _add_product(db_session, store, name="Barato", price="20.00", offer_price="5.00")
    _add_product(db_session, store, name="Caro", price="30.00")

    response = api_client.get(PRODUCTS_URL, params={"sort": sort})

    assert [item["name"] for item in response.json()["items"]] == expected


# --- Pagination ------------------------------------------------------------


def test_pagination_returns_page_metadata(
    api_client: TestClient, db_session: Session, store: Store
) -> None:
    for letter in "ABCDE":
        _add_product(db_session, store, name=f"Producto {letter}")

    response = api_client.get(
        PRODUCTS_URL, params={"page": 2, "page_size": 2}
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


@pytest.mark.parametrize(
    "params", [{"page": 0}, {"page_size": 0}, {"page_size": 101}]
)
def test_pagination_rejects_out_of_range_values(
    api_client: TestClient, params: dict
) -> None:
    response = api_client.get(PRODUCTS_URL, params=params)

    assert response.status_code == 422


def test_search_without_criteria_returns_all_available(
    api_client: TestClient, db_session: Session, store: Store
) -> None:
    _add_product(db_session, store, name="Uno")
    _add_product(db_session, store, name="Dos")
    _add_product(db_session, store, name="Tres")
    _add_product(db_session, store, name="Eliminado", deleted=True)

    response = api_client.get(PRODUCTS_URL)

    body = response.json()
    assert body["total"] == 3
    assert len(body["items"]) == 3


# --- Public categories -----------------------------------------------------


def test_public_categories_are_ordered_by_name(
    api_client: TestClient, db_session: Session
) -> None:
    db_session.add_all(
        [
            Category(name="Zapatos"),
            Category(name="accesorios"),
            Category(name="Indumentaria"),
        ]
    )
    db_session.commit()

    response = api_client.get(CATEGORIES_URL)

    assert response.status_code == 200
    assert [category["name"] for category in response.json()] == [
        "accesorios",
        "Indumentaria",
        "Zapatos",
    ]


def test_public_categories_do_not_require_token(api_client: TestClient) -> None:
    response = api_client.get(CATEGORIES_URL)

    assert response.status_code == 200
    assert response.json() == []


# --- Search events ---------------------------------------------------------


def test_search_with_criteria_records_one_event_per_page_product(
    api_client: TestClient, db_session: Session, store: Store
) -> None:
    products = [
        _add_product(db_session, store, name=f"Remera {index}")
        for index in range(3)
    ]

    response = api_client.get(
        PRODUCTS_URL, params={"search": "remera", "page_size": 2}
    )

    assert response.status_code == 200
    assert response.json()["total"] == 3
    assert len(response.json()["items"]) == 2

    events = db_session.scalars(select(ProductSearchEvent)).all()
    assert len(events) == 2
    assert {event.query for event in events} == {"remera"}
    returned_ids = {item["id"] for item in response.json()["items"]}
    assert {event.product_id for event in events} == returned_ids
    assert {product.id for product in products} >= returned_ids


def test_search_without_criteria_records_no_events(
    api_client: TestClient, db_session: Session, store: Store
) -> None:
    _add_product(db_session, store, name="Uno")
    _add_product(db_session, store, name="Dos")

    response = api_client.get(PRODUCTS_URL)

    assert response.status_code == 200
    assert response.json()["total"] == 2
    assert _event_count(db_session) == 0


def test_search_without_results_records_no_events(
    api_client: TestClient, db_session: Session, store: Store
) -> None:
    _add_product(db_session, store, name="Uno")

    response = api_client.get(PRODUCTS_URL, params={"search": "inexistente"})

    assert response.status_code == 200
    assert response.json()["total"] == 0
    assert _event_count(db_session) == 0


@pytest.mark.parametrize(
    "params",
    [
        {"category_id": 9999},
        {"min_price": "100.00"},
        {"max_price": "1.00"},
        {"search": "zzz"},
    ],
)
def test_categorized_search_without_results_records_no_events(
    api_client: TestClient, db_session: Session, store: Store, params: dict
) -> None:
    _add_product(db_session, store, name="Uno", price="10.00")

    response = api_client.get(PRODUCTS_URL, params=params)

    assert response.status_code == 200
    assert response.json()["total"] == 0
    assert _event_count(db_session) == 0


def test_events_are_kept_after_product_is_deleted(
    api_client: TestClient, db_session: Session, store: Store
) -> None:
    product = _add_product(db_session, store, name="Remera")

    api_client.get(PRODUCTS_URL, params={"search": "remera"})
    db_session.expire_all()
    assert _event_count(db_session) == 1

    product.is_active = False
    product.deleted_at = datetime.now(timezone.utc)
    db_session.commit()

    db_session.expire_all()
    assert _event_count(db_session) == 1

    after = api_client.get(PRODUCTS_URL, params={"search": "remera"})
    assert after.json()["total"] == 0


# --- Product detail (CU #3) ------------------------------------------------


def test_product_detail_without_token_returns_public_contract(
    api_client: TestClient,
    db_session: Session,
    store: Store,
    categories: list[Category],
) -> None:
    store.logo_url = "https://example.com/logo.png"
    store.email = "local@galeria.local"
    store.phone = "1122334455"
    store.whatsapp = "1122334455"
    db_session.commit()

    product = _add_product(
        db_session,
        store,
        name="Remera",
        description="Algodón",
        price="1500.00",
        offer_price="1200.00",
        categories=(categories[0],),
        image_urls=("https://example.com/remera.jpg",),
    )

    response = api_client.get(f"{PRODUCTS_URL}/{product.id}")

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {
        "id",
        "name",
        "description",
        "price",
        "offer_price",
        "effective_price",
        "categories",
        "images",
        "store",
    }
    assert body["id"] == product.id
    assert body["name"] == "Remera"
    assert body["description"] == "Algodón"
    assert body["price"] == "1500.00"
    assert body["offer_price"] == "1200.00"
    assert body["effective_price"] == "1200.00"
    assert body["categories"] == [
        {"id": categories[0].id, "name": categories[0].name}
    ]
    assert len(body["images"]) == 1
    image = body["images"][0]
    assert set(image) == {"id", "url", "alt_text", "position", "is_primary"}
    assert image["url"] == "https://example.com/remera.jpg"
    assert image["alt_text"] is None
    assert image["position"] == 0
    assert image["is_primary"] is True
    assert body["store"] == {
        "id": store.id,
        "number": 1,
        "name": "Local 1",
        "logo_url": "https://example.com/logo.png",
        "email": "local@galeria.local",
        "phone": "1122334455",
        "whatsapp": "1122334455",
    }
    assert "store_id" not in body
    assert "is_active" not in body
    assert "deleted_at" not in body
    assert "password" not in response.text.lower()


def test_product_detail_orders_images_by_position_and_marks_primary(
    api_client: TestClient,
    db_session: Session,
    store: Store,
) -> None:
    product = Product(
        store_id=store.id,
        name="Galería",
        price=Decimal("10.00"),
        is_active=True,
    )
    db_session.add(product)
    db_session.flush()
    db_session.add_all(
        [
            ProductImage(
                product_id=product.id,
                url="https://example.com/tercera.jpg",
                alt_text="Tercera",
                position=2,
                is_primary=False,
            ),
            ProductImage(
                product_id=product.id,
                url="https://example.com/primera.jpg",
                alt_text="Primera",
                position=0,
                is_primary=False,
            ),
            ProductImage(
                product_id=product.id,
                url="https://example.com/segunda.jpg",
                alt_text="Segunda",
                position=1,
                is_primary=True,
            ),
        ]
    )
    db_session.commit()

    response = api_client.get(f"{PRODUCTS_URL}/{product.id}")

    assert response.status_code == 200
    images = response.json()["images"]
    assert [image["url"] for image in images] == [
        "https://example.com/primera.jpg",
        "https://example.com/segunda.jpg",
        "https://example.com/tercera.jpg",
    ]
    assert [image["position"] for image in images] == [0, 1, 2]
    assert [image["is_primary"] for image in images] == [False, True, False]


def test_product_detail_without_offer_uses_base_price(
    api_client: TestClient,
    db_session: Session,
    store: Store,
) -> None:
    product = _add_product(db_session, store, name="Precio", price="1500.00")

    response = api_client.get(f"{PRODUCTS_URL}/{product.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["price"] == "1500.00"
    assert body["offer_price"] is None
    assert body["effective_price"] == "1500.00"


def test_product_detail_with_store_without_optional_fields(
    api_client: TestClient,
    db_session: Session,
    store: Store,
) -> None:
    product = _add_product(db_session, store, name="Sin contacto")

    response = api_client.get(f"{PRODUCTS_URL}/{product.id}")

    assert response.status_code == 200
    assert response.json()["store"] == {
        "id": store.id,
        "number": 1,
        "name": "Local 1",
        "logo_url": None,
        "email": None,
        "phone": None,
        "whatsapp": None,
    }


def test_product_detail_404_when_product_is_not_available(
    api_client: TestClient,
    db_session: Session,
    store: Store,
    inactive_store: Store,
) -> None:
    deleted = _add_product(db_session, store, name="Eliminado", deleted=True)
    inactive = _add_product(db_session, store, name="Inactivo", is_active=False)
    inactive_store_product = _add_product(
        db_session, inactive_store, name="Local inactivo"
    )

    for product_id in (
        deleted.id,
        inactive.id,
        inactive_store_product.id,
        999999,
    ):
        response = api_client.get(f"{PRODUCTS_URL}/{product_id}")

        assert response.status_code == 404


def test_product_detail_non_numeric_id_returns_422(
    api_client: TestClient,
) -> None:
    response = api_client.get(f"{PRODUCTS_URL}/abc")

    assert response.status_code == 422


# --- Similar products (CU #3) ----------------------------------------------


def test_similar_products_by_shared_category(
    api_client: TestClient,
    db_session: Session,
    store: Store,
    categories: list[Category],
) -> None:
    indumentaria, calzado, _ = categories
    base = _add_product(
        db_session, store, name="Remera", categories=(indumentaria,)
    )
    same_category = _add_product(
        db_session, store, name="Zapatilla", categories=(indumentaria,)
    )
    _add_product(db_session, store, name="Lámpara", categories=(calzado,))

    response = api_client.get(f"{PRODUCTS_URL}/{base.id}/similar")

    assert response.status_code == 200
    items = response.json()["items"]
    assert [item["name"] for item in items] == ["Zapatilla"]
    assert set(items[0]) == {
        "id",
        "name",
        "description",
        "price",
        "offer_price",
        "effective_price",
        "categories",
        "primary_image",
        "store",
    }
    assert items[0]["store"] == {
        "id": store.id,
        "number": 1,
        "name": "Local 1",
    }
    assert items[0]["id"] == same_category.id


def test_similar_products_by_word_in_name(
    api_client: TestClient,
    db_session: Session,
    store: Store,
) -> None:
    base = _add_product(db_session, store, name="Campera")
    _add_product(db_session, store, name="Campera Azul")
    _add_product(db_session, store, name="Pantalón")

    response = api_client.get(f"{PRODUCTS_URL}/{base.id}/similar")

    assert response.status_code == 200
    assert [item["name"] for item in response.json()["items"]] == [
        "Campera Azul"
    ]


def test_similar_products_prioritize_shared_categories(
    api_client: TestClient,
    db_session: Session,
    store: Store,
    categories: list[Category],
) -> None:
    indumentaria, calzado, _ = categories
    base = _add_product(
        db_session,
        store,
        name="Remera",
        categories=(indumentaria, calzado),
    )
    _add_product(
        db_session, store, name="Zapatilla", categories=(indumentaria,)
    )
    _add_product(
        db_session,
        store,
        name="Bufanda",
        categories=(indumentaria, calzado),
    )

    response = api_client.get(f"{PRODUCTS_URL}/{base.id}/similar")

    assert [item["name"] for item in response.json()["items"]] == [
        "Bufanda",
        "Zapatilla",
    ]


def test_similar_products_exclude_current_and_limit_to_six(
    api_client: TestClient,
    db_session: Session,
    store: Store,
    categories: list[Category],
) -> None:
    indumentaria = categories[0]
    base = _add_product(
        db_session, store, name="Remera", categories=(indumentaria,)
    )
    for index in range(8):
        _add_product(
            db_session,
            store,
            name=f"Producto {index}",
            categories=(indumentaria,),
        )

    response = api_client.get(f"{PRODUCTS_URL}/{base.id}/similar")

    assert response.status_code == 200
    names = [item["name"] for item in response.json()["items"]]
    assert len(names) == 6
    assert base.name not in names
    assert base.id not in {
        item["id"] for item in response.json()["items"]
    }


def test_similar_products_empty_without_categories_or_significant_words(
    api_client: TestClient,
    db_session: Session,
    store: Store,
    categories: list[Category],
) -> None:
    base = _add_product(db_session, store, name="AB")
    _add_product(db_session, store, name="AB Camisa", categories=(categories[0],))

    response = api_client.get(f"{PRODUCTS_URL}/{base.id}/similar")

    assert response.status_code == 200
    assert response.json() == {"items": []}


def test_similar_products_skips_unavailable_candidates(
    api_client: TestClient,
    db_session: Session,
    store: Store,
    inactive_store: Store,
    categories: list[Category],
) -> None:
    indumentaria = categories[0]
    base = _add_product(
        db_session, store, name="Remera", categories=(indumentaria,)
    )
    _add_product(
        db_session, store, name="Eliminada", categories=(indumentaria,), deleted=True
    )
    _add_product(
        db_session,
        store,
        name="Inactiva",
        categories=(indumentaria,),
        is_active=False,
    )
    _add_product(
        db_session,
        inactive_store,
        name="Local inactivo",
        categories=(indumentaria,),
    )
    available = _add_product(
        db_session, store, name="Disponible", categories=(indumentaria,)
    )

    response = api_client.get(f"{PRODUCTS_URL}/{base.id}/similar")

    assert [item["id"] for item in response.json()["items"]] == [available.id]


@pytest.mark.parametrize(
    ("deleted", "is_active"), [(True, False), (False, False)]
)
def test_similar_products_404_when_base_product_is_not_available(
    api_client: TestClient,
    db_session: Session,
    store: Store,
    deleted: bool,
    is_active: bool,
) -> None:
    product = _add_product(
        db_session,
        store,
        name="Remera",
        deleted=deleted,
        is_active=is_active,
    )

    response = api_client.get(f"{PRODUCTS_URL}/{product.id}/similar")

    assert response.status_code == 404


def test_similar_products_404_for_unknown_product(
    api_client: TestClient,
) -> None:
    response = api_client.get(f"{PRODUCTS_URL}/999999/similar")

    assert response.status_code == 404


# --- Store profile (CU #4) -------------------------------------------------


def _add_hours(session: Session, store: Store, rows: list[tuple[int, str, str]]) -> None:
    for day_of_week, opens_at, closes_at in rows:
        session.add(
            StoreHour(
                store_id=store.id,
                day_of_week=day_of_week,
                opens_at=time.fromisoformat(opens_at),
                closes_at=time.fromisoformat(closes_at),
            )
        )
    session.commit()


def _add_links(
    session: Session, store: Store, rows: list[tuple[str, str, int]]
) -> None:
    for label, url, position in rows:
        session.add(
            StoreLink(
                store_id=store.id,
                label=label,
                url=url,
                position=position,
            )
        )
    session.commit()


def test_store_profile_without_token_returns_public_contract(
    api_client: TestClient,
    db_session: Session,
    store: Store,
) -> None:
    store.description = "Descripción"
    store.logo_url = "https://example.com/logo.png"
    store.email = "local@galeria.local"
    store.phone = "1122334455"
    store.whatsapp = "5491122334455"
    db_session.commit()
    _add_hours(db_session, store, [(0, "09:00:00", "13:00:00")])
    _add_links(
        db_session,
        store,
        [("Instagram", "https://instagram.com/local", 0)],
    )

    response = api_client.get(f"{STORES_URL}/{store.id}")

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {
        "id",
        "number",
        "name",
        "description",
        "logo_url",
        "email",
        "phone",
        "whatsapp",
        "hours",
        "links",
    }
    assert body["id"] == store.id
    assert body["number"] == 1
    assert body["name"] == "Local 1"
    assert body["description"] == "Descripción"
    assert body["logo_url"] == "https://example.com/logo.png"
    assert body["email"] == "local@galeria.local"
    assert body["phone"] == "1122334455"
    assert body["whatsapp"] == "5491122334455"
    assert body["hours"] == [
        {"day_of_week": 0, "opens_at": "09:00:00", "closes_at": "13:00:00"}
    ]
    assert set(body["hours"][0]) == {"day_of_week", "opens_at", "closes_at"}
    assert body["links"] == [
        {
            "label": "Instagram",
            "url": "https://instagram.com/local",
            "position": 0,
        }
    ]
    assert set(body["links"][0]) == {"label", "url", "position"}


def test_store_profile_without_description_or_logo_and_partial_contact(
    api_client: TestClient,
    db_session: Session,
    store: Store,
) -> None:
    store.email = "local@galeria.local"
    db_session.commit()

    response = api_client.get(f"{STORES_URL}/{store.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["description"] is None
    assert body["logo_url"] is None
    assert body["email"] == "local@galeria.local"
    assert body["phone"] is None
    assert body["whatsapp"] is None


def test_store_profile_orders_hours_and_links(
    api_client: TestClient,
    db_session: Session,
    store: Store,
) -> None:
    _add_hours(
        db_session,
        store,
        [
            (0, "15:00:00", "19:00:00"),
            (1, "09:00:00", "13:00:00"),
            (0, "09:00:00", "13:00:00"),
        ],
    )
    _add_links(
        db_session,
        store,
        [
            ("Web", "https://web.example", 2),
            ("Instagram", "https://instagram.example", 0),
            ("Facebook", "https://facebook.example", 1),
        ],
    )

    response = api_client.get(f"{STORES_URL}/{store.id}")

    assert response.status_code == 200
    body = response.json()
    assert [(hour["day_of_week"], hour["opens_at"]) for hour in body["hours"]] == [
        (0, "09:00:00"),
        (0, "15:00:00"),
        (1, "09:00:00"),
    ]
    assert [link["label"] for link in body["links"]] == [
        "Instagram",
        "Facebook",
        "Web",
    ]
    assert [link["position"] for link in body["links"]] == [0, 1, 2]


def test_store_profile_without_hours_contact_or_links(
    api_client: TestClient,
    store: Store,
) -> None:
    response = api_client.get(f"{STORES_URL}/{store.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["hours"] == []
    assert body["links"] == []
    assert body["email"] is None
    assert body["phone"] is None
    assert body["whatsapp"] is None


def test_store_profile_404_for_inactive_and_unknown_store(
    api_client: TestClient,
    inactive_store: Store,
) -> None:
    for store_id in (inactive_store.id, 999999):
        response = api_client.get(f"{STORES_URL}/{store_id}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Local no encontrado."


def test_store_profile_non_numeric_id_returns_422(
    api_client: TestClient,
) -> None:
    response = api_client.get(f"{STORES_URL}/abc")

    assert response.status_code == 422


def test_store_profile_does_not_expose_internal_data(
    api_client: TestClient,
    db_session: Session,
    store: Store,
) -> None:
    _add_hours(db_session, store, [(0, "09:00:00", "13:00:00")])
    _add_links(db_session, store, [("Web", "https://web.example", 0)])
    _add_product(db_session, store, name="Remera")

    response = api_client.get(f"{STORES_URL}/{store.id}")

    assert response.status_code == 200
    body = response.json()
    assert "is_active" not in body
    assert "side" not in body
    assert "position" not in body
    assert "store_id" not in body
    lowered = response.text.lower()
    assert "password" not in lowered
    assert "products" not in lowered
    assert "accounts" not in lowered
    assert "merchants" not in lowered


# --- Explore (CU #2) -------------------------------------------------------

EXPLORE_URL = "/api/public/explore"
PUBLIC_STORES_URL = "/api/public/stores"


def _at(minutes: int) -> datetime:
    return datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(minutes=minutes)


def test_explore_without_token_returns_expected_contract(
    api_client: TestClient,
    db_session: Session,
    store: Store,
    categories: list[Category],
) -> None:
    _add_product(
        db_session,
        store,
        name="Remera en oferta",
        price="1500.00",
        offer_price="1200.00",
        categories=(categories[0],),
        image_urls=("https://example.com/remera.jpg",),
    )

    response = api_client.get(EXPLORE_URL)

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"featured", "offers", "categories", "stores"}

    product = body["featured"][0]
    assert set(product) == {
        "id",
        "name",
        "description",
        "price",
        "offer_price",
        "effective_price",
        "categories",
        "primary_image",
        "store",
    }
    assert product["name"] == "Remera en oferta"
    assert "store_id" not in product
    assert "is_active" not in product

    assert set(body["categories"][0]) == {"id", "name", "product_count"}
    assert body["stores"] == [
        {
            "id": store.id,
            "number": store.number,
            "name": store.name,
            "description": None,
            "logo_url": None,
        }
    ]
    assert "password" not in response.text.lower()


def test_explore_featured_starts_with_recent_offers(
    api_client: TestClient, db_session: Session, store: Store
) -> None:
    _add_product(
        db_session,
        store,
        name="Oferta antigua",
        price="100.00",
        offer_price="80.00",
        created_at=_at(1),
    )
    _add_product(
        db_session,
        store,
        name="Novedad sin oferta",
        price="100.00",
        created_at=_at(5),
    )
    _add_product(
        db_session,
        store,
        name="Oferta reciente",
        price="100.00",
        offer_price="70.00",
        created_at=_at(3),
    )

    response = api_client.get(EXPLORE_URL)

    assert [item["name"] for item in response.json()["featured"]] == [
        "Oferta reciente",
        "Oferta antigua",
        "Novedad sin oferta",
    ]


def test_explore_featured_fills_with_newest_without_repeating_and_limits(
    api_client: TestClient, db_session: Session, store: Store
) -> None:
    _add_product(
        db_session,
        store,
        name="Oferta A",
        price="100.00",
        offer_price="80.00",
        created_at=_at(1),
    )
    _add_product(
        db_session,
        store,
        name="Oferta B",
        price="100.00",
        offer_price="80.00",
        created_at=_at(2),
    )
    for index in range(8):
        _add_product(
            db_session,
            store,
            name=f"Novedad {index}",
            price="100.00",
            created_at=_at(10 + index),
        )

    featured = api_client.get(EXPLORE_URL).json()["featured"]

    names = [item["name"] for item in featured]
    assert len(featured) == 8
    assert names[:2] == ["Oferta B", "Oferta A"]
    assert len(set(names)) == 8
    # The six newest products (Novedad 7..2) complete the section.
    assert names[2:] == [
        "Novedad 7",
        "Novedad 6",
        "Novedad 5",
        "Novedad 4",
        "Novedad 3",
        "Novedad 2",
    ]


def test_explore_offers_only_include_offers_ordered_and_limited(
    api_client: TestClient, db_session: Session, store: Store
) -> None:
    for index in range(10):
        _add_product(
            db_session,
            store,
            name=f"Oferta {index}",
            price="100.00",
            offer_price="80.00",
            created_at=_at(index),
        )
    _add_product(
        db_session,
        store,
        name="Sin oferta",
        price="100.00",
        created_at=_at(20),
    )

    offers = api_client.get(EXPLORE_URL).json()["offers"]

    assert len(offers) == 8
    assert [item["name"] for item in offers] == [
        "Oferta 9",
        "Oferta 8",
        "Oferta 7",
        "Oferta 6",
        "Oferta 5",
        "Oferta 4",
        "Oferta 3",
        "Oferta 2",
    ]
    assert all(item["offer_price"] is not None for item in offers)


def test_explore_offers_section_is_empty_without_offers(
    api_client: TestClient, db_session: Session, store: Store
) -> None:
    _add_product(db_session, store, name="Sin oferta")

    response = api_client.get(EXPLORE_URL)

    assert response.status_code == 200
    assert response.json()["offers"] == []


def test_explore_categories_count_available_products_only(
    api_client: TestClient,
    db_session: Session,
    store: Store,
    other_store: Store,
    inactive_store: Store,
) -> None:
    indumentaria = Category(name="Indumentaria")
    calzado = Category(name="Calzado")
    vacia = Category(name="Accesorios")
    db_session.add_all([indumentaria, calzado, vacia])
    db_session.commit()

    _add_product(
        db_session, store, name="Disponible", categories=(indumentaria,)
    )
    _add_product(
        db_session,
        store,
        name="Eliminado",
        categories=(indumentaria,),
        deleted=True,
    )
    _add_product(
        db_session,
        store,
        name="Inactivo",
        categories=(indumentaria,),
        is_active=False,
    )
    _add_product(
        db_session,
        inactive_store,
        name="Local inactivo",
        categories=(indumentaria,),
    )
    _add_product(db_session, other_store, name="Otro local")

    categories = api_client.get(EXPLORE_URL).json()["categories"]

    assert categories == [
        {"id": vacia.id, "name": "Accesorios", "product_count": 0},
        {"id": calzado.id, "name": "Calzado", "product_count": 0},
        {"id": indumentaria.id, "name": "Indumentaria", "product_count": 1},
    ]


def test_explore_stores_are_six_active_ordered_by_number(
    api_client: TestClient, db_session: Session, store: Store
) -> None:
    for number in range(2, 10):
        db_session.add(
            Store(
                number=number,
                name=f"Local {number}",
                description=f"Descripción {number}",
                logo_url=f"https://example.com/{number}.png",
                side="right",
                position=number,
            )
        )
    db_session.add(
        Store(
            number=10,
            name="Local inactivo",
            side="left",
            position=1,
            is_active=False,
        )
    )
    db_session.commit()

    response = api_client.get(EXPLORE_URL)

    stores = response.json()["stores"]
    assert [item["number"] for item in stores] == [1, 2, 3, 4, 5, 6]
    assert stores[1] == {
        "id": stores[1]["id"],
        "number": 2,
        "name": "Local 2",
        "description": "Descripción 2",
        "logo_url": "https://example.com/2.png",
    }


def test_public_stores_lists_every_active_store_ordered_by_number(
    api_client: TestClient, db_session: Session, store: Store
) -> None:
    for number in range(2, 10):
        db_session.add(
            Store(
                number=number,
                name=f"Local {number}",
                side="right",
                position=number,
            )
        )
    db_session.add(
        Store(
            number=10,
            name="Local inactivo",
            side="left",
            position=1,
            is_active=False,
        )
    )
    db_session.commit()

    response = api_client.get(PUBLIC_STORES_URL)

    assert response.status_code == 200
    body = response.json()
    assert [item["number"] for item in body] == list(range(1, 10))
    assert set(body[0]) == {"id", "number", "name", "description", "logo_url"}


def test_has_offer_filters_products(
    api_client: TestClient, db_session: Session, store: Store
) -> None:
    _add_product(
        db_session, store, name="Oferta", price="100.00", offer_price="80.00"
    )
    _add_product(db_session, store, name="Sin oferta")

    with_filter = api_client.get(PRODUCTS_URL, params={"has_offer": "true"})
    assert with_filter.status_code == 200
    assert [item["name"] for item in with_filter.json()["items"]] == ["Oferta"]

    without_filter = api_client.get(PRODUCTS_URL)
    assert without_filter.json()["total"] == 2

    false_filter = api_client.get(PRODUCTS_URL, params={"has_offer": "false"})
    assert false_filter.json()["total"] == 2


def test_has_offer_combines_with_category_and_price(
    api_client: TestClient,
    db_session: Session,
    store: Store,
    categories: list[Category],
) -> None:
    indumentaria, calzado, _ = categories
    _add_product(
        db_session,
        store,
        name="Remera oferta",
        price="100.00",
        offer_price="60.00",
        categories=(indumentaria,),
    )
    _add_product(
        db_session,
        store,
        name="Remera sin oferta",
        price="100.00",
        categories=(indumentaria,),
    )
    _add_product(
        db_session,
        store,
        name="Zapatilla oferta",
        price="100.00",
        offer_price="60.00",
        categories=(calzado,),
    )

    response = api_client.get(
        PRODUCTS_URL,
        params={
            "has_offer": "true",
            "category_id": indumentaria.id,
            "min_price": "50.00",
        },
    )

    assert [item["name"] for item in response.json()["items"]] == [
        "Remera oferta"
    ]


def test_explore_does_not_record_search_events(
    api_client: TestClient, db_session: Session, store: Store
) -> None:
    _add_product(
        db_session, store, name="Oferta", price="100.00", offer_price="80.00"
    )
    _add_product(db_session, store, name="Novedad")

    response = api_client.get(EXPLORE_URL)

    assert response.status_code == 200
    assert _event_count(db_session) == 0


# --- Gallery map (CU #5) ---------------------------------------------------

MAP_URL = "/api/public/map"


def test_map_without_token_returns_expected_contract(
    api_client: TestClient,
    db_session: Session,
    store: Store,
) -> None:
    store.logo_url = "https://example.com/logo.png"
    db_session.commit()

    response = api_client.get(MAP_URL)

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"stores"}
    assert body["stores"] == [
        {
            "id": store.id,
            "number": 1,
            "name": "Local 1",
            "logo_url": "https://example.com/logo.png",
            "side": "right",
            "position": 1,
        }
    ]
    item = body["stores"][0]
    assert set(item) == {
        "id",
        "number",
        "name",
        "logo_url",
        "side",
        "position",
    }


def test_map_only_includes_active_stores(
    api_client: TestClient,
    db_session: Session,
    store: Store,
    other_store: Store,
    inactive_store: Store,
) -> None:
    response = api_client.get(MAP_URL)

    assert response.status_code == 200
    stores = response.json()["stores"]
    returned_ids = {item["id"] for item in stores}
    assert returned_ids == {store.id, other_store.id}
    assert inactive_store.id not in returned_ids


def test_map_orders_by_side_then_position(
    api_client: TestClient,
    db_session: Session,
    store: Store,
) -> None:
    # The ``store`` fixture is right/1 with number 1; create the rest.
    db_session.add_all(
        [
            Store(number=10, name="Izquierda 2", side="left", position=2),
            Store(number=11, name="Izquierda 1", side="left", position=1),
            Store(number=12, name="Fondo", side="back", position=1),
            Store(number=13, name="Derecha 2", side="right", position=2),
        ]
    )
    db_session.commit()

    response = api_client.get(MAP_URL)

    assert response.status_code == 200
    assert [
        (item["side"], item["position"]) for item in response.json()["stores"]
    ] == [
        ("left", 1),
        ("left", 2),
        ("right", 1),
        ("right", 2),
        ("back", 1),
    ]


def test_map_does_not_expose_internal_data_or_products(
    api_client: TestClient,
    db_session: Session,
    store: Store,
) -> None:
    store.email = "local@galeria.local"
    store.phone = "1122334455"
    store.whatsapp = "1122334455"
    store.description = "Descripción interna"
    db_session.commit()
    _add_product(db_session, store, name="Remera", price="100.00")

    response = api_client.get(MAP_URL)

    assert response.status_code == 200
    item = response.json()["stores"][0]
    assert set(item) == {
        "id",
        "number",
        "name",
        "logo_url",
        "side",
        "position",
    }
    assert "is_active" not in item
    assert "description" not in item
    assert "email" not in item
    assert "phone" not in item
    assert "whatsapp" not in item
    lowered = response.text.lower()
    assert "products" not in lowered
    assert "accounts" not in lowered
    assert "merchants" not in lowered
    assert "password" not in lowered


# --- Store catalog (store-catalog-and-back) --------------------------------


def _store_products_url(store_id: int) -> str:
    return f"{STORES_URL}/{store_id}/products"


def test_store_catalog_without_token_returns_expected_contract(
    api_client: TestClient,
    db_session: Session,
    store: Store,
    categories: list[Category],
) -> None:
    _add_product(
        db_session,
        store,
        name="Remera",
        description="Algodón",
        price="1500.00",
        offer_price="1200.00",
        categories=(categories[0],),
        image_urls=("https://example.com/remera.jpg",),
    )

    response = api_client.get(_store_products_url(store.id))

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"items", "total", "page", "page_size", "pages"}
    assert body["total"] == 1
    assert body["page"] == 1
    assert body["page_size"] == 12
    assert body["pages"] == 1

    item = body["items"][0]
    assert set(item) == {
        "id",
        "name",
        "description",
        "price",
        "offer_price",
        "effective_price",
        "categories",
        "primary_image",
        "store",
    }
    assert item["name"] == "Remera"
    assert item["description"] == "Algodón"
    assert item["price"] == "1500.00"
    assert item["offer_price"] == "1200.00"
    assert item["effective_price"] == "1200.00"
    assert item["categories"] == [
        {"id": categories[0].id, "name": categories[0].name}
    ]
    assert item["primary_image"] == {
        "url": "https://example.com/remera.jpg",
        "alt_text": None,
    }
    assert item["store"] == {"id": store.id, "number": 1, "name": "Local 1"}
    assert "store_id" not in item
    assert "is_active" not in item
    assert "deleted_at" not in item
    assert "password" not in response.text.lower()


def test_store_catalog_paginates(
    api_client: TestClient,
    db_session: Session,
    store: Store,
) -> None:
    for letter in "ABCDE":
        _add_product(db_session, store, name=f"Producto {letter}")

    response = api_client.get(
        _store_products_url(store.id), params={"page": 2, "page_size": 2}
    )

    assert response.status_code == 200
    body = response.json()
    assert [item["name"] for item in body["items"]] == [
        "Producto C",
        "Producto D",
    ]
    assert body["total"] == 5
    assert body["page"] == 2
    assert body["page_size"] == 2
    assert body["pages"] == 3


def test_store_catalog_orders_by_name_case_insensitive(
    api_client: TestClient,
    db_session: Session,
    store: Store,
) -> None:
    _add_product(db_session, store, name="Zapato")
    _add_product(db_session, store, name="camisa")
    _add_product(db_session, store, name="Bufanda")

    response = api_client.get(_store_products_url(store.id))

    assert response.status_code == 200
    assert [item["name"] for item in response.json()["items"]] == [
        "Bufanda",
        "camisa",
        "Zapato",
    ]


def test_store_catalog_excludes_unavailable_and_other_store_products(
    api_client: TestClient,
    db_session: Session,
    store: Store,
    other_store: Store,
) -> None:
    _add_product(db_session, store, name="Disponible")
    _add_product(db_session, store, name="Eliminado", deleted=True)
    _add_product(db_session, store, name="Inactivo", is_active=False)
    _add_product(db_session, other_store, name="Otro local")

    response = api_client.get(_store_products_url(store.id))

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert [item["name"] for item in body["items"]] == ["Disponible"]


def test_store_catalog_is_empty_without_available_products(
    api_client: TestClient,
    db_session: Session,
    store: Store,
) -> None:
    _add_product(db_session, store, name="Eliminado", deleted=True)

    response = api_client.get(_store_products_url(store.id))

    assert response.status_code == 200
    assert response.json() == {
        "items": [],
        "total": 0,
        "page": 1,
        "page_size": 12,
        "pages": 0,
    }


def test_store_catalog_404_for_inactive_and_unknown_store(
    api_client: TestClient,
    db_session: Session,
    inactive_store: Store,
) -> None:
    _add_product(db_session, inactive_store, name="Producto oculto")

    for store_id in (inactive_store.id, 999999):
        response = api_client.get(_store_products_url(store_id))

        assert response.status_code == 404
        assert response.json()["detail"] == "Local no encontrado."


def test_store_catalog_non_numeric_id_returns_422(
    api_client: TestClient,
) -> None:
    response = api_client.get(f"{STORES_URL}/abc/products")

    assert response.status_code == 422


@pytest.mark.parametrize(
    "params", [{"page": 0}, {"page_size": 0}, {"page_size": 101}]
)
def test_store_catalog_pagination_rejects_out_of_range_values(
    api_client: TestClient,
    store: Store,
    params: dict,
) -> None:
    response = api_client.get(_store_products_url(store.id), params=params)

    assert response.status_code == 422


def test_store_catalog_records_no_search_events(
    api_client: TestClient,
    db_session: Session,
    store: Store,
) -> None:
    for index in range(3):
        _add_product(db_session, store, name=f"Producto {index}")

    response = api_client.get(
        _store_products_url(store.id), params={"page_size": 2}
    )

    assert response.status_code == 200
    assert response.json()["total"] == 3
    assert _event_count(db_session) == 0
