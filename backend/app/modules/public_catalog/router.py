"""Public catalog endpoints (CU #1 and CU #3), without authentication."""

from decimal import Decimal
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.public_catalog.schemas import (
    ExploreResponse,
    ExploreStore,
    MapResponse,
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
    get_store_map,
    get_store_profile,
    list_categories,
    list_explore,
    list_products,
    list_public_stores,
    list_similar_products,
    list_store_products,
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
    has_offer: bool = Query(default=False),
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
            has_offer=has_offer,
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
    "/explore",
    response_model=ExploreResponse,
    summary="Get the public discovery page",
)
def get_public_explore(db: Session = Depends(get_db)) -> ExploreResponse:
    """Return featured products, offers, categories and active stores."""
    return list_explore(db)


@router.get(
    "/stores",
    response_model=list[ExploreStore],
    summary="List every active store",
)
def get_public_stores(db: Session = Depends(get_db)) -> list[ExploreStore]:
    """Return every active store ordered by number, without pagination."""
    return list_public_stores(db)


@router.get(
    "/map",
    response_model=MapResponse,
    summary="Get the public gallery map",
)
def get_public_map(db: Session = Depends(get_db)) -> MapResponse:
    """Return every active store with its location, without pagination."""
    return get_store_map(db)


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


@router.get(
    "/stores/{store_id}/products",
    response_model=PaginatedPublicProducts,
    summary="List the available products of a store",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Store not available."},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": (
                "The store identifier is not numeric or the pagination values "
                "are out of range."
            )
        },
    },
)
def get_public_store_products(
    store_id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=12, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PaginatedPublicProducts:
    """Return one page of the store's available products ordered by name."""
    try:
        return list_store_products(db, store_id, page=page, page_size=page_size)
    except StoreNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from None
