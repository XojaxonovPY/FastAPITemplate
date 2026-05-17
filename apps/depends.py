from typing import TypeAlias, Annotated

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from db.sessions import get_session
from services.login import get_current_user

SessionDep: TypeAlias = Annotated[AsyncSession, Depends(get_session)]
UserSession: TypeAlias = Annotated[User, Depends(get_current_user)]
