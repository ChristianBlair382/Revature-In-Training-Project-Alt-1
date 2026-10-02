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
    low_fuel: bool
    model_config = ConfigDict(from_attributes=True)

class Equipment_Update_Status(BaseModel):
    status: EQUIPMENT_STATUS
    model_config = ConfigDict(from_attributes=True)

class Equipment_Update(BaseModel):
    serial_num: str | None = Field(default=None, min_length=1, max_length=50)
    model: str | None = Field(default=None, min_length=1, max_length=50)
    fuel_lvl: Decimal | None = Field(default=None, ge=0, le=100)
    farm_id: int | None = None
    status: EQUIPMENT_STATUS | None = None