from .base import NeteaseSearchResult
from .netease import NeteaseSearcher
from app.core.config import settings

# 注册搜索器（由 __init__.py 统一管理所有平台）
_searchers: dict[str, "BaseSearcher"] = {}

_TYPE_METHOD_MAP = {
    "song": "search_song",
    "artist": "search_artist",
    "album": "search_album",
    "lyric": "search_lyric",
}


def _get_searcher(source: str):
    """懒加载获取搜索器实例"""
    if source not in _searchers:
        if source == "netease":
            _searchers[source] = NeteaseSearcher(cookie=settings.netease_cookie)
        # elif source == "qq":
        #     _searchers[source] = QqSearcher()
        else:
            raise ValueError(f"不支持的来源: {source}")
    return _searchers[source]


async def network_search(
    keyword: str,
    source: str,
    type_: str,
    page: int = 1,
    page_size: int = 30,
) -> list[NeteaseSearchResult]:
    """
    统一网络搜索入口

    Args:
        keyword: 搜索关键词
        source: 来源（netease / qq）
        type_: 类型（song / artist / album / lyric）
        page: 页码（默认 1）
        page_size: 每页数量（默认 30）

    Returns:
        统一格式的搜索结果列表
    """
    searcher = _get_searcher(source)
    method_name = _TYPE_METHOD_MAP.get(type_)
    if not method_name:
        raise ValueError(f"不支持的搜索类型: {type_}")
    method = getattr(searcher, method_name)
    return await method(keyword, page, page_size)


async def network_get_play_url(
    platform_id: str,
    source: str,
    sign: str | None = None,
) -> tuple[str | None, str | None]:
    """获取歌曲播放地址

    Returns:
        (url_or_None, fail_reason_or_None)
    """
    searcher = _get_searcher(source)
    url = await searcher.get_play_url(platform_id, sign)
    if url:
        return url, None
    reason = getattr(searcher, "play_url_fail_reason", None)
    return None, reason or "获取播放地址失败"


async def network_get_lyric(platform_id: str, source: str = "netease") -> str | None:
    """获取歌词"""
    searcher = _get_searcher(source)
    return await searcher.get_lyric(platform_id)


async def network_get_song_detail(platform_id: str, source: str = "netease") -> NeteaseSearchResult | None:
    """获取歌曲详情"""
    searcher = _get_searcher(source)
    return await searcher.get_song_detail(platform_id)


async def network_get_album_detail(platform_id: str, source: str = "netease") -> list[NeteaseSearchResult]:
    """获取专辑详情（专辑信息 + 歌曲列表）"""
    searcher = _get_searcher(source)
    return await searcher.get_album_detail(platform_id)


async def network_get_artist_detail(platform_id: str, source: str = "netease") -> list[NeteaseSearchResult]:
    """获取歌手详情（歌手信息 + 热门歌曲）"""
    searcher = _get_searcher(source)
    return await searcher.get_artist_detail(platform_id)
