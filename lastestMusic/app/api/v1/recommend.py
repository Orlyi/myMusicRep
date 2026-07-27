from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user_optional
from app.core.redis_client import get_redis
from app.core.redis_keys import RECENT_LISTEN_PREFIX
from app.models import Users, Songs, Artists, ArtistSingSong, Playlists, PlaylistSaveSong
from app.schemas.common import APIResponse
from app.core.cache import cached

router = APIRouter()


@router.get("/recommend", response_model=APIResponse)
@cached("rec:song", ttl=300)
async def recommend(
        limit: int = Query(default=10, ge=1, le=30),
        db: AsyncSession = Depends(get_db),
        current_user: Users | None = Depends(get_current_user_optional)):
    """猜你喜欢：从用户最近的播放历史中提取歌手，随机选些歌手，取他们的歌曲"""

    listened_artist_ids: set[int] = set()

    if current_user:
        # 从 Redis 最近播放中提取歌手 ID
        try:
            redis = await get_redis()
            key = f"{RECENT_LISTEN_PREFIX}{current_user.user_id}"
            song_ids = await redis.lrange(key, 0, 49)
            if song_ids:
                sids = [int(s) for s in song_ids]
                result = await db.execute(
                    select(Songs.artist_id)
                    .where(Songs.song_id.in_(sids), Songs.artist_id.isnot(None))
                )
                for (aid,) in result.all():
                    listened_artist_ids.add(aid)
        except Exception:
            pass

    # 没登录或没播放历史 → 从所有歌手取播放最多的一些
    if not listened_artist_ids:
        result = await db.execute(
            select(Artists.artist_id)
            .where(Artists.current_status == 1, Artists.songs_count > 0)
            .order_by(func.rand())
            .limit(limit)
        )
        listened_artist_ids = {row[0] for row in result.all()}

    if not listened_artist_ids:
        return APIResponse(data={"items": []})

    # 随机选最多 10 个歌手
    import random
    chosen = random.sample(list(listened_artist_ids), min(len(listened_artist_ids), 10))

    # 取这些歌手的歌曲（每个歌手最多 3 首），混合后随机排
    all_songs = []
    for aid in chosen:
        result = await db.execute(
            select(Songs, Artists.artist_name)
            .outerjoin(Artists, Songs.artist_id == Artists.artist_id)
            .where(
                Songs.artist_id == aid,
                Songs.current_status == 1,
            )
            .order_by(func.rand())
            .limit(3)
        )
        for s, an in result.all():
            all_songs.append({
                "song_id": s.song_id,
                "song_name": s.song_name,
                "artist_id": s.artist_id,
                "artist_name": an or "",
                "album_id": s.album_id,
                "picture_url": s.picture_url or "",
                "source": s.source or "",
                "platform_id": s.platform_id or "",
                "download_url": s.download_url or "",
                "play_count": s.play_count,
            })

    random.shuffle(all_songs)

    return APIResponse(data={"items": all_songs[:limit]})


@router.get("/playlists", response_model=APIResponse)
@cached("rec:playlists", ttl=300)
async def recommend_playlists(
        limit: int = Query(default=6, ge=1, le=20),
        db: AsyncSession = Depends(get_db)):
    """推荐歌单：公开、有歌曲的歌单，随机排序"""
    result = await db.execute(
        select(Playlists, Users.user_name)
        .outerjoin(Users, Playlists.user_id == Users.user_id)
        .where(
            Playlists.current_status == 1,
            Playlists.is_public == True,
            Playlists.songs_count > 0,
        )
        .order_by(func.rand())
        .limit(limit)
    )
    rows = result.all()
    items = []
    for p, name in rows:
        cover_url = p.cover_url or ""
        # 没封面 → 用最新歌曲的封面
        if not cover_url:
            song_row = await db.execute(
                select(Songs.picture_url)
                .join(PlaylistSaveSong, Songs.song_id == PlaylistSaveSong.song_id)
                .where(PlaylistSaveSong.playlist_id == p.playlist_id)
                .order_by(PlaylistSaveSong.create_time.desc())
                .limit(1)
            )
            pic = song_row.scalar_one_or_none()
            cover_url = pic or ""
        items.append({
            "playlist_id": p.playlist_id,
            "playlist_name": p.playlist_name,
            "user_id": p.user_id,
            "user_name": name or "",
            "cover_url": cover_url,
            "songs_count": p.songs_count,
            "play_count": p.play_count,
            "save_count": p.save_count,
        })

    return APIResponse(data={"items": items})
