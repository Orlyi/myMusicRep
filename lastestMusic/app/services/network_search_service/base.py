from pydantic import BaseModel


class NeteaseSearchResult(BaseModel):
    """网络搜索统一返回格式"""
    platform_id: str
    name: str
    artists: list[dict] = []
    artist_names: str = ""
    album_id: str = ""
    album_name: str = ""
    picture_url: str | None = None
    source: str = "netease"
    duration: int | None = None
    sign: str | None = None


class BaseSearcher:
    """搜索器抽象基类"""

    async def search_song(self, keyword: str, page: int, page_size: int) -> list[NeteaseSearchResult]:
        raise NotImplementedError

    async def search_artist(self, keyword: str, page: int, page_size: int) -> list[NeteaseSearchResult]:
        raise NotImplementedError

    async def search_album(self, keyword: str, page: int, page_size: int) -> list[NeteaseSearchResult]:
        raise NotImplementedError

    async def search_lyric(self, keyword: str, page: int, page_size: int) -> list[NeteaseSearchResult]:
        raise NotImplementedError

    async def get_play_url(self, platform_id: str, sign: str) -> str | None:
        raise NotImplementedError
