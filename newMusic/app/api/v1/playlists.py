from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Users, Playlists, PlaylistSaveSong, Songs
from app.schemas.common import APIResponse, PaginatedResponse
from app.schemas.playlist import (
    PlaylistCreateRequest,
    PlaylistUpdateRequest,
    PlaylistBase,
    SongInPlaylist, PlaylistDetailResponse,
)

router = APIRouter()

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
    return APIResponse(message = "Created new playlist", data={"playlist_id": playlist.playlist_id})

@router.get("", response_model=APIResponse)
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
            cover_url = p.cover_url or "",
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
            cover_url=p.cover_url or "",
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
        select(Songs)
        .join(PlaylistSaveSong, Songs.song_id  == PlaylistSaveSong.song_id)
        .where(PlaylistSaveSong.playlist_id == playlist_id))
    songs = songs_result.scalars().all()

    return APIResponse(
        data=PlaylistDetailResponse(
            playlist=PlaylistBase(
                playlist_id=p.playlist_id,
                playlist_name=p.playlist_name,
                user_id=p.user_id,
                user_name=user_name or "",
                introduction=p.introduction,
                cover_url=p.cover_url,
                songs_count=p.songs_count,
                play_count=p.play_count,
                save_count=p.save_count,
                is_public=p.is_public,
                create_time=p.create_time
            ),
            songs=[SongInPlaylist.model_validate(s) for s in songs]
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
    return APIResponse(message = "Deleted playlist")

