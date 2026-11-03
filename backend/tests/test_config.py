"""Tests for application settings."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_fail_without_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None)

    assert "database_url" in str(exc_info.value)


def test_settings_parse_comma_separated_cors_origins(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CORS_ORIGINS", raising=False)

    settings = Settings(
        _env_file=None,
        database_url="postgresql+psycopg://user:pass@localhost:5432/db",
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
        database_url="postgresql+psycopg://user:pass@localhost:5432/db",
    )

    assert settings.cors_origins_list == ["http://localhost:5173"]


def test_settings_empty_cors_origins_yield_empty_list(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CORS_ORIGINS", raising=False)

    settings = Settings(
        _env_file=None,
        database_url="postgresql+psycopg://user:pass@localhost:5432/db",
        cors_origins=" , ",
    )

    assert settings.cors_origins_list == []
