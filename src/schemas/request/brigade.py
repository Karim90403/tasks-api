from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class BrigadeCreate(BaseModel):
    members: List[str] = Field(..., description="Список участников (user_id или email). Порядок не важен.")
    brigade_name: Optional[str] = Field(None, description="Читаемое имя бригады, если нужно")
    created_by: Optional[str] = Field(None, description="Кто создал бригаду (user id)")