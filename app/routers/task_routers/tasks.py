from typing import Optional
from urllib.parse import urlencode

from fastapi import Depends, Query, Request, APIRouter
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Task
from app.schemas import TaskRead, TaskCreate, PriorityEnum, PaginatedTasks
from app.utils.constants import TASKS_PAGE_SIZE

tasks_router = APIRouter(prefix="/tasks", tags=["Tasks"])


@tasks_router.post(
    path='/',
    response_model=TaskRead,
    tags=["Create a task"]
)
def create_task(task_payload: TaskCreate, db: Session = Depends(get_db)):
    task = Task(**task_payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task



#Returns data in the form {total, next_url, prev_url, items}
#for easy page management client side
@tasks_router.get(
    path='/',
    response_model=PaginatedTasks,
    tags=["Get all tasks"]
)
def get_tasks(
        request: Request,
        db: Session = Depends(get_db),
        completed: Optional[bool] = Query(None, description="Filter by completed"),
        priority: Optional[PriorityEnum] = Query(None, description="Filter by priority"),
        page: int = Query(1, ge=1, description="Page number"),
):
    def build_paginated_url(page_number: int):
        query_params = {
            "page": page_number,
        }
        if completed is not None:
            query_params["completed"] = completed
        if priority is not None:
            query_params["priority"] = priority.value
        return f"{request.url.path}?{urlencode(query_params)}"

    query = db.query(Task)
    if completed is not None:
        query = query.filter(Task.completed == completed)

    if priority is not None:
        query = query.filter(Task.priority == priority.value)

    count = query.count()

    offset = (page - 1) * TASKS_PAGE_SIZE
    limit = TASKS_PAGE_SIZE

    num_full_pages = count // TASKS_PAGE_SIZE
    partial_page = False if num_full_pages * TASKS_PAGE_SIZE == count else True

    tasks = query.offset(offset).limit(limit).all()
    next_url = None if page == num_full_pages and not partial_page else build_paginated_url(page + 1)
    prev_url = None if page == 1 else build_paginated_url(page - 1)

    return PaginatedTasks(
        total=count,
        next_url=next_url,
        prev_url=prev_url,
        items=tasks
    )
