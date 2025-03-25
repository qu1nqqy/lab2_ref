import pytest
from httpx import AsyncClient
from code.main import app

@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
