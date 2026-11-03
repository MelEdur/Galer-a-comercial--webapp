"""Administrative HTTP endpoints for merchants and stores."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import require_admin
from app.modules.merchants.schemas import MerchantCreate, MerchantRead, StoreAdminRead
from app.modules.merchants.service import (
    DuplicateEmailError,
    MerchantNotFoundError,
    StoreNotFoundError,
    StoreOccupiedError,
    create_merchant,
    deactivate_merchant,
    list_merchants,
    list_stores,
)

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


@router.get(
    "/merchants",
    response_model=list[MerchantRead],
    summary="List merchant accounts",
)
def get_merchants(db: Session = Depends(get_db)) -> list[MerchantRead]:
    """Return every merchant ordered by full name."""
    return list_merchants(db)


@router.post(
    "/merchants",
    response_model=MerchantRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a merchant account",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "The store does not exist."},
        status.HTTP_409_CONFLICT: {
            "description": "Duplicate email or store already occupied."
        },
    },
)
def post_merchant(
    payload: MerchantCreate, db: Session = Depends(get_db)
) -> MerchantRead:
    """Create an active merchant assigned to a free store."""
    try:
        return create_merchant(db, payload)
    except StoreNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from None
    except DuplicateEmailError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from None
    except StoreOccupiedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from None


@router.delete(
    "/merchants/{merchant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate a merchant account",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Merchant not found."}},
)
def delete_merchant(
    merchant_id: int, db: Session = Depends(get_db)
) -> Response:
    """Logically deactivate a merchant; repeating it is idempotent."""
    try:
        deactivate_merchant(db, merchant_id)
    except MerchantNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from None
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/stores",
    response_model=list[StoreAdminRead],
    summary="List stores with their active merchant",
)
def get_stores(db: Session = Depends(get_db)) -> list[StoreAdminRead]:
    """Return every store ordered by number with its active merchant."""
    return list_stores(db)
