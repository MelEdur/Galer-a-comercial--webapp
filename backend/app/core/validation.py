"""Shared validation helpers."""

import re
from typing import Annotated

from email_validator import (
    SPECIAL_USE_DOMAIN_NAMES,
    EmailNotValidError,
    validate_email,
)
from pydantic import BeforeValidator

_HOSTNAME_RE = re.compile(
    r"^(?=.{1,253}$)"
    r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)*"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$"
)


def _is_special_use_domain(domain: str) -> bool:
    """Return whether ``domain`` is a reserved/special-use name (e.g. .local)."""
    normalized = domain.lower().rstrip(".")
    return any(
        normalized == name or normalized.endswith(f".{name}")
        for name in SPECIAL_USE_DOMAIN_NAMES
    )


def _validate_email(value: object) -> str:
    """Validate and normalize an email address.

    Deliverability is not checked (the app runs offline). ``email-validator``
    rejects special-use domains such as ``galeria.local``, so those are
    accepted after validating the local part and the domain syntax.
    """
    if not isinstance(value, str):
        raise ValueError("El correo debe ser una cadena de texto.")

    email = value.strip()
    try:
        validated = validate_email(
            email,
            check_deliverability=False,
            test_environment=True,
        )
        return validated.normalized.lower()
    except EmailNotValidError as exc:
        error = exc

    local_part, separator, domain = email.rpartition("@")
    if not separator or not local_part or not _is_special_use_domain(domain):
        raise ValueError(str(error)) from error
    if not _HOSTNAME_RE.match(domain):
        raise ValueError(str(error)) from error
    try:
        validate_email(
            f"{local_part}@example.com",
            check_deliverability=False,
        )
    except EmailNotValidError:
        raise ValueError(str(error)) from error
    return email.lower()


#: Email address type used by API schemas; normalizes to lowercase.
EmailAddress = Annotated[str, BeforeValidator(_validate_email)]
