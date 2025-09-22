from fastapi import APIRouter, Depends, HTTPException
from db.sessions import SessionDep
from instruments.forms import RegisterForm, LoginForm, TokenResponse
from instruments.login import get_user, create_access_token, verify_password
from instruments.login import get_current_user, create_refresh_token, verify_token

login_register = APIRouter()


@login_register.post("/user/register")
async def user_create(session: SessionDep, user: RegisterForm):
    user = await user.save(session)
    return user


@login_register.post("/token", response_model=TokenResponse)
async def login(session: SessionDep, form_data: LoginForm):
    user = await get_user(session, form_data.username)
    verify = await verify_password(form_data.password, user.password)
    if not user or not verify:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = await create_access_token(data={"sub": user.username})
    refresh_token = await create_refresh_token(data={"sub": user.username})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@login_register.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    payload = await verify_token(refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_data = {"sub": payload["sub"]}
    new_access_token = await create_access_token(user_data)
    new_refresh_token = await create_refresh_token(user_data)
    return {"access_token": new_access_token, "refresh_token": new_refresh_token}


@login_register.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user
