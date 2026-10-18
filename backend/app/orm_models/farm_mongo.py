from __future__ import annotations
from typing import TYPE_CHECKING

from beanie import BackLink, Document, Link
from pydantic import Field
from pymongo import ASCENDING, IndexModel

if TYPE_CHECKING:
    from .equipment_mongo import Equipment
    from .hand_mongo import Hand
    from .supervisor_mongo import Supervisor

class Farm(Document):
    name: str = Field(min_length=1, max_length=50)
    location_region: str = Field(min_length=1, max_length=25)
    capacity: int

    supervisor: Link["Supervisor"]
    equipments: list[BackLink["Equipment"]] = Field(
        default_factory=list,
        json_schema_extra={"original_field": "farm"}
    )
    hands: list[BackLink["Hand"]] = Field(
        default_factory=list,
        json_schema_extra={"original_field": "farm"}
    )

    class Settings:
        name = "farms"
        indexes = [
            IndexModel([("name", ASCENDING)]),
        ]

    def __repr__(self) -> str:
        supervisor = getattr(self.supervisor, "ref", self.supervisor)
        return (
            f"Farm (ID = {self.id}, Name = {self.name!r}, "
            f"Location Region = {self.location_region!r}, "
            f"Capacity = {self.capacity}, Supervisor ID = {supervisor.id})"
        )