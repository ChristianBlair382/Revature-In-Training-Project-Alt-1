from pydantic import BaseModel, ConfigDict, Field

from app.orm_models.enums import FIELD_JOB_STATUS, FIELD_JOB_PRIORITY

class Field_Job_Base(BaseModel):
    title: str = Field(min_length=1, max_length=50)
    equipment_id: int
    hand_id: int
    priority: FIELD_JOB_PRIORITY = FIELD_JOB_PRIORITY.MEDIUM
    status: FIELD_JOB_STATUS = FIELD_JOB_STATUS.PENDING

class Field_Job_Create(Field_Job_Base):
    """"""

class Field_Job_Read(Field_Job_Base):
    id: int
    model_config = ConfigDict(from_attributes=True)

class Field_Job_Discrepency_Read(BaseModel):
    field_job_id: int
    title: str = Field(min_length=1, max_length=50)
    equipment_id: int
    hand_id: int
    equipment_farm_id: int
    hand_farm_id: int
    model_config = ConfigDict(from_attributes=True)

class Field_Job_Update_Status(BaseModel):
    status: FIELD_JOB_STATUS
    model_config = ConfigDict(from_attributes=True)

class Field_Job_Update_Priority(BaseModel):
    priority: FIELD_JOB_PRIORITY
    model_config = ConfigDict(from_attributes=True)

class Field_Job_Update(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=50)
    equipment_id: int | None = None
    hand_id: int | None = None
    priority: FIELD_JOB_PRIORITY | None = None
    status: FIELD_JOB_STATUS | None = None