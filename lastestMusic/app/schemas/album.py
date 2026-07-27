from datetime import datetime
from pydantic import BaseModel, Field

class AlbumBase(BaseModel):
    album_id: int
    album_name: str
    artist_id: int | None = None
    cover_url: str | None = None
    source: str | None = None
    songs_count: int

    model_config = {"from_attributes": True}

class AlbumDetail(AlbumBase):
    platform_id:str | None
    current_status: int
    create_time: datetime

class AlbumSearchRequest(BaseModel):
    keyword: str = Field(min_length=1, max_length=20)
    page: int = Field(default=1,ge=1)
    page_size: int = Field(default=20,ge=1,le=100)