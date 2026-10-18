from beanie import PydanticObjectId
from pydantic import BaseModel, ConfigDict, Field

class Supervisor_Base(BaseModel):
    name: str = Field(min_length=1, max_length=50)

class Supervisor_Create(Supervisor_Base):
    pass

class Supervisor_Read(Supervisor_Base):
    id: PydanticObjectId
    model_config = ConfigDict(from_attributes=True)

class Supervisor_Update(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)