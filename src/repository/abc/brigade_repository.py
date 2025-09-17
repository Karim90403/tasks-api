from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class ABCBrigadeRepository(ABC):
    @abstractmethod
    async def create_brigade(self, brigade_data: Dict[str, Any]) -> Dict[str, Any]:
        ...

    async def get_brigade(self, brigade_id: str) -> Optional[Dict[str, Any]]:
        ...

    async def search_brigades(self, name: Optional[str], member: Optional[str], size: int = 20) -> List[Dict[str, Any]]:
        ...
