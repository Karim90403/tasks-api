from typing import Any

from pydantic import BaseModel


class ChangeProjectRequest(BaseModel):
    key: str
    value: Any

class UploadResult(BaseModel):
    filename: str
    size: int
    url: str
    content_type: str
    stage_id: str
    work_type_id: str
    work_kind_id: str
    task_id: str
    subtask_id: str
