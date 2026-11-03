"""Request and response schemas for merchant administration."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.security import BCRYPT_MAX_PASSWORD_BYTES
from app.core.validation import EmailAddress


class StoreRef(BaseModel):
    """Minimal store reference embedded in a merchant."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    number: int
    name: str


class MerchantRead(BaseModel):
    """Merchant account without any credential field."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    is_active: bool
    created_at: datetime
    store: StoreRef | None


class MerchantCreate(BaseModel):
    """Data required to create a merchant from the admin panel."""

    email: EmailAddress
    full_name: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=8, max_length=BCRYPT_MAX_PASSWORD_BYTES)
    store_id: int = Field(gt=0)

    @field_validator("full_name")
    @classmethod
    def normalize_full_name(cls, value: str) -> str:
        """Trim the name and reject whitespace-only values."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("El nombre completo es obligatorio.")
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password_bytes(cls, value: str) -> str:
        """Reject passwords longer than the bcrypt 72-byte limit."""
        if len(value.encode("utf-8")) > BCRYPT_MAX_PASSWORD_BYTES:
            raise ValueError(
                f"La contraseña no puede superar los {BCRYPT_MAX_PASSWORD_BYTES} bytes."
            )
        return value


class StoreMerchantRef(BaseModel):
    """Active merchant assigned to a store."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str


class StoreAdminRead(BaseModel):
    """Store with its active merchant, or ``null`` when available."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    number: int
    name: str
    side: str
    position: int
    is_active: bool
    merchant: StoreMerchantRef | None
