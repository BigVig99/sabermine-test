from typing import Optional, List
from urllib.parse import urlencode

from fastapi import FastAPI, Depends, Query, Request, HTTPException, Body
from sqlalchemy.orm import Session

from app.models import Task
from app.database import SessionLocal
from app.schemas import TaskRead, TaskCreate, PriorityEnum, PaginatedTasks, TaskUpdate
from app.utils.constants import TASKS_PAGE_SIZE

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post(
    "/tasks/",
    response_model=TaskRead
)
def create_task(task_payload: TaskCreate, db: Session = Depends(get_db)):
    task = Task(**task_payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@app.get(
    path="/tasks/",
    response_model=PaginatedTasks
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
        tasks=tasks
    )


@app.get("/tasks/{task_id}/", response_model=TaskRead)
def get_task(
        task_id: int,
        db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return task


@app.put("/tasks/{task_id}/", response_model=TaskRead)
def update_task(
        task_id: int,
        task_update: TaskUpdate = Body(...),
        db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    for key, value in task_update.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task

@app.delete("/tasks/{task_id}/")
def delete_task(
        task_id: int,
        db: Session = Depends(get_db)
):
    task_to_delete = db.query(Task).filter(Task.id == task_id).first()
    if not task_to_delete:
        raise HTTPException(status_code=404, detail="Task not found.")
    db.delete(task_to_delete)
    db.commit()
    return {"message": "Task deleted successfully."}
