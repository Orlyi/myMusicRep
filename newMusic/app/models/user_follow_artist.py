from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class UserFollowArtist(Base):
    __tablename__ = "user_follow_artist"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    artist_id: Mapped[int] = mapped_column(
        ForeignKey("artists.artist_id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())
