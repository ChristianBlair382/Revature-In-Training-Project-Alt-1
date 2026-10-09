from app.orm_models import User
from app.security import verify_password
from tests.conftest import auth_header


async def test_create_user_uses_auth_registration(client, db_session, seeded_users):
    payload = {
        "username": "new_user",
        "password": "secure_password",
    }

    unauthorized_response = await client.post("/users", json=payload)
    assert unauthorized_response.status_code == 401

    response = await client.post(
        "/users",
        json=payload,
        headers=auth_header(seeded_users["admin"]),
    )
    assert response.status_code == 201
    assert response.json()["username"] == payload["username"]
    assert "hashed_password" not in response.json()

    created_user = await db_session.get(User, response.json()["id"])
    assert created_user is not None
    assert verify_password(payload["password"], created_user.hashed_password)

    duplicate_response = await client.post(
        "/users",
        json=payload,
        headers=auth_header(seeded_users["admin"]),
    )
    assert duplicate_response.status_code == 400
