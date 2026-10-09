from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy import select

from app.orm_models import Refresh_Token
from app.security import create_refresh_token, decode_access_token, hash_refresh_token

async def test_login_succeeds_with_correct_credentials(client, seeded_users):
    response = await client.post(
        "/auth/token",
        data={"username": "test_admin", "password": "pw"},
    )

    assert response.status_code == 200
    response_body = response.json()
    assert response_body["token_type"] == "bearer"
    assert response_body["access_token"]
    assert response_body["refresh_token"]


async def test_login_stores_only_refresh_token_hash(
    client,
    db_session,
    seeded_users,
):
    response = await client.post(
        "/auth/token",
        data={"username": "test_admin", "password": "pw"},
    )
    raw_refresh_token = response.json()["refresh_token"]

    result = await db_session.execute(
        select(Refresh_Token).where(
            Refresh_Token.token_hash == hash_refresh_token(raw_refresh_token)
        )
    )
    stored_token = result.scalar_one()

    assert stored_token.user_id == seeded_users["admin"].id
    assert stored_token.token_hash != raw_refresh_token
    assert stored_token.revoked_at is None
    assert stored_token.expires_at > datetime.now(timezone.utc)


async def test_refresh_rotates_token_and_preserves_family(
    client,
    db_session,
    seeded_users,
):
    login_response = await client.post(
        "/auth/token",
        data={"username": "test_admin", "password": "pw"},
    )
    original_raw_token = login_response.json()["refresh_token"]

    original_result = await db_session.execute(
        select(Refresh_Token).where(
            Refresh_Token.token_hash == hash_refresh_token(original_raw_token)
        )
    )
    original_token = original_result.scalar_one()
    original_family_id = original_token.family_id

    response = await client.post(
        "/auth/refresh",
        json={"refresh_token": original_raw_token},
    )

    assert response.status_code == 200
    response_body = response.json()
    replacement_raw_token = response_body["refresh_token"]
    access_payload = decode_access_token(response_body["access_token"])

    assert response_body["token_type"] == "bearer"
    assert replacement_raw_token != original_raw_token
    assert access_payload["sub"] == seeded_users["admin"].username
    assert access_payload["role"] == seeded_users["admin"].role.value
    assert original_token.revoked_at is not None

    replacement_result = await db_session.execute(
        select(Refresh_Token).where(
            Refresh_Token.token_hash == hash_refresh_token(replacement_raw_token)
        )
    )
    replacement_token = replacement_result.scalar_one()

    assert replacement_token.user_id == original_token.user_id
    assert replacement_token.family_id == original_family_id
    assert replacement_token.revoked_at is None
    assert replacement_token.expires_at > datetime.now(timezone.utc)


async def test_refresh_rejects_unknown_token(client):
    response = await client.post(
        "/auth/refresh",
        json={"refresh_token": create_refresh_token()},
    )

    assert response.status_code == 401


async def test_refresh_rejects_expired_token(client, db_session, seeded_users):
    now = datetime.now(timezone.utc)
    expired_raw_token = create_refresh_token()
    expired_token = Refresh_Token(
        user_id=seeded_users["admin"].id,
        token_hash=hash_refresh_token(expired_raw_token),
        created_at=now - timedelta(days=Refresh_Token.DAYS_TILL_EXPIRE + 1),
        expires_at=now - timedelta(seconds=1),
    )
    db_session.add(expired_token)
    await db_session.commit()

    response = await client.post(
        "/auth/refresh",
        json={"refresh_token": expired_raw_token},
    )

    assert response.status_code == 401


async def test_reused_revoked_token_revokes_active_family_tokens(
    client,
    db_session,
    seeded_users,
):
    now = datetime.now(timezone.utc)
    family_id = uuid4()
    reused_raw_token = create_refresh_token()
    revoked_token = Refresh_Token(
        user_id=seeded_users["admin"].id,
        family_id=family_id,
        token_hash=hash_refresh_token(reused_raw_token),
        created_at=now - timedelta(minutes=2),
        expires_at=now + timedelta(days=Refresh_Token.DAYS_TILL_EXPIRE),
        revoked_at=now - timedelta(minutes=1),
    )
    active_raw_token = create_refresh_token()
    active_token = Refresh_Token(
        user_id=seeded_users["admin"].id,
        family_id=family_id,
        token_hash=hash_refresh_token(active_raw_token),
        created_at=now,
        expires_at=now + timedelta(days=Refresh_Token.DAYS_TILL_EXPIRE),
    )
    db_session.add_all([revoked_token, active_token])
    await db_session.commit()

    response = await client.post(
        "/auth/refresh",
        json={"refresh_token": reused_raw_token},
    )

    assert response.status_code == 401
    await db_session.refresh(active_token)
    assert active_token.revoked_at is not None