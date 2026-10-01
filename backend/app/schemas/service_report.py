from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class Service_Report_Base(BaseModel):
    field_job_id: int
    file_url: str = Field(min_length=1)
    notes: str | None = None

class Service_Report_Create(Service_Report_Base):
    """"""

class Service_Report_Read(Service_Report_Base):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Service_Report_Update(BaseModel):
    field_job_id: int | None = None
    file_url: str | None = Field(default=None, min_length=1)
    notes: str | None = None