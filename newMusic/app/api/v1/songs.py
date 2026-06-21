from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Songs, PlayHistory, Users
from app.schemas.common import APIResponse, PaginatedResponse
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
    db.add(PlayHistory(
        user_id= current_user.user_id,
        song_id = song_id,
        artist_id = song.artist_id,
        is_completed = is_completed,
        playlist_duration = playlist_duration,
    ))
    await db.flush()
    return APIResponse(data = {"play_count": song.play_count})

@router.post("/{song_id}/download", response_model=APIResponse)
async def download_song(
        song_id: int,
        db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Songs)
        .where(Songs.song_id == song_id)
    )
    song = result.scalar_one_or_none()
    if not song:
        return APIResponse(code=404, message="Song not found")

    song.download_count += 1
    await db.flush()
    return APIResponse(data={"download_url": song.download_url})

@router.get("", response_model=APIResponse)
async def list_songs(
        page: int = Query(default = 1, ge = 1),
        page_size: int = Query(default = 20, ge = 1, le=100),
        keyword: str = Query(default = "", max_length=100),
        db: AsyncSession = Depends(get_db)):
    query = select(Songs).where(Songs.current_status == 1)
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
    songs = result.scalars().all()

    return APIResponse(
        data = PaginatedResponse(
            items = [
                SongBase.model_validate(s).model_dump() for s in songs
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