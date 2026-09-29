from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .farm import Farm
    from .supervisor import Supervisor
    from .field_job import Field_Job

class Hand(Base):
    __tablename__ = "hands"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    farm_id: Mapped[int] = mapped_column(Integer, ForeignKey("farms.id"))

    farm: Mapped["Farm"] = relationship(back_populates="hands")
    supervisor: Mapped["Supervisor"] = relationship(back_populates="hands")
    field_jobs: Mapped[list["Field_Job"]] = relationship(back_populates="hand")

    def __repr__(self) -> str:
        return (f"Hand (ID = {self.id}, Name = {self.name}, Farm ID = {self.farm_id})")