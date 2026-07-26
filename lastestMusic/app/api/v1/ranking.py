from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models import Songs, Artists, Albums
from app.schemas.common import APIResponse
from app.core.cache import cached


router = APIRouter()


@router.get("/top-songs", response_model=APIResponse)
@cached("rank:top-songs", ttl=300)
async def top_songs(
        limit: int = Query(default=20, ge=1, le=100),
        db: AsyncSession = Depends(get_db)):
    """播放最多的歌曲"""
    result = await db.execute(
        select(Songs, Artists.artist_name)
        .outerjoin(Artists, Songs.artist_id == Artists.artist_id)
        .where(Songs.current_status == 1)
        .order_by(Songs.play_count.desc(), Songs.download_count.desc())
        .limit(limit)
    )
    rows = result.all()
    return APIResponse(data={
        "items": [
            {
                "song_id": s.song_id,
                "song_name": s.song_name,
                "artist_id": s.artist_id,
                "artist_name": artist_name or "",
                "album_id": s.album_id,
                "picture_url": s.picture_url or "",
                "source": s.source or "",
                "platform_id": s.platform_id or "",
                "download_url": s.download_url or "",
                "play_count": s.play_count,
                "download_count": s.download_count,
            }
            for s, artist_name in rows
        ]
    })


@router.get("/top-albums", response_model=APIResponse)
@cached("rank:top-albums", ttl=300)
async def top_albums(
        limit: int = Query(default=20, ge=1, le=100),
        db: AsyncSession = Depends(get_db)):
    """歌曲最多的专辑"""
    result = await db.execute(
        select(Albums)
        .where(Albums.current_status == 1)
        .order_by(Albums.songs_count.desc())
        .limit(limit)
    )
    albums = result.scalars().all()
    return APIResponse(data={
        "items": [
            {
                "album_id": a.album_id,
                "album_name": a.album_name,
                "artist_id": a.artist_id,
                "cover_url": a.cover_url or "",
                "source": a.source or "",
                "songs_count": a.songs_count,
            }
            for a in albums
        ]
    })


@router.get("/top-artists", response_model=APIResponse)
@cached("rank:top-artists", ttl=300)
async def top_artists(
        limit: int = Query(default=20, ge=1, le=100),
        db: AsyncSession = Depends(get_db)):
    """歌曲最多的歌手"""
    result = await db.execute(
        select(Artists)
        .where(Artists.current_status == 1)
        .order_by(Artists.songs_count.desc(), Artists.fans_count.desc())
        .limit(limit)
    )
    artists = result.scalars().all()
    return APIResponse(data={
        "items": [
            {
                "artist_id": a.artist_id,
                "artist_name": a.artist_name,
                "avartar_url": a.avartar_url or "",
                "source": a.source or "",
                "songs_count": a.songs_count,
                "album_count": a.album_count,
                "fans_count": a.fans_count,
            }
            for a in artists
        ]
    })
