"""Unit tests for authentication and security functions.

These tests verify password hashing, JWT token operations, and security properties
like timing attack resistance in the bcrypt verification flow.
"""

from __future__ import annotations

import timeit
from datetime import timedelta

import pytest
from jose import JWTError, jwt

from app.core.config import settings
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)


def test_password_hashing_roundtrip() -> None:
    """Test password hashing and verification work correctly.

    Verifies:
    - hash_password produces a bcrypt hash (starts with $2b$)
    - verify_password returns True for correct password
    - verify_password returns False for incorrect password
    - Hashed password is different from plain password
    """
    plain_password = "my-secure-password-123"

    hashed = hash_password(plain_password)

    assert hashed != plain_password, "Hash should not equal plain password"
    assert hashed.startswith("$2b$"), "Should be bcrypt hash format"
    assert verify_password(plain_password, hashed) is True, (
        "Correct password should verify"
    )
    assert verify_password("wrong-password", hashed) is False, (
        "Wrong password should not verify"
    )


def test_jwt_creation_and_validation() -> None:
    """Test JWT token creation and decoding.

    Verifies:
    - create_access_token produces a valid JWT string
    - Token can be decoded with correct secret
    - Decoded payload contains expected data
    - Token includes expiration time
    """
    payload_data = {
        "sub": "test-user",
        "role": "editor",
        "user_id": 42,
    }

    token = create_access_token(payload_data)

    assert isinstance(token, str), "Token should be a string"
    assert len(token) > 20, "Token should be substantial length"

    secret = settings.jwt_secret or "test-jwt-secret"
    decoded = jwt.decode(token, secret, algorithms=[settings.jwt_algorithm])

    assert decoded["sub"] == "test-user", "Username should match"
    assert decoded["role"] == "editor", "Role should match"
    assert decoded["user_id"] == 42, "User ID should match"
    assert "exp" in decoded, "Token should have expiration"


def test_expired_token_rejected() -> None:
    """Test that expired JWT tokens are properly rejected.

    Verifies:
    - Token with negative expiry delta is created
    - Decoding expired token raises JWTError
    - Error is related to expiration (not malformed token)
    """
    payload_data = {"sub": "test-user", "role": "viewer"}

    expired_token = create_access_token(
        payload_data,
        expires_delta=timedelta(seconds=-10),
    )

    secret = settings.jwt_secret or "test-jwt-secret"

    with pytest.raises(JWTError) as exc_info:
        jwt.decode(expired_token, secret, algorithms=[settings.jwt_algorithm])

    error_msg = str(exc_info.value).lower()
    assert "expired" in error_msg or "signature" in error_msg, (
        f"Expected expiration error, got: {error_msg}"
    )


def test_timing_attack_prevention() -> None:
    """Test verify_password has consistent timing (timing attack resistance).

    Verifies:
    - verify_password takes similar time for correct password
    - verify_password takes similar time for incorrect password
    - Mean execution times are within 20% of each other

    This prevents timing attacks where attackers measure response times
    to determine if a username exists or guess password characters.

    bcrypt's design ensures constant-time comparison, but we verify it here.
    """
    plain_password = "correct-password-123"
    hashed = hash_password(plain_password)
    wrong_password = "wrong-password-456"

    iterations = 100

    def time_correct_password() -> None:
        verify_password(plain_password, hashed)

    def time_wrong_password() -> None:
        verify_password(wrong_password, hashed)

    correct_time = timeit.timeit(time_correct_password, number=iterations)
    wrong_time = timeit.timeit(time_wrong_password, number=iterations)

    correct_mean = correct_time / iterations
    wrong_mean = wrong_time / iterations

    max_time = max(correct_mean, wrong_mean)
    min_time = min(correct_mean, wrong_mean)

    time_difference_ratio = (max_time - min_time) / max_time

    assert time_difference_ratio < 0.20, (
        f"Timing difference too large: {time_difference_ratio:.2%}. "
        f"Correct: {correct_mean * 1000:.2f}ms, Wrong: {wrong_mean * 1000:.2f}ms. "
        f"This suggests vulnerability to timing attacks."
    )
