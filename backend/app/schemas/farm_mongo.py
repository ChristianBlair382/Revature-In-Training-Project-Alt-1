from beanie import PydanticObjectId
from pydantic import AliasChoices, AliasPath, BaseModel, ConfigDict, Field

class Farm_Base(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    location_region: str = Field(min_length=1, max_length=25)
    capacity: int
    supervisor_id: PydanticObjectId

class Farm_Create(Farm_Base):
    pass

class Farm_Read(Farm_Base):
    id: PydanticObjectId
    supervisor_id: PydanticObjectId = Field(
        validation_alias=AliasChoices(
            "supervisor_id",
            AliasPath("supervisor", "ref", "id"),
            AliasPath("supervisor", "id"),
        )
    )
    model_config = ConfigDict(from_attributes=True)

class Farm_Update(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    location_region: str | None = Field(default=None, min_length=1, max_length=25)
    capacity: int | None = None
    supervisor_id: PydanticObjectId | None = None