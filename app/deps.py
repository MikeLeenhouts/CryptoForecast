# app/deps.py
from collections.abc import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import SessionLocal

async def db() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency that yields an AsyncSession."""
    async with SessionLocal() as session:
        yield session
