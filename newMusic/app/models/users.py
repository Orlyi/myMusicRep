from datetime import date, datetime
from sqlalchemy import String, Enum, Date, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from app.models.base import Base


class Users(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_name: Mapped[str] = mapped_column(String(20), nullable=False, default="默认用户")
    password: Mapped[str] = mapped_column(String(60), nullable=False)
    email: Mapped[str | None] = mapped_column(String(32), default="")
    avatar_url: Mapped[str | None] = mapped_column(String(256), default="")
    roles: Mapped[str] = mapped_column(String(20), default="user")
    current_status: Mapped[int] = mapped_column(default=1)
    create_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.current_timestamp())

    # 关系
    # noinspection PyTypeHints
    user_detail: Mapped[Optional["UserDetails"]] = relationship(back_populates="user", uselist=False)
