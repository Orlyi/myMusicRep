from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models import Albums, Songs
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.album import AlbumBase, AlbumDetail
from app.schemas.song import SongBase

router = APIRouter()


@router.get("", response_model=APIResponse)
async def list_albums(
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
        keyword: str = Query(default="", max_length=20),
        db: AsyncSession = Depends(get_db)):
    query = select(Albums).where(Albums.current_status == 1)
    count_query = select(func.count()).select_from(Albums).where(Albums.current_status == 1)
    if keyword :
        query = query.where(Albums.album_name.like(f"%{keyword}%"))
        count_query = count_query.where(Albums.album_name.like(f"%{keyword}%"))
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    result = await db.execute(query.offset((page - 1) * page_size).limit(page_size))
    albums = result.scalars().all()

    return APIResponse(
        data=PaginatedResponse(
            items=[AlbumBase.model_validate(a) for a in albums],
            total=total,
            page=page,
            page_size=page_size,
        )
    )

@router.get("/{album_id}", response_model=APIResponse)
async def get_album(album_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Albums).where(Albums.album_id == album_id))
    album = result.scalar_one_or_none()
    if not album:
        return APIResponse(code=404,message="Album not found")
    return APIResponse(data=AlbumDetail.model_validate(album))

@router.get("/{album_id}/songs", response_model=APIResponse)
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
        select(Songs)
        .where(Songs.album_id == album_id)
        .order_by(Songs.create_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    songs = result.scalars().all()

    return APIResponse(
        data=PaginatedResponse(
            items=[SongBase.model_validate(s) for s in songs],
            total=total,
            page=page,
            page_size=page_size,
        )
    )
