from fastapi import Depends, HTTPException, Body, APIRouter
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Task
from app.schemas import TaskRead, TaskUpdate

task_router = APIRouter(prefix="/tasks", tags=["Task Details"])


@task_router.get(
    "/tasks/{task_id}/",
    response_model=TaskRead,
    tags=["Get individual task"],
)
def get_task(
        task_id: int,
        db: Session = Depends(get_db)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return task


@task_router.put(
    "/tasks/{task_id}/",
    response_model=TaskRead,
    tags=["Update individual task"],
)
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


@task_router.delete(
    "/tasks/{task_id}/",
    tags=["Delete individual task"],
)
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
