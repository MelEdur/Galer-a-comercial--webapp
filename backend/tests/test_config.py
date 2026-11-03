"""Tests for application settings."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings

DATABASE_URL = "postgresql+psycopg://user:pass@localhost:5432/db"
JWT_SECRET = "test-secret"


def test_settings_fail_without_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None, jwt_secret=JWT_SECRET)

    assert "database_url" in str(exc_info.value)


def test_settings_fail_without_jwt_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("JWT_SECRET", raising=False)

    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None, database_url=DATABASE_URL)

    assert "jwt_secret" in str(exc_info.value)


def test_settings_jwt_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("JWT_ALGORITHM", raising=False)
    monkeypatch.delenv("JWT_EXPIRE_MINUTES", raising=False)

    settings = Settings(
        _env_file=None,
        database_url=DATABASE_URL,
        jwt_secret=JWT_SECRET,
    )

    assert settings.jwt_algorithm == "HS256"
    assert settings.jwt_expire_minutes == 60


def test_settings_read_jwt_variables_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("JWT_ALGORITHM", "HS512")
    monkeypatch.setenv("JWT_EXPIRE_MINUTES", "15")

    settings = Settings(
        _env_file=None,
        database_url=DATABASE_URL,
        jwt_secret=JWT_SECRET,
    )

    assert settings.jwt_algorithm == "HS512"
    assert settings.jwt_expire_minutes == 15


def test_settings_parse_comma_separated_cors_origins(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CORS_ORIGINS", raising=False)

    settings = Settings(
        _env_file=None,
        database_url=DATABASE_URL,
        jwt_secret=JWT_SECRET,
        cors_origins="http://localhost:5173, http://localhost:3000",
    )

    assert settings.cors_origins_list == [
        "http://localhost:5173",
        "http://localhost:3000",
    ]


def test_settings_use_default_cors_origin(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CORS_ORIGINS", raising=False)

    settings = Settings(
        _env_file=None,
        database_url=DATABASE_URL,
        jwt_secret=JWT_SECRET,
    )

    assert settings.cors_origins_list == ["http://localhost:5173"]


def test_settings_empty_cors_origins_yield_empty_list(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CORS_ORIGINS", raising=False)

    settings = Settings(
        _env_file=None,
        database_url=DATABASE_URL,
        jwt_secret=JWT_SECRET,
        cors_origins=" , ",
    )

    assert settings.cors_origins_list == []
