from fastapi import FastAPI

from app.routers.task import task_router
from app.routers.tasks import tasks_router

app = FastAPI()

app.include_router(router=task_router,prefix="/tasks")
app.include_router(router=tasks_router, prefix="/tasks")