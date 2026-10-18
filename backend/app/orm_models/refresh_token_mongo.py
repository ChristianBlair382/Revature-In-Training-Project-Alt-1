from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, ClassVar
from uuid import UUID, uuid4

from beanie import Document, Link
from pydantic import Field
from pymongo import ASCENDING, IndexModel

if TYPE_CHECKING:
    from .user_mongo import User

class Refresh_Token(Document):
    DAYS_TILL_EXPIRE: ClassVar[int] = 30

    user: Link["User"]
    family_id: UUID = Field(default_factory=uuid4)
    token_hash: str = Field(min_length=64, max_length=64)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime
    revoked_at: datetime | None = None

    class Settings:
        name = "refresh_tokens"
        indexes = [
            IndexModel([("user", ASCENDING)]),
            IndexModel([("family_id", ASCENDING)]),
            IndexModel([("token_hash", ASCENDING)], unique=True),
        ]

    def __repr__(self) -> str:
        user = getattr(self.user, "ref", self.user)
        return (
            f"Refresh Token (ID: {self.id}, User ID: {user.id}, "
            f"Family ID: {self.family_id}, Expires At: {self.expires_at}, "
            f"Revoked At: {self.revoked_at})"
        )
