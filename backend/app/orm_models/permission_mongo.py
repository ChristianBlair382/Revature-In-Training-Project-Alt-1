from beanie import Document
from pydantic import BaseModel, Field
from pymongo import ASCENDING, IndexModel

from .enums import USER_ROLE


class PermissionEntry(BaseModel):
    name: str
    description: str | None = None


class RolePermission(Document):
    role: USER_ROLE
    permissions: list[PermissionEntry] = Field(default_factory=list)

    class Settings:
        name = "role_permissions"
        indexes = [
            IndexModel([("role", ASCENDING)], unique=True),
        ]
