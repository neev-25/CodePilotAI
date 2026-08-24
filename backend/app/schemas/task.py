from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None

class TaskResponse(BaseModel):
    id: int
    repository_id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True
