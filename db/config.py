from datetime import datetime
from typing import Optional
from sqlalchemy import update, text, func
from sqlalchemy.ext.declarative import declared_attr
from sqlmodel import SQLModel, Field, select

from db.sessions import SessionDep


class AbstractClass:
    @classmethod
    async def create(cls, session: SessionDep, **kwargs):
        obj = cls(**kwargs)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    @classmethod
    async def update(cls, session: SessionDep, id_: int, form):
        values = form.dict(exclude_unset=True)
        stmt = update(cls).filter(cls.id == id_).values(**values)
        await session.execute(stmt)
        await session.commit()
        return await session.get(cls, id_)

    @classmethod
    async def delete(cls, session: SessionDep, id_: int):
        obj = await session.get(cls, id_)
        await session.delete(obj)
        await session.commit()
        return True

    @classmethod
    async def get_all(cls, session: SessionDep,sorted_by:list[str]=None):
        stmt =select(cls)
        if sorted_by:
            stmt = stmt.order_by(*sorted_by)
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def gets(cls, session: SessionDep, filter_column, value):
        stmt = select(cls).where(filter_column == value)
        result = await session.execute(stmt)
        return result.scalars().all()

    @classmethod
    async def get(cls, session: SessionDep, id_: int):
        return await session.get(cls, id_)

    @classmethod
    async def query(cls, session: SessionDep, stmt,one=False):
        query = await session.execute(stmt)
        if one:
            return query.scalars().first()
        return query.scalars().all()


class CreatedModel(SQLModel, AbstractClass, table=False):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + "s"

    id: Optional[int] = Field(primary_key=True)
    created_at: Optional[datetime] = Field(
        sa_column_kwargs={
            "server_default": text("TIMEZONE('Asia/Tashkent', NOW())"),
            "nullable": False,
        },
    )
    updated_at: Optional[datetime] = Field(
        sa_column_kwargs={
            "server_default": text("TIMEZONE('Asia/Tashkent', NOW())"),
            "onupdate": func.now(),
            "nullable": False,
        },
    )


