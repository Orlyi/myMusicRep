from datetime import datetime
from pydantic import BaseModel



class LyricResponse(BaseModel):
    lyric_id: int
    song_id: int
    lyric_text: str | None = None
    plain_lyric: str | None = None
    create_time: datetime

    model_config = {"from_attributes": True}
