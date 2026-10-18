import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.orm_models.enums import USER_ROLE
from app.orm_models.permission_mongo import RolePermission
from app.orm_models.user_mongo import User
from app.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    user = await User.find_one(User.username == username)
    if user is None:
        raise credentials_exception
    return user

def require_role(*allowed_roles: USER_ROLE):
    async def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Role '{current_user.role.value}' is not permitted "
                    "to perform this action."
                ),
            )
        return current_user

    return role_checker

def require_permission(*allowed_permissions: str):
    async def permission_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        role_permissions = await RolePermission.find_one(
            RolePermission.role == current_user.role
        )
        granted_permissions = (
            {permission.name for permission in role_permissions.permissions}
            if role_permissions is not None
            else set()
        )

        if not granted_permissions.intersection(allowed_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"User does not have '{allowed_permissions}' permission "
                    "to perform this action."
                ),
            )
        return current_user

    return permission_checker