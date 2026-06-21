from datetime import datetime
from pydantic import BaseModel, Field


class CommentCreateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=500)
    parent_id: int | None = None

class CommentResponse(BaseModel):
    comment_id: int
    song_id: int
    user_id: int | None = None
    user_name: str = ""
    content: str
    parent_id: int | None = None
    root_id: int
    like_count: int
    is_top: bool
    create_time: datetime

    model_config = {"from_attributes": True}