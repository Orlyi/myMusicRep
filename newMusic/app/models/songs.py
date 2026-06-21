
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base



class Songs(Base):
    __tablename__ = "songs"

    song_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    platform_id: Mapped[str | None] = mapped_column(String(200))
    song_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    artist_id: Mapped[int | None] = mapped_column(Integer, index=True)
    album_id: Mapped[int | None] = mapped_column(Integer)
    lyric_id: Mapped[str | None] = mapped_column(String(200))
    picture_id: Mapped[str | None] = mapped_column(String(200))
    picture_url: Mapped[str | None] = mapped_column(String(200))
    sources: Mapped[str | None] = mapped_column(String(50))
    url_id: Mapped[str | None] = mapped_column(String(200))
    introduction: Mapped[str | None] = mapped_column(Text, default="")
    download_url: Mapped[str | None] = mapped_column(String(500))
    download_count: Mapped[int] = mapped_column(default=0)
    play_count: Mapped[int] = mapped_column(default=0)
    current_status: Mapped[int] = mapped_column(default=1, index=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())

    # noinspection PyTypeHints
    lyric: Mapped[Optional["Lyrics"]] = relationship(back_populates="song", uselist=False)
