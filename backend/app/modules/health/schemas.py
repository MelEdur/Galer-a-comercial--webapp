"""Schemas for the health check endpoint."""

from typing import Literal

from pydantic import BaseModel

ServiceStatus = Literal["ok", "degraded"]
DatabaseStatus = Literal["ok", "unavailable"]


class HealthResponse(BaseModel):
    """Result of the backend and database health check."""

    status: ServiceStatus
    database: DatabaseStatus
