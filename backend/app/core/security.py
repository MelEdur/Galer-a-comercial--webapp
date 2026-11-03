"""Password hashing and JWT helpers used by authentication."""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings

# bcrypt only considers the first 72 bytes of a password. Rejecting longer
# values avoids silent truncation.
BCRYPT_MAX_PASSWORD_BYTES = 72


class InvalidTokenError(Exception):
    """Raised when an access token cannot be decoded or has expired."""


def _password_bytes(password: str) -> bytes:
    """Encode a password and enforce the bcrypt 72-byte limit."""
    if not isinstance(password, str):
        raise ValueError("La contraseña debe ser una cadena de texto.")
    raw = password.encode("utf-8")
    if not raw:
        raise ValueError("La contraseña no puede estar vacía.")
    if len(raw) > BCRYPT_MAX_PASSWORD_BYTES:
        raise ValueError(
            f"La contraseña no puede superar los {BCRYPT_MAX_PASSWORD_BYTES} bytes."
        )
    return raw


def hash_password(password: str) -> str:
    """Return a bcrypt hash with a fresh random salt."""
    raw = _password_bytes(password)
    return bcrypt.hashpw(raw, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Return whether ``password`` matches ``password_hash``.

    Any malformed input is treated as a non-match instead of raising.
    """
    try:
        raw = password.encode("utf-8")
    except (AttributeError, UnicodeEncodeError):
        return False
    if not raw or len(raw) > BCRYPT_MAX_PASSWORD_BYTES:
        return False
    try:
        return bcrypt.checkpw(raw, password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(subject: str, role: str) -> str:
    """Create a signed JWT for ``subject`` including ``role`` and expiry."""
    issued_at = datetime.now(timezone.utc)
    payload = {
        "sub": str(subject),
        "role": role,
        "iat": issued_at,
        "exp": issued_at + timedelta(minutes=settings.jwt_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT, raising ``InvalidTokenError`` on failure."""
    try:
        return jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.PyJWTError as exc:
        raise InvalidTokenError("Token inválido o vencido.") from exc
