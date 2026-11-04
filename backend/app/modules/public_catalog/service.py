"""Business logic for the public product search (CU #1).

The service implements the availability rules, the combinable filters, the
ordering, the pagination and the search-event registration. The router only
translates domain errors into HTTP responses.
"""

import logging
import re
from decimal import Decimal

from sqlalchemy import exists, func, insert, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from app.modules.analytics.models import ProductSearchEvent
from app.modules.catalog.models import Category, Product, ProductCategory
from app.modules.public_catalog.schemas import (
    PaginatedPublicProducts,
    PublicCategory,
    PublicImage,
    PublicImageDetail,
    PublicProduct,
    PublicProductDetail,
    PublicSimilarProducts,
    PublicStore,
    PublicStoreDetail,
    PublicStoreHour,
    PublicStoreLink,
    PublicStoreProfile,
)
from app.modules.stores.models import Store, StoreHour, StoreLink

logger = logging.getLogger(__name__)

SIMILAR_RESULTS_LIMIT = 6
SIMILAR_CANDIDATES_LIMIT = 50
# A "significant" word is a run of letters (any alphabet) of at least 3 chars.
_WORD_PATTERN = re.compile(r"[^\W\d_]+", re.UNICODE)


class InvalidPriceRangeError(Exception):
    """The minimum price is greater than the maximum price."""


class ProductNotFoundError(Exception):
    """The requested product does not exist or is not publicly available."""


class StoreNotFoundError(Exception):
    """The requested store does not exist or is not publicly available."""


