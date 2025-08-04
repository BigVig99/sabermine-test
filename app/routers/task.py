from fastapi import Depends, HTTPException, Body, APIRouter
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.task import Task
from app.schemas.task import TaskRead, TaskUpdate

task_router = APIRouter(tags=["Task Details"])


@task_router.get(
    "/{task_id}/",
    response_model=TaskRead,
)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """
        Retrieve a task by its ID.

        Fetches the task corresponding to the given `task_id`. If no such task exists, raises 404.

        Returns:
        - TaskRead
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return task


@task_router.put(
    "/{task_id}/",
    response_model=TaskRead,
)
def update_task(
        task_id: int,
        task_update: TaskUpdate = Body(...),
        db: Session = Depends(get_db),
):
    """
        Update a task by its ID.

        Allows modification of an existing task identified by `task_id`. All fields in the
        payload are optional; only the provided fields will be updated. If the task does not exist a 404 will be raised

        Payload may include:
        - title (str)
        - description (str)
        - priority (int): 1-3 inclusive
        - due_date (datetime)
        - completed (bool)

        Returns:
        - TaskRead: The updated task object.
"""
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    for key, value in task_update.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task


@task_router.delete(
    "/{task_id}/",
)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """
        Delete a task by its ID.

        Deletes the task with the given `task_id` from the database. If the task
        does not exist, a 404 error is raised.

        Parameters:
        - task_id (int): The ID of the task to delete.

        Returns:
        - dict: A confirmation message indicating successful deletion.
"""
    task_to_delete = db.query(Task).filter(Task.id == task_id).first()
    if not task_to_delete:
        raise HTTPException(status_code=404, detail="Task not found.")
    db.delete(task_to_delete)
    db.commit()
    return {"message": "Task deleted successfully."}
