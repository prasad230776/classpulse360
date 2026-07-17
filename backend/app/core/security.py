import jwt
from datetime import datetime, timezone, timedelta
from typing import Any, Optional, Dict
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing context configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies that a plain text password matches its cryptographically hashed version.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Computes the secure bcrypt hash of a plain text password.
    """
    return pwd_context.hash(password)


def create_access_token(subject: Any, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a cryptographically signed JWT access token.

    :param subject: User identifier or payload subject.
    :param expires_delta: Optional expiration override.
    :return: Signed JWT token string.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: Any, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a cryptographically signed JWT refresh token.

    :param subject: User identifier or payload subject.
    :param expires_delta: Optional expiration override.
    :return: Signed JWT token string.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates a signed JWT token.
    Raises jwt.PyJWTError (e.g. ExpiredSignatureError) if signature/payload check fails.

    :param token: Signed JWT token.
    :return: Dictionary representation of token payload.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
