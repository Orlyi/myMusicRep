from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Users, Playlists, PlaylistSaveSong, Songs, Artists, Albums
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.playlist import (
    PlaylistCreateRequest,
    PlaylistUpdateRequest,
    PlaylistBase,
    SongInPlaylist, PlaylistDetailResponse,
)
from app.core.cache import cached, cache_delete

router = APIRouter()

DEFAULT_COVER = "/static/defaults/photo.jpg"


async def _resolve_cover(playlist, db: AsyncSession) -> str:
    """歌单封面：有 cover_url → 用它；没图但有歌 → 用最新歌曲的封面；没歌 → 默认图"""
    if playlist.cover_url:
        return playlist.cover_url
    # 查最新加入的歌曲的封面
    row = await db.execute(
        select(Songs.picture_url)
        .join(PlaylistSaveSong, Songs.song_id == PlaylistSaveSong.song_id)
        .where(PlaylistSaveSong.playlist_id == playlist.playlist_id)
        .order_by(PlaylistSaveSong.create_time.desc())
        .limit(1)
    )
    pic = row.scalar_one_or_none()
    return pic or DEFAULT_COVER

@router.post("", response_model=APIResponse)
async def create_playlist(
        body: PlaylistCreateRequest,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    playlist = Playlists(
        playlist_name = body.playlist_name,
        introduction = body.introduction,
        is_public = body.is_public,
        user_id = current_user.user_id)
    db.add(playlist)
    await db.flush()
    await cache_delete("pl:*")
    return APIResponse(message = "Created new playlist", data={"playlist_id": playlist.playlist_id})

@router.get("", response_model=APIResponse)
@cached("pl:list", ttl=120)
async def list_playlist(
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
        keyword: str = Query(default="", max_length=32),
        db: AsyncSession = Depends(get_db)):
    query = (select(Playlists, Users.user_name)
             .outerjoin(Users, Playlists.user_id == Users.user_id)
             .where(Playlists.current_status == 1, Playlists.is_public == True))
    count_query = select(func.count()).select_from(Playlists).where(Playlists.current_status == 1, Playlists.is_public == True)

    if keyword:
        query = query.where(Playlists.playlist_name.like(f"%{keyword}%"))
        count_query = count_query.where(Playlists.playlist_name.like(f"%{keyword}%"))

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    result = await db.execute(
        query.order_by(Playlists.create_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size))
    rows = result.all()

    items = [
        PlaylistBase(
            playlist_id = p.playlist_id,
            playlist_name = p.playlist_name,
            user_id = p.user_id,
            user_name = name or "",
            introduction = p.introduction or "",
            cover_url = await _resolve_cover(p, db),
            songs_count = p.songs_count,
            play_count = p.play_count,
            save_count = p.save_count,
            is_public = p.is_public,
            create_time = p.create_time
        ).model_dump()
        for p, name in rows
    ]

    return APIResponse(
        data=PaginatedResponse(
            items = items,
            total = total,
            page = page,
            page_size = page_size,
        )
    )


@router.get("/my", response_model=APIResponse)
@cached("pl:my", ttl=120)
async def my_playlists(
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    base_query = (select(Playlists)
                  .where(Playlists.user_id == current_user.user_id, Playlists.current_status == 1))
    count_query = (select(func.count())
                    .select_from(Playlists)
                    .where(Playlists.user_id == current_user.user_id, Playlists.current_status == 1))

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    result = await db.execute(
        base_query.order_by(Playlists.create_time.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    playlists = result.scalars().all()

    items = [
        PlaylistBase(
            playlist_id=p.playlist_id,
            playlist_name=p.playlist_name,
            user_id=p.user_id,
            user_name="",
            introduction=p.introduction or "",
            cover_url=await _resolve_cover(p, db),
            songs_count=p.songs_count,
            play_count=p.play_count,
            save_count=p.save_count,
            is_public=p.is_public,
            create_time=p.create_time
        ).model_dump()
        for p in playlists
    ]

    return APIResponse(
        data=PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )
    )

@router.get("/{playlist_id}", response_model=APIResponse)
@cached("pl:detail", ttl=120)
async def get_playlist(playlist_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Playlists, Users.user_name)
        .outerjoin(Users, Playlists.user_id == Users.user_id)
        .where(Playlists.playlist_id == playlist_id)
    )
    row = result.one_or_none()
    if not row:
        return APIResponse(code = 404, message = "Playlist not found")
    p, user_name = row

    songs_result = await db.execute(
        select(Songs, Artists.artist_name, Albums.album_name)
        .join(PlaylistSaveSong, Songs.song_id  == PlaylistSaveSong.song_id)
        .outerjoin(Artists, Songs.artist_id == Artists.artist_id)
        .outerjoin(Albums, Songs.album_id == Albums.album_id)
        .where(PlaylistSaveSong.playlist_id == playlist_id))
    srows = songs_result.all()

    # 实时歌曲数
    count_result = await db.execute(
        select(func.count())
        .select_from(PlaylistSaveSong)
        .where(PlaylistSaveSong.playlist_id == playlist_id)
    )
    real_songs_count = count_result.scalar() or 0

    return APIResponse(
        data=PlaylistDetailResponse(
            playlist=PlaylistBase(
                playlist_id=p.playlist_id,
                playlist_name=p.playlist_name,
                user_id=p.user_id,
                user_name=user_name or "",
                introduction=p.introduction,
                cover_url=await _resolve_cover(p, db),
                songs_count=real_songs_count,
                play_count=p.play_count,
                save_count=p.save_count,
                is_public=p.is_public,
                create_time=p.create_time
            ),
            songs=[{
                "song_id": s.song_id,
                "song_name": s.song_name,
                "artist_id": s.artist_id,
                "artist_name": artist_name or "",
                "album_id": s.album_id,
                "album_name": album_name or "",
                "picture_url": s.picture_url or "",
                "source": s.source or "",
                "platform_id": s.platform_id or "",
                "download_url": s.download_url or "",
            } for s, artist_name, album_name in srows]
        ).model_dump()
    )

@router.put("/{playlist_id}", response_model=APIResponse)
async def update_playlist(
        playlist_id: int,
        body: PlaylistUpdateRequest,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Playlists)
        .where(Playlists.playlist_id == playlist_id)
    )
    playlist = result.scalar_one_or_none()
    if not playlist:
        return APIResponse(code = 404, message = "Playlist not found")
    if playlist.user_id != current_user.user_id:
        return APIResponse(code = 403, message = "Cannot update playlist")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(playlist, field, value)
    await db.flush()
    await cache_delete("pl:*")
    return APIResponse(message = "Updated playlist")

@router.delete("/{playlist_id}", response_model=APIResponse)
async def delete_playlist(
        playlist_id: int,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Playlists)
        .where(Playlists.playlist_id == playlist_id)
    )
    playlist = result.scalar_one_or_none()
    if not playlist:
        return APIResponse(code = 404, message = "Playlist not found")
    if playlist.user_id != current_user.user_id:
        return APIResponse(code = 403, message = "Cannot delete playlist")

    playlist.current_status = 0
    await db.flush()
    await cache_delete("pl:*")
    return APIResponse(message = "Deleted playlist")


