"""Pytest fixtures shared by the backend test suite."""

import os
from collections.abc import Generator, Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient

# The application reads its configuration at import time, so a placeholder URL
# is required to import it. It is never used to open a connection: health tests
# override the ``get_db`` dependency and the database test uses
# ``TEST_DATABASE_URL`` explicitly.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://backend_test:backend_test@localhost:5432/backend_test",
)
os.environ.setdefault("ENVIRONMENT", "test")

from app.core.database import get_db  # noqa: E402
from app.main import app  # noqa: E402

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

requires_database = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason=(
        "TEST_DATABASE_URL is not set; skipping database tests. "
        "Set it to a disposable test database to enable them."
    ),
)


@pytest.fixture
def client() -> Iterator[TestClient]:
    """Provide a test client and clean dependency overrides afterwards."""
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def override_db_session() -> Generator[Any, None, None]:
    """Return a helper that overrides ``get_db`` with a fake session."""

    def _override(session: Any) -> None:
        def _get_db_override() -> Iterator[Any]:
            yield session

        app.dependency_overrides[get_db] = _get_db_override

    yield _override
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture(scope="session")
def db_engine() -> Generator[Any, None, None]:
    """Create the schema once on the disposable test database."""
    if not TEST_DATABASE_URL:
        pytest.skip(
            "TEST_DATABASE_URL is not set; skipping database tests. "
            "Set it to a disposable test database to enable them."
        )

    from sqlalchemy import create_engine

    import app.db.registry  # noqa: F401  (register all models)
    from app.db.base import Base

    engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def clean_database(db_engine: Any) -> Generator[None, None, None]:
    """Truncate every domain table before each test."""
    from sqlalchemy import text

    from app.db.base import Base

    table_names = ", ".join(table.name for table in Base.metadata.sorted_tables)
    with db_engine.begin() as connection:
        connection.execute(
            text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE")
        )
    yield


@pytest.fixture
def db_session(clean_database: None, db_engine: Any) -> Generator[Any, None, None]:
    """Provide an isolated SQLAlchemy session bound to the test database."""
    from sqlalchemy.orm import Session

    with Session(db_engine, expire_on_commit=False) as session:
        yield session
