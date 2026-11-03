"""Analytics module: product search events used for statistics."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.modules.catalog.models import Product


class ProductSearchEvent(Base):
    """A single occurrence of a product being returned in a search."""

    __tablename__ = "product_search_events"
    __table_args__ = (
        Index(
            "ix_product_search_events_product_searched",
            "product_id",
            "searched_at",
        ),
        Index("ix_product_search_events_searched_at", "searched_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    product_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
    )
    query: Mapped[str | None] = mapped_column(String(200), nullable=True)
    searched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    product: Mapped[Product] = relationship(back_populates="search_events")
