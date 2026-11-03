"""Idempotent creation of the initial administrator account.

Run from ``backend/`` with::

    python -m scripts.create_admin

Credentials come from the environment:

- ``ADMIN_EMAIL`` (required)
- ``ADMIN_PASSWORD`` (required)
- ``ADMIN_FULL_NAME`` (optional, defaults to ``Administrador``)

The script never modifies an existing account: if the email is already
registered it reports it and exits successfully.
"""

import os
import sys

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

import app.db.registry  # noqa: F401  (registers all models)
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.modules.accounts.models import User

DEFAULT_FULL_NAME = "Administrador"


def create_admin() -> int:
    """Create the initial administrator; return the process exit code."""
    email = (os.getenv("ADMIN_EMAIL") or "").strip().lower()
    password = os.getenv("ADMIN_PASSWORD") or ""
    full_name = (os.getenv("ADMIN_FULL_NAME") or "").strip() or DEFAULT_FULL_NAME

    if not email or not password:
        print(
            "Error: ADMIN_EMAIL y ADMIN_PASSWORD son obligatorios. "
            "No se creó ninguna cuenta.",
            file=sys.stderr,
        )
        return 1

    try:
        password_hash = hash_password(password)
    except ValueError as exc:
        print(f"Error: {exc} No se creó ninguna cuenta.", file=sys.stderr)
        return 1

    with SessionLocal() as session:
        existing = session.scalar(
            select(User).where(func.lower(User.email) == email)
        )
        if existing is not None:
            print(
                f"El administrador {email} ya existe (id={existing.id}); "
                "no se modificó nada."
            )
            return 0

        session.add(
            User(
                email=email,
                full_name=full_name,
                password_hash=password_hash,
                role="admin",
                store_id=None,
                is_active=True,
            )
        )
        try:
            session.commit()
        except IntegrityError:
            # A concurrent execution created the same email first.
            session.rollback()
            print(
                f"El administrador {email} ya existe; no se modificó nada."
            )
            return 0

        print(
            f"Administrador creado: {email} ({full_name}). "
            "La contraseña se almacenó como hash."
        )
    return 0


def main() -> None:
    sys.exit(create_admin())


if __name__ == "__main__":
    main()
