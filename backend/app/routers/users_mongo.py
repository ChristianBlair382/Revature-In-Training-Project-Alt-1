from fastapi import APIRouter, Depends, HTTPException, Response, status
from beanie import PydanticObjectId
from bson import DBRef

from app.dependencies_mongo import get_current_user, require_permission
from app.orm_models.enums import USER_ROLE
from app.orm_models.permission_mongo import RolePermission
from app.orm_models.refresh_token_mongo import Refresh_Token
from app.orm_models.user_mongo import User
from app.schemas.user_mongo import (
    Role_Permissions_Read,
    User_Permissions_Read,
    User_Read,
    User_Update,
)
from app.security import encrypt_password

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me/permissions", response_model=User_Permissions_Read)
async def get_my_permissions(
    current_user: User = Depends(get_current_user),
) -> User_Permissions_Read:
    role_permissions = await RolePermission.find_one(
        RolePermission.role == current_user.role
    )
    return User_Permissions_Read(
        role=current_user.role,
        permissions=role_permissions.permissions if role_permissions else [],
    )

@router.get(
    "/roles-permissions",
    response_model=list[Role_Permissions_Read],
)
async def list_role_permissions(
    _: User = Depends(require_permission("users:read")),
) -> list[Role_Permissions_Read]:
    role_documents = await RolePermission.find_all().to_list()
    permissions_by_role = {role: [] for role in USER_ROLE}

    for role_document in role_documents:
        permissions_by_role[role_document.role] = role_document.permissions

    return [
        Role_Permissions_Read(role=role, permissions=permissions_by_role[role])
        for role in USER_ROLE
    ]

@router.get("", response_model=list[User_Read])
async def list_users(
    _: User = Depends(require_permission("users:read")),
) -> list[User]:
    return await User.find_all().sort("+id").to_list()

@router.get("/{user_id}", response_model=User_Read)
async def find_user_by_id(
    user_id: PydanticObjectId,
    _: User = Depends(require_permission("users:read")),
) -> User:
    target_user = await User.get(user_id)
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' does not exist.",
        )
    return target_user

@router.patch("/{user_id}", response_model=User_Read)
async def update_user(
    user_id: PydanticObjectId,
    payload: User_Update,
    _: User = Depends(require_permission("users:update")),
) -> User:
    target_user = await User.get(user_id)
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' does not exist.",
        )

    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    if "password" in changes:
        changes["hashed_password"] = encrypt_password(changes.pop("password"))

    for field, value in changes.items():
        setattr(target_user, field, value)

    await target_user.save()
    return target_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: PydanticObjectId,
    _: User = Depends(require_permission("users:delete")),
) -> Response:
    target_user = await User.get(user_id)
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' does not exist.",
        )

    await Refresh_Token.get_motor_collection().delete_many(
        {"user": DBRef(User.Settings.name, target_user.id)}
    )
    await target_user.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
