"""Request and response schemas for authentication."""

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.security import BCRYPT_MAX_PASSWORD_BYTES
from app.core.validation import EmailAddress


class LoginRequest(BaseModel):
    """Credentials submitted by a user."""

    email: EmailAddress
    password: str = Field(min_length=1, max_length=BCRYPT_MAX_PASSWORD_BYTES)

    @field_validator("password")
    @classmethod
    def validate_password_bytes(cls, value: str) -> str:
        """Reject passwords longer than the bcrypt 72-byte limit."""
        if len(value.encode("utf-8")) > BCRYPT_MAX_PASSWORD_BYTES:
            raise ValueError(
                f"La contraseña no puede superar los {BCRYPT_MAX_PASSWORD_BYTES} bytes."
            )
        return value


class TokenResponse(BaseModel):
    """Access token issued after a successful login."""

    access_token: str
    token_type: str = "bearer"


class StoreSummary(BaseModel):
    """Basic store data included in the session identity."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    number: int
    name: str


class UserRead(BaseModel):
    """Identity of the authenticated account (never includes the hash)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    store_id: int | None
    store: StoreSummary | None
