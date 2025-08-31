from typing import Optional

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    project_id: str
    project_name: str
    foreman_id: Optional[str] = None
    work_stages: Optional[list] = []
