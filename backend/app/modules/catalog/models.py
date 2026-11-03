"""Catalog module: categories, products, their association and images."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Numeric,
    PrimaryKeyConstraint,
    SmallInteger,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.modules.analytics.models import ProductSearchEvent
    from app.modules.stores.models import Store


class Category(TimestampMixin, Base):
    """A global catalog category, unique regardless of letter case."""

    __tablename__ = "categories"
    __table_args__ = (
        Index("uq_categories_name_lower", text("lower(name)"), unique=True),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)

    product_categories: Mapped[list[ProductCategory]] = relationship(
        back_populates="category",
    )


class Product(TimestampMixin, Base):
    """A product belonging to a single store, with optional offer price."""

    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_products_price_non_negative"),
        CheckConstraint(
            "offer_price IS NULL OR (offer_price >= 0 AND offer_price < price)",
            name="ck_products_offer_price",
        ),
        Index("ix_products_store_id", "store_id"),
        Index("ix_products_price", "price"),
        Index("ix_products_name_lower", text("lower(name)")),
        Index(
            "ix_products_featured_active",
            "is_featured",
            postgresql_where=text("is_featured AND deleted_at IS NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    store_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("stores.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    offer_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    is_featured: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    store: Mapped[Store] = relationship(back_populates="products")
    product_categories: Mapped[list[ProductCategory]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )
    images: Mapped[list[ProductImage]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
        order_by="ProductImage.position",
    )
    search_events: Mapped[list[ProductSearchEvent]] = relationship(
        back_populates="product",
        passive_deletes=True,
    )


class ProductCategory(Base):
    """Association between a product and a category (composite key)."""

    __tablename__ = "product_categories"
    __table_args__ = (
        PrimaryKeyConstraint(
            "product_id", "category_id", name="pk_product_categories"
        ),
        Index("ix_product_categories_category_id", "category_id"),
    )

    product_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    category_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
    )

    product: Mapped[Product] = relationship(back_populates="product_categories")
    category: Mapped[Category] = relationship(back_populates="product_categories")


class ProductImage(Base):
    """An ordered image of a product, at most one marked as primary."""

    __tablename__ = "product_images"
    __table_args__ = (
        CheckConstraint("position >= 0", name="ck_product_images_position"),
        Index(
            "uq_product_images_primary",
            "product_id",
            unique=True,
            postgresql_where=text("is_primary"),
        ),
        Index("ix_product_images_product_id", "product_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    product_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    alt_text: Mapped[str | None] = mapped_column(String(200), nullable=True)
    position: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default=text("0")
    )
    is_primary: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )

    product: Mapped[Product] = relationship(back_populates="images")
