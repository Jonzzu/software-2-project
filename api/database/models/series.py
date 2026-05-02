from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database.models.base import Base
from api.database.models.collection import collection_series

if TYPE_CHECKING:
    from api.database.models.collection import Collection


class Series(Base):
    __tablename__ = "series"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    anilist_id: Mapped[Optional[int]] = mapped_column(nullable=True)  # External API ID
    average_score: Mapped[float] = mapped_column(Float, default=0.0)
    description: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    cover_image_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Relationship: Many-to-Many with Collections
    collections: Mapped[List["Collection"]] = relationship(
        secondary=collection_series,
        back_populates="series",
    )

    def __repr__(self) -> str:
        return f"<Series(id={self.id}, name={self.name}, rating={self.average_score})>"