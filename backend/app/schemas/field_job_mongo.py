from beanie import PydanticObjectId
from pydantic import AliasChoices, AliasPath, BaseModel, ConfigDict, Field

from app.orm_models.enums import FIELD_JOB_STATUS, FIELD_JOB_PRIORITY

class Field_Job_Base(BaseModel):
    title: str = Field(min_length=1, max_length=50)
    equipment_id: PydanticObjectId
    hand_id: PydanticObjectId
    priority: FIELD_JOB_PRIORITY = FIELD_JOB_PRIORITY.MEDIUM
    status: FIELD_JOB_STATUS = FIELD_JOB_STATUS.PENDING

class Field_Job_Create(Field_Job_Base):
    pass

class Field_Job_Read(Field_Job_Base):
    id: PydanticObjectId
    equipment_id: PydanticObjectId = Field(
        validation_alias=AliasChoices(
            "equipment_id",
            AliasPath("equipment", "ref", "id"),
            AliasPath("equipment", "id"),
        )
    )
    hand_id: PydanticObjectId = Field(
        validation_alias=AliasChoices(
            "hand_id",
            AliasPath("hand", "ref", "id"),
            AliasPath("hand", "id"),
        )
    )
    model_config = ConfigDict(from_attributes=True)

class Field_Job_Discrepency_Read(BaseModel):
    field_job_id: PydanticObjectId
    title: str = Field(min_length=1, max_length=50)
    equipment_id: PydanticObjectId
    hand_id: PydanticObjectId
    equipment_farm_id: PydanticObjectId
    hand_farm_id: PydanticObjectId
    model_config = ConfigDict(from_attributes=True)

class Field_Job_Update_Status(BaseModel):
    status: FIELD_JOB_STATUS
    model_config = ConfigDict(from_attributes=True)

class Field_Job_Update_Priority(BaseModel):
    priority: FIELD_JOB_PRIORITY
    model_config = ConfigDict(from_attributes=True)

class Field_Job_Update(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=50)
    equipment_id: PydanticObjectId | None = None
    hand_id: PydanticObjectId | None = None
    priority: FIELD_JOB_PRIORITY | None = None
    status: FIELD_JOB_STATUS | None = None