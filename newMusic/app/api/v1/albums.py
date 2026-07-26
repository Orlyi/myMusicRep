from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models import Albums, Songs, Artists
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.album import AlbumBase, AlbumDetail
from app.schemas.song import SongBase
from app.core.cache import cached

router = APIRouter()


@router.get("", response_model=APIResponse)
@cached("alb:list", ttl=300)
async def list_albums(
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
        keyword: str = Query(default="", max_length=20),
        db: AsyncSession = Depends(get_db)):
    query = select(Albums, Artists.artist_name).outerjoin(Artists, Albums.artist_id == Artists.artist_id).where(Albums.current_status == 1)
    count_query = select(func.count()).select_from(Albums).where(Albums.current_status == 1)
    if keyword :
        query = query.where(Albums.album_name.like(f"%{keyword}%"))
        count_query = count_query.where(Albums.album_name.like(f"%{keyword}%"))
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    result = await db.execute(query.order_by(Albums.create_time.desc()).offset((page - 1) * page_size).limit(page_size))
    rows = result.all()

    return APIResponse(
        data=PaginatedResponse(
            items=[
                {
                    "album_id": a.album_id,
                    "album_name": a.album_name,
                    "artist_id": a.artist_id,
                    "artist_name": artist_name or "",
                    "cover_url": a.cover_url,
                    "source": a.source,
                    "songs_count": a.songs_count,
                }
                for a, artist_name in rows
            ],
            total=total,
            page=page,
            page_size=page_size,
        )
    )

@router.get("/{album_id}", response_model=APIResponse)
@cached("alb:detail", ttl=300)
async def get_album(album_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Albums, Artists.artist_name)
        .outerjoin(Artists, Albums.artist_id == Artists.artist_id)
        .where(Albums.album_id == album_id)
    )
    row = result.one_or_none()
    if not row:
        return APIResponse(code=404, message="Album not found")

    album, artist_name = row
    data = AlbumDetail.model_validate(album).model_dump()
    data["artist_name"] = artist_name or ""
    return APIResponse(data=data)

@router.get("/{album_id}/songs", response_model=APIResponse)
@cached("alb:songs", ttl=300)
async def get_songs(
        album_id: int,
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
        db: AsyncSession = Depends(get_db)):
    album = (await db.execute(select(Albums).where(Albums.album_id == album_id))).scalar_one_or_none()
    if not album:
        return APIResponse(code=404,message="Album not found")

    total_result = await db.execute(
        select(func.count())
        .select_from(Songs)
        .where(Songs.album_id == album_id)
    )
    total = total_result.scalar() or 0

    result = await db.execute(
        select(Songs, Artists.artist_name)
        .outerjoin(Artists, Songs.artist_id == Artists.artist_id)
        .where(Songs.album_id == album_id)
        .order_by(Songs.create_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    rows = result.all()

    return APIResponse(
        data=PaginatedResponse(
            items=[
                {
                    "song_id": s.song_id,
                    "platform_id": s.platform_id,
                    "song_name": s.song_name,
                    "artist_id": s.artist_id,
                    "artist_name": artist_name or "",
                    "album_id": s.album_id,
                    "picture_url": s.picture_url,
                    "source": s.source,
                    "download_url": s.download_url,
                    "download_count": s.download_count,
                    "play_count": s.play_count,
                    "is_love": False,
                }
                for s, artist_name in rows
            ],
            total=total,
            page=page,
            page_size=page_size,
        )
    )
