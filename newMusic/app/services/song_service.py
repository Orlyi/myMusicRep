from sqlalchemy.ext.asyncio import AsyncSession
from app.models import UserSaveSong


async def is_song_loved(user_id: int, song_id: int, db: AsyncSession) -> bool:
    saved = await db.get(UserSaveSong, (user_id, song_id))
    return saved is not None

