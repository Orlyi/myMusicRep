from datetime import datetime
from typing import List

from sqlalchemy import String, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Artists(Base):
    __tablename__ = "artists"

    artist_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    platform_id: Mapped[str | None] = mapped_column(String(50))
    artist_name: Mapped[str] = mapped_column(String(50), default="群星", index=True)
    songs_count: Mapped[int] = mapped_column(default=0)
    album_count: Mapped[int] = mapped_column(default=0)
    fans_count: Mapped[int] = mapped_column(default=0)
    introduction: Mapped[str | None] = mapped_column(Text, default="")
    current_status: Mapped[int] = mapped_column(default=1, index=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())
