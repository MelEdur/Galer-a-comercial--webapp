"""Tests for the idempotent store seed script."""

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

import scripts.seed_stores as seed_module
from app.modules.stores.models import Store
from tests.conftest import requires_database

pytestmark = requires_database


def test_seed_creates_21_stores_and_is_idempotent(
    monkeypatch, db_engine, clean_database
) -> None:
    factory = sessionmaker(bind=db_engine, expire_on_commit=False)
    monkeypatch.setattr(seed_module, "SessionLocal", factory)

    assert seed_module.seed_stores() == (21, 0)
    assert seed_module.seed_stores() == (0, 21)

    with factory() as session:
        stores = session.execute(select(Store).order_by(Store.number)).scalars().all()

    assert len(stores) == 21
    assert [store.number for store in stores] == list(range(1, 22))

    by_number = {store.number: store for store in stores}
    for position in range(1, 11):
        right = by_number[2 * position - 1]
        left = by_number[2 * position]
        assert (right.side, right.position) == ("right", position)
        assert (left.side, left.position) == ("left", position)

    back = by_number[21]
    assert (back.side, back.position) == ("back", 1)

    for store in stores:
        assert store.name == f"Local {store.number}"
        assert store.is_active is True
        assert store.description is None
        assert store.logo_url is None
        assert store.email is None
        assert store.phone is None
        assert store.whatsapp is None
