"""Constraint and invariant tests for the domain model.

Every test runs against ``TEST_DATABASE_URL``; the fixtures in ``conftest.py``
create the schema once per session and truncate the tables between tests.
"""

from datetime import datetime, time, timezone
from decimal import Decimal

import pytest
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError

from app.modules.accounts.models import User
from app.modules.analytics.models import ProductSearchEvent
from app.modules.catalog.models import (
    Category,
    Product,
    ProductCategory,
    ProductImage,
)
from app.modules.stores.models import Store, StoreHour, StoreLink
from tests.conftest import requires_database

pytestmark = requires_database


def _store(
    session,
    *,
    number: int = 1,
    side: str = "right",
    position: int = 1,
    name: str = "Local de prueba",
) -> Store:
    store = Store(number=number, name=name, side=side, position=position)
    session.add(store)
    session.flush()
    return store


def _product(session, store: Store, **kwargs) -> Product:
    kwargs.setdefault("name", "Producto")
    kwargs.setdefault("price", Decimal("10.00"))
    product = Product(store=store, **kwargs)
    session.add(product)
    session.flush()
    return product


def _expect_integrity_error(session) -> None:
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()


def _expect_delete_error(session, statement) -> None:
    with pytest.raises(IntegrityError):
        session.execute(statement)
    session.rollback()


def test_store_number_is_unique(db_session) -> None:
    _store(db_session, number=1, side="right", position=1)
    db_session.commit()

    db_session.add(Store(number=1, name="Duplicado", side="left", position=2))
    _expect_integrity_error(db_session)


def test_store_side_position_is_unique(db_session) -> None:
    _store(db_session, number=1, side="right", position=1)
    db_session.commit()

    db_session.add(Store(number=3, name="Duplicado", side="right", position=1))
    _expect_integrity_error(db_session)


@pytest.mark.parametrize(
    ("side", "position"),
    [("right", 11), ("left", 0), ("back", 2), ("middle", 1)],
)
def test_store_side_position_check(db_session, side: str, position: int) -> None:
    db_session.add(Store(number=1, name="Inválido", side=side, position=position))
    _expect_integrity_error(db_session)


def test_merchant_requires_store(db_session) -> None:
    db_session.add(
        User(
            email="merchant@example.com",
            password_hash="hash",
            role="merchant",
            store_id=None,
        )
    )
    _expect_integrity_error(db_session)


def test_admin_cannot_have_store(db_session) -> None:
    store = _store(db_session)
    db_session.add(
        User(
            email="admin@example.com",
            password_hash="hash",
            role="admin",
            store_id=store.id,
        )
    )
    _expect_integrity_error(db_session)


def test_invalid_role_is_rejected(db_session) -> None:
    db_session.add(
        User(
            email="visitor@example.com",
            password_hash="hash",
            role="visitor",
            store_id=None,
        )
    )
    _expect_integrity_error(db_session)


def test_only_one_merchant_per_store(db_session) -> None:
    store = _store(db_session)
    db_session.add(
        User(
            email="first@example.com",
            password_hash="hash",
            role="merchant",
            store_id=store.id,
        )
    )
    db_session.commit()

    db_session.add(
        User(
            email="second@example.com",
            password_hash="hash",
            role="merchant",
            store_id=store.id,
        )
    )
    _expect_integrity_error(db_session)


def test_email_is_unique_case_insensitive(db_session) -> None:
    db_session.add(
        User(
            email="merchant@example.com",
            password_hash="hash",
            role="merchant",
            store_id=_store(db_session).id,
        )
    )
    db_session.commit()

    db_session.add(
        User(
            email="MERCHANT@example.com",
            password_hash="hash",
            role="merchant",
            store_id=_store(db_session, number=2, side="left", position=1).id,
        )
    )
    _expect_integrity_error(db_session)


def test_negative_price_is_rejected(db_session) -> None:
    store = _store(db_session)
    db_session.add(Product(store=store, name="Producto", price=Decimal("-0.01")))
    _expect_integrity_error(db_session)


def test_offer_price_must_be_lower_than_price(db_session) -> None:
    store = _store(db_session)
    db_session.add(
        Product(
            store=store,
            name="Producto",
            price=Decimal("100.00"),
            offer_price=Decimal("100.00"),
        )
    )
    _expect_integrity_error(db_session)


def test_higher_offer_price_is_rejected(db_session) -> None:
    store = _store(db_session)
    db_session.add(
        Product(
            store=store,
            name="Producto",
            price=Decimal("100.00"),
            offer_price=Decimal("150.00"),
        )
    )
    _expect_integrity_error(db_session)


def test_product_without_offer_is_allowed(db_session) -> None:
    store = _store(db_session)
    product = _product(db_session, store, price=Decimal("100.00"))
    db_session.commit()

    assert product.offer_price is None
    assert product.is_active is True
    assert product.deleted_at is None


def test_category_name_is_unique_case_insensitive(db_session) -> None:
    db_session.add(Category(name="Bebidas"))
    db_session.commit()

    db_session.add(Category(name="bebidas"))
    _expect_integrity_error(db_session)


def test_product_can_have_multiple_categories(db_session) -> None:
    store = _store(db_session)
    product = _product(db_session, store)
    first = Category(name="Bebidas")
    second = Category(name="Almacén")
    db_session.add_all([first, second])
    db_session.flush()

    db_session.add_all(
        [
            ProductCategory(product_id=product.id, category_id=first.id),
            ProductCategory(product_id=product.id, category_id=second.id),
        ]
    )
    db_session.commit()

    count = db_session.execute(
        select(func.count())
        .select_from(ProductCategory)
        .where(ProductCategory.product_id == product.id)
    ).scalar_one()
    assert count == 2


