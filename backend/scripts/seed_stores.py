"""Idempotent seed for the 21 fixed stores of the gallery.

Run from ``backend/`` with::

    python -m scripts.seed_stores

Stores are keyed by their natural key ``number``, so running the script more
than once never duplicates data.
"""

from sqlalchemy import select

import app.db.registry  # noqa: F401  (registers all models / relationship targets)
from app.core.database import SessionLocal
from app.modules.stores.models import Store


def _planned_stores() -> list[dict[str, object]]:
    """Return the 21 stores with interleaved numbering.

    Right side positions 1..10 -> odd numbers 1..19.
    Left side positions 1..10 -> even numbers 2..20.
    Back position 1 -> number 21.
    """
    stores: list[dict[str, object]] = []
    for position in range(1, 11):
        stores.append(
            {
                "number": 2 * position - 1,
                "name": f"Local {2 * position - 1}",
                "side": "right",
                "position": position,
            }
        )
    for position in range(1, 11):
        stores.append(
            {
                "number": 2 * position,
                "name": f"Local {2 * position}",
                "side": "left",
                "position": position,
            }
        )
    stores.append({"number": 21, "name": "Local 21", "side": "back", "position": 1})
    return stores


def seed_stores() -> tuple[int, int]:
    """Insert missing stores and return ``(created, existing)`` counts."""
    created = 0
    existing = 0

    with SessionLocal() as session:
        for data in _planned_stores():
            store_id = session.execute(
                select(Store.id).where(Store.number == data["number"])
            ).scalar_one_or_none()
            if store_id is not None:
                existing += 1
                continue
            session.add(Store(is_active=True, **data))
            created += 1
        session.commit()

    return created, existing


def main() -> None:
    created, existing = seed_stores()
    print(
        f"Locales creados: {created}. Locales ya existentes: {existing}. "
        f"Total esperado: {created + existing}."
    )


if __name__ == "__main__":
    main()
