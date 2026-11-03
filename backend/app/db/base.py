"""Declarative base shared by all SQLAlchemy models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for declarative models.

    ``Base.metadata`` is the target metadata used by Alembic. The application
    never creates tables automatically at startup.
    """
