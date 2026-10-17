from __future__ import annotations
from typing import TYPE_CHECKING

from beanie import BackLink, Document, Link
from pydantic import Field
from pymongo import ASCENDING, IndexModel

if TYPE_CHECKING:
    from .equipment import Equipment
    from .hand import Hand
    from .supervisor import Supervisor

class Farm(Document):
    name: str = Field(min_length=1, max_length=50)
    location_region: str = Field(min_length=1, max_length=25)
    capacity: int

    supervisor: Link["Supervisor"]
    equipments: list[BackLink["Equipment"]] = Field(
        json_schema_extra={"original_field": "farm"}
    )
    hands: list[BackLink["Hand"]] = Field(
        json_schema_extra={"original_field": "farm"}
    )

    class Settings:
        name = "farms"
        indexes = [
            IndexModel([("name", ASCENDING)]),
        ]

    def __repr__(self):
        return (
            f"Farm (ID = {self.id}, Name = {self.name!r}, "
            f"Capacity = {self.capacity})"
        )