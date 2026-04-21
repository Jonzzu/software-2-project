from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database.models.base import Base

if TYPE_CHECKING:
    # Avoiding circular imports for relationships
    from api.database.models.country import Country
    from api.database.models.game import Game


class Airport(Base):
    __tablename__ = "airport"

    ident: Mapped[str] = mapped_column(String(40), primary_key=True)
    id: Mapped[int] = mapped_column(Integer)
    type: Mapped[str] = mapped_column(String(40))
    name: Mapped[str] = mapped_column(String(256))
    latitude_deg: Mapped[float] = mapped_column(Float)
    longitude_deg: Mapped[float] = mapped_column(Float)
    elevation_ft: Mapped[Optional[int]] = mapped_column(Integer)
    continent: Mapped[str] = mapped_column(String(2))
    iso_region: Mapped[str] = mapped_column(String(10))
    municipality: Mapped[str] = mapped_column(String(100))

    # Foreign Key to Country
    iso_country: Mapped[str] = mapped_column(ForeignKey("country.iso_country"))

    # Relationships
    country: Mapped["Country"] = relationship(back_populates="airports")
    games: Mapped[List["Game"]] = relationship(back_populates="current_airport")

    def __repr__(self) -> str:
        return f"<Airport(ident={self.ident}, name={self.name})>"


