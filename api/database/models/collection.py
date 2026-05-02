from typing import List, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Integer, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database.models.base import Base

if TYPE_CHECKING:
    from api.database.models.series import Series

# Association table for many-to-many relationship between Collection and Series
collection_series = Table(
    "collection_series",
    Base.metadata,
    Column("collection_id", ForeignKey("collection.id"), primary_key=True),
    Column("series_id", ForeignKey("series.id"), primary_key=True),
)


class Collection(Base):
    __tablename__ = "collection"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    screen_name: Mapped[str] = mapped_column(
        String(256), ForeignKey("game.screen_name"), nullable=False
    )

    # Relationship: Many-to-Many with Series
    series: Mapped[List["Series"]] = relationship(
        secondary=collection_series,
        back_populates="collections",
    )

    def __repr__(self) -> str:
        return f"<Collection(id={self.id}, screen_name={self.screen_name})>"
