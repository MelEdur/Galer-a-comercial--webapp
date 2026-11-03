"""Business logic for authentication."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.modules.accounts.models import User

INVALID_CREDENTIALS = "Credenciales inválidas"


def normalize_email(email: str) -> str:
    """Return a trimmed, lowercase email for case-insensitive lookups."""
    return email.strip().lower()


def authenticate_user(session: Session, email: str, password: str) -> User | None:
    """Return the active account matching the credentials, or ``None``.

    A missing email, a wrong password and an inactive account all yield
    ``None`` so the caller can answer with a single uniform error.
    """
    user = session.scalar(
        select(User).where(func.lower(User.email) == normalize_email(email))
    )
    if user is None:
        return None
    if not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
