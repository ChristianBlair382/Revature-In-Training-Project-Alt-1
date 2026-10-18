from decimal import Decimal

from beanie import PydanticObjectId
from pydantic import AliasChoices, AliasPath, BaseModel, ConfigDict, Field

from app.orm_models.enums import EQUIPMENT_STATUS

class Equipment_Base(BaseModel):
    serial_num: str = Field(min_length=1, max_length=50)
    model: str = Field(min_length=1, max_length=50)
    fuel_lvl: Decimal = Field(
        ge=Decimal("0"),
        le=Decimal("100"),
        max_digits=5,
        decimal_places=2,
    )
    farm_id: PydanticObjectId
    status: EQUIPMENT_STATUS = EQUIPMENT_STATUS.IDLE

class Equipment_Create(Equipment_Base):
    pass

class Equipment_Read(Equipment_Base):
    id: PydanticObjectId
    farm_id: PydanticObjectId = Field(
        validation_alias=AliasChoices(
            "farm_id",
            AliasPath("farm", "ref", "id"),
            AliasPath("farm", "id"),
        )
    )
    low_fuel: bool
    model_config = ConfigDict(from_attributes=True)

class Equipment_Update_Status(BaseModel):
    status: EQUIPMENT_STATUS

class Equipment_Update(BaseModel):
    serial_num: str | None = Field(default=None, min_length=1, max_length=50)
    model: str | None = Field(default=None, min_length=1, max_length=50)
    fuel_lvl: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
        le=Decimal("100"),
        max_digits=5,
        decimal_places=2,
    )
    farm_id: PydanticObjectId | None = None
    status: EQUIPMENT_STATUS | None = None