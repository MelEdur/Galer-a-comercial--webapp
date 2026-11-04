"""Public catalog endpoints (CU #1 and CU #3), without authentication."""

from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.public_catalog.schemas import (
    PaginatedPublicProducts,
    PublicCategory,
    PublicProductDetail,
    PublicSimilarProducts,
    PublicStoreProfile,
)
from app.modules.public_catalog.service import (
    InvalidPriceRangeError,
    ProductNotFoundError,
    StoreNotFoundError,
    get_product_detail,
    get_store_profile,
    list_categories,
    list_products,
    list_similar_products,
)

router = APIRouter(prefix="/public", tags=["public"])


@router.get(
    "/products",
    response_model=PaginatedPublicProducts,
    summary="Search the available public product catalog",
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Invalid filters or pagination values."
        }
    },
)
def get_public_products(
    search: str | None = Query(default=None),
    category_id: int | None = Query(default=None),
    min_price: Decimal | None = Query(default=None, ge=0),
    max_price: Decimal | None = Query(default=None, ge=0),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort: Literal["name", "price_asc", "price_desc"] = Query(default="name"),
    db: Session = Depends(get_db),
) -> PaginatedPublicProducts:
    """Return one page of available products filtered by the visitor."""
    try:
        return list_products(
            db,
            search=search,
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            page=page,
            page_size=page_size,
            sort=sort,
        )
    except InvalidPriceRangeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from None


@router.get(
    "/categories",
    response_model=list[PublicCategory],
    summary="List the global product categories",
)
def get_public_categories(db: Session = Depends(get_db)) -> list[PublicCategory]:
    """Return every category ordered by name."""
    return list_categories(db)


@router.get(
    "/products/{product_id}",
    response_model=PublicProductDetail,
    summary="Get the public detail of an available product",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Product not available."},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "The product identifier is not numeric."
        },
    },
)
def get_public_product(
    product_id: int, db: Session = Depends(get_db)
) -> PublicProductDetail:
    """Return the product detail with its images and store contact data."""
    try:
        return get_product_detail(db, product_id)
    except ProductNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from None


@router.get(
    "/products/{product_id}/similar",
    response_model=PublicSimilarProducts,
    summary="List products similar to an available product",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Product not available."},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "The product identifier is not numeric."
        },
    },
)
def get_public_similar_products(
    product_id: int, db: Session = Depends(get_db)
) -> PublicSimilarProducts:
    """Return up to six products sharing categories or name words."""
    try:
        return list_similar_products(db, product_id)
    except ProductNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from None


@router.get(
    "/stores/{store_id}",
    response_model=PublicStoreProfile,
    summary="Get the public profile of an available store",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Store not available."},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "The store identifier is not numeric."
        },
    },
)
def get_public_store(
    store_id: int, db: Session = Depends(get_db)
) -> PublicStoreProfile:
    """Return the store profile with its hours, contact data and links."""
    try:
        return get_store_profile(db, store_id)
    except StoreNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from None
