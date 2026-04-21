from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database.models.base import Base

goal_reached = Table(
    "goal_reached",
    Base.metadata,
    Column("game_id", ForeignKey("game.id"), primary_key=True),
    Column("goal_id", ForeignKey("goal.id"), primary_key=True),
)


class Game(Base):
    __tablename__ = "game"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    points: Mapped[int] = mapped_column(Integer, default=0)
    money: Mapped[int] = mapped_column(Integer, default=0)
    screen_name: Mapped[str] = mapped_column(String(256))

    # Foreign Key pointing to airport.ident
    location: Mapped[str] = mapped_column(ForeignKey("airport.ident"))

    # Relationship: Each game has a current location (Airport)
    current_airport: Mapped["Airport"] = relationship(back_populates="games")

    def __repr__(self) -> str:
        return f"<Game(id={self.id}, player={self.screen_name}, loc={self.location})>"

