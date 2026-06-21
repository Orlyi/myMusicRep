from datetime import date, datetime

from sqlalchemy import String, Enum, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class UserDetails(Base):
    __tablename__ = "user_details"

    detail_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), index=True)
    nick_name: Mapped[str | None] = mapped_column(String(20), default="")
    gender: Mapped[str | None] = mapped_column(Enum("男", "女", "其他"), default="其他")
    birthdate: Mapped[date | None] = mapped_column(Date, default="2026-05-20")
    phone_number: Mapped[str | None] = mapped_column(String(20), default="")
    real_name: Mapped[str | None] = mapped_column(String(20), default="")
    city: Mapped[str | None] = mapped_column(String(20), default="", index=True)
    fans_count: Mapped[int] = mapped_column(default=0)
    followed_count: Mapped[int] = mapped_column(default=0)
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())
    update_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())

    # 关系
    user: Mapped["Users"] = relationship(back_populates="user_detail")
