from abc import ABC, abstractmethod
from typing import Any, Dict, List


class ABCForemanRepository(ABC):
    @abstractmethod
    async def get_projects(self, foreman_id: str) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    async def get_tasks(self, foreman_id: str) -> List[Dict[str, Any]]:
        ...
