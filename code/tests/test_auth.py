import pytest

@pytest.mark.asyncio
async def test_register_user(async_client):
    response = await async_client.post("/register", json={
        "username": "testuser",
        "password": "testpass"
    })
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_login_user(async_client):
    # Предполагаем, что пользователь уже зарегистрирован
    response = await async_client.post("/token", data={
        "username": "testuser",
        "password": "testpass"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
