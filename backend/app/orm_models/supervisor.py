from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .farm import Farm
    from .hand import Hand

class Supervisor(Base):
    __tablename__ = "supervisors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))

    farm: Mapped["Farm"] = relationship(back_populates="supervisors")
    hands: Mapped[list["Hand"]] = relationship(back_populates="supervisor")

    def __repr__(self) -> str:
        return (f"Supervisor (ID = {self.id}, Name = {self.name})")