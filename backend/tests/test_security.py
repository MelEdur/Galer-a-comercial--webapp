"""Unit tests for password hashing and JWT helpers (no database needed)."""

from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.core.config import settings
from app.core.security import (
    BCRYPT_MAX_PASSWORD_BYTES,
    InvalidTokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_returns_bcrypt_hash_with_salt() -> None:
    first = hash_password("secret1234")
    second = hash_password("secret1234")

    assert first != "secret1234"
    assert first.startswith("$2")
    assert first != second  # different random salt
    assert len(first) <= 255


def test_verify_password_accepts_correct_password() -> None:
    password_hash = hash_password("secret1234")

    assert verify_password("secret1234", password_hash) is True


@pytest.mark.parametrize("candidate", ["secret1235", "", "SECRET1234"])
def test_verify_password_rejects_wrong_password(candidate: str) -> None:
    password_hash = hash_password("secret1234")

    assert verify_password(candidate, password_hash) is False


def test_verify_password_handles_malformed_hash() -> None:
    assert verify_password("secret1234", "not-a-bcrypt-hash") is False


def test_hash_password_rejects_more_than_72_bytes() -> None:
    with pytest.raises(ValueError):
        hash_password("a" * (BCRYPT_MAX_PASSWORD_BYTES + 1))


def test_hash_password_rejects_multibyte_password_over_limit() -> None:
    # 40 two-byte characters = 80 bytes but only 40 characters.
    with pytest.raises(ValueError):
        hash_password("ñ" * 40)


def test_hash_password_rejects_empty_password() -> None:
    with pytest.raises(ValueError):
        hash_password("")


def test_verify_password_rejects_password_over_limit() -> None:
    password_hash = hash_password("secret1234")

    assert verify_password("a" * (BCRYPT_MAX_PASSWORD_BYTES + 1), password_hash) is False


def test_create_and_decode_access_token_round_trip() -> None:
    token = create_access_token("42", "admin")

    payload = decode_access_token(token)

    assert payload["sub"] == "42"
    assert payload["role"] == "admin"
    assert "iat" in payload
    assert "exp" in payload


def test_decode_access_token_rejects_garbage() -> None:
    with pytest.raises(InvalidTokenError):
        decode_access_token("not-a-token")


def test_decode_access_token_rejects_token_signed_with_other_secret() -> None:
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "sub": "1",
            "role": "admin",
            "iat": now,
            "exp": now + timedelta(minutes=5),
        },
        "another-secret",
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(InvalidTokenError):
        decode_access_token(token)


def test_decode_access_token_rejects_expired_token() -> None:
    past = datetime.now(timezone.utc) - timedelta(hours=1)
    token = jwt.encode(
        {
            "sub": "1",
            "role": "admin",
            "iat": past - timedelta(minutes=5),
            "exp": past,
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(InvalidTokenError):
        decode_access_token(token)