def test_category_in_use_cannot_be_deleted(db_session) -> None:
    store = _store(db_session)
    product = _product(db_session, store)
    category = Category(name="Bebidas")
    db_session.add(category)
    db_session.flush()
    db_session.add(
        ProductCategory(product_id=product.id, category_id=category.id)
    )
    db_session.commit()

    _expect_delete_error(
        db_session, delete(Category).where(Category.id == category.id)
    )


def test_second_primary_image_is_rejected(db_session) -> None:
    store = _store(db_session)
    product = _product(db_session, store)
    db_session.add(
        ProductImage(product_id=product.id, url="https://example.com/1.png", is_primary=True)
    )
    db_session.commit()

    db_session.add(
        ProductImage(product_id=product.id, url="https://example.com/2.png", is_primary=True)
    )
    _expect_integrity_error(db_session)


def test_multiple_images_with_order(db_session) -> None:
    store = _store(db_session)
    product = _product(db_session, store)
    db_session.add_all(
        [
            ProductImage(product_id=product.id, url="https://example.com/b.png", position=1),
            ProductImage(product_id=product.id, url="https://example.com/a.png", position=0),
        ]
    )
    db_session.commit()
    db_session.refresh(product)

    assert [image.position for image in product.images] == [0, 1]


def test_store_hour_close_must_be_after_open(db_session) -> None:
    store = _store(db_session)
    db_session.add(
        StoreHour(
            store_id=store.id,
            day_of_week=0,
            opens_at=time(18, 0),
            closes_at=time(18, 0),
        )
    )
    _expect_integrity_error(db_session)


def test_store_hour_closing_before_opening_is_rejected(db_session) -> None:
    store = _store(db_session)
    db_session.add(
        StoreHour(
            store_id=store.id,
            day_of_week=0,
            opens_at=time(18, 0),
            closes_at=time(9, 0),
        )
    )
    _expect_integrity_error(db_session)


def test_store_allows_multiple_hour_slots_per_day(db_session) -> None:
    store = _store(db_session)
    db_session.add_all(
        [
            StoreHour(
                store_id=store.id,
                day_of_week=0,
                opens_at=time(9, 0),
                closes_at=time(13, 0),
            ),
            StoreHour(
                store_id=store.id,
                day_of_week=0,
                opens_at=time(16, 0),
                closes_at=time(20, 0),
            ),
        ]
    )
    db_session.commit()
    db_session.refresh(store)

    assert len(store.hours) == 2


def test_store_links_are_returned_in_order(db_session) -> None:
    store = _store(db_session)
    db_session.add_all(
        [
            StoreLink(store_id=store.id, label="Instagram", url="https://ig.example", position=1),
            StoreLink(store_id=store.id, label="Web", url="https://web.example", position=0),
        ]
    )
    db_session.commit()
    db_session.refresh(store)

    assert [link.label for link in store.links] == ["Web", "Instagram"]


def test_store_with_products_cannot_be_deleted(db_session) -> None:
    store = _store(db_session)
    _product(db_session, store)
    db_session.commit()

    _expect_delete_error(db_session, delete(Store).where(Store.id == store.id))


def test_store_with_merchant_cannot_be_deleted(db_session) -> None:
    store = _store(db_session)
    db_session.add(
        User(
            email="merchant@example.com",
            password_hash="hash",
            role="merchant",
            store_id=store.id,
        )
    )
    db_session.commit()

    _expect_delete_error(db_session, delete(Store).where(Store.id == store.id))


def test_search_events_can_be_counted_by_product_and_date_range(db_session) -> None:
    store = _store(db_session)
    product = _product(db_session, store)
    other = _product(db_session, store, name="Otro producto")
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = datetime(2026, 1, 31, 23, 59, tzinfo=timezone.utc)
    db_session.add_all(
        [
            ProductSearchEvent(
                product_id=product.id,
                query="bebida",
                searched_at=datetime(2026, 1, 10, tzinfo=timezone.utc),
            ),
            ProductSearchEvent(
                product_id=product.id,
                query="bebida",
                searched_at=datetime(2026, 1, 20, tzinfo=timezone.utc),
            ),
            ProductSearchEvent(
                product_id=product.id,
                query="bebida",
                searched_at=datetime(2025, 12, 31, tzinfo=timezone.utc),
            ),
            ProductSearchEvent(
                product_id=other.id,
                query="bebida",
                searched_at=datetime(2026, 1, 15, tzinfo=timezone.utc),
            ),
        ]
    )
    db_session.commit()

    count = db_session.execute(
        select(func.count())
        .select_from(ProductSearchEvent)
        .where(
            ProductSearchEvent.product_id == product.id,
            ProductSearchEvent.searched_at >= start,
            ProductSearchEvent.searched_at <= end,
        )
    ).scalar_one()
    assert count == 2


def test_search_events_survive_product_logical_delete(db_session) -> None:
    store = _store(db_session)
    product = _product(db_session, store)
    db_session.add(ProductSearchEvent(product_id=product.id, query="oferta"))
    db_session.commit()

    product.is_active = False
    product.deleted_at = datetime.now(timezone.utc)
    db_session.commit()

    count = db_session.execute(
        select(func.count())
        .select_from(ProductSearchEvent)
        .where(ProductSearchEvent.product_id == product.id)
    ).scalar_one()
    assert count == 1
