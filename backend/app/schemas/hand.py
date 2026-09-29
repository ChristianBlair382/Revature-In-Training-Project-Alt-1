from pydantic import BaseModel, ConfigDict, Field

class Hand_Base(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    farm_id: int

class Hand_Create(Hand_Base):
    """"""

class Hand_Read(Hand_Base):
    id: int
    model_config = ConfigDict(from_attributes=True)