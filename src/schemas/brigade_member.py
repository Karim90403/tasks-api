from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class BrigadeMember(BaseModel):
    user_id: str = Field(..., description="Идентификатор пользователя (может быть email или user id)")
    email: Optional[str] = Field(None, description="Email участника (опционально)")