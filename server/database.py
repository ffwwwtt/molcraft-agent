"""Async SQLAlchemy database setup — SQLite for local dev, PostgreSQL-ready."""

from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

import os

# SQLite database in project root (D: drive = local, no UNC path issues)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DB_FILE = _PROJECT_ROOT / "molcraft.db"
_DB_PATH = _DB_FILE.as_posix()  # forward slashes for URL
DATABASE_URL = f"sqlite+aiosqlite:///{_DB_PATH}"

# Enable WAL mode BEFORE creating engine (needed for background thread writes)
import sqlite3 as _sqlite3
DB_FILE = _DB_FILE
_conn = _sqlite3.connect(str(_DB_FILE))
_conn.execute("PRAGMA journal_mode=WAL")
_conn.commit()
_conn.close()

engine = create_async_engine(DATABASE_URL, echo=False, future=True,
    connect_args={"check_same_thread": False})
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency — yields an async DB session."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Create all tables (call on startup)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
