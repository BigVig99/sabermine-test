from datetime import datetime
from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class PriorityEnum(int, Enum):
    HIGH = 1
    MEDIUM = 2
    LOW = 3


class TaskCreate(BaseModel):
    title: str
    description: str
    priority: PriorityEnum
    due_date: datetime


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    due_date: Optional[datetime] = None
    completed: Optional[bool] = None


class TaskRead(TaskCreate):
    id: int
    completed: bool
    title: str
    description: str
    priority: PriorityEnum
    due_date: datetime
    model_config = ConfigDict(from_attributes=True)


class PaginatedTasks(BaseModel):
    total: int
    next_url: Optional[str] = None
    prev_url: Optional[str] = None
    items: List[TaskRead]

    model_config = ConfigDict(from_attributes=True)

