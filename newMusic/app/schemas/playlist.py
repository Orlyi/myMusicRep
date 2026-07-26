from datetime import datetime
from pydantic import BaseModel, Field


class PlaylistCreateRequest(BaseModel):
    playlist_name: str = Field(min_length=1, max_length=32)
    introduction: str = ""
    is_public: bool = Field(default=True)

class PlaylistUpdateRequest(BaseModel):
    playlist_name: str | None = None
    introduction: str | None = None
    is_public: bool | None = None

class PlaylistBase(BaseModel):
    playlist_id: int
    playlist_name: str
    user_id: int | None = None
    user_name: str = ""
    introduction: str = ""
    cover_url: str = ""
    songs_count: int
    play_count: int
    save_count: int
    is_public: bool
    create_time: datetime

    model_config = {"from_attributes": True}

class SongInPlaylist(BaseModel):
    song_id: int
    song_name: str
    artist_id: int | None = None
    artist_name: str = ""
    album_id: int | None = None
    album_name: str = ""
    picture_url: str | None = None
    source: str | None = None
    platform_id: str | None = None
    download_url: str | None = None

    model_config = {"from_attributes": True}

class PlaylistDetailResponse(BaseModel):
    playlist:PlaylistBase
    songs: list[SongInPlaylist]