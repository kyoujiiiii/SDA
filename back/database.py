"""SQLAlchemy engine and session factory."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from config import DATABASE_URL


class Base(DeclarativeBase):
    pass


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False,
)

SessionLocal = sessionmaker(bind=engine)


def init_db() -> None:
    """Create all tables defined by ORM models."""
    Base.metadata.create_all(bind=engine)
