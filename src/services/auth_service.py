import uuid
from datetime import timedelta

from fastapi import Depends

from core.environment_config import settings
from core.security import hash_password, verify_password, create_jwt_token
from repository.abc.user_repository import ABCUserRepository
from repository.elasticsearch_implementation.user_repository import get_user_elastic_repository
from schemas.auth import Token
from schemas.user import UserCreate, UserPublic, UserInDB


class AuthService:
    def __init__(self, user_repo: ABCUserRepository):
        self.user_repo = user_repo

    async def register_user(self, user_data: UserCreate) -> UserPublic:
        existing = await self.user_repo.get_user_by_email(user_data.email)
        if existing:
            raise ValueError("User already exists")

        user = UserInDB(
            id=str(uuid.uuid4()),
            email=user_data.email,
            hashed_password=hash_password(user_data.password)
        )
        await self.user_repo.create_user(user)
        return UserPublic(id=user.id, email=user.email)

    async def authenticate_user(self, email: str, password: str) -> Token:
        user = await self.user_repo.get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("Invalid credentials")

        access_token = create_jwt_token({"sub": user.id}, timedelta(minutes=settings.jwt.access_token_expire_minutes))
        refresh_token = create_jwt_token({"sub": user.id}, timedelta(days=settings.jwt.refresh_token_expire_days))

        return Token(access_token=access_token, refresh_token=refresh_token)

def get_auth_service(
    repo: ABCUserRepository = Depends(get_user_elastic_repository),
) -> AuthService:
    return AuthService(repo)