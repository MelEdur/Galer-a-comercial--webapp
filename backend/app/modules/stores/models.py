"""Stores module: gallery stores, opening hours and external links."""

from __future__ import annotations

from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Identity,
    Index,
    SmallInteger,
    String,
    Text,
    Time,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.modules.accounts.models import User
    from app.modules.catalog.models import Product


class Store(TimestampMixin, Base):
    """A physical store in the gallery, identified by side and position."""

    __tablename__ = "stores"
    __table_args__ = (
        CheckConstraint(
            "(side IN ('left', 'right') AND position BETWEEN 1 AND 10) "
            "OR (side = 'back' AND position = 1)",
            name="ck_stores_side_position",
        ),
        UniqueConstraint("side", "position", name="uq_stores_side_position"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    number: Mapped[int] = mapped_column(SmallInteger, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    whatsapp: Mapped[str | None] = mapped_column(String(30), nullable=True)
    side: Mapped[str] = mapped_column(String(10), nullable=False)
    position: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )

    hours: Mapped[list[StoreHour]] = relationship(
        back_populates="store",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
        order_by="StoreHour.day_of_week, StoreHour.opens_at",
    )
    links: Mapped[list[StoreLink]] = relationship(
        back_populates="store",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
        order_by="StoreLink.position",
    )
    products: Mapped[list[Product]] = relationship(
        back_populates="store",
        passive_deletes=True,
    )
    merchant: Mapped[User | None] = relationship(
        back_populates="store",
        uselist=False,
    )


class StoreHour(Base):
    """An opening interval for a given weekday (0 = Monday)."""

    __tablename__ = "store_hours"
    __table_args__ = (
        CheckConstraint(
            "day_of_week BETWEEN 0 AND 6", name="ck_store_hours_day"
        ),
        CheckConstraint("closes_at > opens_at", name="ck_store_hours_range"),
        UniqueConstraint(
            "store_id",
            "day_of_week",
            "opens_at",
            name="uq_store_hours_store_day_open",
        ),
        Index("ix_store_hours_store_id", "store_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    store_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("stores.id", ondelete="CASCADE"),
        nullable=False,
    )
    day_of_week: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    opens_at: Mapped[time] = mapped_column(Time, nullable=False)
    closes_at: Mapped[time] = mapped_column(Time, nullable=False)

    store: Mapped[Store] = relationship(back_populates="hours")


class StoreLink(Base):
    """An ordered external link published by a store."""

    __tablename__ = "store_links"
    __table_args__ = (
        UniqueConstraint(
            "store_id", "url", name="uq_store_links_store_url"
        ),
        Index("ix_store_links_store_id", "store_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    store_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("stores.id", ondelete="CASCADE"),
        nullable=False,
    )
    label: Mapped[str] = mapped_column(String(60), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    position: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default=text("0")
    )

    store: Mapped[Store] = relationship(back_populates="links")
