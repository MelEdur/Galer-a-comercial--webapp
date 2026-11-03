"""Pytest fixtures shared by the backend test suite."""

import os
from collections.abc import Generator, Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# The application reads its configuration at import time, so placeholder values
# are required to import it. The database URL is never used to open a
# connection here: health tests override the ``get_db`` dependency and
# database tests use ``TEST_DATABASE_URL`` explicitly.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://backend_test:backend_test@localhost:5432/backend_test",
)
os.environ.setdefault(
    "JWT_SECRET", "test-only-secret-with-enough-entropy-0123456789"
)
os.environ.setdefault("ENVIRONMENT", "test")

import app.db.registry  # noqa: E402,F401  (register all models)
from app.core.database import get_db  # noqa: E402
from app.core.security import (  # noqa: E402
    create_access_token,
    hash_password,
)
from app.db.base import Base  # noqa: E402
from app.main import app  # noqa: E402
from app.modules.accounts.models import User  # noqa: E402
from app.modules.stores.models import Store  # noqa: E402

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

    table_names = ", ".join(table.name for table in Base.metadata.sorted_tables)
    with db_engine.begin() as connection:
        connection.execute(
            text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE")
        )
    yield


@pytest.fixture
def db_session(clean_database: None, db_engine: Any) -> Generator[Any, None, None]:
    """Provide an isolated SQLAlchemy session bound to the test database."""
    with Session(db_engine, expire_on_commit=False) as session:
        yield session


@pytest.fixture
def api_client(
    clean_database: None, db_engine: Any
) -> Iterator[TestClient]:
    """Test client whose requests use sessions on the test database."""
    factory = sessionmaker(bind=db_engine, expire_on_commit=False)

    def _get_db_override() -> Iterator[Session]:
        session = factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _get_db_override
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def store(db_session: Session) -> Store:
    """A single store available for merchant assignment."""
    item = Store(number=1, name="Local 1", side="right", position=1)
    db_session.add(item)
    db_session.commit()
    return item


@pytest.fixture
def admin_user(db_session: Session) -> User:
    """An active administrator account."""
    user = User(
        email="admin@galeria.local",
        full_name="Administrador",
        password_hash=hash_password("admin1234"),
        role="admin",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def merchant_user(db_session: Session, store: Store) -> User:
    """An active merchant assigned to the ``store`` fixture."""
    user = User(
        email="merchant@galeria.local",
        full_name="Comerciante Prueba",
        password_hash=hash_password("merchant1234"),
        role="merchant",
        is_active=True,
        store_id=store.id,
    )
    db_session.add(user)
    db_session.commit()
    return user


def auth_headers(user: User) -> dict[str, str]:
    """Build a bearer header for ``user``."""
    token = create_access_token(str(user.id), user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(admin_user: User) -> dict[str, str]:
    return auth_headers(admin_user)


@pytest.fixture
def merchant_headers(merchant_user: User) -> dict[str, str]:
    return auth_headers(merchant_user)
