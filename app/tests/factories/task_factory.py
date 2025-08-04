from datetime import datetime, timedelta
from app.models.task import Task
from sqlalchemy.orm import Session


def create_task(
        db: Session,
        title="Test",
        description="test task",
        priority=1,
        due_date=datetime.now() + timedelta(days=7),
        completed=False
):
    task = Task(title=title, description=description, priority=priority, due_date=due_date, completed=completed)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
