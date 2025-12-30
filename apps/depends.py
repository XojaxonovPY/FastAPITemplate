from typing import TypeAlias, Annotated

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.sessions import get_session

SessionDep: TypeAlias = Annotated[AsyncSession, Depends(get_session)]
