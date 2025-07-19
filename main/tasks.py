from fastapi import APIRouter, Depends
from sqlalchemy import select, func

from db.models import Category, Task, StatusType
from db.sessions import SessionDep
from instruments.forms import CategoryForm, TaskForm, TaskUpdateForm
from instruments.login import get_current_user

tasks = APIRouter()


@tasks.post('/save/category')
async def save_category(form: CategoryForm, session: SessionDep,current_user:dict=Depends(get_current_user)):
    category = await Category.create(session, **dict(form))
    return category


@tasks.get('/get/category', response_model=list[Category])
async def get_category(session: SessionDep):
    categories = await Category.get_all(session)
    return categories


@tasks.post('/save/tasks')
async def save_tasks(form: TaskForm, session: SessionDep):
    tasks = await Task.create(session, **dict(form))
    return tasks


@tasks.get('/get/tasks/')
async def get_tasks(status: str, category_id: int, priority: str, limit: int, sort_by: str, session: SessionDep):
    tasks = await Task.query(session, select(Task).
                             filter(Task.status == status, Task.category_id == category_id, Task.priority == priority).
                             limit(limit).order_by(sort_by))
    return tasks


@tasks.patch('/update/tasks/{id}', response_model=Task)
async def update_tasks(id: int, form: TaskUpdateForm, session: SessionDep):
    tasks = await Task.update(session, id, form)
    return tasks


@tasks.delete('/delete/tasks/{id}')
async def delete_tasks(id: int, session: SessionDep):
    tasks = await Task.delete(session, id)
    return {"success": 205, "message": "Vazifa muvaffaqiyatli o'chirildi"}


@tasks.get('/get/statistic/')
async def get_statistic(session: SessionDep):
    total_task = await Task.query(session, select(func.count()).select_from())
    task_completed = await Task.query(session,
                                      select(func.count()).select_from(Task).where(Task.status == StatusType.COMPLETED))
    task_new = await Task.query(session, select(func.count()).select_from(Task).where(Task.status == StatusType.NEW))
    task_in_progress = await Task.query(session, select(func.count()).select_from(Task).where(
        Task.status == StatusType.IN_PROGRESS))
    statistic = {
        "total_task": total_task or 0,
        "task_completed": task_completed or 0,
        "task_new": task_new or 0,
        "task_in_progress": task_in_progress or 0
    }
    return statistic
