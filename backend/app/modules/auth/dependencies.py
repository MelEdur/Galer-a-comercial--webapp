"""FastAPI dependencies for authentication and role authorization."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import InvalidTokenError, decode_access_token
from app.modules.accounts.models import User

_AUTH_HEADERS = {"WWW-Authenticate": "Bearer"}

bearer_scheme = HTTPBearer(auto_error=False)


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers=_AUTH_HEADERS,
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Return the active account identified by the bearer token."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthorized("No autenticado")

    try:
        payload = decode_access_token(credentials.credentials)
    except InvalidTokenError:
        raise _unauthorized("Token inválido o vencido") from None

    subject = payload.get("sub")
    try:
        user_id = int(subject)
    except (TypeError, ValueError):
        raise _unauthorized("Token inválido o vencido") from None

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise _unauthorized("No autenticado")
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Allow only accounts with the ``admin`` role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado",
        )
    return current_user
