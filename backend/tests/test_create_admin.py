"""Tests for the idempotent initial administrator script."""

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

import scripts.create_admin as create_admin_module
from app.core.security import verify_password
from app.modules.accounts.models import User
from tests.conftest import requires_database

pytestmark = requires_database


@pytest.fixture
def script_session_factory(db_engine, clean_database, monkeypatch):
    """Bind the script to the test database."""
    factory = sessionmaker(bind=db_engine, expire_on_commit=False)
    monkeypatch.setattr(create_admin_module, "SessionLocal", factory)
    return factory


def _set_env(monkeypatch, **values) -> None:
    for key in ("ADMIN_EMAIL", "ADMIN_PASSWORD", "ADMIN_FULL_NAME"):
        monkeypatch.delenv(key, raising=False)
    for key, value in values.items():
        monkeypatch.setenv(key, value)


def test_create_admin_creates_active_admin(
    monkeypatch, script_session_factory
) -> None:
    _set_env(
        monkeypatch,
        ADMIN_EMAIL="Admin@Galeria.local",
        ADMIN_PASSWORD="admin1234",
        ADMIN_FULL_NAME="Administrador General",
    )

    assert create_admin_module.create_admin() == 0

    with script_session_factory() as session:
        admin = session.scalar(select(User))

    assert admin is not None
    assert admin.email == "admin@galeria.local"
    assert admin.full_name == "Administrador General"
    assert admin.role == "admin"
    assert admin.is_active is True
    assert admin.store_id is None
    assert admin.password_hash != "admin1234"
    assert verify_password("admin1234", admin.password_hash) is True


def test_create_admin_uses_default_full_name(
    monkeypatch, script_session_factory
) -> None:
    _set_env(
        monkeypatch,
        ADMIN_EMAIL="admin@galeria.local",
        ADMIN_PASSWORD="admin1234",
    )

    assert create_admin_module.create_admin() == 0

    with script_session_factory() as session:
        admin = session.scalar(select(User))

    assert admin.full_name == "Administrador"


def test_create_admin_is_idempotent(monkeypatch, script_session_factory) -> None:
    _set_env(
        monkeypatch,
        ADMIN_EMAIL="admin@galeria.local",
        ADMIN_PASSWORD="admin1234",
    )

    assert create_admin_module.create_admin() == 0
    with script_session_factory() as session:
        original_hash = session.scalar(select(User.password_hash))

    monkeypatch.setenv("ADMIN_PASSWORD", "another-password")
    assert create_admin_module.create_admin() == 0

    with script_session_factory() as session:
        count = session.scalar(select(func.count()).select_from(User))
        current_hash = session.scalar(select(User.password_hash))

    assert count == 1
    assert current_hash == original_hash


@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("", "admin1234"),
        ("admin@galeria.local", ""),
        ("", ""),
    ],
)
def test_create_admin_fails_without_required_variables(
    monkeypatch, script_session_factory, email: str, password: str, capsys
) -> None:
    _set_env(monkeypatch, ADMIN_EMAIL=email, ADMIN_PASSWORD=password)

    assert create_admin_module.create_admin() == 1

    captured = capsys.readouterr()
    assert "ADMIN_EMAIL" in captured.err
    assert "ADMIN_PASSWORD" in captured.err

    with script_session_factory() as session:
        assert session.scalar(select(func.count()).select_from(User)) == 0


def test_create_admin_rejects_password_over_72_bytes(
    monkeypatch, script_session_factory
) -> None:
    _set_env(
        monkeypatch,
        ADMIN_EMAIL="admin@galeria.local",
        ADMIN_PASSWORD="a" * 73,
    )

    assert create_admin_module.create_admin() == 1

    with script_session_factory() as session:
        assert session.scalar(select(func.count()).select_from(User)) == 0
