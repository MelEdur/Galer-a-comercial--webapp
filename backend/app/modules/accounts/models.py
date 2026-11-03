"""Accounts module: user accounts for administrators and merchants."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    ForeignKey,
    Identity,
    Index,
    String,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.modules.stores.models import Store


class User(TimestampMixin, Base):
    """An administrator or a merchant assigned to a single store."""

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('admin', 'merchant')", name="ck_users_role"),
        CheckConstraint(
            "(role = 'merchant' AND store_id IS NOT NULL) "
            "OR (role = 'admin' AND store_id IS NULL)",
            name="ck_users_store_assignment",
        ),
        Index("uq_users_email_lower", text("lower(email)"), unique=True),
        Index(
            "uq_users_store_merchant",
            "store_id",
            unique=True,
            postgresql_where=text("role = 'merchant'"),
        ),
        Index("ix_users_store_id", "store_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, Identity(), primary_key=True)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    store_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("stores.id", ondelete="RESTRICT"),
        nullable=True,
    )

    store: Mapped[Store | None] = relationship(back_populates="merchant")
