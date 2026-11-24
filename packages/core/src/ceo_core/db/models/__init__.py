"""SQLAlchemy declarative base. Domain modules register tables on this metadata."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
