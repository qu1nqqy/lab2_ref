import pytest

@pytest.mark.asyncio
async def test_homepage(async_client):
    response = await async_client.get("/")
    assert response.status_code == 200
