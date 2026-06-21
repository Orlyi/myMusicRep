from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Albums(Base):
    __tablename__ = "albums"

    album_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    platform_id: Mapped[str | None] = mapped_column(String(50))
    artist_id: Mapped[int | None] = mapped_column(ForeignKey("artists.artist_id", ondelete="CASCADE"), index=True)
    album_name: Mapped[str] = mapped_column(String(50), default="", index=True)
    songs_count: Mapped[int] = mapped_column(default=0)
    current_status: Mapped[int] = mapped_column(default=1, index=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())
