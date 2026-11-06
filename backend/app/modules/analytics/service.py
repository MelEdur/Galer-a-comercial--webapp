"""Business logic for merchant product search statistics (CU #10).

The statistics are derived from the events recorded by the public product
search (CU #1). The store always comes from the authenticated merchant, and
the period boundaries are interpreted in the Buenos Aires local day and then
converted to UTC to filter ``searched_at``.
"""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.analytics.models import ProductSearchEvent
from app.modules.analytics.schemas import ProductStatItem, ProductStatsResponse
from app.modules.catalog.models import Product

#: Buenos Aires uses UTC-3 all year round; a fixed offset avoids tzdata.
BUENOS_AIRES = timezone(timedelta(hours=-3))

DEFAULT_DAYS = 30
RANKING_LIMIT = 10
ALLOWED_PRESETS = (7, 30, 90)


class InvalidPeriodError(Exception):
    """The requested period arguments are missing or contradictory."""


@dataclass(frozen=True)
class Period:
    """A local date range and its equivalent UTC instant boundaries."""

    from_date: date
    to_date: date
    start_utc: datetime
    end_utc: datetime


def _start_of_local_day(value: date) -> datetime:
    """Return 00:00 local time of ``value`` as an aware UTC instant."""
    local = datetime.combine(value, time.min, tzinfo=BUENOS_AIRES)
    return local.astimezone(timezone.utc)


def resolve_period(
    *,
    days: int | None,
    from_date: date | None,
    to_date: date | None,
    today: date | None = None,
) -> Period:
    """Validate the period arguments and build the query boundaries.

    Rules:
        - no arguments -> the last 30 days;
        - ``days`` combined with any date -> error;
        - only one of the dates -> error;
        - ``from_date`` later than ``to_date`` -> error.

    Raises:
        InvalidPeriodError: when the arguments cannot define a valid period.
    """
    if days is not None and days not in ALLOWED_PRESETS:
        raise InvalidPeriodError(
            "El período en días debe ser 7, 30 o 90."
        )

    if days is not None and (from_date is not None or to_date is not None):
        raise InvalidPeriodError(
            "No se puede combinar el período en días con fechas."
        )

    if (from_date is None) != (to_date is None):
        raise InvalidPeriodError(
            "Debe indicar la fecha desde y la fecha hasta."
        )

    local_today = today if today is not None else datetime.now(BUENOS_AIRES).date()

    if days is None and from_date is None:
        days = DEFAULT_DAYS

    if days is not None:
        start_date = local_today - timedelta(days=days - 1)
        end_date = local_today
    else:
        assert from_date is not None and to_date is not None
        if from_date > to_date:
            raise InvalidPeriodError(
                "La fecha desde no puede ser posterior a la fecha hasta."
            )
        start_date = from_date
        end_date = to_date

    return Period(
        from_date=start_date,
        to_date=end_date,
        start_utc=_start_of_local_day(start_date),
        end_utc=_start_of_local_day(end_date + timedelta(days=1)),
    )


def _to_buenos_aires(value: datetime) -> datetime:
    """Express a stored instant in the fixed Buenos Aires offset."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(BUENOS_AIRES)


def get_product_stats(
    session: Session, store_id: int, period: Period
) -> ProductStatsResponse:
    """Return the top products searched in ``store_id`` during ``period``.

    Deleted products are included and marked. Products without events in the
    period are excluded. Querying never creates search events.
    """
    conditions = [
        Product.store_id == store_id,
        ProductSearchEvent.searched_at >= period.start_utc,
        ProductSearchEvent.searched_at < period.end_utc,
    ]

    search_count = func.count(ProductSearchEvent.id)
    last_searched_at = func.max(ProductSearchEvent.searched_at)

    rows = session.execute(
        select(
            Product.id,
            Product.name,
            Product.deleted_at,
            search_count.label("search_count"),
            last_searched_at.label("last_searched_at"),
        )
        .join(Product, Product.id == ProductSearchEvent.product_id)
        .where(*conditions)
        .group_by(Product.id, Product.name, Product.deleted_at)
        .order_by(
            search_count.desc(),
            func.lower(Product.name).asc(),
            Product.id.asc(),
        )
        .limit(RANKING_LIMIT)
    ).all()

    total_searches = (
        session.scalar(
            select(func.count(ProductSearchEvent.id))
            .join(Product, Product.id == ProductSearchEvent.product_id)
            .where(*conditions)
        )
        or 0
    )

    items = [
        ProductStatItem(
            product_id=product_id,
            name=name,
            search_count=count,
            is_deleted=deleted_at is not None,
            last_searched_at=_to_buenos_aires(last),
        )
        for product_id, name, deleted_at, count, last in rows
    ]

    return ProductStatsResponse(
        from_date=period.from_date,
        to_date=period.to_date,
        total_searches=total_searches,
        items=items,
    )
