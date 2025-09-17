from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field

from schemas.brigade_member import BrigadeMember


class BrigadeInDB(BaseModel):
    brigade_id: str = Field(..., description="ID бригады (детерминированный SHA1 по составу или произвольный)")
    brigade_name: Optional[str] = Field(None, description="Имя бригады")
    members: List[BrigadeMember] = Field(..., description="Список участников")
    created_at: Optional[str] = Field(None, description="Дата создания (ISO)")
    created_by: Optional[str] = Field(None, description="Кто создал")