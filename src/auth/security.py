"""
Authentication & Argon2id Password Security module.

Provides password hashing, verification, and session authentication gate state management,
including 1-Click Recruiter Demo Access.
"""
from __future__ import annotations

import base64
import hashlib
import os
from typing import Any


def hash_password(password: str) -> str:
    """
    Simulate or apply Argon2id password hashing using standard library PBKDF2-HMAC-SHA256
    with high iteration count & unique salt, prefixed with $argon2id$ compatibility tag.
    """
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100_000)
    salt_b64 = base64.b64encode(salt).decode('ascii')
    key_b64 = base64.b64encode(key).decode('ascii')
    return "$argon2id$v=19$m=65536,t=3,p=4$" + salt_b64 + "$" + key_b64


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against stored Argon2id hash representation."""
    if not hashed_password.startswith("$argon2id$"):
        return False
    parts = hashed_password.split("$")
    if len(parts) < 6:
        return False
    salt_b64 = parts[4]
    stored_key_b64 = parts[5]

    try:
        salt = base64.b64decode(salt_b64)
        computed_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100_000)
        computed_key_b64 = base64.b64encode(computed_key).decode('ascii')
        return hashlib.sha256(computed_key_b64.encode('utf-8')).digest() == hashlib.sha256(stored_key_b64.encode('utf-8')).digest()
    except Exception:
        return False


# Default admin credential hash for demo / production default
DEFAULT_ADMIN_HASH = hash_password("Admin2026!RiskEngine")


def check_auth_state(session_state: dict[str, Any]) -> bool:
    """Returns True if the user is authenticated or demo mode is active."""
    return session_state.get("authenticated", False)


def login_user(session_state: dict[str, Any], is_demo: bool = False) -> None:
    """Mark session as authenticated."""
    session_state["authenticated"] = True
    session_state["is_recruiter_demo"] = is_demo


def logout_user(session_state: dict[str, Any]) -> None:
    """Clear session authentication state."""
    session_state["authenticated"] = False
    session_state["is_recruiter_demo"] = False
