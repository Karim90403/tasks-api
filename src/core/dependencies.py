from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from repositories.user_repository import UserRepository
from core.security import decode_jwt_token
from models.user import UserInDB
import jwt

from repository.abc.user_repository import ABCUserRepository
from repository.elasticsearch_implementation.user_repository import get_user_elastic_repository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), repo: ABCUserRepository = Depends(get_user_elastic_repository)) -> UserInDB:
    try:
        payload = decode_jwt_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except jwt.exceptions.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    return await repo.get_user_by_id(id=user_id)
