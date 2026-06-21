from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ArtistSingSong(Base):
    __tablename__ = "artist_sing_song"

    artist_id: Mapped[int] = mapped_column(
        ForeignKey("artists.artist_id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    song_id: Mapped[int] = mapped_column(
        ForeignKey("songs.song_id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())
