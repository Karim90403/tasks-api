from typing import Any

from pydantic import BaseModel


class ChangeProjectRequest(BaseModel):
    key: str
    value: Any
