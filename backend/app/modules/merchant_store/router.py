"""HTTP endpoints for the authenticated merchant's own store settings."""

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.accounts.models import User
from app.modules.auth.dependencies import require_merchant
from app.modules.merchant_store import service
from app.modules.merchant_store.schemas import StoreRead, StoreUpdate

router = APIRouter(
    prefix="/merchant",
    tags=["merchant"],
    dependencies=[Depends(require_merchant)],
)


def _not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="El local no existe.",
    )


@router.get(
    "/store",
    response_model=StoreRead,
    summary="Get the authenticated merchant's store",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Store not found."}},
)
def get_store(
    current_user: User = Depends(require_merchant),
    db: Session = Depends(get_db),
) -> StoreRead:
    """Return the store derived from the merchant's session."""
    try:
        return service.get_store(db, current_user.store_id)
    except service.StoreNotFoundError:
        raise _not_found() from None


@router.put(
    "/store",
    response_model=StoreRead,
    summary="Update the authenticated merchant's store",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Store not found."}},
)
def put_store(
    payload: StoreUpdate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_merchant),
    db: Session = Depends(get_db),
) -> StoreRead:
    """Replace the editable store data and refresh its assistant document."""
    try:
        store = service.update_store(db, current_user.store_id, payload)
    except service.StoreNotFoundError:
        raise _not_found() from None

    # Imported here to keep the assistant module out of the store module's
    # import graph. The task is best-effort: failures never undo the save.
    from app.modules.assistant.indexing import reindex_store_safely

    background_tasks.add_task(reindex_store_safely, current_user.store_id)
    return store
