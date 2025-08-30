# tests/conftest.py
import os
import asyncio
import pytest
import pytest_asyncio
import httpx
from dotenv import load_dotenv

# Load .env.test if present (BASE_URL etc.)
load_dotenv(".env.test")

BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def client():
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=20.0) as c:
        # Health probe
        r = await c.get("/healthz")
        r.raise_for_status()
        yield c

@pytest.fixture(autouse=True)
def reset_db():
    """
    Reset strategy (idempotent):
    - If you expose /test/reset, call it here.
    - Otherwise, tests create unique content via timestamped names,
    so they won't collide across runs.
    """
    yield
