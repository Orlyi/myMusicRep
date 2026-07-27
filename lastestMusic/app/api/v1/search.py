from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models import Songs, Artists, Albums, Lyrics
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.song import SongBase
from app.schemas.artist import ArtistBase
from app.schemas.album import AlbumBase
from app.core.cache import cached

router = APIRouter()


@router.get("/song-name", response_model=APIResponse)
@cached("search:song", ttl=300)
async def search_song_name(
        keyword: str = Query(min_length=1, max_length=100),
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
        db: AsyncSession = Depends(get_db)):
    query = select(Songs).where(
        Songs.current_status == 1,
        Songs.song_name.like(f"%{keyword}%")
    )
    count_query = select(func.count()).select_from(Songs).where(
        Songs.current_status == 1,
        Songs.song_name.like(f"%{keyword}%")
    )
    total = (await db.execute(count_query)).scalar() or 0
    result = await db.execute(
        query.order_by(Songs.create_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return APIResponse(data=PaginatedResponse(
        items=[SongBase.model_validate(s).model_dump() for s in result.scalars().all()],
        total=total, page=page, page_size=page_size
    ))


@router.get("/artist-name", response_model=APIResponse)
@cached("search:artist", ttl=300)
async def search_artist_name(
        keyword: str = Query(min_length=1, max_length=20),
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
        db: AsyncSession = Depends(get_db)):
    query = select(Artists).where(
        Artists.current_status == 1,
        Artists.artist_name.like(f"%{keyword}%")
    )
    count_query = select(func.count()).select_from(Artists).where(
        Artists.current_status == 1,
        Artists.artist_name.like(f"%{keyword}%")
    )
    total = (await db.execute(count_query)).scalar() or 0
    result = await db.execute(
        query.order_by(Artists.create_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return APIResponse(data=PaginatedResponse(
        items=[ArtistBase.model_validate(a).model_dump() for a in result.scalars().all()],
        total=total, page=page, page_size=page_size
    ))


@router.get("/album-name", response_model=APIResponse)
@cached("search:album", ttl=300)
async def search_album_name(
        keyword: str = Query(min_length=1, max_length=20),
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
        db: AsyncSession = Depends(get_db)):
    query = select(Albums).where(
        Albums.current_status == 1,
        Albums.album_name.like(f"%{keyword}%")
    )
    count_query = select(func.count()).select_from(Albums).where(
        Albums.current_status == 1,
        Albums.album_name.like(f"%{keyword}%")
    )
    total = (await db.execute(count_query)).scalar() or 0
    result = await db.execute(
        query.order_by(Albums.create_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return APIResponse(data=PaginatedResponse(
        items=[AlbumBase.model_validate(a).model_dump() for a in result.scalars().all()],
        total=total, page=page, page_size=page_size
    ))


@router.get("/plain-lyric", response_model=APIResponse)
@cached("search:lyric", ttl=300)
async def search_plain_lyric(
        keyword: str = Query(min_length=1, max_length=100),
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
        db: AsyncSession = Depends(get_db)):
    query = select(Lyrics, Songs.song_name).outerjoin(
        Songs, Lyrics.song_id == Songs.song_id
    ).where(
        Lyrics.plain_lyric.like(f"%{keyword}%")
    )
    count_query = select(func.count()).select_from(Lyrics).where(
        Lyrics.plain_lyric.like(f"%{keyword}%")
    )
    total = (await db.execute(count_query)).scalar() or 0
    result = await db.execute(
        query.order_by(Lyrics.create_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    rows = result.all()
    return APIResponse(data=PaginatedResponse(
        items=[{
            "lyric_id": lyric.lyric_id,
            "song_id": lyric.song_id,
            "song_name": song_name or "",
            "plain_lyric": lyric.plain_lyric,
        } for lyric, song_name in rows],
        total=total, page=page, page_size=page_size
    ))
