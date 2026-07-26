from datetime import datetime
from pydantic import BaseModel

class FavoriteSongResponse(BaseModel):
    song_id: int
    song_name: str
    artist_id: int | None = None
    artist_name: str | None = None
    album_id: int | None  = None
    album_name: str | None = None
    picture_url: str | None  = None
    source: str | None = None
    platform_id: str | None = None
    download_url: str | None = None
    is_love: bool = True
    create_time: datetime

    model_config = {"from_attributes": True}

class FavoritePlaylistResponse(BaseModel):
    playlist_id: int
    playlist_name: str
    user_id: int | None = None
    cover_url: str | None = None
    songs_count: int
    is_love: bool = True
    create_time: datetime

    model_config = {"from_attributes": True}

class FavoriteAlbumResponse(BaseModel):
    album_id: int
    album_name: str
    artist_id: int | None = None
    cover_url: str | None = None
    is_love: bool = True
    create_time: datetime

    model_config = {"from_attributes": True}