@router.post("/{playlist_id}/songs/{song_id}", response_model=APIResponse)
async def add_song_to_playlist(
        playlist_id: int,
        song_id: int,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    playlist = await db.get(Playlists, playlist_id)
    if not playlist:
        return APIResponse(code=404, message="Playlist not found")
    if playlist.user_id != current_user.user_id:
        return APIResponse(code=403, message="Not your playlist")

    song = await db.get(Songs, song_id)
    if not song:
        return APIResponse(code=404, message="Song not found")

    existing = await db.get(PlaylistSaveSong, (playlist_id, song_id))
    if existing:
        return APIResponse(code=400, message="Song already in playlist")

    db.add(PlaylistSaveSong(playlist_id=playlist_id, song_id=song_id))
    playlist.songs_count += 1
    await db.flush()
    await cache_delete("pl:*")
    return APIResponse(message="Song added to playlist")


@router.delete("/{playlist_id}/songs/{song_id}", response_model=APIResponse)
async def remove_song_from_playlist(
        playlist_id: int,
        song_id: int,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    playlist = await db.get(Playlists, playlist_id)
    if not playlist:
        return APIResponse(code=404, message="Playlist not found")
    if playlist.user_id != current_user.user_id:
        return APIResponse(code=403, message="Not your playlist")

    entry = await db.get(PlaylistSaveSong, (playlist_id, song_id))
    if not entry:
        return APIResponse(code=404, message="Song not in playlist")

    await db.delete(entry)
    if playlist.songs_count > 0:
        playlist.songs_count -= 1
    await db.flush()
    await cache_delete("pl:*")
    return APIResponse(message="Song removed from playlist")

