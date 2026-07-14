import asyncio
import os
import re
from pathlib import Path

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis_client import get_redis
from app.core.redis_keys import CDN_URL_PREFIX, CDN_URL_TTL
from app.models import Songs, Artists, Albums, Lyrics, ArtistSingSong
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
    - DB 只有 CDN 链接时，查 Redis 有无新鲜 CDN 缓存
    - 都没有则调破解接口获取 → 存入 Redis → 返回
    """
    result = await db.execute(
        select(Songs).where(
            Songs.platform_id == platform_id,
            or_(Songs.source == source, Songs.source.is_(None)),
        ).limit(1)
    )
    song = result.scalar_one_or_none()

    redis = await get_redis()
    redis_key = f"{CDN_URL_PREFIX}{platform_id}"
    is_cdn = False

    if song and song.download_url:
        # 已下载到本地 → 直接返回本地路径
        if song.download_url.startswith("/static"):
            return APIResponse(data={
                "url": song.download_url,
                "song_id": song.song_id,
                "picture_url": song.picture_url or "",
                "from_cache": True,
                "is_cdn": False,
            })

        # 只有 CDN 链接 → 先查 Redis 缓存
        cached_url = await redis.get(redis_key)
        if cached_url:
            return APIResponse(data={
                "url": cached_url,
                "song_id": song.song_id,
                "picture_url": song.picture_url or "",
                "from_cache": True,
                "is_cdn": True,
            })

        # 本地文件是否存在（上次下载成功的）
        local_path = Path("uploads") / "music" / f"{song.song_id}.mp3"
        if local_path.exists():
            song.download_url = f"/static/music/{song.song_id}.mp3"
            await db.commit()
            return APIResponse(data={
                "url": song.download_url,
                "song_id": song.song_id,
                "picture_url": song.picture_url or "",
                "from_cache": True,
                "is_cdn": False,
            })

        # Redis 也没有、本地也没有 → 调 API 重新获取 CDN 链
        url = await network_get_play_url(platform_id, source, sign)
        if url:
            await redis.setex(redis_key, CDN_URL_TTL, url)
            song.download_url = url
            await db.commit()
            return APIResponse(data={
                "url": url,
                "song_id": song.song_id,
                "picture_url": song.picture_url or "",
                "from_cache": False,
                "is_cdn": True,
            })

        # API 也失败了 → 返回 DB 里的旧链接
        return APIResponse(data={
            "url": song.download_url,
            "song_id": song.song_id,
            "picture_url": song.picture_url or "",
            "from_cache": True,
            "is_cdn": True,
        })

    # 调破解接口
    url = await network_get_play_url(platform_id, source, sign)
    if not url:
        return APIResponse(code=404, message="获取播放地址失败")

    song_id = None

    # --- 补全元数据：歌手、专辑、歌词、封面 ---
    real_artist_platform_ids: list[str] = []
    real_album_platform_id: str | None = None
    artist_avatar_url: str | None = None
    album_cover_url: str | None = None
    album_artist_names: str | None = None
    all_artist_names: list[str] = []

    if source == "netease":
        try:
            # 1. 获取歌曲详情 → 拿到 song_name, picture_url, artists数组, album_id
            detail = await network_get_song_detail(platform_id, source)
            if detail:
                if not song_name:
                    song_name = detail.name
                if not picture_url:
                    picture_url = detail.picture_url

                # 从 artists 数组中提取歌手真实 ID
                for art in detail.artists:
                    aid = art.get("id") or art.get("artistId")
                    if aid:
                        real_artist_platform_ids.append(str(aid))

                # 获取专辑真实 ID
                real_album_platform_id = detail.album_id or None

            # 2. 用真实歌手ID → 调 artist-detail 获取所有歌手名 + 头像
            all_artist_names: list[str] = []
            for rid in real_artist_platform_ids:
                artist_result = await network_get_artist_detail(rid, source)
                if artist_result and len(artist_result) > 0:
                    ai = artist_result[0]
                    all_artist_names.append(ai.artist_names or ai.name or "")
                    if not artist_avatar_url:
                        artist_avatar_url = ai.picture_url or ""
            if all_artist_names and not artist_names:
                artist_names = "、".join(all_artist_names)

            # 3. 用真实专辑ID → 调 album-detail 获取专辑名 + 封面 + 专辑所属艺人
            album_artist_names: str | None = None
            if real_album_platform_id:
                album_result = await network_get_album_detail(real_album_platform_id, source)
                if album_result and len(album_result) > 0:
                    al = album_result[0]
                    if not album_name:
                        album_name = al.album_name or al.name
                    if not album_cover_url:
                        album_cover_url = al.picture_url or ""
                    if not picture_url:
                        picture_url = al.picture_url or ""
                    # 记录专辑所属艺人名，用于匹配
                    album_artist_names = al.artist_names or None

            # 4. 获取歌词
            lyric_text = await network_get_lyric(platform_id, source)

        except Exception as e:
            print(f"获取歌曲详情异常: {e}")

    # 查找或创建歌手（用真实 platform_id × 真实 artist_name）
    # 每个真实歌手独立创建，避免 "阿虾、崔铭珈" 被当成一个歌手
    artist_id = None
    if artist_names:
        if real_artist_platform_ids:
            # 有多歌手 → 分别创建/查找，artist_id 取第一个作为主歌手
            for i, rid in enumerate(real_artist_platform_ids):
                name_for_this = all_artist_names[i] if i < len(all_artist_names) else ""
                db_artist = await db.execute(
                    select(Artists).where(
                        Artists.platform_id == rid,
                        Artists.source == source,
                    ).limit(1)
                )
                db_artist = db_artist.scalar_one_or_none()
                if not db_artist:
                    db_artist = Artists(
                        artist_name=name_for_this,
                        platform_id=rid,
                        source=source,
                        avartar_url=artist_avatar_url if i == 0 else "",
                    )
                    db.add(db_artist)
                    await db.flush()
                if i == 0:
                    artist_id = db_artist.artist_id
        else:
            # 没有单独歌手ID（兜底）
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
                    avartar_url=artist_avatar_url or "",
                )
                db.add(db_artist)
                await db.flush()
            artist_id = db_artist.artist_id

    # 查找或创建专辑
    # 用专辑的 artist_names 去匹配已创建的歌手，匹配上才收录，匹配不上就不收录
    album_id = None
    matched_album_artist_id = None
    if album_name or real_album_platform_id:
        real_album_pid = real_album_platform_id or platform_id

        # 有专辑艺人名 → 尝试匹配歌手
        if album_artist_names and real_artist_platform_ids:
            album_artist_set = set(a.strip() for a in album_artist_names.split("、"))
            for rid, aname in zip(real_artist_platform_ids, all_artist_names):
                if aname in album_artist_set:
                    db_artist = await db.execute(
                        select(Artists).where(
                            Artists.platform_id == rid,
                            Artists.source == source,
                        ).limit(1)
                    )
                    db_artist = db_artist.scalar_one_or_none()
                    if db_artist:
                        matched_album_artist_id = db_artist.artist_id
                        break

        # 匹配到了 → 创建/查找专辑
        if matched_album_artist_id:
            db_album = await db.execute(
                select(Albums).where(
                    Albums.platform_id == real_album_pid,
                    Albums.source == source,
                ).limit(1)
            )
            db_album = db_album.scalar_one_or_none()
            if not db_album:
                db_album = Albums(
                    album_name=album_name or "",
                    platform_id=real_album_pid,
                    cover_url=album_cover_url or picture_url or "",
                    source=source,
                    artist_id=matched_album_artist_id,
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

    # 写入多歌手关联表
    if real_artist_platform_ids:
        for rid in real_artist_platform_ids:
            ass_artist = await db.execute(
                select(Artists).where(
                    Artists.platform_id == rid,
                    Artists.source == source,
                ).limit(1)
            )
            ass_artist = ass_artist.scalar_one_or_none()
            if ass_artist:
                # 避免重复写入
                existing_ass = await db.execute(
                    select(ArtistSingSong).where(
                        ArtistSingSong.artist_id == ass_artist.artist_id,
                        ArtistSingSong.song_id == song_id,
                    ).limit(1)
                )
                if not existing_ass.scalar_one_or_none():
                    db.add(ArtistSingSong(artist_id=ass_artist.artist_id, song_id=song_id))

    # 存储歌词（如果有）
    if lyric_text:
        db_lyric = Lyrics(
            song_id=song_id,
            lyric_text=lyric_text,
            # plain_lyric 由数据库触发器 trg_lyrics_insert 自动提取
        )
        db.add(db_lyric)
        await db.flush()
        song.lyric_id = db_lyric.lyric_id

    await db.commit()

    # 缓存 CDN URL 到 Redis（即使下载失败，Redis 里的链还能用 CDN_TTL 时间）
    await redis.setex(redis_key, CDN_URL_TTL, url)

    # 下载歌曲到本地永久保存（后台任务，不阻塞返回）
    local_path = await _download_mp3(url, song_id)
    if local_path:
        song.download_url = f"/static/music/{song_id}.mp3"
        await db.commit()

    # 返回本地路径（优先）或 CDN 路径
    is_local = song.download_url and song.download_url.startswith("/static")

    return APIResponse(data={
        "url": song.download_url if is_local else url,
        "song_id": song_id,
        "picture_url": picture_url or "",
        "from_cache": False,
        "is_cdn": not is_local,
    })


@router.get("/audio-proxy")
async def network_audio_proxy_api(
    url: str = Query(min_length=1, description="CDN 音频 URL（需 URL 编码）"),
):
    """
    音频流代理 — 绕过防盗链
    前端播放 CDN 链接时代理到这个端点，自动添加 Referer 头。
    同时检查 Redis 中是否有缓存的 CDN 链，过期则重新获取。

    用法：
      <audio src="/api/v1/network/audio-proxy?url=编码后的CDN链" />
    """
    import urllib.parse
    decoded_url = urllib.parse.unquote(url)

    if not decoded_url.startswith("http"):
        raise HTTPException(status_code=400, detail="无效的 URL")

    # 注意：不能用 async with 管理 client 生命周期，
    # 因为 StreamingResponse 在 handler 返回后才开始迭代
    client = httpx.AsyncClient(timeout=120)
    try:
        req = client.build_request("GET", decoded_url, headers={
            "Referer": "https://music.163.com/",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 KHTML, like Gecko "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        })
        resp = await client.send(req, stream=True)
        if resp.status_code != 200:
            await resp.aclose()
            await client.aclose()
            raise HTTPException(status_code=502, detail=f"上游返回 {resp.status_code}")

        media_type = resp.headers.get("content-type", "audio/mpeg")

        async def stream(resp=resp, client=client):
            try:
                async for chunk in resp.aiter_bytes():
                    yield chunk
            except Exception:
                pass
            finally:
                await resp.aclose()
                await client.aclose()

        return StreamingResponse(
            stream(),
            media_type=media_type,
            headers={
                "Accept-Ranges": "bytes",
                "Cache-Control": "public, max-age=600",
            },
        )
    except httpx.TimeoutException:
        await client.aclose()
        raise HTTPException(status_code=504, detail="上游超时")
    except Exception as e:
        await client.aclose()
        raise HTTPException(status_code=502, detail=f"代理错误: {str(e)}")


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
