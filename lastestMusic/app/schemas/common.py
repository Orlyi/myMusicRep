from datetime import datetime
from typing import Any

from pydantic import BaseModel


# ── 通用响应模型 ──

class APIResponse(BaseModel):
    """标准 API 响应格式"""
    code: int = 0
    message: str = "success"
    data: Any = None


class PaginatedResponse(BaseModel):
    """分页响应"""
    items: list
    total: int
    page: int
    page_size: int
