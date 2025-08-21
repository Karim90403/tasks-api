import uuid
from typing import Optional

from fastapi import Depends

from core.security import create_access_token, create_refresh_token, hash_password, verify_password
from repository.abc.user_repository import ABCUserRepository
from repository.elasticsearch_implementation.user_repository import get_user_elastic_repository
from schemas.auth import Token
from schemas.user import UserCreate, UserInDB, UserPublic


class AuthService:
    def __init__(self, user_repo: ABCUserRepository):
        self.user_repo = user_repo

    async def create_user(self, user: UserInDB) -> None:
        await self.user_repo.create_user(user)

    async def register_user(self, user_data: UserCreate) -> UserPublic:
        existing = await self.user_repo.get_user_by_email(user_data.email)
        if existing:
            raise ValueError("User already exists")

        user = UserInDB(
            id=str(uuid.uuid4()),
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
        )
        await self.user_repo.create_user(user)
        return UserPublic(id=user.id, email=user.email, role=user.role, is_active=user.is_active)

    async def authenticate_user(self, email: str, password: str) -> Token:
        user = await self.user_repo.get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("Invalid credentials")

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        return Token(access_token=access_token, refresh_token=refresh_token)

    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        return await self.user_repo.get_user_by_id(user_id)

    @staticmethod
    async def refresh_tokens(user_id: str) -> Token:
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)
        return Token(access_token=access_token, refresh_token=refresh_token)

def get_auth_service(
    repo: ABCUserRepository = Depends(get_user_elastic_repository),
) -> AuthService:
    return AuthService(repo)
