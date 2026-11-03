"""Tests for the health check endpoint."""

from typing import Any
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError, SQLAlchemyError


def test_health_returns_ok_when_database_is_available(
    client: TestClient, override_db_session: Any
) -> None:
    session = MagicMock()
    override_db_session(session)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}
    session.execute.assert_called_once()


@pytest.mark.parametrize(
    "error",
    [
        OperationalError("SELECT 1", {}, Exception("connection refused")),
        SQLAlchemyError("unexpected database error"),
    ],
)
def test_health_returns_503_when_database_fails(
    client: TestClient, override_db_session: Any, error: SQLAlchemyError
) -> None:
    session = MagicMock()
    session.execute.side_effect = error
    override_db_session(session)

    response = client.get("/api/health")

    assert response.status_code == 503
    assert response.json() == {"status": "degraded", "database": "unavailable"}
    body = response.text
    assert "connection refused" not in body
    assert "SELECT 1" not in body
    assert "unexpected database error" not in body


def test_health_route_is_served_under_api_prefix(client: TestClient, override_db_session: Any) -> None:
    override_db_session(MagicMock())

    response = client.get("/api/health")

    assert response.status_code == 200
