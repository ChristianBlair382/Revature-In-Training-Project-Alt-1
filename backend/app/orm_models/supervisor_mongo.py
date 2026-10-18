from __future__ import annotations

from typing import TYPE_CHECKING

from beanie import BackLink, Document
from pydantic import Field
from pymongo import ASCENDING, IndexModel

if TYPE_CHECKING:
    from .farm_mongo import Farm

class Supervisor(Document):
    name: str = Field(min_length=1, max_length=50)
    farms: list[BackLink["Farm"]] = Field(
        default_factory=list,
        json_schema_extra={"original_field": "supervisor"}
    )

    class Settings:
        name = "supervisors"
        indexes = [
            IndexModel([("name", ASCENDING)]),
        ]

    def __repr__(self) -> str:
        return f"Supervisor (ID = {self.id}, Name = {self.name})"
