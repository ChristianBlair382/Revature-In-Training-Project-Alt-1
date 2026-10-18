from __future__ import annotations

from typing import TYPE_CHECKING

from beanie import BackLink, Document, Link
from pydantic import Field
from pymongo import ASCENDING, IndexModel

from .enums import FIELD_JOB_PRIORITY, FIELD_JOB_STATUS

if TYPE_CHECKING:
    from .equipment_mongo import Equipment
    from .hand_mongo import Hand
    from .service_report_mongo import Service_Report


class Field_Job(Document):
    title: str = Field(min_length=1, max_length=50)
    priority: FIELD_JOB_PRIORITY = FIELD_JOB_PRIORITY.MEDIUM
    status: FIELD_JOB_STATUS = FIELD_JOB_STATUS.PENDING
    equipment: Link["Equipment"]
    hand: Link["Hand"]
    service_reports: list[BackLink["Service_Report"]] = Field(
        default_factory=list,
        json_schema_extra={"original_field": "field_job"}
    )

    class Settings:
        name = "field_jobs"
        indexes = [
            IndexModel([("priority", ASCENDING)]),
            IndexModel([("status", ASCENDING)]),
        ]

    def __repr__(self) -> str:
        equipment = getattr(self.equipment, "ref", self.equipment)
        hand = getattr(self.hand, "ref", self.hand)
        return (
            f"Field Job (ID = {self.id}, Title = {self.title}, "
            f"Priority = {self.priority.value}, Status = {self.status.value}, "
            f"Equipment ID = {equipment.id}, Hand ID = {hand.id})"
        )

    def update_status(self, new_status: FIELD_JOB_STATUS) -> None:
        if not isinstance(new_status, FIELD_JOB_STATUS):
            raise TypeError(
                f"Expected FieldJobStatus enum, got {type(new_status).__name__}"
            )
        self.status = new_status

    def update_priority(self, new_priority: FIELD_JOB_PRIORITY) -> None:
        if not isinstance(new_priority, FIELD_JOB_PRIORITY):
            raise TypeError(
                f"Expected FieldJobPriority enum, got {type(new_priority).__name__}"
            )
        self.priority = new_priority
