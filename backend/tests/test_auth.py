from tests.conftest import auth_header

async def test_login_succeeds_with_correct_credentials(client, seeded_users):
    response = await client.post(
        "/auth/token",
        data={"username": "test_admin", "password": "pw"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()