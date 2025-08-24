from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session

def db(s: AsyncSession = Depends(get_session)) -> AsyncSession:
    return s
