"""Idempotent seed for the initial global catalog categories.

Run from ``backend/`` with::

    python -m scripts.seed_categories

Categories are keyed by their case-insensitive name, so running the script more
than once never duplicates data.
"""

from sqlalchemy import func, select

import app.db.registry  # noqa: F401  (registers all models / relationship targets)
from app.core.database import SessionLocal
from app.modules.catalog.models import Category

CATEGORY_NAMES = (
    "Indumentaria",
    "Calzado",
    "Accesorios",
    "Belleza",
    "Tecnología",
    "Hogar",
    "Deportes",
    "Juguetería",
    "Librería",
    "Gastronomía",
)


def seed_categories() -> tuple[int, int]:
    """Insert missing categories and return ``(created, existing)`` counts."""
    created = 0
    existing = 0

    with SessionLocal() as session:
        known_names = set(
            session.scalars(select(func.lower(Category.name))).all()
        )
        for name in CATEGORY_NAMES:
            key = name.lower()
            if key in known_names:
                existing += 1
                continue
            session.add(Category(name=name))
            known_names.add(key)
            created += 1
        session.commit()

    return created, existing


def main() -> None:
    created, existing = seed_categories()
    print(
        f"Categorías creadas: {created}. Categorías ya existentes: {existing}. "
        f"Total esperado: {created + existing}."
    )


if __name__ == "__main__":
    main()
