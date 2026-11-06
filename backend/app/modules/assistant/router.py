"""Public HTTP endpoint for the gallery assistant (CU #11)."""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque

from fastapi import APIRouter, HTTPException, Request, status

from app.core.config import settings
from app.modules.assistant import service
from app.modules.assistant.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/public/assistant", tags=["assistant"])

_rate_lock = threading.Lock()
_rate_hits: dict[str, deque[float]] = defaultdict(deque)

RATE_LIMIT_MESSAGE = (
    "Has hecho demasiadas consultas. Espera un momento e inténtalo de nuevo."
)
UNAVAILABLE_MESSAGE = (
    "El asistente no está disponible en este momento. Inténtalo más tarde."
)


def reset_rate_limit() -> None:
    """Clear the in-memory counters; intended for tests."""
    with _rate_lock:
        _rate_hits.clear()


def _client_ip(request: Request) -> str:
    """Return the visitor IP used as the rate-limit key."""
    if request.client is None:
        return "unknown"
    return request.client.host or "unknown"


def _within_rate_limit(client_ip: str) -> bool:
    """Register a request for ``client_ip`` if it is inside the limit."""
    now = time.monotonic()
    window = settings.assistant_rate_window_seconds
    limit = settings.assistant_rate_limit

    with _rate_lock:
        hits = _rate_hits[client_ip]
        while hits and now - hits[0] >= window:
            hits.popleft()
        if len(hits) >= limit:
            return False
        hits.append(now)
        return True


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Ask the public gallery assistant",
    responses={
        status.HTTP_429_TOO_MANY_REQUESTS: {
            "description": "Too many requests from this IP."
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "The assistant provider is unavailable."
        },
    },
)
def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    """Answer a visitor question with knowledge-based information or an action."""
    if not _within_rate_limit(_client_ip(request)):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=RATE_LIMIT_MESSAGE,
        )

    try:
        return service.answer(payload)
    except service.AssistantUnavailableError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=UNAVAILABLE_MESSAGE,
        ) from None
