from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

from app.orm_models.enums import EQUIPMENT_STATUS

class Equipment_Base(BaseModel):
    serial_num: str = Field(min_length=1, max_length=50)
    model: str = Field(min_length=1, max_length=50)
    fuel_lvl: Decimal = Field(ge=0, le=100)
    farm_id: int
    status: EQUIPMENT_STATUS = EQUIPMENT_STATUS.IDLE

class Equipment_Create(Equipment_Base):
    """"""

class Equipment_Read(Equipment_Base):
    id: int
    model_config = ConfigDict(from_attributes=True)