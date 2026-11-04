"""Request and response schemas for the merchant's own store settings."""

from __future__ import annotations

from datetime import time

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)

from app.core.validation import EmailAddress

NAME_MAX_LENGTH = 120
DESCRIPTION_MAX_LENGTH = 2000
LOGO_URL_MAX_LENGTH = 500
EMAIL_MAX_LENGTH = 320
PHONE_MAX_LENGTH = 30
LINK_LABEL_MAX_LENGTH = 60
LINK_URL_MAX_LENGTH = 500
MAX_LINKS = 10

_PHONE_PATTERN = r"^[0-9+\-() ]+$"


def _strip_optional(value: object) -> object:
    """Trim optional strings and turn empty ones into ``None``."""
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned or None
    return value


def _strip_required(value: object, message: str) -> str:
    """Trim a required string and reject empty or non-string values."""
    if not isinstance(value, str):
        raise ValueError(message)
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(message)
    return cleaned


class StoreHourRead(BaseModel):
    """An opening interval of the store, as exposed by the API."""

    model_config = ConfigDict(from_attributes=True)

    day_of_week: int
    opens_at: time
    closes_at: time


class StoreLinkRead(BaseModel):
    """An ordered external link of the store."""

    model_config = ConfigDict(from_attributes=True)

    label: str
    url: str
    position: int


class StoreHourInput(BaseModel):
    """A weekday opening interval submitted by the merchant."""

    model_config = ConfigDict(extra="forbid")

    day_of_week: int = Field(ge=0, le=6)
    opens_at: time
    closes_at: time

    @model_validator(mode="after")
    def validate_range(self) -> "StoreHourInput":
        """Reject intervals that do not close after they open."""
        if self.closes_at <= self.opens_at:
            raise ValueError(
                "La hora de cierre debe ser posterior a la de apertura."
            )
        return self


class StoreLinkInput(BaseModel):
    """An external link submitted by the merchant."""

    model_config = ConfigDict(extra="forbid")

    label: str = Field(min_length=1, max_length=LINK_LABEL_MAX_LENGTH)
    url: HttpUrl

    @field_validator("label", mode="before")
    @classmethod
    def normalize_label(cls, value: object) -> str:
        """Trim the label and reject whitespace-only values."""
        return _strip_required(value, "La etiqueta del enlace es obligatoria.")

    @field_validator("url")
    @classmethod
    def validate_url_length(cls, value: HttpUrl) -> HttpUrl:
        """Reject URLs longer than the database column allows."""
        if len(str(value)) > LINK_URL_MAX_LENGTH:
            raise ValueError(
                f"La URL del enlace no puede superar los {LINK_URL_MAX_LENGTH} caracteres."
            )
        return value


class StoreRead(BaseModel):
    """Public representation of the authenticated merchant's store."""

    id: int
    number: int
    side: str
    position: int
    name: str
    description: str | None
    logo_url: str | None
    email: str | None
    phone: str | None
    whatsapp: str | None
    hours: list[StoreHourRead]
    links: list[StoreLinkRead]


class StoreUpdate(BaseModel):
    """Full update of the store; hours and links replace the previous ones."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=NAME_MAX_LENGTH)
    description: str | None = Field(
        default=None, max_length=DESCRIPTION_MAX_LENGTH
    )
    logo_url: HttpUrl | None = None
    email: EmailAddress | None = Field(default=None, max_length=EMAIL_MAX_LENGTH)
    phone: str | None = Field(
        default=None, max_length=PHONE_MAX_LENGTH, pattern=_PHONE_PATTERN
    )
    whatsapp: str | None = Field(
        default=None, max_length=PHONE_MAX_LENGTH, pattern=_PHONE_PATTERN
    )
    hours: list[StoreHourInput] = Field(default_factory=list)
    links: list[StoreLinkInput] = Field(default_factory=list)

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: object) -> str:
        """Trim the name and reject whitespace-only values."""
        return _strip_required(value, "El nombre del local es obligatorio.")

    @field_validator(
        "description", "logo_url", "email", "phone", "whatsapp", mode="before"
    )
    @classmethod
    def normalize_optional_strings(cls, value: object) -> object:
        """Turn blank optional strings into ``None``."""
        return _strip_optional(value)

    @field_validator("logo_url")
    @classmethod
    def validate_logo_url_length(cls, value: HttpUrl | None) -> HttpUrl | None:
        """Reject logos longer than the database column allows."""
        if value is not None and len(str(value)) > LOGO_URL_MAX_LENGTH:
            raise ValueError(
                f"La URL del logo no puede superar los {LOGO_URL_MAX_LENGTH} caracteres."
            )
        return value

    @model_validator(mode="after")
    def validate_collections(self) -> "StoreUpdate":
        """Reject duplicated hours and duplicated link URLs."""
        hour_keys = [(hour.day_of_week, hour.opens_at) for hour in self.hours]
        if len(set(hour_keys)) != len(hour_keys):
            raise ValueError(
                "No puede haber dos tramos con el mismo día y apertura."
            )

        if len(self.links) > MAX_LINKS:
            raise ValueError(
                f"No se pueden guardar más de {MAX_LINKS} enlaces."
            )

        urls = [str(link.url) for link in self.links]
        if len(set(urls)) != len(urls):
            raise ValueError("No puede haber dos enlaces con la misma URL.")

        return self
