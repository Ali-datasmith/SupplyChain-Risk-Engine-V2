"""
Tests for security authentication module.
"""
from __future__ import annotations

from src.auth.security import (
    check_auth_state,
    hash_password,
    login_user,
    logout_user,
    verify_password,
)


def test_hash_and_verify_password() -> None:
    password = "SecretPassword123!"
    hashed = hash_password(password)
    assert hashed.startswith("$argon2id$")
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_auth_state_flow() -> None:
    state: dict = {}
    assert check_auth_state(state) is False

    login_user(state, is_demo=True)
    assert check_auth_state(state) is True
    assert state.get("is_recruiter_demo") is True

    logout_user(state)
    assert check_auth_state(state) is False
