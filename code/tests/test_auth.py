import pytest

@pytest.mark.asyncio
async def test_register_user(async_client):
    response = await async_client.post("/register", data={
        "username": "testuser",
        "password": "testpass",
        "password_tmp": "testpass",
        "mail": "test@example.com"
    })

    assert response.status_code == 200

