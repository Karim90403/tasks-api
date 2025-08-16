from abc import ABC, abstractmethod
from typing import Any, Dict, List


class ABCManagerRepository(ABC):
    @abstractmethod
    async def get_projects(self) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    async def get_tasks(self) -> List[Dict[str, Any]]:
        ...
