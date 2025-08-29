from abc import ABC, abstractmethod
from typing import Optional, Any

from schemas.user import UserInDB


class ABCUserRepository(ABC):
    @abstractmethod
    async def create_user(self, user: UserInDB) -> None:
        ...

    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
       ...

    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        ...

    @abstractmethod
    async def get_all_users(self) -> list[dict[str, Any]]:
        ...