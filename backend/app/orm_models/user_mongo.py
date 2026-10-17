from beanie import Document
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from app.orm_models.enums import USER_ROLE


class User(Document):
    username: str = Field(max_length=50)
    hashed_password: str = Field(max_length=255)
    role: USER_ROLE = USER_ROLE.AUD
    is_active: bool = True

    class Settings:
        name = "users"
        indexes = [
            IndexModel([("username", ASCENDING)], unique=True),
        ]

    def __repr__(self) -> str:
        return (
            f"User (ID = {self.id}, Username = {self.username!r}, "
            f"Role = {self.role.value})"
        )