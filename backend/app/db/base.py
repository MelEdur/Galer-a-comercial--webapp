"""Declarative base shared by all SQLAlchemy models."""

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Explicit, stable constraint and index names so Alembic migrations and tests
# can reference them. Constraints that already carry an explicit name keep it.
NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Base class for declarative models.

    ``Base.metadata`` is the target metadata used by Alembic. The application
    never creates tables automatically at startup. Models are registered by
    importing :mod:`app.db.registry`; this module must not import models to
    avoid circular imports.
    """

    metadata = MetaData(naming_convention=NAMING_CONVENTION)
