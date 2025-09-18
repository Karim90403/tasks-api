from abc import ABC, abstractmethod
from typing import Any, Optional

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

    @abstractmethod
    async def add_project_to_user(self, user_id: str, project_id: str) -> None:
        ...

    @abstractmethod
    async def remove_project_from_user(self, user_id: str, project_id: str) -> None:
        ...

    @abstractmethod
    async def update_user(self, user: UserInDB) -> None:
        ...
