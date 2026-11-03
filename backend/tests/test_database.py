"""Tests for the database session dependency and real PostgreSQL connection.

The real connection test runs only when ``TEST_DATABASE_URL`` is defined, so the
suite stays green without a local PostgreSQL instance.
"""

import os

import pytest
from sqlalchemy import create_engine, text

from app.core import database as database_module
from app.core.database import get_db

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")


class FakeSession:
    """Minimal stand-in that records whether it was closed."""

    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True


def test_get_db_yields_session_and_closes_it(monkeypatch: pytest.MonkeyPatch) -> None:
    session = FakeSession()
    monkeypatch.setattr(database_module, "SessionLocal", lambda: session)

    dependency = get_db()
    assert next(dependency) is session

    with pytest.raises(StopIteration):
        next(dependency)

    assert session.closed is True


@pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason=(
        "TEST_DATABASE_URL is not set; skipping the real PostgreSQL connection test. "
        "Set it to a disposable test database to enable it."
    ),
)
def test_database_connection_executes_select_one() -> None:
    engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            assert connection.execute(text("SELECT 1")).scalar_one() == 1
    finally:
        engine.dispose()
