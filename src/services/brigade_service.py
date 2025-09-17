from datetime import datetime, timezone
from functools import lru_cache
import hashlib
from typing import Any, Dict, List, Optional, Tuple

from fastapi import Depends

from repository.abc.brigade_repository import ABCBrigadeRepository
from repository.elasticsearch_implementation.brigade_repository import get_brigade_repository  # путь подставь свой


class BrigadeService:
    def __init__(self, repo: ABCBrigadeRepository):
        self.repo = repo

    @staticmethod
    def make_brigade_id(members: List[str]) -> str:
        """
        Детерминированный id бригады по составу участников.
        Сортируем участников, склеиваем через '|' и берём sha1.
        """
        members_sorted = [str(m) for m in members]
        members_sorted.sort()
        joined = "|".join(members_sorted)
        return hashlib.sha1(joined.encode("utf-8")).hexdigest()

    @staticmethod
    def make_brigade_snapshot(brigade_name: str, members: List[str]) -> Dict[str, Any]:
        return {
            "brigade_name": brigade_name,
            "members": [{"user_id": m, "email": None} for m in members]
        }

    async def create_brigade(self, brigade_id: str, brigade_name: str, members: List[str], created_by: Optional[str] = None) -> Dict[str, Any]:
        """
        Создать бригаду с указанным id (если нужен детерминированный id — используй make_brigade_id()).
        Возвращает ответ ES (index response).
        """
        doc = {
            "brigade_id": brigade_id,
            "brigade_name": brigade_name,
            "members": [{"user_id": m, "email": None} for m in members],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": created_by,
        }
        return await self.repo.create_brigade(doc)

    async def get_brigade(self, brigade_id: str) -> Optional[Dict[str, Any]]:
        return await self.repo.get_brigade(brigade_id)

    async def search_brigades(self, name: Optional[str], member: Optional[str], size: int = 20) -> List[Dict[str, Any]]:
        return await self.repo.search_brigades(name, member, size=size)

    async def create_or_get_brigade_by_members(
        self,
        members: List[str],
        brigade_name: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        По списку участников возвращает (brigade_id, brigade_doc).
        Если бригада с таким составом уже есть — возвращает её,
        иначе создаёт новую и возвращает созданный документ.
        """
        if not members:
            raise ValueError("members list must not be empty")

        # детерминированный id
        brigade_id = self.make_brigade_id(members)

        # пробуем получить
        existing = await self.get_brigade(brigade_id)
        if existing:
            return brigade_id, existing

        # создаём
        default_name = brigade_name or f"Бригада {brigade_id[:6]}"
        created_resp = await self.create_brigade(
            brigade_id=brigade_id,
            brigade_name=default_name,
            members=members,
            created_by=created_by,
        )

        # После index ES возвращает метаданные; получим документ через get_brigade чтобы вернуть полноценный объект
        created_doc = await self.get_brigade(brigade_id)
        return brigade_id, created_doc or {
            "brigade_id": brigade_id,
            "brigade_name": default_name,
            "members": [{"user_id": m, "email": None} for m in members],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": created_by,
        }

    async def ensure_brigade_on_subtask_payload(
        self,
        payload: Dict[str, Any],
        members_field: str = "assignees",
        brigade_field: str = "brigade_id",
        snapshot_field: str = "brigade_snapshot",
        created_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Удобный метод для сервисов, которые получают payload подзадачи с 'assignees':
        - если в payload есть members_field (например 'assignees') и он непустой,
          создаёт/получает бригаду и:
            * добавляет brigade_field = brigade_id
            * добавляет brigade_snapshot (опционально)
            * удаляет members_field
        - возвращает изменённый payload
        """
        members = payload.get(members_field) or []
        if not members:
            # ничего не делаем
            return payload

        members = [str(m) for m in members]
        brigade_id, brigade_doc = await self.create_or_get_brigade_by_members(members, created_by=created_by)

        # вставляем в payload
        payload[brigade_field] = brigade_id
        payload[snapshot_field] = {
            "brigade_name": brigade_doc.get("brigade_name"),
            "members": brigade_doc.get("members", [])
        }
        # удаляем старое поле
        if members_field in payload:
            payload.pop(members_field, None)

        return payload

@lru_cache
def get_brigade_service(
    repo: ABCBrigadeRepository = Depends(get_brigade_repository),
) -> BrigadeService:
    return BrigadeService(repo)
