from datetime import datetime

from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Playlists(Base):
    __tablename__ = "playlists"

    playlist_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    playlist_name: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.user_id", ondelete="SET NULL"), index=True)
    introduction: Mapped[str | None] = mapped_column(String(200), default="")
    cover_url: Mapped[str | None] = mapped_column(String(500), default="")
    songs_count: Mapped[int] = mapped_column(default=0)
    play_count: Mapped[int] = mapped_column(default=0)
    save_count: Mapped[int] = mapped_column(default=0)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    current_status: Mapped[int] = mapped_column(default=1, index=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())
