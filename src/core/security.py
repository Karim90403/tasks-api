from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

import jwt
from passlib.context import CryptContext

from core.environment_config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def _create_token(data: dict, expires_delta: timedelta, token_type: str) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.jwt.access_token_expire_minutes))
    to_encode.update({"exp": expire, "iat": now, "type": token_type})
    return jwt.encode(to_encode, settings.jwt.secret_key, algorithm=settings.jwt.algorithm)

def create_access_token(sub: str) -> str:
    return _create_token(
        {"sub": sub},
        timedelta(minutes=settings.jwt.access_token_expire_minutes),
        token_type="access"
    )

def create_refresh_token(sub: str) -> str:
    return _create_token(
        {"sub": sub},
        timedelta(days=settings.jwt.refresh_token_expire_days),
        token_type="refresh"
    )

def decode_jwt_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt.secret_key, algorithms=[settings.jwt.algorithm])

def is_token_expiring_soon(payload: dict, threshold_seconds: int) -> bool:
    """Проверка, что до exp осталось меньше threshold_seconds."""
    exp = payload.get("exp")
    if not exp:
        return True
    now = datetime.now(timezone.utc).timestamp()
    return (exp - now) <= threshold_seconds

def try_decode_access(token: str) -> Tuple[dict, Optional[Exception]]:
    try:
        payload = decode_jwt_token(token)
        if payload.get("type") != "access":
            raise jwt.exceptions.InvalidTokenError("Invalid token type")
        else:
            return payload, None
    except jwt.exceptions.InvalidTokenError:
        raise
    except Exception as e:
        return {}, e

def try_decode_refresh(token: str) -> Tuple[dict, Optional[Exception]]:
    try:
        payload = decode_jwt_token(token)
        if payload.get("type") != "refresh":
            raise jwt.exceptions.InvalidTokenError("Invalid token type")
        else:
            return payload, None
    except jwt.exceptions.InvalidTokenError:
        raise
    except Exception as e:
        return {}, e
