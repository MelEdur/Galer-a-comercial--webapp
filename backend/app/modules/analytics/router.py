"""HTTP endpoints for the authenticated merchant's product statistics."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.accounts.models import User
from app.modules.analytics import service
from app.modules.analytics.schemas import ProductStatsResponse
from app.modules.auth.dependencies import require_merchant

router = APIRouter(
    prefix="/merchant/stats",
    tags=["merchant"],
    dependencies=[Depends(require_merchant)],
)


@router.get(
    "/products",
    response_model=ProductStatsResponse,
    summary="Get the most searched products of the authenticated merchant",
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Invalid period arguments."
        }
    },
)
def get_product_stats(
    days: int | None = Query(
        default=None,
        description="Período en días: 7, 30 o 90.",
    ),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    current_user: User = Depends(require_merchant),
    db: Session = Depends(get_db),
) -> ProductStatsResponse:
    """Return the Top 10 products of the merchant's store for a period.

    The store is always derived from the authenticated account, never from a
    client-supplied identifier.
    """
    try:
        period = service.resolve_period(
            days=days,
            from_date=from_date,
            to_date=to_date,
        )
    except service.InvalidPeriodError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from None

    return service.get_product_stats(db, current_user.store_id, period)
