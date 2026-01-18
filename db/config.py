from datetime import datetime
from typing import Type, TypeVar, Any

from fastapi import HTTPException, status
from sqlalchemy import Select, Update, Result, Delete, TextClause
from sqlalchemy import select, update, text, DateTime, delete
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr

T = TypeVar("T", bound="Model")


class Base(DeclarativeBase):
    pass


class Manager:
    @classmethod
    async def create(cls: Type[T], session: AsyncSession, **values):
        obj = cls(**values)
        try:
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj
        except (IntegrityError, DataError, SQLAlchemyError) as e:
            await session.rollback()
            cls._handle_db_error(e)

    @classmethod
    async def all_(cls, session: AsyncSession, order_by: list[Any] | None = None):
        try:
            stmt: Select[Any] = select(cls)
            if order_by is not None:
                stmt = stmt.order_by(*order_by)
            result: Result[Any] = await session.execute(stmt)
            return result.scalars().all()
        except SQLAlchemyError as e:
            cls._handle_db_error(e)

    @classmethod
    async def filter(cls: Type[T], session: AsyncSession, *filters, order_by: list[Any] | None = None):
        try:
            stmt: Select[Any] = select(cls).filter(*filters)
            if order_by is not None:
                stmt = stmt.order_by(*order_by)
            result: Result[Any] = await session.execute(stmt)
            return result.scalars().all()
        except SQLAlchemyError as e:
            cls._handle_db_error(e)

    @classmethod
    async def get(cls: Type[T], session: AsyncSession, **filters):
        try:
            stmt: Select[Any] = select(cls).filter_by(**filters)
            result: Result[Any] = await session.execute(stmt)
            return result.scalars().first()
        except SQLAlchemyError as e:
            cls._handle_db_error(e)

    @classmethod
    async def update(cls: Type[T], session: AsyncSession, filter_: dict[Any, Any], **values):
        try:
            stmt: Update = update(cls).filter_by(**filter_).values(**values).returning(cls)
            result: Result[Any] = await session.execute(stmt)
            obj: Any | None = result.scalar_one_or_none()
            await session.commit()
            return obj
        except (IntegrityError, DataError, SQLAlchemyError) as e:
            await session.rollback()
            cls._handle_db_error(e)

    @classmethod
    async def delete(cls: Type[T], session: AsyncSession, filter_: dict[Any, Any]):
        try:
            stmt: Delete = delete(cls).filter_by(**filter_)
            await session.execute(stmt)
            await session.commit()
            return True
        except SQLAlchemyError as e:
            await session.rollback()
            cls._handle_db_error(e)

    @classmethod
    async def query(cls: Type[T], session: AsyncSession, stmt: Select[Any], all_: bool = False):
        try:
            result: Result[Any] = await session.execute(stmt)
            if all_:
                return result.scalars().all()
            return result.scalars().first()
        except SQLAlchemyError as e:
            cls._handle_db_error(e)

    @staticmethod
    async def core_get(session: AsyncSession, query: str, **params):
        try:
            stmt: TextClause = text(query)
            result: Result[Any] = await session.execute(stmt, params)
            return result.mappings().all()
        except SQLAlchemyError as e:
            Manager._handle_db_error(e)

    @staticmethod
    async def core_commit(session: AsyncSession, query: str, **params):
        try:
            stmt: TextClause = text(query)
            await session.execute(stmt, params)
            await session.commit()
        except (IntegrityError, DataError, SQLAlchemyError) as e:
            await session.rollback()
            Manager._handle_db_error(e)

    @staticmethod
    def _handle_db_error(e: Exception):
        if isinstance(e, IntegrityError):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Ma'lumot nusxalangan: {str(e.orig)}")
        if isinstance(e, DataError):
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Noto'g'ri ma'lumot: {str(e.orig)}"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Baza xatosi: {str(e)}"
        )


class Model(Base, Manager):
    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + "s"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
