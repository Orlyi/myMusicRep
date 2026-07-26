from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PlaylistSaveSong(Base):
    __tablename__ = "playlist_save_song"

    playlist_id: Mapped[int] = mapped_column(
        ForeignKey("playlists.playlist_id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    song_id: Mapped[int] = mapped_column(
        ForeignKey("songs.song_id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())
