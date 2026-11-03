"""HTTP endpoints for authentication."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.core.security import create_access_token
from app.modules.accounts.models import User
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.schemas import LoginRequest, TokenResponse, UserRead
from app.modules.auth.service import INVALID_CREDENTIALS, authenticate_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate with email and password",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Invalid credentials, unknown email or inactive account."
        }
    },
)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Validate credentials and issue a signed access token."""
    user = authenticate_user(db, payload.email, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_CREDENTIALS,
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=create_access_token(str(user.id), user.role))


@router.get(
    "/me",
    response_model=UserRead,
    summary="Return the authenticated account identity",
)
def read_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """Return the authenticated user, including its store, without sensitive fields."""
    return db.execute(
        select(User)
        .options(selectinload(User.store))
        .where(User.id == current_user.id)
    ).scalar_one()
