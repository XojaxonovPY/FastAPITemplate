from fastapi import FastAPI

from main.login_register import login_register
from main.tasks import tasks

app = FastAPI(title="User API")

app.include_router(tasks, prefix="/tasks", tags=["tasks"])
app.include_router(login_register, prefix="/login", tags=["login"])
