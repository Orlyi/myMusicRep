from datetime import datetime

from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Messages(Base):
    __tablename__ = "messages"

    message_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sender_id: Mapped[int | None] = mapped_column(ForeignKey("users.user_id", ondelete="SET NULL"), index=True)
    receiver_id: Mapped[int | None] = mapped_column(ForeignKey("users.user_id", ondelete="SET NULL"), index=True)
    content: Mapped[str] = mapped_column(String(1000), nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deleted_sender: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deleted_receiver: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp(), index=True)
    read_time: Mapped[datetime | None] = mapped_column(DateTime)
    current_status: Mapped[int] = mapped_column(default=1, index=True)
