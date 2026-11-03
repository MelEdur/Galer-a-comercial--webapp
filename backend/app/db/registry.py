"""Model registry.

Importing this module registers every ORM model on ``Base.metadata`` so that
Alembic (and tests) see the complete schema. ``app.db.base`` intentionally does
not import models to avoid circular imports.
"""

from app.db.base import Base
from app.modules.accounts.models import User
from app.modules.analytics.models import ProductSearchEvent
from app.modules.catalog.models import (
    Category,
    Product,
    ProductCategory,
    ProductImage,
)
from app.modules.stores.models import Store, StoreHour, StoreLink

#: The complete metadata object consumed by Alembic.
metadata = Base.metadata

__all__ = [
    "metadata",
    "Base",
    "User",
    "Store",
    "StoreHour",
    "StoreLink",
    "Category",
    "Product",
    "ProductCategory",
    "ProductImage",
    "ProductSearchEvent",
]
