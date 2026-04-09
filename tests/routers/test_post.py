import pytest
from httpx import AsyncClient
from fastapi import status


async def create_post(body: str, async_client: AsyncClient) -> dict:
    response = await async_client.post("/post", json={"body": body})
    return response.json()


@pytest.fixture()
async def created_post(async_client: AsyncClient):
    return await create_post("Test Post", async_client)


async def create_comment(body: str, post_id: int, async_client: AsyncClient) -> dict:
    response = await async_client.post(
        "/comment",
        json={
            "body": body,
            "post_id": post_id,
        },
    )
    return response.json()


@pytest.mark.anyio
async def test_create_post(async_client: AsyncClient):
    body = "Test Post"

    response = await async_client.post("/post", json={"body": body})

    assert response.status_code == status.HTTP_201_CREATED
    assert {"id": 0, "body": body}.items() <= response.json().items()


@pytest.mark.anyio
async def test_create_post_missing_data(async_client: AsyncClient):
    response = await async_client.post("/post", json={})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.anyio
async def test_get_all_posts(async_client: AsyncClient, created_post: dict):
    response = await async_client.get("/post")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [created_post]
