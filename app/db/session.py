import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")  # e.g., mysql+aiomysql://user:pass@host:3306/db

engine = create_async_engine(
    DATABASE_URL,
    pool_size=5, max_overflow=10, pool_recycle=300, echo=os.getenv("SQL_ECHO") == "1"
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_session() -> AsyncSession:
    async with SessionLocal() as s:
        yield s
