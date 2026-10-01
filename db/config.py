import re
from datetime import datetime
from functools import lru_cache
from typing import Type, TypeVar, Any, Sequence, Union

from pydantic import BaseModel
from sqlalchemy import DateTime, Select
from sqlalchemy import select, update, delete, insert, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr, InstrumentedAttribute, load_only

from core.settings import get_current_uzb_time
from db.exceptions import DatabaseException, logger

T = TypeVar("T", bound="Model")

FIELDS = Union[type[BaseModel], Sequence[str], Sequence[InstrumentedAttribute]] | None

RELATIONS = Sequence[Any] | None


class Base(DeclarativeBase):
    pass


class Manager:
    @classmethod
    @lru_cache(maxsize=128)
    def _get_cached_schema_attributes(
            cls, schema_cls: type[BaseModel]
    ) -> tuple[InstrumentedAttribute, ...]:
        resolved = []
        for field in schema_cls.model_fields.keys():
            if hasattr(cls, field):
                attr = getattr(cls, field)
                if isinstance(attr, InstrumentedAttribute):
                    resolved.append(attr)
        return tuple(resolved)

    @classmethod
    def _parse_fields(cls, fields: FIELDS) -> Sequence[InstrumentedAttribute]:
        if not fields:
            return ()

        # 1. Pydantic schema berilsa keshdan olinadi
        if isinstance(fields, type) and issubclass(fields, BaseModel):
            return cls._get_cached_schema_attributes(fields)

        resolved = []
        for field in fields:
            if isinstance(field, str):
                if hasattr(cls, field):
                    attr = getattr(cls, field)
                    if isinstance(attr, InstrumentedAttribute):
                        resolved.append(attr)
            elif isinstance(field, InstrumentedAttribute):
                resolved.append(field)
        return tuple(resolved)

    @classmethod
    def _build_select(
            cls: Type[T],
            *filters: Any,
            fields: FIELDS = None,
            relations: RELATIONS = None,
            order_by: Sequence[Any] | None = None,
    ) -> Select[tuple[T]]:
        stmt = select(cls)

        if filters:
            stmt = stmt.where(*filters)

        selected_attrs = cls._parse_fields(fields)
        if selected_attrs:
            stmt = stmt.options(load_only(*selected_attrs))

        if relations:
            stmt = stmt.options(*relations)

        if order_by is not None:
            stmt = stmt.order_by(*order_by)

        return stmt

    @classmethod
    async def get(
            cls: Type[T],
            session: AsyncSession,
            *filters: Any,
            fields: FIELDS = None,
            relations: RELATIONS = None,
    ) -> T | None:
        try:
            stmt = cls._build_select(
                *filters, fields=fields, relations=relations
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            cls._handle_db_error(e)
            raise e

    @classmethod
    async def get_all(
            cls: Type[T],
            session: AsyncSession,
            *filters: Any,
            fields: FIELDS = None,
            relations: RELATIONS = None,
            order_by: Sequence[Any] | None = None,
            limit: int | None = None,
            offset: int | None = None,
    ) -> Sequence[T]:
        try:
            stmt = cls._build_select(
                *filters, fields=fields, relations=relations, order_by=order_by
            )
            if limit is not None:
                stmt = stmt.limit(limit)
            if offset is not None:
                stmt = stmt.offset(offset)

            result = await session.execute(stmt)
            return result.scalars().all()
        except SQLAlchemyError as e:
            cls._handle_db_error(e)
            raise e

    @classmethod
    async def get_query(
            cls: Type[T], session: AsyncSession, stmt: Select[Any]
    ) -> Any:
        try:
            return await session.execute(stmt)
        except SQLAlchemyError as e:
            cls._handle_db_error(e)
            raise e

    @classmethod
    async def create(cls: Type[T], session: AsyncSession, **values) -> Any:
        try:
            dialect = session.bind.dialect.name
            stmt = insert(cls).values(**values)
            if dialect == "mysql":
                res = await session.execute(stmt)
                await session.flush()
                return res.inserted_primary_key[0]
            else:
                stmt = stmt.returning(cls.id)
                res = await session.execute(stmt)
                await session.flush()
                return res.scalar_one()
        except SQLAlchemyError as e:
            await session.rollback()
            cls._handle_db_error(e)

    @classmethod
    async def update(cls: Type[T], session: AsyncSession, *filter_, **values) -> int | None:
        try:
            stmt = update(cls).where(*filter_).values(**values)
            result = await session.execute(stmt)
            await session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            await session.rollback()
            cls._handle_db_error(e)

    @classmethod
    async def delete(cls: Type[T], session: AsyncSession, *filter_) -> int | None:
        try:
            stmt = delete(cls).where(*filter_)
            result = await session.execute(stmt)
            await session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            await session.rollback()
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
    def _extract_field_name(error_msg: str) -> str | None:
        """Extracts the specific column/key name that caused the constraint violation."""
        pg_match = re.search(r"Key \((.*?)\)=", error_msg)
        if pg_match:
            return pg_match.group(1)

        mysql_match = re.search(r"for key '.*?\.?(?:uq_)?(.*?)'", error_msg)
        if mysql_match:
            return mysql_match.group(1)

        return None

    @classmethod
    def _handle_db_error(cls, e: Exception) -> None:
        orig = getattr(e, "orig", None)
        error_msg = str(orig) if orig else str(e)

        if isinstance(e, IntegrityError):
            pg_code = getattr(orig, "sqlstate", None) or getattr(
                orig, "pgcode", None
            )

            mysql_code = (
                orig.args[0]
                if orig and hasattr(orig, "args") and len(orig.args) > 0
                else None
            )

            if pg_code == "23505" or mysql_code == 1062:
                field = cls._extract_field_name(error_msg)
                msg = (
                    f"The specified '{field}' already exists."
                    if field
                    else "A record with this information already exists."
                )
                raise DatabaseException(message=msg, code=409)

            elif pg_code == "23503" or mysql_code in (1452, 1451):
                if mysql_code == 1451 or "still referenced" in error_msg:
                    raise DatabaseException(
                        message="Cannot delete or update this record because it is referenced by other resources.",
                        code=409,
                    )
                raise DatabaseException(
                    message="Referenced record not found. Please provide a valid identifier.",
                    code=400,
                )

            elif pg_code == "23502" or mysql_code in (1048, 1364):
                raise DatabaseException(
                    message="Missing required field(s). Please provide all mandatory values.",
                    code=422,
                )

            logger.warning(f"Database Integrity Violation: {error_msg}")
            raise DatabaseException(
                message="Data integrity constraint violated.",
                code=409,
            )

        if isinstance(e, DataError):
            logger.warning(f"Database Data Error: {error_msg}")
            raise DatabaseException(
                message="Invalid data format or value exceeds column constraints.",
                code=400,
            )

        if isinstance(e, OperationalError):
            logger.error(
                f"Database Connection/Operational Error: {e}", exc_info=True
            )
            raise DatabaseException(
                message="Database service is temporarily unavailable. Please try again later.",
                code=503,
            )

        logger.error(f"Unexpected Database Error: {e}", exc_info=True)
        raise DatabaseException(
            message="An unexpected internal database error occurred.",
            code=500,
        )


class Model(Base, Manager):
    __abstract__ = True

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + "s"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=get_current_uzb_time)
