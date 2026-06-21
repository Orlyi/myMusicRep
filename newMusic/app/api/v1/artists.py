from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models import Artists, ArtistSingSong, Songs, Albums
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.artist import ArtistBase, ArtistDetail
from app.schemas.song import SongBase
from app.schemas.album import AlbumBase

router = APIRouter()

@router.get("",response_model=APIResponse)
async def list_artists(
        page: int = Query(default=1,ge=1),
        page_size: int = Query(default=20,ge=1, le=100),
        keyword: str = Query(default="",max_length=20),
        db: AsyncSession = Depends(get_db)
):
    query = select(Artists).where(Artists.current_status == 1)

    if keyword:
        query = query.where(Artists.artist_name.like(f"%{keyword}%"))

    count_query = select(func.count()).select_from(Artists).where(Artists.current_status == 1)
    if keyword:
        count_query = count_query.where(Artists.artist_name.like(f"%{keyword}%"))

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    result = await db.execute(query.offset((page - 1)* page_size).limit(page_size))
    artists = result.scalars().all()

    return APIResponse(
        data=PaginatedResponse(
            items=[ArtistBase.model_validate(a) for a in artists],
            total=total,
            page=page,
            page_size=page_size
        )
    )


@router.get("/{artist_id}/songs", response_model=APIResponse)
async def artist_songs(
        artist_id: int,
        page: int = Query(default=1,ge=1),
        page_size: int = Query(default=20,ge=1, le=100),
        db: AsyncSession = Depends(get_db)):
    artist = await db.get(Artists, artist_id)
    if not artist:
        return APIResponse(code=404, message="Artist not found")

    total_result = await db.execute(
        select(func.count())
        .select_from(ArtistSingSong)
        .where(ArtistSingSong.artist_id == artist_id)
    )
    total = total_result.scalar() or 0

    result = await db.execute(
        select(Songs)
        .join(ArtistSingSong, Songs.song_id == ArtistSingSong.song_id)
        .where(ArtistSingSong.artist_id == artist_id)
        .order_by(Songs.create_time.desc())
        .offset((page - 1)* page_size)
        .limit(page_size)
    )
    songs = result.scalars().all()

    return APIResponse(
        data=PaginatedResponse(
            items=[SongBase.model_validate(s) for s in songs],
            total=total,
            page=page,
            page_size=page_size
        )
    )

@router.get("/{artist_id}/albums", response_model=APIResponse)
async def artist_albums(
        artist_id: int,
        page: int = Query(default=1,ge=1),
        page_size: int = Query(default=20,ge=1, le=100),
        db: AsyncSession = Depends(get_db)):
    artist = await db.get(Artists, artist_id)
    if not artist:
        return APIResponse(code=404, message="Artist not found")

    total_result = await db.execute(
        select(func.count())
        .select_from(Albums)
        .where(Albums.artist_id == artist_id)
    )
    total = total_result.scalar() or 0

    result = await db.execute(
        select(Albums)
        .where(Albums.artist_id == artist_id)
        .order_by(Albums.create_time.desc())
        .offset((page - 1)* page_size)
        .limit(page_size)
    )
    albums = result.scalars().all()

    return APIResponse(
        data=PaginatedResponse(
            items=[AlbumBase.model_validate(a) for a in albums],
            total=total,
            page=page,
            page_size=page_size
        )
    )

@router.get("/{artist_id}",response_model=APIResponse)
async def get_artist(artist_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Artists).where(Artists.artist_id == artist_id))
    artist = result.scalar_one_or_none()
    if not artist:
        return APIResponse(code=404, message="Artist not found")
    return APIResponse(data=ArtistDetail.model_validate(artist))