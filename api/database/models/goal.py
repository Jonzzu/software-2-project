from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import String, ForeignKey, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from api.database.models.game import goal_reached

from api.database.models.base import Base


class Goal(Base):
    __tablename__ = "goal"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    description: Mapped[Optional[str]] = mapped_column(String(512))
    icon: Mapped[Optional[str]] = mapped_column(String(256))
    target: Mapped[Optional[int]] = mapped_column(Integer)
    target_minvalue: Mapped[Optional[int]] = mapped_column(Integer)
    target_maxvalue: Mapped[Optional[int]] = mapped_column(Integer)
    target_text: Mapped[Optional[str]] = mapped_column(String(256))

    reached_by_games: Mapped[List["Game"]] = relationship(
        secondary=goal_reached, back_populates="achieved_goals"
    )