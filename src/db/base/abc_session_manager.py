from abc import ABC, abstractmethod


class BaseSessionManager(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass

    @abstractmethod
    def session(self):
        pass
