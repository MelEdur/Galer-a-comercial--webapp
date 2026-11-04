"""Tests for the idempotent category seed script."""

from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

import scripts.seed_categories as seed_module
from app.modules.catalog.models import Category
from tests.conftest import requires_database

pytestmark = requires_database


def test_seed_creates_ten_categories_and_is_idempotent(
    monkeypatch, db_engine, clean_database
) -> None:
    factory = sessionmaker(bind=db_engine, expire_on_commit=False)
    monkeypatch.setattr(seed_module, "SessionLocal", factory)

    assert seed_module.seed_categories() == (10, 0)
    assert seed_module.seed_categories() == (0, 10)

    with factory() as session:
        names = session.scalars(select(Category.name).order_by(Category.name)).all()

    assert len(names) == 10
    assert sorted(names) == sorted(seed_module.CATEGORY_NAMES)


def test_seed_compares_names_case_insensitively(
    monkeypatch, db_engine, clean_database
) -> None:
    factory = sessionmaker(bind=db_engine, expire_on_commit=False)
    monkeypatch.setattr(seed_module, "SessionLocal", factory)

    with factory() as session:
        session.add(Category(name="indumentaria"))
        session.commit()

    assert seed_module.seed_categories() == (9, 1)

    with factory() as session:
        count = session.scalar(select(func.count()).select_from(Category))

    assert count == 10
