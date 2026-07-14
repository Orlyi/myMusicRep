from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user, get_current_user_optional
from app.core.redis_client import get_redis
from app.core.redis_keys import RECENT_LISTEN_PREFIX, RECENT_LISTEN_MAX, RECENT_LISTEN_TTL
from app.models import Songs, PlayHistory, Users, Artists, UserSaveSong
from app.schemas.common import APIResponse, PaginatedResponse
from app.services.song_service import is_song_loved
from app.schemas.song import SongBase, SongDetail

router = APIRouter()

@router.post("/{song_id}/play", response_model=APIResponse)
async def play_song(
        song_id: int,
        is_completed: bool = True,
        playlist_duration: int = 0,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Songs)
        .where(Songs.song_id == song_id)
    )
    song = result.scalar_one_or_none()
    if not song:
        return APIResponse(code=404, message="Song not found")

    song.play_count += 1
    await db.flush()

    return APIResponse(data = {"play_count": song.play_count})


@router.post("/{song_id}/listen", response_model=APIResponse)
async def record_listen(
        song_id: int,
        current_user: Users = Depends(get_current_user)):
    """记录一次播放到 Redis 最近播放（仅 Redis，不写 MySQL）"""
    try:
        redis = await get_redis()
        key = f"{RECENT_LISTEN_PREFIX}{current_user.user_id}"
        await redis.lrem(key, 0, song_id)
        await redis.lpush(key, song_id)
        await redis.ltrim(key, 0, RECENT_LISTEN_MAX - 1)
        await redis.expire(key, RECENT_LISTEN_TTL)
    except Exception as e:
        print(f"Redis 最近播放写入失败: {e}")
        return APIResponse(code=500, message="记录播放失败")
    return APIResponse()


@router.post("/{song_id}/download", response_model=APIResponse)
async def download_song(
        song_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: Users | None = Depends(get_current_user_optional)):
    result = await db.execute(
        select(Songs, Artists.artist_name)
        .outerjoin(Artists, Songs.artist_id == Artists.artist_id)
        .where(Songs.song_id == song_id)
    )
    row = result.one_or_none()
    if not row:
        return APIResponse(code=404, message="Song not found")

    song, artist_name = row
    song.download_count += 1

    is_love = False
    if current_user:
        is_love = await is_song_loved(current_user.user_id, song_id, db)

    await db.flush()
    return APIResponse(data={
        "song_id": song.song_id,
        "song_name": song.song_name,
        "picture_url": song.picture_url,
        "download_url": song.download_url,
        "artist_name": artist_name or "",
        "is_love": is_love,
    })

@router.get("", response_model=APIResponse)
async def list_songs(
        page: int = Query(default = 1, ge = 1),
        page_size: int = Query(default = 20, ge = 1, le=100),
        keyword: str = Query(default = "", max_length=100),
        db: AsyncSession = Depends(get_db),
        current_user: Users | None = Depends(get_current_user_optional)):
    query = (
        select(Songs, Artists.artist_name)
        .outerjoin(Artists, Songs.artist_id == Artists.artist_id)
        .where(Songs.current_status == 1)
    )
    count_query = (select(func.count())
                   .select_from(Songs)
                   .where(Songs.current_status == 1))

    if keyword:
        query = query.where(Songs.song_name.like(f"%{keyword}%"))
        count_query = count_query.where(Songs.song_name.like(f"%{keyword}%"))

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    result = await db.execute(
        query
        .order_by(Songs.create_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    rows = result.all()

    # 已登录 → 批量查收藏状态
    loved_ids: set[int] = set()
    if current_user and rows:
        song_ids = [s.song_id for s, _ in rows]
        saved_result = await db.execute(
            select(UserSaveSong.song_id)
            .where(UserSaveSong.user_id == current_user.user_id,
                   UserSaveSong.song_id.in_(song_ids))
        )
        loved_ids = {row[0] for row in saved_result}

    return APIResponse(
        data = PaginatedResponse(
            items = [
                {
                    "song_id": s.song_id,
                    "song_name": s.song_name,
                    "artist_id": s.artist_id,
                    "artist_name": artist_name or "",
                    "album_id": s.album_id,
                    "picture_url": s.picture_url,
                    "source": s.source,
                    "download_url": s.download_url,
                    "download_count": s.download_count,
                    "play_count": s.play_count,
                    "is_love": s.song_id in loved_ids,
                }
                for s, artist_name in rows
            ],
            total = total,
            page = page,
            page_size = page_size,
        )
    )


@router.get("/{song_id}/play-count", response_model=APIResponse)
async def play_count(
        song_id: int,
        db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Songs.play_count)
        .where(Songs.song_id == song_id)
    )
    count = result.scalar_one_or_none()
    if not count:
        return APIResponse(code=404, message="Song not found")

    return APIResponse(data={"play_count": count})

@router.get("/{song_id}/download-count", response_model=APIResponse)
async def download_count(
        song_id: int,
        db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Songs.download_count)
        .where(Songs.song_id == song_id)
    )
    count = result.scalar_one_or_none()
    if not count:
        return APIResponse(code=404, message="Song not found")

    return APIResponse(data={"download_count": count})







@router.get("/{song_id}", response_model=APIResponse)
async def get_song(
        song_id: int,
        db: AsyncSession = Depends(get_db)):
    query = select(Songs).where(Songs.song_id == song_id)

    result = await db.execute(query)
    song = result.scalar_one_or_none()
    if not song:
        return APIResponse(code=404, message="Song not found")

    return APIResponse(
        data=SongDetail.model_validate(song).model_dump())