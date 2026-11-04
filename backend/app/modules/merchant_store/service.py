"""Business rules for the authenticated merchant's own store settings.

The store is always derived from the authenticated account (``store_id``); no
operation accepts a store identifier from the client. The service raises
domain exceptions that the router translates into HTTP responses.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.merchant_store.schemas import (
    StoreHourRead,
    StoreLinkRead,
    StoreRead,
    StoreUpdate,
)
from app.modules.stores.models import Store, StoreHour, StoreLink


class StoreNotFoundError(Exception):
    """The store assigned to the merchant does not exist."""


def _to_read(store: Store) -> StoreRead:
    """Build the API representation without leaking internal columns."""
    hours = [
        StoreHourRead(
            day_of_week=hour.day_of_week,
            opens_at=hour.opens_at,
            closes_at=hour.closes_at,
        )
        for hour in store.hours
    ]
    hours.sort(key=lambda hour: (hour.day_of_week, hour.opens_at))

    links = [
        StoreLinkRead(label=link.label, url=link.url, position=link.position)
        for link in store.links
    ]
    links.sort(key=lambda link: link.position)

    return StoreRead(
        id=store.id,
        number=store.number,
        side=store.side,
        position=store.position,
        name=store.name,
        description=store.description,
        logo_url=store.logo_url,
        email=store.email,
        phone=store.phone,
        whatsapp=store.whatsapp,
        hours=hours,
        links=links,
    )


def _get_store(session: Session, store_id: int) -> Store:
    """Return the store with its hours and links or raise a domain error."""
    store = session.scalar(
        select(Store)
        .where(Store.id == store_id)
        .options(selectinload(Store.hours), selectinload(Store.links))
    )
    if store is None:
        raise StoreNotFoundError("El local no existe.")
    return store


def get_store(session: Session, store_id: int) -> StoreRead:
    """Return the store assigned to the merchant."""
    return _to_read(_get_store(session, store_id))


def update_store(
    session: Session, store_id: int, payload: StoreUpdate
) -> StoreRead:
    """Replace the store's editable data, hours and links atomically."""
    store = _get_store(session, store_id)

    store.name = payload.name
    store.description = payload.description
    store.logo_url = str(payload.logo_url) if payload.logo_url else None
    store.email = payload.email
    store.phone = payload.phone
    store.whatsapp = payload.whatsapp

    # Flush between collections so deleting one does not collide with the
    # insertion of a new row sharing a unique (store_id, day/URL) key.
    store.hours.clear()
    session.flush()
    store.hours.extend(
        StoreHour(
            day_of_week=hour.day_of_week,
            opens_at=hour.opens_at,
            closes_at=hour.closes_at,
        )
        for hour in payload.hours
    )

    store.links.clear()
    session.flush()
    store.links.extend(
        StoreLink(
            label=link.label,
            url=str(link.url),
            position=position,
        )
        for position, link in enumerate(payload.links)
    )

    session.commit()
    return _to_read(store)
