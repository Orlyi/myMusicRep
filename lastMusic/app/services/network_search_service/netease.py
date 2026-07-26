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
        self.play_url_fail_reason: str | None = None  # 上一次 get_play_url 失败原因

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
        import sys
        print(f"[play-url-async] 进入 get_play_url platform_id={platform_id}", flush=True)
        sys.stderr.flush()
        result = await asyncio.to_thread(self._get_play_url_sync, platform_id)
        print(f"[play-url-async] _get_play_url_sync 返回: {result}", flush=True)
        return result

    def _get_play_url_sync(self, platform_id: str) -> str | None:
        self.play_url_fail_reason = None  # 重置

        def debug(msg):
            import sys
            print(f"[play-url] {msg}", flush=True)
            sys.stderr.write(f"[play-url] {msg}\n")
            sys.stderr.flush()

        try:
            from encrypt import get_encrypted_params
            encrypted = get_encrypted_params(int(platform_id))
        except ImportError as e:
            debug(f"encrypt 模块导入失败: {e}")
            self.play_url_fail_reason = "解密模块加载失败"
            return None
        except Exception as e:
            debug(f"get_encrypted_params 失败: {e}")
            self.play_url_fail_reason = "参数加密失败"
            return None

        data = {"params": encrypted["params"], "encSecKey": encrypted["encSecKey"]}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://music.163.com/",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": self._cookie,
        }
        # 从 Cookie 中提取 csrf_token 拼到 URL
        csrf_token = ""
        for part in self._cookie.split(";"):
            part = part.strip()
            if part.startswith("__csrf="):
                csrf_token = part[len("__csrf="):]
                break
        play_url = PLAY_URL
        if csrf_token:
            play_url += f"?csrf_token={csrf_token}"
        debug(f"请求 platform_id={platform_id}, csrf_token={csrf_token[:10] if csrf_token else '无'}, cookie前20={repr(self._cookie[:20]) if self._cookie else '空'}")

        try:
            import requests as sync_req
            resp = sync_req.post(play_url, data=data, headers=headers, timeout=10)
            debug(f"响应 status={resp.status_code}")
            if resp.status_code != 200:
                debug(f"状态码异常 {resp.status_code}: {resp.text[:200]}")
                self.play_url_fail_reason = f"网易云响应状态码异常: {resp.status_code}"
                return None
            result = resp.json()
            code = result.get("code")
            data_arr = result.get("data", [])
            debug(f"API code={code}, data条数={len(data_arr)}")
            if code != 200:
                debug(f"网易云返回错误码 {code}, msg={result.get('message','')}, 完整响应={str(result)[:300]}")
                self.play_url_fail_reason = f"网易云API返回错误: {result.get('message', '')}"
                return None
            if not data_arr:
                debug(f"data 为空数组, 完整响应={str(result)[:300]}")
                self.play_url_fail_reason = "歌曲不存在或已下架"
                return None
            url = data_arr[0].get("url")
            if not url:
                fee = data_arr[0].get("fee", -1)
                free_trial = data_arr[0].get("freeTrialInfo")
                if fee == 1:
                    debug(f"❌ VIP歌曲，需要会员：fee={fee}, freeTrialInfo={free_trial}")
                    self.play_url_fail_reason = "VIP歌曲，需开通网易云会员"
                elif fee == 4:
                    debug(f"❌ 数字专辑需购买：fee={fee}")
                    self.play_url_fail_reason = "数字专辑，需单独购买"
                elif fee == 8:
                    debug(f"❌ 仅试听片段：fee={fee}")
                    self.play_url_fail_reason = "仅提供试听片段"
                else:
                    debug(f"❌ url为空，fee={fee}, freeTrialInfo={free_trial}, data[0]={str(data_arr[0])[:200]}")
                    self.play_url_fail_reason = f"无法获取播放地址(fee={fee})"
            else:
                debug(f"✅ 获取到 url (前80): {url[:80]}")
            return url
        except requests.exceptions.Timeout as e:
            debug(f"请求超时: {e}")
            self.play_url_fail_reason = "请求网易云超时"
            return None
        except requests.exceptions.ConnectionError as e:
            debug(f"连接失败: {e}")
            self.play_url_fail_reason = "无法连接网易云服务器"
            return None
        except Exception as e:
            import traceback
            debug(f"未知异常: {e}\n{traceback.format_exc()}")
            self.play_url_fail_reason = f"获取播放地址异常: {str(e)[:60]}"
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
