from http.client import HTTPException

from fastapi import APIRouter, Depends

from db.sessions import SessionDep
from instruments.forms import RegisterForm, LoginForm
from instruments.login import get_user, verify_password, create_access_token, get_current_user

login_register = APIRouter()


@login_register.post("/user/register")
async def user_create(session: SessionDep, user: RegisterForm):
    user = await user.save(session)
    return user


@login_register.post("/token")
async def login(session: SessionDep, form_data: LoginForm = Depends()):
    user = await get_user(session, form_data.username)
    verify = await verify_password(form_data.password, user.password)
    if not user or not verify:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = await create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@login_register.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user
