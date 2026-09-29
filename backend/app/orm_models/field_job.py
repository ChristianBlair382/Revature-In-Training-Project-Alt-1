from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import FIELD_JOB_STATUS, FIELD_JOB_PRIORITY

if TYPE_CHECKING:
    from .equipment import Equipment
    from .hand import Hand
    from .service_report import Service_Report

class Field_Job(Base):
    __tablename__ = "field_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50))
    priority: Mapped[FIELD_JOB_PRIORITY] = mapped_column(
        SqlEnum(
            FIELD_JOB_PRIORITY,
            name="field_job_priority",
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        default=FIELD_JOB_PRIORITY.MEDIUM,
    )
    status: Mapped[FIELD_JOB_STATUS] = mapped_column(
        SqlEnum(
            FIELD_JOB_STATUS,
            name="field_job_status",
            values_callable=lambda enum_cls: [member.value for member in enum_cls]
        ),
        default=FIELD_JOB_STATUS.PENDING,
    )
    equipment_id: Mapped[int] = mapped_column(Integer, ForeignKey("equipments.id"))
    hand_id: Mapped[int] = mapped_column(Integer, ForeignKey("hands.id"))

    equipment: Mapped["Equipment"] = relationship(back_populates="field_jobs")
    hand: Mapped["Hand"] = relationship(back_populates="field_jobs")
    service_reports: Mapped[list["Service_Report"]] = relationship(back_populates="field_job")

    def __repr__(self) -> str:
        return (f"Field Job (ID = {self.id}, Title = {self.title}, Priority = {self.priority.value}, Status = {self.status.value}, Equipment ID = {self.equipment_id}, Hand ID = {self.hand_id})")
    
    def update_status(self, new_status: FIELD_JOB_STATUS) -> None:
        if not isinstance(new_status, FIELD_JOB_STATUS):
            raise TypeError(f"Expected FieldJobStatus enum, got {type(new_status).__name__}")
        if self.status == new_status:
            return
        self.status = new_status

    def update_priority(self, new_priority: FIELD_JOB_PRIORITY) -> None:
        if not isinstance(new_priority, FIELD_JOB_PRIORITY):
            raise TypeError(f"Expected FieldJobPriority enum, got {type(new_status).__name__}")
        if self.priority == new_priority:
            return
        self.priority = new_priority