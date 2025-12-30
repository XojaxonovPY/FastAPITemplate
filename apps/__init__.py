from fastapi import APIRouter

from apps.login_register import router as auth
from apps.tasks import router as tasks

main_router = APIRouter()

main_router.include_router(tasks, prefix="/tasks", tags=["Tasks"])
main_router.include_router(auth, prefix="/auth", tags=["Auth"])
