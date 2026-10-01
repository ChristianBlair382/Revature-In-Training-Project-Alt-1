from pydantic import BaseModel, ConfigDict, Field

class Farm_Base(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    location_region: str = Field(min_length=1, max_length=25)
    capacity: int
    supervisor_id: int

class Farm_Create(Farm_Base):
    """"""

class Farm_Read(Farm_Base):
    id: int
    model_config = ConfigDict(from_attributes=True)

class Farm_Update(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    location_region: str | None = Field(default= None, min_length=1, max_length=25)
    capacity: int | None = None
    supervisor_id: int | None = None