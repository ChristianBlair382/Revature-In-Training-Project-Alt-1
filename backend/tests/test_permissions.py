import pytest
from fastapi import HTTPException
from sqlalchemy import select

from app.dependencies import require_permission
from app.orm_models import Permission, RolePermission, USER_ROLE
from scripts.seed_tables import seed_permissions
from tests.conftest import auth_header


async def test_seed_permissions_creates_catalog_and_role_assignments(db_session):
    await seed_permissions(db_session)
    await db_session.flush()
    await seed_permissions(db_session)
    await db_session.flush()

    permission_names = (
        await db_session.execute(select(Permission.name))
    ).scalars().all()
    role_assignments = (
        await db_session.execute(
            select(RolePermission.role, Permission.name).join(Permission)
        )
    ).all()

    assert len(permission_names) == 28
    assert len(role_assignments) == 43
    assert (USER_ROLE.FH.value, "field_jobs:update") in role_assignments
    assert (USER_ROLE.FOA.value, "farms:create") in role_assignments
    assert (USER_ROLE.FOA.value, "users:delete") in role_assignments


async def test_permission_checker_allows_assigned_permission(db_session, seeded_users):
    permission = Permission(name="farms:create")
    db_session.add(permission)
    await db_session.flush()
    db_session.add(
        RolePermission(
            role=USER_ROLE.FOA.value,
            permission_id=permission.id,
        )
    )
    await db_session.commit()

    checker = require_permission("farms:create")
    result = await checker(current_user=seeded_users["admin"], db=db_session)

    assert result is seeded_users["admin"]


async def test_permission_checker_denies_unassigned_permission(db_session, seeded_users):
    permission = Permission(name="farms:create")
    db_session.add(permission)
    await db_session.flush()
    db_session.add(
        RolePermission(
            role=USER_ROLE.FOA.value,
            permission_id=permission.id,
        )
    )
    await db_session.commit()

    checker = require_permission("farms:delete")
    with pytest.raises(HTTPException) as exc_info:
        await checker(current_user=seeded_users["admin"], db=db_session)

    assert exc_info.value.status_code == 403


async def test_current_user_can_read_only_their_role_permissions(
    client,
    db_session,
    seeded_users,
):
    permissions = [
        Permission(name="users:read", description="Read users"),
        Permission(name="farms:read", description="Read farms"),
    ]
    db_session.add_all(permissions)
    await db_session.flush()
    db_session.add_all(
        RolePermission(
            role=USER_ROLE.FOA.value,
            permission_id=permission.id,
        )
        for permission in permissions
    )
    await db_session.commit()

    response = await client.get(
        "/users/me/permissions",
        headers=auth_header(seeded_users["admin"]),
    )

    assert response.status_code == 200
    response_body = response.json()
    assert response_body["role"] == USER_ROLE.FOA.value
    assert {permission["name"] for permission in response_body["permissions"]} == {
        "users:read",
        "farms:read",
    }


async def test_current_user_permissions_requires_authentication(client):
    response = await client.get("/users/me/permissions")

    assert response.status_code == 401


async def test_admin_can_list_permissions_for_each_role(
    client,
    db_session,
    seeded_users,
):
    permissions = [
        Permission(name="users:read", description="Read users"),
        Permission(name="farms:read", description="Read farms"),
    ]
    db_session.add_all(permissions)
    await db_session.flush()
    db_session.add_all(
        RolePermission(
            role=USER_ROLE.FOA.value,
            permission_id=permission.id,
        )
        for permission in permissions
    )
    await db_session.commit()

    response = await client.get(
        "/users/roles-permissions",
        headers=auth_header(seeded_users["admin"]),
    )

    assert response.status_code == 200
    result = {row["role"]: row["permissions"] for row in response.json()}
    assert {permission["name"] for permission in result[USER_ROLE.FOA.value]} == {
        "users:read",
        "farms:read",
    }
    assert result[USER_ROLE.FH.value] == []
    assert result[USER_ROLE.AUD.value] == []


async def test_role_permissions_list_requires_users_read(
    client,
    seeded_users,
):
    response = await client.get(
        "/users/roles-permissions",
        headers=auth_header(seeded_users["field_hand"]),
    )

    assert response.status_code == 403
