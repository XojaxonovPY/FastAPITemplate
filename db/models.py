from sqlalchemy import String, CHAR
from sqlalchemy.orm import mapped_column, Mapped

from db.config import Model, Base
from db.sessions import AsyncSessionLocal


class Admin(Model):
    username: Mapped[str] = mapped_column(CHAR(length=55))
    password: Mapped[str] = mapped_column(String(length=105))

    @staticmethod
    async def check_admin(**kwargs):
        async with AsyncSessionLocal() as session:
            obj = await Admin.get(session, **kwargs)
            return obj

    @staticmethod
    async def create_admin(**kwargs):
        async with AsyncSessionLocal() as session:
            obj = await Admin.create(session, **kwargs)
            return obj


class User(Model):
    first_name: Mapped[str] = mapped_column(String(length=50), nullable=True)
    username: Mapped[str] = mapped_column(String(length=50), unique=True)
    password: Mapped[str] = mapped_column(String(length=200))


metadata = Base.metadata
