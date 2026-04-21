from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database.models.base import Base


class Country(Base):
    __tablename__ = "country"

    iso_country: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    continent: Mapped[str] = mapped_column(String(2))

    # Relationship: One country has many airports
    airports: Mapped[List["Airport"]] = relationship(back_populates="country")
