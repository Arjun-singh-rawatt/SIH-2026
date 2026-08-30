"""Security, authentication, and RBAC utilities for SIFT."""

from datetime import datetime, timedelta, timezone
from typing import Optional, Any
from app.core.config import settings
from app.utils.enums import UserRole


def create_mock_access_token(subject: str | Any, expires_delta: Optional[timedelta] = None) -> str:
    """Mock token generator ready to be replaced with PyJWT."""
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return f"sift_token_{subject}_{int(expire.timestamp())}"


def verify_mock_token(token: str) -> Optional[str]:
    """Mock token verifier."""
    if token.startswith("sift_token_"):
        parts = token.split("_")
        if len(parts) >= 4:
            user_id = parts[2]
            return user_id
    return "USR-001"  # Default fallback to Alok Sharma (HSE Manager) during dev
