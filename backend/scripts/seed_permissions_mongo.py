# Run with: python -m scripts.seed_permissions_mongo
# From: backend/ with the Mongo dependencies installed

import asyncio

from app.database_mongo import close_mongo_connection, connect_to_mongo
from app.orm_models.enums import USER_ROLE
from app.orm_models.permission_mongo import PermissionEntry, RolePermission

PERMISSION_RESOURCES = (
    "farms",
    "equipments",
    "field_jobs",
    "service_reports",
    "hands",
    "supervisors",
    "users",
)
PERMISSION_ACTIONS = ("create", "read", "update", "delete")

READABLE_RESOURCES = (
    "farms",
    "equipments",
    "field_jobs",
    "service_reports",
    "hands",
    "supervisors",
)

ROLE_PERMISSIONS = {
    USER_ROLE.AUD: {f"{resource}:read" for resource in READABLE_RESOURCES},
    USER_ROLE.FH: {
        *(f"{resource}:read" for resource in READABLE_RESOURCES),
        "equipments:update",
        "field_jobs:update",
        "service_reports:create",
    },
    USER_ROLE.FOA: {
        f"{resource}:{action}"
        for resource in PERMISSION_RESOURCES
        for action in PERMISSION_ACTIONS
    },
}


async def seed_permissions() -> None:
    for role in USER_ROLE:
        permissions = [
            PermissionEntry(
                name=f"{resource}:{action}",
                description=f"{action.title()} {resource.replace('_', ' ')}",
            )
            for resource in PERMISSION_RESOURCES
            for action in PERMISSION_ACTIONS
            if f"{resource}:{action}" in ROLE_PERMISSIONS[role]
        ]

        role_permissions = await RolePermission.find_one(
            RolePermission.role == role
        )
        if role_permissions is None:
            role_permissions = RolePermission(role=role, permissions=permissions)
            await role_permissions.insert()
        else:
            role_permissions.permissions = permissions
            await role_permissions.save()


async def main() -> None:
    await connect_to_mongo()
    try:
        await seed_permissions()
        print("Permissions seeded to MongoDB.")
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(main())