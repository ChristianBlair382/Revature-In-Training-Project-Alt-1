from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from beanie import Document, Link
from pydantic import Field
from pymongo import ASCENDING, IndexModel

if TYPE_CHECKING:
    from .field_job_mongo import Field_Job

class Service_Report(Document):
    file_url: str
    notes: str | None = None
    field_job: Link["Field_Job"]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "service_reports"
        indexes = [
            IndexModel([("file_url", ASCENDING)], unique=True),
            IndexModel([("created_at", ASCENDING)]),
        ]

    def __repr__(self) -> str:
        field_job = getattr(self.field_job, "ref", self.field_job)
        return (
            f"Service Report (ID = {self.id}, File URL = {self.file_url!r}, "
            f"Field Job ID = {field_job.id}, Created At = {self.created_at})"
        )
