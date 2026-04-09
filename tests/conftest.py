from typing import AsyncGenerator, Generator

from fastapi.testclient import TestClient
import pytest
from main import app
from routers.post import comment_table, post_table
from httpx import AsyncClient, ASGITransport


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
def client() -> Generator:
    yield TestClient(app)


@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    post_table.clear()
    comment_table.clear()
    yield


@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    async with AsyncClient(transport=ASGITransport(app=app), base_url=client.base_url) as ac:
        yield ac
