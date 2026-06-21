from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Users, UserSaveSong, Songs, UserSavePlaylist, UserSaveAlbum, Playlists, Albums
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.favorite import FavoriteSongResponse, FavoritePlaylistResponse, FavoriteAlbumResponse

router = APIRouter()


@router.post("/songs/{song_id}", response_model=APIResponse)
async def save_song(
        song_id: int,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    song = await db.get(Songs,song_id)
    if not song:
        return APIResponse(code=404, message="Song not found")

    existing = await db.get(UserSaveSong, (current_user.user_id, song_id))
    if existing:
        return APIResponse(code=400, message="Already exists")

    db.add(UserSaveSong(user_id=current_user.user_id, song_id=song_id))
    await db.flush()
    return APIResponse(message="Song saved")




@router.post("/playlists/{playlist_id}", response_model=APIResponse)
async def save_playlist(
        playlist_id: int,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    playlist = await db.get(Playlists, playlist_id)
    if not playlist:
        return APIResponse(code=404, message="Playlist not found")

    existing = await db.get(UserSavePlaylist, (current_user.user_id, playlist_id))
    if existing:
        return APIResponse(code=400, message="Already exists")

    db.add(UserSavePlaylist(playlist_id=playlist_id, user_id=current_user.user_id))
    await db.flush()
    return APIResponse(message="Playlist saved")



@router.post("/albums/{album_id}", response_model=APIResponse)
async def save_album(
        album_id: int,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    album = await db.get(Albums, album_id)
    if not album:
        return APIResponse(code=404, message="Album not found")

    exiting = await db.get(UserSaveAlbum, (current_user.user_id, album_id))
    if exiting:
        return APIResponse(code=400, message="Album already exists")

    db.add(UserSaveAlbum(user_id=current_user.user_id, album_id=album_id))
    await db.flush()
    return APIResponse(message="Album saved")


@router.get("/list", response_model=APIResponse)
async def list_favorites(
        type: str = Query(..., pattern="^(song|album|playlist)$"),
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    if type == "song":
        base = (
            select(Songs.song_id, Songs.song_name, Songs.artist_id, Songs.album_id, Songs.picture_url, UserSaveSong.create_time)
            .join(UserSaveSong, Songs.song_id==UserSaveSong.song_id)
            .where(UserSaveSong.user_id == current_user.user_id)
        )
        count_base = (
            select(func.count())
            .select_from(UserSaveSong)
            .where(UserSaveSong.user_id == current_user.user_id)
        )
        total_result = await db.execute(count_base)
        total = total_result.scalar() or 0
        result = await db.execute(
            base
            .order_by(UserSaveSong.create_time.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = result.all()
        items = [
            FavoriteSongResponse(
                song_id=row.song_id,
                song_name=row.song_name,
                artist_id=row.artist_id,
                album_id=row.album_id,
                picture_url=row.picture_url,
                create_time=row.create_time
            ).model_dump() for row in rows
        ]

    elif type == "playlist":
        base = (
            select(Playlists, UserSavePlaylist.create_time)
            .join(UserSavePlaylist, Playlists.playlist_id==UserSavePlaylist.playlist_id)
            .where(UserSavePlaylist.user_id == current_user.user_id)
        )
        count_base = (
            select(func.count())
            .select_from(UserSavePlaylist)
            .where(UserSavePlaylist.user_id == current_user.user_id)
        )
        total_result = await db.execute(count_base)
        total = total_result.scalar() or 0
        result = await db.execute(
            base
            .order_by(Playlists.create_time.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = result.all()
        items = [
            FavoritePlaylistResponse(
                playlist_id=row.playlist_id,
                playlist_name=row.playlist_name,
                user_id=row.user_id,
                cover_url=row.cover_url,
                songs_count=row.songs_count,
                create_time=ct,
            ).model_dump() for row,ct in rows
        ]

    elif type == "album":
        base = (
            select(Albums, UserSaveAlbum.create_time)
            .join(UserSaveAlbum, Albums.album_id==UserSaveAlbum.album_id)
            .where(UserSaveAlbum.user_id == current_user.user_id)
        )
        count_base = (
            select(func.count())
            .select_from(UserSaveAlbum)
            .where(UserSaveAlbum.user_id == current_user.user_id)
        )
        total_result = await db.execute(count_base)
        total = total_result.scalar() or 0
        result = await db.execute(
            base
            .order_by(Albums.create_time.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = result.all()
        items = [
            FavoriteAlbumResponse(
                album_id=row.album_id,
                album_name=row.album_name,
                artist_id=row.artist_id,
                cover_url=row.cover_url,
                create_time=ct
            ).model_dump() for row,ct in rows
        ]

    return APIResponse(
        data=PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.delete("/songs/{song_id}", response_model=APIResponse)
async def unsave_song(
        song_id: int,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    saved = await db.get(UserSaveSong, (current_user.user_id, song_id))
    if not saved:
        return APIResponse(code=404, message="Not saved")

    await db.delete(saved)
    await db.flush()
    return APIResponse(message="Song unsaved")

@router.delete("/playlists/{playlist_id}", response_model=APIResponse)
async def unsave_playlist(
        playlist_id: int,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    playlist = await db.get(Playlists, playlist_id)
    if not playlist:
        return APIResponse(code=404, message="Playlist not found")

    saved = await db.get(UserSavePlaylist, (current_user.user_id, playlist_id))
    if not saved:
        return APIResponse(code=404, message="Playlist not saved")

    await db.delete(saved)
    await db.flush()
    return APIResponse(message="Playlist unsaved")

@router.delete("/albums/{album_id}", response_model=APIResponse)
async def unsave_album(
        album_id: int,
        current_user: Users = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    album = await db.get(Albums, album_id)
    if not album:
        return APIResponse(code=404, message="Album not found")

    saved = await db.get(UserSaveAlbum, (current_user.user_id, album_id))
    if not saved:
        return APIResponse(code=404, message="Album not saved")
    await db.delete(saved)
    await db.flush()
    return APIResponse(message="Album unsaved")