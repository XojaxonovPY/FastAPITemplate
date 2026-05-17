import logging
from datetime import datetime
from typing import Type, TypeVar, Any

from sqlalchemy import DateTime
from sqlalchemy import select, update, delete, insert, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr

T = TypeVar("T", bound="Model")


class Base(DeclarativeBase):
    pass


class DatabaseException(Exception):
    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.message = message
        self.original_error = original_error


class Manager:
    @classmethod
    async def create(cls: Type[T], session: AsyncSession, **values) -> T:
        try:
            async with session.begin():
                stmt = insert(cls).values(**values).returning(cls)
                result = await session.execute(stmt)
                return result.scalar_one()
        except SQLAlchemyError as e:
            cls._handle_db_error(e)

    @classmethod
    async def update(cls: Type[T], session: AsyncSession, filter_: dict[str, Any], **values) -> T | None:
        try:
            async with session.begin():
                stmt = update(cls).filter_by(**filter_).values(**values).returning(cls)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            cls._handle_db_error(e)

    @classmethod
    async def delete(cls: Type[T], session: AsyncSession, filter_: dict[str, Any]) -> bool:
        try:
            async with session.begin():
                stmt = delete(cls).filter_by(**filter_)
                await session.execute(stmt)
                return True
        except SQLAlchemyError as e:
            cls._handle_db_error(e)

    @classmethod
    async def get_all(cls, session: AsyncSession, order_by: list[Any]):
        try:
            stmt = select(cls)
            if order_by is not None:
                stmt = stmt.order_by(*order_by)
            result = await session.execute(stmt)
            return result.scalars().all()
        except SQLAlchemyError as e:
            cls._handle_db_error(e)

    @classmethod
    async def get(cls: Type[T], session: AsyncSession, **filters) -> T | None:
        try:
            stmt = select(cls).filter_by(**filters)
            result = await session.execute(stmt)
            return result.scalars().first()
        except SQLAlchemyError as e:
            cls._handle_db_error(e)

    @classmethod
    async def get_filter(cls: Type[T], session: AsyncSession, *filters, order_by: list[Any] | None = None):
        try:
            stmt = select(cls).filter(*filters)
            if order_by is not None:
                stmt = stmt.order_by(*order_by)
            result = await session.execute(stmt)
            return result.scalars().all()
        except SQLAlchemyError as e:
            cls._handle_db_error(e)

    @staticmethod
    async def core_get(session: AsyncSession, query: str, **params):
        try:
            stmt = text(query)
            result = await session.execute(stmt, params)
            return result.mappings().all()
        except SQLAlchemyError as e:
            Manager._handle_db_error(e)

    @staticmethod
    async def core_commit(session: AsyncSession, query: str, **params):
        try:
            async with session.begin():
                stmt = text(query)
                await session.execute(stmt, params)
        except SQLAlchemyError as e:
            Manager._handle_db_error(e)

    @staticmethod
    def _handle_db_error(e: Exception):
        logging.error(f"Database Error: {e}", exc_info=True)
        if isinstance(e, IntegrityError):
            raise DatabaseException(f"Ma'lumot nusxalangan yoki bog'liqlik xatosi: {str(e.orig)}", e)
        if isinstance(e, DataError):
            raise DatabaseException(f"Ma'lumot formatida xato: {str(e.orig)}", e)
        raise DatabaseException(f"Kutilmagan baza xatosi: {str(e)}", e)


class Model(Base, Manager):
    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + "s"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
