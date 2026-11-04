"""Response schemas for the public product catalog.

These schemas are the public API contract: they expose only the data a visitor
needs and never internal columns such as ``store_id``, ``is_active`` or
``deleted_at``.
"""

from datetime import time
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PublicCategory(BaseModel):
    """A global category available to filter the public search."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class PublicImage(BaseModel):
    """The primary image of a product, when it has one."""

    url: str
    alt_text: str | None


class PublicStore(BaseModel):
    """The store that offers a product."""

    id: int
    number: int
    name: str


class PublicProduct(BaseModel):
    """A product as shown to a visitor in the public search."""

    id: int
    name: str
    description: str | None
    price: Decimal
    offer_price: Decimal | None
    effective_price: Decimal
    categories: list[PublicCategory]
    primary_image: PublicImage | None
    store: PublicStore


class PaginatedPublicProducts(BaseModel):
    """One page of the public product search."""

    items: list[PublicProduct]
    total: int
    page: int
    page_size: int
    pages: int


class PublicImageDetail(BaseModel):
    """A product image in the public detail, with its gallery position."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    alt_text: str | None
    position: int
    is_primary: bool


class PublicStoreDetail(BaseModel):
    """The store that sells a product, with its public contact details."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    number: int
    name: str
    logo_url: str | None
    email: str | None
    phone: str | None
    whatsapp: str | None


class PublicProductDetail(BaseModel):
    """The full public detail of a product, including every image."""

    id: int
    name: str
    description: str | None
    price: Decimal
    offer_price: Decimal | None
    effective_price: Decimal
    categories: list[PublicCategory]
    images: list[PublicImageDetail]
    store: PublicStoreDetail


class PublicSimilarProducts(BaseModel):
    """Products similar to the one being viewed."""

    items: list[PublicProduct]


class PublicStoreHour(BaseModel):
    """An opening interval of a store, as shown in its public profile."""

    model_config = ConfigDict(from_attributes=True)

    day_of_week: int
    opens_at: time
    closes_at: time


class PublicStoreLink(BaseModel):
    """An ordered external link of a store."""

    model_config = ConfigDict(from_attributes=True)

    label: str
    url: str
    position: int


class PublicStoreProfile(BaseModel):
    """The public profile of an available store.

    Only visitor-facing data is exposed: internal columns such as ``is_active``,
    ``side`` or ``position`` and related accounts or products are never included.
    """

    id: int
    number: int
    name: str
    description: str | None
    logo_url: str | None
    email: str | None
    phone: str | None
    whatsapp: str | None
    hours: list[PublicStoreHour]
    links: list[PublicStoreLink]
