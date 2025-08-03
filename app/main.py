from fastapi import FastAPI

from app.routers.task_routers.task import task_router
from app.routers.task_routers.tasks import tasks_router

app = FastAPI()

app.include_router(router=task_router)
app.include_router(router=tasks_router)