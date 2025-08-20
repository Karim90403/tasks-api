from abc import ABC, abstractmethod

from schemas.user import UserInDB


class ABCUserRepository(ABC):
    @abstractmethod
    async def create_user(self, user: UserInDB) -> None:
        ...

    @abstractmethod
    async def get_user_by_email(self, email: str) -> UserInDB | None:
       ...

    @abstractmethod
    async def get_user_by_id(self, id: str) -> UserInDB | None:
        ...