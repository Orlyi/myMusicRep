from datetime import datetime

from sqlalchemy import String, ForeignKey, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SearchHistory(Base):
    __tablename__ = "search_history"

    search_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), index=True)
    keyword: Mapped[str | None] = mapped_column(String(32), index=True)
    search_type: Mapped[str | None] = mapped_column(
        Enum("artist", "song", "lyric", "album", "playlist", "user", "other"),
        default="song",
        index=True,
    )
