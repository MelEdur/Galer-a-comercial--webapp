"""Business rules for merchant administration.

The service validates and normalizes input, applies the uniqueness rules and
raises domain exceptions that the router translates into HTTP responses.
"""

from sqlalchemy import and_, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.security import hash_password
from app.modules.accounts.models import User
from app.modules.merchants.schemas import (
    MerchantCreate,
    MerchantRead,
    StoreAdminRead,
    StoreMerchantRef,
    StoreRef,
)
from app.modules.stores.models import Store

EMAIL_CONSTRAINT = "uq_users_email_lower"
STORE_CONSTRAINT = "uq_users_store_merchant"


class MerchantAdminError(Exception):
    """Base class for expected merchant-administration errors."""


class StoreNotFoundError(MerchantAdminError):
    """The requested store does not exist."""


class MerchantNotFoundError(MerchantAdminError):
    """The requested merchant account does not exist."""


class DuplicateEmailError(MerchantAdminError):
    """The email is already registered."""


class StoreOccupiedError(MerchantAdminError):
    """The store already has an active merchant."""


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _constraint_name(error: IntegrityError) -> str | None:
    """Extract the violated constraint name from a psycopg error, if any."""
    diag = getattr(error.orig, "diag", None)
    return getattr(diag, "constraint_name", None)


def list_merchants(session: Session) -> list[MerchantRead]:
    """Return every merchant ordered by full name, with its store."""
    rows = (
        session.execute(
            select(User)
            .where(User.role == "merchant")
            .options(selectinload(User.store))
            .order_by(func.lower(User.full_name), User.id)
        )
        .scalars()
        .all()
    )
    return [MerchantRead.model_validate(user) for user in rows]


def create_merchant(session: Session, payload: MerchantCreate) -> MerchantRead:
    """Create an active merchant assigned to an existing free store."""
    email = _normalize_email(payload.email)

    store = session.get(Store, payload.store_id)
    if store is None:
        raise StoreNotFoundError("El local indicado no existe.")

    duplicate = session.scalar(
        select(User.id).where(func.lower(User.email) == email)
    )
    if duplicate is not None:
        raise DuplicateEmailError("El correo ya está registrado.")

    occupied = session.scalar(
        select(User.id).where(
            User.store_id == payload.store_id,
            User.role == "merchant",
            User.is_active.is_(True),
        )
    )
    if occupied is not None:
        raise StoreOccupiedError("El local ya tiene un comerciante activo.")

    user = User(
        email=email,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role="merchant",
        is_active=True,
        store_id=store.id,
    )
    session.add(user)

    try:
        session.commit()
    except IntegrityError as error:
        session.rollback()
        constraint = _constraint_name(error)
        if constraint == STORE_CONSTRAINT:
            raise StoreOccupiedError(
                "El local ya tiene un comerciante activo."
            ) from None
        if constraint == EMAIL_CONSTRAINT:
            raise DuplicateEmailError("El correo ya está registrado.") from None
        raise

    session.refresh(user)
    return MerchantRead(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at,
        store=StoreRef.model_validate(store),
    )


def deactivate_merchant(session: Session, merchant_id: int) -> None:
    """Logically deactivate a merchant, keeping its store as history."""
    user = session.scalar(
        select(User).where(User.id == merchant_id, User.role == "merchant")
    )
    if user is None:
        raise MerchantNotFoundError("El comerciante no existe.")
    if user.is_active:
        user.is_active = False
        session.commit()


def list_stores(session: Session) -> list[StoreAdminRead]:
    """Return every store with its active merchant using one query."""
    rows = session.execute(
        select(Store, User)
        .outerjoin(
            User,
            and_(
                User.store_id == Store.id,
                User.role == "merchant",
                User.is_active.is_(True),
            ),
        )
        .order_by(Store.number)
    ).all()

    return [
        StoreAdminRead(
            id=store.id,
            number=store.number,
            name=store.name,
            side=store.side,
            position=store.position,
            is_active=store.is_active,
            merchant=StoreMerchantRef.model_validate(user) if user else None,
        )
        for store, user in rows
    ]
