"""Health check endpoint."""

import logging

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.health.schemas import HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Backend and database health check",
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": HealthResponse,
            "description": "The database is not available.",
        }
    },
)
def health_check(db: Session = Depends(get_db)) -> HealthResponse | JSONResponse:
    """Report service health, probing the database with ``SELECT 1``."""
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        # Log only the exception type: no credentials, statements or tracebacks.
        logger.error("Database health check failed (%s)", type(exc).__name__)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "degraded", "database": "unavailable"},
        )

    return HealthResponse(status="ok", database="ok")
