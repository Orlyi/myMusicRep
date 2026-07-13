import sys
import os

# 把 spiders 目录加到 path，方便 import encrypt.py
_spiders_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "spiders")
if _spiders_dir not in sys.path:
    sys.path.insert(0, _spiders_dir)

import asyncio

import httpx

from .base import BaseSearcher, NeteaseSearchResult

# ---- 常量 ----
SEARCH_URL = "https://music.163.com/api/search/get/web"
SONG_DETAIL_URL = "http://music.163.com/api/song/detail"
LYRIC_URL = "https://music.163.com/api/song/lyric"
ALBUM_URL = "https://music.163.com/api/album"
ARTIST_URL = "https://music.163.com/api/artist"
PLAY_URL = "https://music.163.com/weapi/song/enhance/player/url/v1"


class NeteaseSearcher(BaseSearcher):
    """网易云音乐搜索器"""

    def __init__(self, cookie: str | None = None):
        self._client: httpx.AsyncClient | None = None
        self._cookie = cookie or ""

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                  "AppleWebKit/537.36 KHTML, like Gecko Chrome/120.0.0.0 Safari/537.36",
                    "Referer": "https://music.163.com/",
                },
                timeout=15,
            )
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    # ==================== 搜索 ====================

    async def _search(self, keyword: str, page: int, page_size: int, type_: int) -> dict:
        client = await self._get_client()
        offset = (page - 1) * page_size
        resp = await client.get(SEARCH_URL, params={
            "s": keyword, "type": type_, "limit": page_size, "offset": offset,
        })
        return resp.json()

    async def search_song(self, keyword: str, page: int, page_size: int) -> list[NeteaseSearchResult]:
        data = await self._search(keyword, page, page_size, 1)
        if data.get("code") != 200:
            return []
        songs = data.get("result", {}).get("songs", [])
        return [self._parse_song(s) for s in songs]

    async def search_artist(self, keyword: str, page: int, page_size: int) -> list[NeteaseSearchResult]:
        data = await self._search(keyword, page, page_size, 100)
        if data.get("code") != 200:
            return []
        artists = data.get("result", {}).get("artists", [])
        return [
            NeteaseSearchResult(
                platform_id=str(a["id"]),
                name=a["name"],
                artist_names=a.get("name", ""),
                picture_url=a.get("picUrl") or a.get("img1v1Url") or "",
                source="netease",
            )
            for a in artists
        ]

    async def search_album(self, keyword: str, page: int, page_size: int) -> list[NeteaseSearchResult]:
        data = await self._search(keyword, page, page_size, 10)
        if data.get("code") != 200:
            return []
        albums = data.get("result", {}).get("albums", [])
        results = []
        for a in albums:
            arts = a.get("artists", [])
            artist_names = "、".join(art["name"] for art in arts) if arts else ""
            results.append(NeteaseSearchResult(
                platform_id=str(a["id"]),
                name=a["name"],
                artist_names=artist_names,
                album_name=a["name"],
                picture_url=a.get("picUrl") or "",
                source="netease",
            ))
        return results

    async def search_lyric(self, keyword: str, page: int, page_size: int) -> list[NeteaseSearchResult]:
        """搜歌词 → 返回匹配的歌曲列表"""
        data = await self._search(keyword, page, page_size, 1006)
        if data.get("code") != 200:
            return []
        songs = data.get("result", {}).get("songs", [])
        return [self._parse_song(s) for s in songs]

    # ==================== 详情 ====================

    async def get_song_detail(self, platform_id: str) -> NeteaseSearchResult | None:
        client = await self._get_client()
        resp = await client.get(SONG_DETAIL_URL, params={
            "id": platform_id, "ids": f"[{platform_id}]",
        })
        data = resp.json()
        if data.get("code") != 200:
            return None
        songs = data.get("songs", [])
        return self._parse_song(songs[0]) if songs else None

    async def get_lyric(self, platform_id: str) -> str | None:
        """获取歌词（LRC 格式）"""
        client = await self._get_client()
        resp = await client.get(LYRIC_URL, params={
            "id": platform_id, "lv": 1, "kv": 1, "tv": -1,
        })
        data = resp.json()
        if data.get("code") != 200:
            return None
        lrc = data.get("lrc", {})
        return lrc.get("lyric")

    async def get_album_detail(self, platform_id: str) -> list[NeteaseSearchResult]:
        """专辑详情 → 专辑信息 + 歌曲列表"""
        client = await self._get_client()
        resp = await client.get(f"{ALBUM_URL}/{platform_id}")
        data = resp.json()
        if data.get("code") != 200:
            return []
        album = data.get("album", {})
        songs = data.get("songs", []) or album.get("songs", [])
        arts = album.get("artists", [])
        artist_names = "、".join(art["name"] for art in arts) if arts else ""
        results = [NeteaseSearchResult(
            platform_id=str(album["id"]),
            name=album["name"],
            artist_names=artist_names,
            album_name=album["name"],
            picture_url=album.get("picUrl") or "",
            source="netease",
        )]
        for s in songs:
            results.append(self._parse_song(s))
        return results

    async def get_artist_detail(self, platform_id: str) -> list[NeteaseSearchResult]:
        """歌手详情 → 歌手信息 + 热门歌曲"""
        client = await self._get_client()
        resp = await client.get(f"{ARTIST_URL}/{platform_id}")
        data = resp.json()
        if data.get("code") != 200:
            return []
        artist = data.get("artist", {})
        hot_songs = data.get("hotSongs", [])
        results = [NeteaseSearchResult(
            platform_id=str(artist["id"]),
            name=artist["name"],
            artist_names=artist.get("name", ""),
            picture_url=artist.get("picUrl") or artist.get("img1v1Url") or "",
            source="netease",
        )]
        for s in hot_songs:
            results.append(self._parse_song(s))
        return results

    # ==================== 播放地址 ====================

    async def get_play_url(self, platform_id: str, sign: str | None = None) -> str | None:
        """获取播放地址（复用 spiders/encrypt.py 的 AES + RSA 加密破解）"""
        return await asyncio.to_thread(self._get_play_url_sync, platform_id)

    def _get_play_url_sync(self, platform_id: str) -> str | None:
        try:
            from encrypt import get_encrypted_params
            encrypted = get_encrypted_params(int(platform_id))
        except Exception:
            return None

        data = {"params": encrypted["params"], "encSecKey": encrypted["encSecKey"]}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://music.163.com/",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": self._cookie,
        }

        try:
            import requests as sync_req
            resp = sync_req.post(PLAY_URL, data=data, headers=headers, timeout=10)
            if resp.status_code != 200:
                return None
            result = resp.json()
            if result.get("code") == 200 and result.get("data"):
                return result["data"][0].get("url")
        except Exception:
            return None
        return None

    def _parse_song(self, s: dict) -> NeteaseSearchResult:
        """统一解析歌曲 JSON（兼容全称和缩写两种格式）"""
        # 处理 artists/ar 两种格式
        artists = s.get("artists") or s.get("ar") or []
        if isinstance(artists, dict):
            artists = [artists]
        artist_names = "、".join(a["name"] for a in artists) if artists else ""

        # 处理 album/al 两种格式
        album = s.get("album") or s.get("al") or {}
        if isinstance(album, dict):
            album_name = album.get("name", "")
            pic_url = album.get("picUrl") or ""
        else:
            album_name = ""
            pic_url = ""

        # 兜底取歌曲自己的 picUrl
        if not pic_url:
            pic_url = s.get("picUrl", "")

        # 时长（dt 是毫秒）
        duration = s.get("duration") or s.get("dt")

        return NeteaseSearchResult(
            platform_id=str(s["id"]),
            name=s.get("name", ""),
            artists=artists,
            artist_names=artist_names,
            album_id=str(album.get("id", "")) if isinstance(album, dict) else "",
            album_name=album_name,
            picture_url=pic_url,
            duration=duration,
            source="netease",
        )
