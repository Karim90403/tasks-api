from typing import Optional

from fastapi import Depends, Header, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer

from core.environment_config import settings
from core.security import create_access_token, is_token_expiring_soon, try_decode_access, try_decode_refresh
from repository.abc.user_repository import ABCUserRepository
from repository.elasticsearch_implementation.user_repository import get_user_elastic_repository
from schemas.user import UserInDB

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/loginform")

async def get_current_user(
        response: Response,
        token: str = Depends(oauth2_scheme),
        refresh_token: Optional[str] = Header(default=None, alias="X-Refresh-Token"),
        repo: ABCUserRepository = Depends(get_user_elastic_repository)
) -> UserInDB:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized. Empty token")
    payload, err = try_decode_access(token)
    if not err:
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        # Превентивно обновим access, если вот-вот истечёт
        if is_token_expiring_soon(payload, settings.jwt.access_token_proactive_refresh_seconds):
            new_access = create_access_token(user_id)
            response.headers["X-New-Access-Token"] = new_access

        user = await repo.get_user_by_id(user_id=user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
        return user

    # 2) Если access невалиден/истёк — пробуем refresh (если передан)
    if not refresh_token:
        # оригинальную ошибку маскируем одной 401
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized. Empty refresh token")

    r_payload, r_err = try_decode_refresh(refresh_token)
    if r_err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Unauthorized, {r_err}")

    user_id: str = r_payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized, user_id not found")

    user = await repo.get_user_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    # Выпускаем новый access и возвращаем его в заголовке; запрос продолжается
    new_access = create_access_token(user_id)
    response.headers["X-New-Access-Token"] = new_access
    return user
