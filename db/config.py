from typing import TypeVar, Type

from pydantic import BaseModel
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declared_attr
from sqlmodel import SQLModel, Field, select

T = TypeVar("T", bound="Model")


class Manager:

    @classmethod
    async def create(cls: Type[T], session: AsyncSession, data: BaseModel | dict):
        values: dict = data.model_dump(exclude_unset=True)
        obj = cls(**values)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    @classmethod
    async def get(cls: Type[T], session: AsyncSession, **filters):
        stmt = select(cls).filter_by(**filters)
        result = await session.execute(stmt)
        return result.scalars().first()

    @classmethod
    async def filter(cls: Type[T], session: AsyncSession, **filters):
        stmt = select(cls).filter_by(**filters)
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def all(cls: Type[T], session: AsyncSession):
        stmt = select(cls)
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def update(cls, session: AsyncSession, id_: int, data: BaseModel | dict):
        values = data.model_dump(exclude_unset=True)
        stmt = update(cls).where(cls.id == id_).values(**values)
        await session.execute(stmt)
        await session.commit()
        return await session.get(cls, id_)

    @classmethod
    async def delete(cls, session: AsyncSession, id_: int) -> bool:
        obj = await session.get(cls, id_)
        if not obj:
            return False
        await session.delete(obj)
        await session.commit()
        return True

    @classmethod
    async def query(cls, session: AsyncSession, stmt, all_: bool = False):
        result = await session.execute(stmt)
        scalars = result.scalars()
        if all_:
            return scalars.all()
        return scalars.first()


# ---------------- BaseModel ---------------- #

class Model(SQLModel, Manager):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + "s"

    id: int = Field(primary_key=True)
