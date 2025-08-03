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
    description: Optional[str] = None
    priority: PriorityEnum
    due_date: datetime


class TaskUpdate(TaskCreate):
    completed: bool


class TaskRead(TaskCreate):
    id: int
    completed: bool

    model_config = ConfigDict(from_attributes=True)


class PaginatedTasks(BaseModel):
    total: int
    next_url: Optional[str] = None
    prev_url: Optional[str] = None
    tasks: List[TaskRead]

    model_config = ConfigDict(from_attributes=True)
