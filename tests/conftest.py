import os
import asyncio
import pytest
import pytest_asyncio
import httpx
from dotenv import load_dotenv

load_dotenv(".env.test")

BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def client():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=15.0) as c:
        # health check
        r = await c.get("/healthz")
        r.raise_for_status()
        yield c

@pytest.fixture(autouse=True)
def reset_db():
    """
    Reset strategy:
    - If you expose a protected /test/reset endpoint (recommended) call it here.
    - If not, delete by business keys to clean test data (idempotent).
    Replace this placeholder with your preferred approach.
    """
    # Example (commented): await client.post("/test/reset")
    yield
