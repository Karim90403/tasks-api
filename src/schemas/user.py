from datetime import datetime, timezone
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserInDB(BaseModel):
    id: str
    email: EmailStr
    hashed_password: str
    role: Optional[str] = Field(default="user")
    is_active: Optional[bool] =  Field(default=True)
    created_at: Optional[datetime] = Field(default=datetime.now(timezone.utc))
    managed_projects: List[str] = Field(default_factory=list)

class UserPublic(BaseModel):
    id: str
    email: EmailStr
    role: Optional[str]
    is_active: Optional[bool]
