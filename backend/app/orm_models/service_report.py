from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .field_job import Field_Job

class Service_Report(Base):
    __tablename__ = "service_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    file_url: Mapped[str] = mapped_column(Text, unique=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    service_report_id: Mapped[int] = mapped_column(Integer, ForeignKey("field_jobs.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    field_job: Mapped["Field_Job"] = relationship(back_populates="service_reports")

    def __repr__(self) -> str:
        return (f"Service Report (ID = {self.id}, File URL = {self.file_url!r}, Service Report ID = {self.service_report_id!r}, Created At = {self.created_at})")