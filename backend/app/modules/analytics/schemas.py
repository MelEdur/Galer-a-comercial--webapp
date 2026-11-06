"""Response schemas for merchant product search statistics (CU #10)."""

from datetime import date, datetime

from pydantic import BaseModel


class ProductStatItem(BaseModel):
    """One product of the merchant's ranking."""

    product_id: int
    name: str
    search_count: int
    is_deleted: bool
    last_searched_at: datetime


class ProductStatsResponse(BaseModel):
    """Top products searched in the merchant's store for a period."""

    from_date: date
    to_date: date
    total_searches: int
    items: list[ProductStatItem]
