from datetime import datetime
from typing import Type, TypeVar, Any

from sqlalchemy import DateTime, Select
from sqlalchemy import select, update, delete, insert, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr

from db.exceptions import DatabaseException, logger

T = TypeVar("T", bound="Model")


class Base(DeclarativeBase):
    pass


class Manager:
    @classmethod
    async def create(cls: Type[T], session: AsyncSession, **values) -> T:
        try:
            stmt = insert(cls).values(**values).returning(cls)
            result = await session.execute(stmt)
            await session.flush()
            return result.scalar_one()
        except SQLAlchemyError as e:
            await session.rollback()
            cls._handle_db_error(e)

    @classmethod
    async def update(cls: Type[T], session: AsyncSession, filter_: dict[str, Any], **values) -> T | None:
        try:
            stmt = update(cls).filter_by(**filter_).values(**values).returning(cls)
            result = await session.execute(stmt)
            await session.flush()
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            await session.rollback()
            cls._handle_db_error(e)

    @classmethod
    async def delete(cls: Type[T], session: AsyncSession, filter_: dict[str, Any]) -> bool:
        try:
            stmt = delete(cls).filter_by(**filter_)
            await session.execute(stmt)
            await session.flush()
            return True
        except SQLAlchemyError as e:
            await session.rollback()
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

    @classmethod
    async def get_query(cls: Type[T], session: AsyncSession, stmt: Select[Any]):
        try:
            result = await session.execute(stmt)
            return result
        except SQLAlchemyError as e:
            cls._handle_db_error(e)

    @staticmethod
    async def core_get(session: AsyncSession, query: str, **params):
        try:
            stmt = text(query)
            result = await session.execute(stmt, params)
            return result
        except SQLAlchemyError as e:
            Manager._handle_db_error(e)

    @staticmethod
    async def core_commit(session: AsyncSession, query: str, **params):
        try:
            stmt = text(query)
            await session.execute(stmt, params)
            await session.flush()
        except SQLAlchemyError as e:
            await session.rollback()
            Manager._handle_db_error(e)

    @staticmethod
    def _handle_db_error(e: Exception):
        if isinstance(e, IntegrityError):
            sqlstate = getattr(e.orig, "sqlstate", None)

            if sqlstate == "23505":
                raise DatabaseException(
                    message="Bu foydalanuvchi nomi (username) allaqachon band. Iltimos, boshqa nom kiriting.",
                    code=409,
                    original_error=e
                )

            elif sqlstate == "23503":
                raise DatabaseException(
                    message="Bog'langan ma'lumot topilmadi yoki xato ID yuborildi.",
                    code=409,
                    original_error=e
                )

            raise DatabaseException(
                message="Ma'lumotlar yaxlitligi buzildi (Tizim xatosi).",
                code=409,
                original_error=e
            )

        if isinstance(e, DataError):
            logger.warning(f"Database Data Warning: {e}")
            raise DatabaseException(f"Ma'lumot formatida xato: {str(e.orig)}", 400, e)

        if isinstance(e, OperationalError):
            logger.error(f"Database Operational Error: {e}", exc_info=True)
            raise DatabaseException(
                "Ma'lumotlar bazasi bilan aloqa uzildi. Birozdan so'ng urunib ko'ring.", 500, e
            )

        logger.error(f"Unexpected Database Error: {e}", exc_info=True)
        raise DatabaseException(f"Kutilmagan baza xatosi: {str(e)}", 500, e)


class Model(Base, Manager):
    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + "s"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
