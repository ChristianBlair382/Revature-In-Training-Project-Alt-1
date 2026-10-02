from __future__ import annotations
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric, String, Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .enums import EQUIPMENT_STATUS

if TYPE_CHECKING:
    from .farm import Farm
    from .field_job import Field_Job

class Equipment(Base):
    __tablename__ = "equipments"

    __table_args__ = (
        CheckConstraint(
            "fuel_lvl BETWEEN 0 AND 100",
            name="fuel_lvl_range"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    serial_num: Mapped[str] = mapped_column(String(50), unique=True)
    model: Mapped[str] = mapped_column(String(50))
    status: Mapped[EQUIPMENT_STATUS] = mapped_column(
        SqlEnum(
            EQUIPMENT_STATUS, 
            name="equipment_status", 
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        default=EQUIPMENT_STATUS.IDLE,
    )
    fuel_lvl: Mapped[Decimal] = mapped_column(Numeric(5,2))
    farm_id: Mapped[int] = mapped_column(Integer, ForeignKey("farms.id"))

    farm: Mapped["Farm"] = relationship(back_populates="equipments")
    field_jobs: Mapped[list["Field_Job"]] = relationship(back_populates="equipment")

    def __repr__(self) -> str:
        return (f"Equipment (ID = {self.id}, Serial Number = {self.serial_num}, Model = {self.model}, Fuel Level = {self.fuel_lvl}, Status = {self.status.value}, Farm ID = {self.farm_id})")

    LOW_FUEL_THRESHOLD: int = 20

    def is_low_fuel(self, threshold: int | None = None) -> bool:
        limit = threshold if threshold is not None else Equipment.LOW_FUEL_THRESHOLD
        return self.fuel_lvl <= limit

    @property
    def low_fuel(self) -> bool:
        return self.is_low_fuel()

    def needs_maintenance(self) -> bool:
        return self.status == EQUIPMENT_STATUS.MAINTENANCE

    def update_status(self, new_status: EQUIPMENT_STATUS) -> None:
        if not isinstance(new_status, EQUIPMENT_STATUS):
            raise TypeError(f"Expected EquipmentStatus enum, got {type(new_status).__name__}")
        if self.status == new_status:
            return
        self.status = new_status