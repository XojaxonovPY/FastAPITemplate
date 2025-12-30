from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped

from db.config import Model, Base


class User(Model):
    first_name: Mapped[str] = mapped_column(String(length=50),nullable=True)
    username: Mapped[str] = mapped_column(String(length=50), unique=True)
    password: Mapped[str] = mapped_column(String(length=200))


metadata = Base.metadata
