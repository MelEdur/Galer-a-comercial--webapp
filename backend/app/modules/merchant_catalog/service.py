"""Business rules for the merchant product catalog.

Every operation is scoped to the store of the authenticated merchant. The
service raises domain exceptions that the router translates into HTTP
responses, keeping ownership checks out of the HTTP layer.
"""

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import exists, func, select
from sqlalchemy.orm import Session, selectinload

from app.modules.catalog.models import (
    Category,
    Product,
    ProductCategory,
    ProductImage,
)
from app.modules.merchant_catalog.schemas import (
    CategoryRead,
    ImageInput,
    ImageRead,
    PaginatedProducts,
    ProductCreate,
    ProductRead,
    ProductUpdate,
)


class MerchantCatalogError(Exception):
    """Base class for expected merchant catalog errors."""


class ProductNotFoundError(MerchantCatalogError):
    """The product does not exist or belongs to another store."""


class ProductDeletedError(MerchantCatalogError):
    """The product is logically deleted and cannot be modified."""


class CategoryNotFoundError(MerchantCatalogError):
    """One or more requested categories do not exist."""


class InvalidOfferPriceError(MerchantCatalogError):
    """The offer price is not strictly lower than the product price."""


def _escape_like(value: str) -> str:
    """Escape SQL ``LIKE`` wildcards so they are matched literally."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _load_options() -> tuple:
    """Eager-load the relationships needed to serialize a product."""
    return (
        selectinload(Product.images),
        selectinload(Product.product_categories).selectinload(
            ProductCategory.category
        ),
    )


def _to_read(product: Product) -> ProductRead:
    """Build the API representation without leaking internal columns."""
    categories = [
        CategoryRead(id=link.category.id, name=link.category.name)
        for link in product.product_categories
    ]
    categories.sort(key=lambda category: (category.name.lower(), category.id))

    images = [
        ImageRead(
            id=image.id,
            url=image.url,
            alt_text=image.alt_text,
            position=image.position,
            is_primary=image.is_primary,
        )
        for image in product.images
    ]
    images.sort(key=lambda image: image.position)

    return ProductRead(
        id=product.id,
        name=product.name,
        description=product.description,
        price=product.price,
        offer_price=product.offer_price,
        categories=categories,
        images=images,
        is_active=product.is_active,
        deleted_at=product.deleted_at,
        created_at=product.created_at,
        updated_at=product.updated_at,
    )


def _validate_offer_price(price: Decimal, offer_price: Decimal | None) -> None:
    """Enforce the offer rule with a clear domain error."""
    if offer_price is not None and offer_price >= price:
        raise InvalidOfferPriceError(
            "El precio de oferta debe ser menor que el precio."
        )


def _validate_categories(
    session: Session, category_ids: list[int]
) -> list[Category]:
    """Return every requested category or raise a clear domain error."""
    unique_ids = list(dict.fromkeys(category_ids))
    categories = list(
        session.scalars(select(Category).where(Category.id.in_(unique_ids))).all()
    )
    found = {category.id for category in categories}
    missing = [category_id for category_id in unique_ids if category_id not in found]
    if missing:
        raise CategoryNotFoundError(
            "Alguna de las categorías indicadas no existe."
        )
    by_id = {category.id: category for category in categories}
    return [by_id[category_id] for category_id in unique_ids]


def _new_images(images: list[ImageInput] | None) -> list[ProductImage]:
    """Build ordered image rows, marking the first one as primary."""
    if not images:
        return []
    return [
        ProductImage(
            url=str(image.url),
            alt_text=image.alt_text,
            position=position,
            is_primary=position == 0,
        )
        for position, image in enumerate(images)
    ]


def list_products(
    session: Session,
    store_id: int,
    *,
    search: str | None,
    status: str,
    category_id: int | None,
    page: int,
    page_size: int,
) -> PaginatedProducts:
    """Return one filtered page of the products owned by ``store_id``."""
    conditions = [Product.store_id == store_id]

    if status == "active":
        conditions.append(Product.deleted_at.is_(None))
    elif status == "deleted":
        conditions.append(Product.deleted_at.is_not(None))

    if search and search.strip():
        pattern = f"%{_escape_like(search.strip())}%"
        conditions.append(Product.name.ilike(pattern, escape="\\"))

    if category_id is not None:
        conditions.append(
            exists(
                select(ProductCategory.product_id).where(
                    ProductCategory.product_id == Product.id,
                    ProductCategory.category_id == category_id,
                )
            )
        )

    total = (
        session.scalar(
            select(func.count()).select_from(Product).where(*conditions)
        )
        or 0
    )

    products = list(
        session.scalars(
            select(Product)
            .where(*conditions)
            .options(*_load_options())
            .order_by(func.lower(Product.name), Product.id)
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
    )

    pages = (total + page_size - 1) // page_size
    return PaginatedProducts(
        items=[_to_read(product) for product in products],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


def _get_owned_product(
    session: Session, store_id: int, product_id: int
) -> Product:
    """Return a product of the store or raise ``ProductNotFoundError``."""
    product = session.scalar(
        select(Product)
        .where(Product.id == product_id, Product.store_id == store_id)
        .options(*_load_options())
    )
    if product is None:
        raise ProductNotFoundError("El producto no existe.")
    return product


def get_product(session: Session, store_id: int, product_id: int) -> ProductRead:
    """Return a single product of the store, including deleted ones."""
    return _to_read(_get_owned_product(session, store_id, product_id))


def create_product(
    session: Session, store_id: int, payload: ProductCreate
) -> ProductRead:
    """Create a product owned by ``store_id`` with categories and images."""
    _validate_offer_price(payload.price, payload.offer_price)
    categories = _validate_categories(session, payload.category_ids)

    product = Product(
        store_id=store_id,
        name=payload.name,
        description=payload.description,
        price=payload.price,
        offer_price=payload.offer_price,
        is_active=True,
    )
    for category in categories:
        product.product_categories.append(ProductCategory(category=category))
    product.images.extend(_new_images(payload.images))

    session.add(product)
    session.commit()
    return _to_read(product)


def update_product(
    session: Session,
    store_id: int,
    product_id: int,
    payload: ProductUpdate,
) -> ProductRead:
    """Apply a partial update to a non-deleted product of the store."""
    product = _get_owned_product(session, store_id, product_id)
    if product.deleted_at is not None:
        raise ProductDeletedError(
            "El producto está eliminado y no se puede modificar."
        )

    fields = payload.model_fields_set

    if "name" in fields:
        product.name = payload.name
    if "description" in fields:
        product.description = payload.description
    if "price" in fields:
        product.price = payload.price
    if "offer_price" in fields:
        product.offer_price = payload.offer_price

    _validate_offer_price(product.price, product.offer_price)

    if "category_ids" in fields:
        categories = _validate_categories(session, payload.category_ids or [])
        product.product_categories.clear()
        session.flush()
        for category in categories:
            product.product_categories.append(ProductCategory(category=category))

    if "images" in fields:
        product.images.clear()
        session.flush()
        product.images.extend(_new_images(payload.images))

    product.updated_at = datetime.now(timezone.utc)
    session.commit()
    return _to_read(product)


def delete_product(session: Session, store_id: int, product_id: int) -> None:
    """Logically delete an owned product; repeating it changes nothing."""
    product = _get_owned_product(session, store_id, product_id)
    if product.deleted_at is not None:
        return

    now = datetime.now(timezone.utc)
    product.deleted_at = now
    product.is_active = False
    product.updated_at = now
    session.commit()


def restore_product(
    session: Session, store_id: int, product_id: int
) -> ProductRead:
    """Restore an owned deleted product; repeating it changes nothing."""
    product = _get_owned_product(session, store_id, product_id)
    if product.deleted_at is None:
        return _to_read(product)

    now = datetime.now(timezone.utc)
    product.deleted_at = None
    product.is_active = True
    product.updated_at = now
    session.commit()
    return _to_read(product)


def list_categories(session: Session) -> list[CategoryRead]:
    """Return every global category ordered by name."""
    rows = session.scalars(
        select(Category).order_by(func.lower(Category.name), Category.id)
    ).all()
    return [CategoryRead.model_validate(category) for category in rows]
