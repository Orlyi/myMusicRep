import asyncio
import os
import re
from pathlib import Path

import httpx
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Songs, Artists, Albums, Lyrics
from app.schemas.common import APIResponse
from app.services.network_search_service import (
    network_search,
    network_get_play_url,
    network_get_lyric,
    network_get_song_detail,
    network_get_album_detail,
    network_get_artist_detail,
)

router = APIRouter()


@router.get("/search", response_model=APIResponse)
async def network_search_api(
    keyword: str = Query(min_length=1, max_length=100),
    source: str = Query(default="netease", pattern="^(netease|qq)$"),
    type_: str = Query(default="song", alias="type", pattern="^(song|artist|album|lyric)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=30, ge=1, le=100),
):
    """
    网络搜索（实时调第三方 API）
    - source: netease / qq
    - type: song / artist / album / lyric
    """
    try:
        results = await network_search(keyword, source, type_, page, page_size)
        return APIResponse(data={
            "items": [r.model_dump() for r in results],
            "total": len(results),
            "page": page,
            "page_size": page_size,
        })
    except ValueError as e:
        return APIResponse(code=400, message=str(e))


@router.get("/play-url", response_model=APIResponse)
async def network_play_url_api(
    platform_id: str = Query(min_length=1),
    source: str = Query(default="netease", pattern="^(netease|qq)$"),
    sign: str | None = Query(default=None),
    song_name: str | None = Query(default=None),
    artist_names: str | None = Query(default=None),
    album_name: str | None = Query(default=None),
    picture_url: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """
    获取歌曲播放地址
    - 先查 DB，有本地文件则直接返回本地路径
    - 没有则调用破解接口获取 → 存入 DB → 返回
    - 拿到播放地址后，自动补全歌词/歌手/专辑详情到数据库
    """
    result = await db.execute(
        select(Songs).where(
            Songs.platform_id == platform_id,
            or_(Songs.source == source, Songs.source.is_(None)),
        ).limit(1)
    )
    song = result.scalar_one_or_none()

    if song and song.download_url:
        # 已下载到本地 → 直接返回本地路径
        if song.download_url.startswith("/static"):
            return APIResponse(data={
                "url": song.download_url,
                "song_id": song.song_id,
                "from_cache": True,
            })
        # 只有 CDN 缓存 → 查本地文件是否存在，存在就更新路径
        local_path = Path("uploads") / "music" / f"{song.song_id}.mp3"
        if local_path.exists():
            song.download_url = f"/static/music/{song.song_id}.mp3"
            await db.commit()
            return APIResponse(data={
                "url": song.download_url,
                "song_id": song.song_id,
                "from_cache": True,
            })
        # 只有 CDN 临时链 → 返回该链，让前端走代理端点播放
        return APIResponse(data={
            "url": song.download_url,
            "song_id": song.song_id,
            "from_cache": True,
        })

    # 调破解接口
    url = await network_get_play_url(platform_id, source, sign)
    if not url:
        return APIResponse(code=404, message="获取播放地址失败")

    song_id = None

    # --- 补全元数据：歌手、专辑、歌词、封面 ---
    if source == "netease":
        try:
            # 1. 获取歌手详情（含歌手封面）
            artist_result = await network_get_artist_detail(platform_id, source)
            if artist_result and len(artist_result) > 0:
                artist_info = artist_result[0]  # 第一个是歌手本身信息
                if not artist_names:
                    artist_names = artist_info.artist_names

            # 2. 获取专辑详情（含专辑封面、歌曲列表）
            album_detail = None
            if song_name:
                album_detail = await network_get_album_detail(platform_id, source)
                if album_detail and len(album_detail) > 0:
                    album_info = album_detail[0]
                    if not album_name:
                        album_name = album_info.album_name
                    if not picture_url:
                        picture_url = album_info.picture_url

            # 3. 获取歌词
            lyric_text = await network_get_lyric(platform_id, source)

            # 4. 获取歌曲详情（如果上面没拿到封面）
            if not picture_url:
                detail = await network_get_song_detail(platform_id, source)
                if detail and detail.picture_url:
                    picture_url = detail.picture_url

        except Exception as e:
            print(f"获取歌曲详情异常: {e}")

    # 查找或创建歌手
    artist_id = None
    if artist_names:
        db_artist = await db.execute(
            select(Artists).where(
                Artists.artist_name == artist_names,
                Artists.source == source,
            ).limit(1)
        )
        db_artist = db_artist.scalar_one_or_none()
        if not db_artist:
            db_artist = Artists(
                artist_name=artist_names,
                platform_id=platform_id,
                source=source,
            )
            db.add(db_artist)
            await db.flush()
        artist_id = db_artist.artist_id

    # 查找或创建专辑
    album_id = None
    if album_name and artist_id:
        db_album = await db.execute(
            select(Albums).where(
                Albums.album_name == album_name,
                Albums.platform_id == platform_id,
            ).limit(1)
        )
        db_album = db_album.scalar_one_or_none()
        if not db_album:
            db_album = Albums(
                album_name=album_name,
                platform_id=platform_id,
                cover_url=picture_url or "",
                source=source,
                artist_id=artist_id,
            )
            db.add(db_album)
            await db.flush()
        album_id = db_album.album_id

    # 创建歌曲
    song = Songs(
        platform_id=platform_id,
        song_name=song_name or "",
        artist_id=artist_id,
        album_id=album_id,
        picture_url=picture_url or "",
        source=source,
        download_url=url,
    )
    db.add(song)
    await db.flush()
    song_id = song.song_id

    # 存储歌词（如果有）
    if lyric_text:
        # LRC → plain text（去掉时间戳）
        import re
        plain = re.sub(r'\[\d{2}:\d{2}.\d{2,3}\]', '', lyric_text).strip()
        db_lyric = Lyrics(
            song_id=song_id,
            lyric_text=lyric_text,
            plain_lyric=plain,
        )
        db.add(db_lyric)
        await db.flush()
        song.lyric_id = db_lyric.lyric_id

    await db.commit()

    # 下载歌曲到本地永久保存
    local_path = await _download_mp3(url, song_id)
    if local_path:
        song.download_url = f"/static/music/{song_id}.mp3"
        await db.commit()

    # 返回本地路径（优先）或 CDN 路径
    play_url = song.download_url if song.download_url and song.download_url.startswith("/static") else url

    return APIResponse(data={
        "url": play_url,
        "song_id": song_id,
        "from_cache": False,
    })


@router.get("/lyric", response_model=APIResponse)
async def network_lyric_api(
    platform_id: str = Query(min_length=1),
    source: str = Query(default="netease"),
):
    """获取歌词（LRC 格式）"""
    lyric = await network_get_lyric(platform_id, source)
    if lyric:
        return APIResponse(data={"lyric": lyric})
    return APIResponse(code=404, message="获取歌词失败")


@router.get("/song-detail", response_model=APIResponse)
async def network_song_detail_api(
    platform_id: str = Query(min_length=1),
    source: str = Query(default="netease"),
):
    """获取歌曲详情"""
    detail = await network_get_song_detail(platform_id, source)
    if detail:
        return APIResponse(data=detail.model_dump())
    return APIResponse(code=404, message="获取歌曲详情失败")


@router.get("/album-detail", response_model=APIResponse)
async def network_album_detail_api(
    platform_id: str = Query(min_length=1),
    source: str = Query(default="netease"),
):
    """获取专辑详情（含歌曲列表）"""
    results = await network_get_album_detail(platform_id, source)
    return APIResponse(data=[r.model_dump() for r in results])


@router.get("/artist-detail", response_model=APIResponse)
async def network_artist_detail_api(
    platform_id: str = Query(min_length=1),
    source: str = Query(default="netease"),
):
    """获取歌手详情（含热门歌曲）"""
    results = await network_get_artist_detail(platform_id, source)
    return APIResponse(data=[r.model_dump() for r in results])


async def _download_mp3(url: str, song_id: int) -> str | None:
    """下载歌曲到本地永久保存"""
    music_dir = Path("uploads") / "music"
    music_dir.mkdir(parents=True, exist_ok=True)
    local_path = music_dir / f"{song_id}.mp3"

    if local_path.exists():
        return str(local_path)

    try:
        # 必须带 Referer，否则网易云 CDN 403
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.get(
                url,
                headers={
                    "Referer": "https://music.163.com/",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                  "AppleWebKit/537.36 KHTML, like Gecko Chrome/120.0.0.0 Safari/537.36",
                },
            )
            if resp.status_code == 200:
                local_path.write_bytes(resp.content)
                print(f"✅ 歌曲已下载到本地: {local_path}")
                return str(local_path)
            else:
                print(f"下载 mp3 失败，状态码: {resp.status_code}")
    except Exception as e:
        print(f"下载 mp3 异常: {e}")
    return None
