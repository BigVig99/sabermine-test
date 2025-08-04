from typing import Optional
from urllib.parse import urlencode

from fastapi import Depends, Query, Request, APIRouter
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.task import Task
from app.schemas.task import TaskRead, TaskCreate, PriorityEnum, PaginatedTasks
from app.utils.constants import TASKS_PAGE_SIZE

tasks_router = APIRouter(tags=["Tasks"])


@tasks_router.post(
    path="/",
    response_model=TaskRead,
)
def create_task(task_payload: TaskCreate, db: Session = Depends(get_db)):
    task = Task(**task_payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task




@tasks_router.get(
    path="/",
    response_model=PaginatedTasks,
)
def get_tasks(
    request: Request,
    db: Session = Depends(get_db),
    completed: Optional[bool] = Query(None),
    priority: Optional[PriorityEnum] = Query(None),
    search_string: Optional[str] = Query(
        None
    ),
    page: int = Query(1, ge=1, description="Page number"),
):
    """
       Returns tasks (paginated) with respect to filtering and searching (can be done simultaneously).

       Parameters:
       - completed: Filter by task completion status.
       - priority: Filter by task priority level (1, 2, or 3).
       - search_string: String to search in title/description (substring match).
       - page: Page number (1-indexed).

       Returns:
       - A PaginatedTasks object of form {total, next_url, prev_url, items}.
       """

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

    if search_string is not None:
        query = query.filter(
            or_(
                Task.title.ilike(f"%{search_string}%"),
                Task.description.ilike(f"%{search_string}%"),
            )
        )

    count = query.count()

    next_url = None
    prev_url = None
    tasks = []

    if count != 0:
        offset = (page - 1) * TASKS_PAGE_SIZE
        limit = TASKS_PAGE_SIZE

        num_full_pages, partial_page_size = divmod(count, TASKS_PAGE_SIZE)

        tasks = query.offset(offset).limit(limit).all()
        next_url = (
            None
            if page == num_full_pages and partial_page_size == 0 or page == num_full_pages + 1
            else build_paginated_url(page + 1)
        )
        prev_url = None if page == 1 else build_paginated_url(page - 1)

    return PaginatedTasks(
        total=count, next_url=next_url, prev_url=prev_url, items=tasks
    )
