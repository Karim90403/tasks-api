from abc import ABC, abstractmethod
from typing import Any, Dict, List


class ABCForemanRepository(ABC):
    @abstractmethod
    async def get_projects(self, foreman_id: str) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    async def get_tasks(self, foreman_id: str) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    async def start_shift(self, foreman_id: str, task_ids: List[str], subtask_ids: List[str]) -> None:
        ...

    @abstractmethod
    async def stop_shift(self, foreman_id: str, task_ids: List[str], subtask_ids: List[str]) -> None:
        ...

    @abstractmethod
    async def get_shift_history(self, foreman_id: str) -> List[Dict[str, Any]]:
        ...

    @abstractmethod
    async def get_shift_status(self, foreman_id: str) -> str:
        ...