def _escape_like(value: str) -> str:
    """Escape SQL ``LIKE`` wildcards so they are matched literally."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _effective_price():
    """SQL expression for the price the visitor actually pays."""
    return func.coalesce(Product.offer_price, Product.price)


def _primary_image(product: Product) -> PublicImage | None:
    """Pick the primary image, falling back to the lowest position."""
    if not product.images:
        return None
    primary = next(
        (image for image in product.images if image.is_primary), None
    )
    if primary is None:
        primary = min(product.images, key=lambda image: (image.position, image.id))
    return PublicImage(url=primary.url, alt_text=primary.alt_text)


def _to_read(product: Product) -> PublicProduct:
    """Build the public representation without leaking internal columns."""
    categories = [
        PublicCategory(id=link.category.id, name=link.category.name)
        for link in product.product_categories
    ]
    categories.sort(key=lambda category: (category.name.lower(), category.id))

    effective_price = (
        product.offer_price if product.offer_price is not None else product.price
    )

    return PublicProduct(
        id=product.id,
        name=product.name,
        description=product.description,
        price=product.price,
        offer_price=product.offer_price,
        effective_price=effective_price,
        categories=categories,
        primary_image=_primary_image(product),
        store=PublicStore(
            id=product.store.id,
            number=product.store.number,
            name=product.store.name,
        ),
    )


def _base_conditions() -> list:
    """Availability rules shared by the count and the page query."""
    return [
        Product.deleted_at.is_(None),
        Product.is_active.is_(True),
        Store.is_active.is_(True),
    ]


def _detail_options() -> tuple:
    """Eager loads that avoid N+1 queries when serializing a product."""
    return (
        selectinload(Product.store),
        selectinload(Product.images),
        selectinload(Product.product_categories).selectinload(
            ProductCategory.category
        ),
    )


def _load_available_product(
    session: Session, product_id: int, *, detail: bool
) -> Product | None:
    """Load a publicly available product or return ``None``.

    The detail query also loads the store and every image. The lighter query
    used by the similar-products endpoint only needs the categories.
    """
    query = (
        select(Product)
        .join(Store, Product.store_id == Store.id)
        .where(Product.id == product_id, *_base_conditions())
    )
    if detail:
        query = query.options(*_detail_options())
    else:
        query = query.options(
            selectinload(Product.product_categories).selectinload(
                ProductCategory.category
            )
        )
    return session.scalars(query).first()


def _sorted_categories(product: Product) -> list[PublicCategory]:
    """Public categories ordered by name, independent of letter case."""
    categories = [
        PublicCategory(id=link.category.id, name=link.category.name)
        for link in product.product_categories
    ]
    categories.sort(key=lambda category: (category.name.lower(), category.id))
    return categories


def _to_detail(product: Product) -> PublicProductDetail:
    """Build the detail representation of an available product."""
    images = sorted(product.images, key=lambda image: (image.position, image.id))
    effective_price = (
        product.offer_price if product.offer_price is not None else product.price
    )

    return PublicProductDetail(
        id=product.id,
        name=product.name,
        description=product.description,
        price=product.price,
        offer_price=product.offer_price,
        effective_price=effective_price,
        categories=_sorted_categories(product),
        images=[PublicImageDetail.model_validate(image) for image in images],
        store=PublicStoreDetail.model_validate(product.store),
    )


def get_product_detail(session: Session, product_id: int) -> PublicProductDetail:
    """Return the public detail of an available product.

    Raises:
        ProductNotFoundError: if the product is missing, deleted, inactive or
            belongs to an inactive store.
    """
    product = _load_available_product(session, product_id, detail=True)
    if product is None:
        raise ProductNotFoundError("Producto no encontrado.")
    return _to_detail(product)


def _significant_words(name: str) -> list[str]:
    """Extract the lowercase letter runs of three or more characters."""
    words: list[str] = []
    seen: set[str] = set()
    for match in _WORD_PATTERN.finditer(name):
        word = match.group(0).lower()
        if len(word) < 3 or word in seen:
            continue
        seen.add(word)
        words.append(word)
    return words


def _candidate_score(
    product: Product, category_ids: set[int], words: list[str]
) -> tuple[int, int]:
    """Return shared categories and matching words for a similar candidate."""
    candidate_categories = {
        link.category_id for link in product.product_categories
    }
    lowered_name = product.name.lower()
    matched_words = sum(1 for word in words if word in lowered_name)
    return len(category_ids & candidate_categories), matched_words


def list_similar_products(
    session: Session, product_id: int
) -> PublicSimilarProducts:
    """Return up to six available products similar to the requested one.

    Raises:
        ProductNotFoundError: if the base product is not publicly available.
    """
    base = _load_available_product(session, product_id, detail=False)
    if base is None:
        raise ProductNotFoundError("Producto no encontrado.")

    category_ids = {link.category_id for link in base.product_categories}
    words = _significant_words(base.name)
    if not category_ids and not words:
        return PublicSimilarProducts(items=[])

    conditions = []
    if category_ids:
        conditions.append(
            exists(
                select(ProductCategory.product_id).where(
                    ProductCategory.product_id == Product.id,
                    ProductCategory.category_id.in_(category_ids),
                )
            )
        )
    for word in words:
        pattern = f"%{_escape_like(word)}%"
        conditions.append(Product.name.ilike(pattern, escape="\\"))

    candidates = list(
        session.scalars(
            select(Product)
            .join(Store, Product.store_id == Store.id)
            .where(
                Product.id != product_id,
                *_base_conditions(),
                or_(*conditions),
            )
            .options(*_detail_options())
            .order_by(func.lower(Product.name), Product.id)
            .limit(SIMILAR_CANDIDATES_LIMIT)
        ).all()
    )

    ranked = sorted(
        candidates,
        key=lambda product: (
            -_candidate_score(product, category_ids, words)[0],
            -_candidate_score(product, category_ids, words)[1],
            product.name.lower(),
            product.id,
        ),
    )
    return PublicSimilarProducts(
        items=[_to_read(product) for product in ranked[:SIMILAR_RESULTS_LIMIT]]
    )


def _record_events(
    session: Session, product_ids: list[int], query: str | None
) -> None:
    """Insert one search event per returned product in a single statement.

    Failure must never break the search: the transaction is rolled back and a
    warning is logged, leaving the already-serialized response untouched.
    """
    rows = [{"product_id": product_id, "query": query} for product_id in product_ids]
    try:
        session.execute(insert(ProductSearchEvent), rows)
        session.commit()
    except SQLAlchemyError as exc:
        session.rollback()
        logger.warning(
            "No se pudieron registrar los eventos de búsqueda (%s)",
            type(exc).__name__,
        )


def list_products(
    session: Session,
    *,
    search: str | None,
    category_id: int | None,
    min_price: Decimal | None,
    max_price: Decimal | None,
    page: int,
    page_size: int,
    sort: str,
) -> PaginatedPublicProducts:
    """Return one filtered, ordered page of the available public catalog."""
    if min_price is not None and max_price is not None and min_price > max_price:
        raise InvalidPriceRangeError(
            "El precio mínimo no puede ser mayor que el precio máximo."
        )

    normalized_search = search.strip() if search is not None else ""
    has_criteria = (
        bool(normalized_search)
        or category_id is not None
        or min_price is not None
        or max_price is not None
    )

    conditions = _base_conditions()

    if normalized_search:
        pattern = f"%{_escape_like(normalized_search)}%"
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

    effective_price = _effective_price()
    if min_price is not None:
        conditions.append(effective_price >= min_price)
    if max_price is not None:
        conditions.append(effective_price <= max_price)

    total = (
        session.scalar(
            select(func.count())
            .select_from(Product)
            .join(Store, Product.store_id == Store.id)
            .where(*conditions)
        )
        or 0
    )

    if sort == "price_asc":
        order_by = (effective_price.asc(), func.lower(Product.name), Product.id)
    elif sort == "price_desc":
        order_by = (effective_price.desc(), func.lower(Product.name), Product.id)
    else:
        order_by = (func.lower(Product.name), Product.id)

    products = list(
        session.scalars(
            select(Product)
            .join(Store, Product.store_id == Store.id)
            .where(*conditions)
            .options(
                selectinload(Product.store),
                selectinload(Product.images),
                selectinload(Product.product_categories).selectinload(
                    ProductCategory.category
                ),
            )
            .order_by(*order_by)
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
    )

    items = [_to_read(product) for product in products]
    pages = (total + page_size - 1) // page_size
    result = PaginatedPublicProducts(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )

    if has_criteria and products:
        _record_events(
            session,
            [product.id for product in products],
            normalized_search or None,
        )

    return result


def list_categories(session: Session) -> list[PublicCategory]:
    """Return every global category ordered by name."""
    rows = session.scalars(
        select(Category).order_by(func.lower(Category.name), Category.id)
    ).all()
    return [PublicCategory.model_validate(category) for category in rows]


def get_store_profile(session: Session, store_id: int) -> PublicStoreProfile:
    """Return the public profile of an available store.

    Hours are ordered by weekday and opening time, links by their position.
    Both collections are eager loaded to avoid N+1 queries.

    Raises:
        StoreNotFoundError: if the store is missing or inactive.
    """
    store = session.scalars(
        select(Store)
        .where(Store.id == store_id, Store.is_active.is_(True))
        .options(selectinload(Store.hours), selectinload(Store.links))
    ).first()
    if store is None:
        raise StoreNotFoundError("Local no encontrado.")

    hours = sorted(
        store.hours,
        key=lambda hour: (hour.day_of_week, hour.opens_at, hour.id),
    )
    links = sorted(store.links, key=lambda link: (link.position, link.id))

    return PublicStoreProfile(
        id=store.id,
        number=store.number,
        name=store.name,
        description=store.description,
        logo_url=store.logo_url,
        email=store.email,
        phone=store.phone,
        whatsapp=store.whatsapp,
        hours=[PublicStoreHour.model_validate(hour) for hour in hours],
        links=[PublicStoreLink.model_validate(link) for link in links],
    )
