from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Lyrics(Base):
    __tablename__ = "lyrics"

    lyric_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    song_id: Mapped[int] = mapped_column(ForeignKey("songs.song_id", ondelete="CASCADE"), index=True)
    platform_id: Mapped[str | None] = mapped_column(String(200))
    lyric_text: Mapped[str | None] = mapped_column(LONGTEXT)
    plain_lyric: Mapped[str | None] = mapped_column(Text, comment="纯文本")
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())

    # 关系
    song: Mapped["Songs"] = relationship(back_populates="lyric")
