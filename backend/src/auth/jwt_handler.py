"""JWT token creation and validation."""

import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from src.config import Config


def create_access_token(user_id: int, email: str, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    config = Config()
    if expires_delta is None:
        expires_delta = timedelta(days=config.TOKEN_EXPIRE_DAYS)

    expire = datetime.utcnow() + expires_delta
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow()
    }

    encoded_jwt = jwt.encode(payload, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify JWT token and return payload."""
    config = Config()
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
