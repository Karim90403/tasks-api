from abc import ABC, abstractmethod
from typing import Any, Dict, List


class ABCManagerRepository(ABC):
    @abstractmethod
    async def get_projects(self) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    async def get_tasks(self, project_id: str) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    async def get_shift_history(self, project_id: str) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    async def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        ...

    @abstractmethod
    async def change_project(self, project_id: str, key: str, value: Any) -> Dict[str, Any]:
        ...
