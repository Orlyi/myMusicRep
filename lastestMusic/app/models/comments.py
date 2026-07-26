from datetime import datetime

from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Comments(Base):
    __tablename__ = "comments"

    comment_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    song_id: Mapped[int | None] = mapped_column(ForeignKey("songs.song_id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.user_id", ondelete="SET NULL"), index=True)
    content: Mapped[str | None] = mapped_column(String(1000))
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("comments.comment_id", ondelete="SET NULL"), default=None,nullable=True
    )
    root_id: Mapped[int] = mapped_column(default=0)
    like_count: Mapped[int] = mapped_column(default=0)
    reply_count: Mapped[int] = mapped_column(default=0)
    current_status: Mapped[int] = mapped_column(default=1, index=True)
    is_top: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), index=True)
