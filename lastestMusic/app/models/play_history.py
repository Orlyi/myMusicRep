from datetime import datetime

from sqlalchemy import Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PlayHistory(Base):
    __tablename__ = "play_history"

    play_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.user_id", ondelete="SET NULL"), index=True)
    song_id: Mapped[int | None] = mapped_column(ForeignKey("songs.song_id", ondelete="CASCADE"), index=True)
    artist_id: Mapped[int | None] = mapped_column(ForeignKey("artists.artist_id", ondelete="SET NULL"))
    playlist_id: Mapped[int | None] = mapped_column(ForeignKey("playlists.playlist_id", ondelete="SET NULL"), index=True)
    playlist_duration: Mapped[int] = mapped_column(default=0, comment="秒")
    is_completed: Mapped[bool] = mapped_column(Boolean, default=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), index=True)
