from fastapi import APIRouter, Depends, HTTPException, status

from db.models import User
from db.sessions import SessionDep
from instruments.forms import RegisterForm, LoginForm, TokenResponse
from instruments.login import get_current_user, create_refresh_token, verify_token, get_password_hash
from instruments.login import get_user, create_access_token, verify_password

login_register = APIRouter()


@login_register.post("/user/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def user_create(session: SessionDep, user: RegisterForm):
    user.password = await get_password_hash(user.password)
    user = await User.create(session, user)
    return user


@login_register.post("/login", response_model=TokenResponse)
async def login(session: SessionDep, form_data: LoginForm):
    user = await get_user(session, username=form_data.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    verify = await verify_password(form_data.password, user.password)
    if not user or not verify:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")
    access_token = await create_access_token(data={"sub": user.username})
    refresh_token = await create_refresh_token(data={"sub": user.username})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@login_register.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token_: str):
    payload = await verify_token(refresh_token_)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_data = {"sub": payload["sub"]}
    new_access_token = await create_access_token(user_data)
    new_refresh_token = await create_refresh_token(user_data)
    return {"access_token": new_access_token, "refresh_token": new_refresh_token}


@login_register.get("/users/me", response_model=User, status_code=status.HTTP_200_OK)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user
