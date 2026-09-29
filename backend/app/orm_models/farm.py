from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .equipment import Equipment
    from .hand import Hand
    from .supervisor import Supervisor

class Farm(Base):
    __tablename__ = "farms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    location_region: Mapped[str] = mapped_column(String(25))
    capacity: Mapped[int] = mapped_column(Integer)
    supervisor_id: Mapped[int] = mapped_column(Integer, ForeignKey("supervisors.id"))

    supervisor: Mapped["Supervisor"] = relationship(back_populates="farms")
    equipments: Mapped[list["Equipment"]] = relationship(back_populates="farm")
    hands: Mapped[list["Hand"]] = relationship(back_populates="farm")

    def __repr__(self) -> str:
        return (f"Farm (ID = {self.id}, Name = {self.name}, Location Region = {self.location_region!r}, Capacity = {self.capacity}, Supervisor ID = {self.supervisor_id})")