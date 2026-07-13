from datetime import datetime
from pydantic import BaseModel, Field


class SongBase(BaseModel):
    song_id: int
    song_name: str
    artist_id: int | None = None
    artist_name: str | None = None
    album_id: int | None = None
    picture_url: str | None = None
    source: str | None = None
    download_url: str | None = None
    download_count: int
    play_count: int
    is_love: bool = False

    model_config = {"from_attributes": True}


class SongDetail(SongBase):
    introduction: str | None = None
    lyric_id: int | None = None
    create_time: datetime


class SongSearchRequest(BaseModel):
    keyword: str = Field(min_length=1, max_length=100)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
