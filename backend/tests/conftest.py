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
