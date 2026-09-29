from pydantic import BaseModel, ConfigDict, Field

class Supervisor_Base(BaseModel):
    name: str = Field(min_length=1, max_length=50)

class Supervisor_Create(Supervisor_Base):
    """"""

class Supervisor_Read(Supervisor_Base):
    id: int
    model_config = ConfigDict(from_attributes=True)