"""HTTP endpoints for the authenticated merchant's product catalog."""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.accounts.models import User
from app.modules.auth.dependencies import require_merchant
from app.modules.merchant_catalog.schemas import (
    CategoryRead,
    PaginatedProducts,
    ProductCreate,
    ProductRead,
    ProductUpdate,
)
from app.modules.merchant_catalog.service import (
    CategoryNotFoundError,
    InvalidOfferPriceError,
    ProductDeletedError,
    ProductNotFoundError,
    create_product,
    delete_product,
    get_product,
    list_categories,
    list_products,
    restore_product,
    update_product,
)

router = APIRouter(
    prefix="/merchant",
    tags=["merchant"],
    dependencies=[Depends(require_merchant)],
)


def _unprocessable(exc: Exception) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=str(exc),
    )


@router.get(
    "/products",
    response_model=PaginatedProducts,
    summary="List the products of the authenticated merchant",
)
def get_products(
    search: str | None = Query(default=None),
    product_status: Literal["active", "deleted", "all"] = Query(
        default="active", alias="status"
    ),
    category_id: int | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(require_merchant),
    db: Session = Depends(get_db),
) -> PaginatedProducts:
    """Return one filtered, paginated page of the merchant's catalog."""
    return list_products(
        db,
        current_user.store_id,
        search=search,
        status=product_status,
        category_id=category_id,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/products/{product_id}",
    response_model=ProductRead,
    summary="Get a product of the authenticated merchant",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Product not found."}},
)
def get_merchant_product(
    product_id: int,
    current_user: User = Depends(require_merchant),
    db: Session = Depends(get_db),
) -> ProductRead:
    """Return an owned product, including logically deleted ones."""
    try:
        return get_product(db, current_user.store_id, product_id)
    except ProductNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from None


@router.post(
    "/products",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a product in the authenticated merchant's store",
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Invalid data or unknown category."
        }
    },
)
def post_product(
    payload: ProductCreate,
    current_user: User = Depends(require_merchant),
    db: Session = Depends(get_db),
) -> ProductRead:
    """Create a product; ownership always comes from the token."""
    try:
        return create_product(db, current_user.store_id, payload)
    except (CategoryNotFoundError, InvalidOfferPriceError) as exc:
        raise _unprocessable(exc) from None


@router.patch(
    "/products/{product_id}",
    response_model=ProductRead,
    summary="Partially update a product of the authenticated merchant",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Product not found."},
        status.HTTP_409_CONFLICT: {"description": "Product is deleted."},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Invalid data or unknown category."
        },
    },
)
def patch_product(
    product_id: int,
    payload: ProductUpdate,
    current_user: User = Depends(require_merchant),
    db: Session = Depends(get_db),
) -> ProductRead:
    """Apply a partial update to an owned, non-deleted product."""
    try:
        return update_product(db, current_user.store_id, product_id, payload)
    except ProductNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from None
    except ProductDeletedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from None
    except (CategoryNotFoundError, InvalidOfferPriceError) as exc:
        raise _unprocessable(exc) from None


@router.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logically delete a product of the authenticated merchant",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Product not found."}},
)
def delete_merchant_product(
    product_id: int,
    current_user: User = Depends(require_merchant),
    db: Session = Depends(get_db),
) -> Response:
    """Logically delete an owned product; repeating it is idempotent."""
    try:
        delete_product(db, current_user.store_id, product_id)
    except ProductNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from None
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/products/{product_id}/restore",
    response_model=ProductRead,
    summary="Restore a logically deleted product of the authenticated merchant",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Product not found."}},
)
def post_restore_product(
    product_id: int,
    current_user: User = Depends(require_merchant),
    db: Session = Depends(get_db),
) -> ProductRead:
    """Restore an owned product; restoring an active product is a no-op."""
    try:
        return restore_product(db, current_user.store_id, product_id)
    except ProductNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from None


@router.get(
    "/categories",
    response_model=list[CategoryRead],
    summary="List the global product categories",
)
def get_categories(db: Session = Depends(get_db)) -> list[CategoryRead]:
    """Return every category ordered by name (read-only)."""
    return list_categories(db)
