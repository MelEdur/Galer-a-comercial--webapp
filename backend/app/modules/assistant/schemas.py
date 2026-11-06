"""Request and response schemas for the public assistant (CU #11)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.config import settings

MESSAGE_MAX_CHARS = settings.assistant_max_message_chars
HISTORY_MAX_MESSAGES = settings.assistant_max_history_messages


class ChatMessage(BaseModel):
    """A previous message sent by the visitor or the assistant."""

    model_config = ConfigDict(extra="forbid")

    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=MESSAGE_MAX_CHARS)

    @field_validator("content", mode="before")
    @classmethod
    def strip_content(cls, value: object) -> str:
        """Trim surrounding whitespace and reject blank messages."""
        if not isinstance(value, str):
            raise ValueError("El mensaje debe ser texto.")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("El mensaje no puede estar vacío.")
        return cleaned


class ChatRequest(BaseModel):
    """A question plus the last messages of the conversation."""

    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1, max_length=MESSAGE_MAX_CHARS)
    history: list[ChatMessage] = Field(
        default_factory=list, max_length=HISTORY_MAX_MESSAGES
    )

    @field_validator("message", mode="before")
    @classmethod
    def strip_message(cls, value: object) -> str:
        """Trim the question and reject whitespace-only messages."""
        if not isinstance(value, str):
            raise ValueError("El mensaje debe ser texto.")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("El mensaje no puede estar vacío.")
        return cleaned


class AssistantAction(BaseModel):
    """A navigation suggestion the visitor can confirm in the widget."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["search", "map"]
    label: str
    query: str | None = None
    href: str


class AssistantSource(BaseModel):
    """A knowledge source used to build an informational answer."""

    model_config = ConfigDict(extra="forbid")

    title: str
    type: Literal["static", "store"]


class ChatResponse(BaseModel):
    """The assistant answer with an optional action and its sources."""

    model_config = ConfigDict(extra="forbid")

    answer: str
    action: AssistantAction | None = None
    sources: list[AssistantSource] = Field(default_factory=list)
