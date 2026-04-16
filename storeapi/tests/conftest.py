import os
from typing import AsyncGenerator, Generator

from fastapi.testclient import TestClient
import pytest
from httpx import AsyncClient, ASGITransport


os.environ["ENV_STATE"] = "test"
from storeapi.database import database  # noqa: E402
from storeapi.main import app  # noqa: E402


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
def client() -> Generator:
    yield TestClient(app)


@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    await database.connect()
    yield
    await database.disconnect()


@pytest.fixture()
async def async_client() -> AsyncGenerator:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        yield ac
