"""Request and response schemas for the merchant product catalog."""

from datetime import datetime
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)

NAME_MAX_LENGTH = 160
DESCRIPTION_MAX_LENGTH = 2000
IMAGE_URL_MAX_LENGTH = 500
IMAGE_ALT_TEXT_MAX_LENGTH = 200
MAX_IMAGES = 5


def _clean_name(value: str) -> str:
    """Trim the name and reject whitespace-only values."""
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("El nombre del producto es obligatorio.")
    return cleaned


class CategoryRead(BaseModel):
    """A global category available to classify products."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class ImageInput(BaseModel):
    """An image submitted as an ``http`` or ``https`` URL."""

    model_config = ConfigDict(extra="forbid")

    url: HttpUrl
    alt_text: str | None = Field(default=None, max_length=IMAGE_ALT_TEXT_MAX_LENGTH)

    @field_validator("url")
    @classmethod
    def validate_url_length(cls, value: HttpUrl) -> HttpUrl:
        """Reject URLs longer than the database column allows."""
        if len(str(value)) > IMAGE_URL_MAX_LENGTH:
            raise ValueError(
                f"La URL de la imagen no puede superar los {IMAGE_URL_MAX_LENGTH} caracteres."
            )
        return value


class ImageRead(BaseModel):
    """An ordered image of a product."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    alt_text: str | None
    position: int
    is_primary: bool


class ProductCreate(BaseModel):
    """Data required to create a product in the authenticated merchant's store."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=NAME_MAX_LENGTH)
    description: str | None = Field(default=None, max_length=DESCRIPTION_MAX_LENGTH)
    price: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    offer_price: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    category_ids: list[int] = Field(min_length=1)
    images: list[ImageInput] | None = Field(default=None, max_length=MAX_IMAGES)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return _clean_name(value)

    @model_validator(mode="after")
    def validate_offer_price(self) -> "ProductCreate":
        """Reject an offer price that is not strictly lower than the price."""
        if self.offer_price is not None and self.offer_price >= self.price:
            raise ValueError(
                "El precio de oferta debe ser menor que el precio."
            )
        return self


class ProductUpdate(BaseModel):
    """Partial update; provided collections replace the previous ones."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=NAME_MAX_LENGTH)
    description: str | None = Field(default=None, max_length=DESCRIPTION_MAX_LENGTH)
    price: Decimal | None = Field(
        default=None, ge=0, max_digits=10, decimal_places=2
    )
    offer_price: Decimal | None = Field(
        default=None, ge=0, max_digits=10, decimal_places=2
    )
    category_ids: list[int] | None = Field(default=None, min_length=1)
    images: list[ImageInput] | None = Field(default=None, max_length=MAX_IMAGES)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        return _clean_name(value) if value is not None else None

    @model_validator(mode="after")
    def validate_provided_fields(self) -> "ProductUpdate":
        """Reject explicit nulls for required fields and validate the offer."""
        for field in ("name", "price", "category_ids"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"El campo '{field}' no puede ser nulo.")
        if (
            self.price is not None
            and self.offer_price is not None
            and self.offer_price >= self.price
        ):
            raise ValueError(
                "El precio de oferta debe ser menor que el precio."
            )
        return self


class ProductRead(BaseModel):
    """Public representation of a product owned by the merchant."""

    id: int
    name: str
    description: str | None
    price: Decimal
    offer_price: Decimal | None
    categories: list[CategoryRead]
    images: list[ImageRead]
    is_active: bool
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime


class PaginatedProducts(BaseModel):
    """One page of the merchant's products."""

    items: list[ProductRead]
    total: int
    page: int
    page_size: int
    pages: int
