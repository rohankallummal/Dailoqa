"""SQLAlchemy async engine, session factory, and declarative base."""

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

APP_SCHEMA = "app"

engine = create_async_engine(get_settings().database_url, pool_pre_ping=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Declarative base pinned to the isolated ``app`` schema."""

    metadata = MetaData(schema=APP_SCHEMA)
