from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, ClassVar

from beanie import BackLink, Document, Link
from bson.decimal128 import Decimal128
from pydantic import Field, field_validator
from pymongo import ASCENDING, IndexModel

from .enums import EQUIPMENT_STATUS

if TYPE_CHECKING:
    from .farm_mongo import Farm
    from .field_job_mongo import Field_Job

class Equipment(Document):
    serial_num: str = Field(min_length=1, max_length=50)
    model: str = Field(min_length=1, max_length=50)
    status: EQUIPMENT_STATUS = EQUIPMENT_STATUS.IDLE
    fuel_lvl: Decimal = Field(
        ge=Decimal("0"),
        le=Decimal("100"),
        max_digits=5,
        decimal_places=2,
    )

    farm: Link["Farm"]
    field_jobs: list[BackLink["Field_Job"]] = Field(
        default_factory=list,
        json_schema_extra={"original_field": "equipment"}
    )

    @field_validator("fuel_lvl", mode="before")
    @classmethod
    def convert_decimal128(cls, value: object) -> object:
        if isinstance(value, Decimal128):
            return value.to_decimal()
        return value

    class Settings:
        name = "equipments"
        indexes = [
            IndexModel([("serial_num", ASCENDING)], unique=True),
        ]

    LOW_FUEL_THRESHOLD: ClassVar[int] = 20

    def __repr__(self) -> str:
        farm = getattr(self.farm, "ref", self.farm)
        return (
            f"Equipment (ID = {self.id}, Serial Number = {self.serial_num}, "
            f"Model = {self.model}, Fuel Level = {self.fuel_lvl}, "
            f"Status = {self.status.value}, Farm ID = {farm.id})"
        )

    def is_low_fuel(self, threshold: int | None = None) -> bool:
        limit = threshold if threshold is not None else self.LOW_FUEL_THRESHOLD
        return self.fuel_lvl <= limit

    @property
    def low_fuel(self) -> bool:
        return self.is_low_fuel()

    def needs_maintenance(self) -> bool:
        return self.status == EQUIPMENT_STATUS.MAINTENANCE

    def update_status(self, new_status: EQUIPMENT_STATUS) -> None:
        if not isinstance(new_status, EQUIPMENT_STATUS):
            raise TypeError(
                f"Expected EquipmentStatus enum, got {type(new_status).__name__}"
            )
        self.status = new_status
