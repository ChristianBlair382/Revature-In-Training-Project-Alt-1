from beanie import PydanticObjectId
from pydantic import AliasChoices, AliasPath, BaseModel, ConfigDict, Field

class Hand_Base(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    farm_id: PydanticObjectId

class Hand_Create(Hand_Base):
    pass

class Hand_Read(Hand_Base):
    id: PydanticObjectId
    farm_id: PydanticObjectId = Field(
        validation_alias=AliasChoices(
            "farm_id",
            AliasPath("farm", "ref", "id"),
            AliasPath("farm", "id"),
        )
    )
    model_config = ConfigDict(from_attributes=True)

class Hand_Update(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    farm_id: PydanticObjectId | None = None