from __future__ import annotations

from typing import TYPE_CHECKING

from beanie import BackLink, Document, Link
from pydantic import Field
from pymongo import ASCENDING, IndexModel

if TYPE_CHECKING:
    from .farm_mongo import Farm
    from .field_job_mongo import Field_Job

class Hand(Document):
    name: str = Field(min_length=1, max_length=50)
    farm: Link["Farm"]
    field_jobs: list[BackLink["Field_Job"]] = Field(
        default_factory=list,
        json_schema_extra={"original_field": "hand"}
    )

    class Settings:
        name = "hands"
        indexes = [
            IndexModel([("name", ASCENDING)]),
        ]

    def __repr__(self) -> str:
        farm = getattr(self.farm, "ref", self.farm)
        return f"Hand (ID = {self.id}, Name = {self.name}, Farm ID = {farm.id})"
