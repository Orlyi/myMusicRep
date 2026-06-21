from datetime import datetime
from pydantic import BaseModel,Field


class ArtistBase(BaseModel):
    artist_id: int
    artist_name: str
    songs_count:int
    album_count:int
    fans_count:int

    model_config = {"from_attributes": True}

class ArtistDetail(ArtistBase):
    introduction: str | None = None
    create_time:datetime

    model_config = {"from_attributes": True}

class ArtistSearchRequest(BaseModel):
    keyword: str = Field(min_length=1, max_length=20)
    page: int = Field(default=1,ge=1)
    page_size: int = Field(default=20,ge=1,le=100)