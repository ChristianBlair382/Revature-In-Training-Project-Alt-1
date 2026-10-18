from datetime import datetime

from beanie import PydanticObjectId
from pydantic import AliasChoices, AliasPath, BaseModel, ConfigDict, Field


class Service_Report_Base(BaseModel):
    field_job_id: PydanticObjectId
    file_url: str = Field(min_length=1)
    notes: str | None = None

class Service_Report_Create(Service_Report_Base):
    pass

class Service_Report_Read(Service_Report_Base):
    id: PydanticObjectId
    field_job_id: PydanticObjectId = Field(
        validation_alias=AliasChoices(
            "field_job_id",
            AliasPath("field_job", "ref", "id"),
            AliasPath("field_job", "id"),
        )
    )
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Service_Report_Update(BaseModel):
    field_job_id: PydanticObjectId | None = None
    file_url: str | None = Field(default=None, min_length=1)
    notes: str | None = None