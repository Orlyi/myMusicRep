from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models import Lyrics
from app.schemas.common import APIResponse
from app.schemas.lyric import LyricResponse
from app.core.cache import cached

router = APIRouter()

@router.get("/{song_id}", response_model=APIResponse)
@cached("lyric:detail", ttl=600)
async def get_lyrics(song_id: int, db: AsyncSession = Depends(get_db)) -> APIResponse:
    result = await db.execute(select(Lyrics).where(Lyrics.song_id == song_id))
    lyrics = result.scalar_one_or_none()
    if not lyrics:
        return APIResponse(code=404, message="No lyrics found")
    return APIResponse(data=LyricResponse.model_validate(lyrics))