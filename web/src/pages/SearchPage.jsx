import {useNavigate} from "react-router-dom";
import {useState, useCallback, useRef, useEffect} from "react";
import "./SearchPage.css"
import {FingerprintPattern, Music2, Search, DiscAlbum, UserRound, FileText, Headphones} from "lucide-react"
import {networkSearch, networkPlayUrl} from "../api/search.js"
import {SearchSongItem} from "../components/SearchSongItem.jsx"
import {usePlayer} from "../layouts/PlayerContext.jsx"


const TYPE_MAP = [
    {key: "song", label: "歌曲", icon: <Headphones size="2em" />},
    {key: "album", label: "专辑", icon: <DiscAlbum size="2em" />},
    {key: "artist", label: "歌手", icon: <UserRound size="2em" />},
    {key: "lyric", label: "歌词", icon: <FileText size="2em" />},
]


export default function SearchPage(){
    const navigate = useNavigate()
    const {play, addToQueue} = usePlayer()
    const [source, setSource] = useState("netease")
    const [type, setType] = useState("song")
    const [keyword, setKeyword] = useState("")
    const [loading, setLoading] = useState(false)
    const [results, setResults] = useState([])
    const [page, setPage] = useState(1)
    const [hasMore, setHasMore] = useState(true)
    const sentinelRef = useRef(null)
    const pageRef = useRef(1)

    // 首次搜索 / 切换条件时重置
    const handleSearch = useCallback(async () => {
        if (!keyword.trim()) return
        setLoading(true)
        setPage(1)
        pageRef.current = 1
        setHasMore(true)
        try {
            const res = await networkSearch({
                keyword: keyword.trim(),
                source,
                type,
                page: 1,
                page_size: 30,
            })
            const items = res.data.items || []
            setResults(items)
            setHasMore(items.length >= 30)
        } catch (e) {
            console.error("搜索失败", e)
        } finally {
            setLoading(false)
        }
    }, [keyword, source, type])

    // 加载下一页（追加）
    const loadMore = useCallback(async () => {
        if (loading || !hasMore) return
        const nextPage = pageRef.current + 1
        setLoading(true)
        try {
            const res = await networkSearch({
                keyword: keyword.trim(),
                source,
                type,
                page: nextPage,
                page_size: 30,
            })
            const items = res.data.items || []
            setResults(prev => [...prev, ...items])
            setPage(nextPage)
            pageRef.current = nextPage
            setHasMore(items.length >= 30)
        } catch (e) {
            console.error("加载更多失败", e)
        } finally {
            setLoading(false)
        }
    }, [keyword, source, type, loading, hasMore])

    // IntersectionObserver 监听底部
    useEffect(() => {
        const el = sentinelRef.current
        if (!el) return
        const observer = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting && hasMore && !loading) {
                loadMore()
            }
        }, {rootMargin: "200px"})
        observer.observe(el)
        return () => observer.disconnect()
    }, [hasMore, loading, loadMore])

    const handleKeyDown = (e) => {
        if (e.key === "Enter") handleSearch()
    }

    const handlePlay = async (platformId) => {
        try {
            // 从搜索结果里找到对应歌曲
            const song = results.find(r => r.platform_id === platformId)
            if (!song) return

            // 调播放地址接口（DB 缓存 → API 兜底）
            const res = await networkPlayUrl({
                platform_id: platformId,
                source,
                song_name: song.name,
                artist_names: song.artist_names,
                album_name: song.album_name,
                picture_url: song.picture_url,
            })
            if (res.data?.url) {
                play({...song, song_id: res.data.song_id}, res.data.url)
            }
        } catch (e) {
            console.error("获取播放地址失败", e)
        }
    }

    return (
        <div className="page column">
            <div className="search-bar">
                <div className="search" style={{margin:"0 0 0 5vw"}}>
                    <Search onClick={handleSearch} />
                    <input className="search-content"
                           placeholder="喵"
                           value={keyword}
                           onChange={e => setKeyword(e.target.value)}
                           onKeyDown={handleKeyDown} />
                </div>
                <button className="cancel" onClick={() => navigate(-1)}>取消</button>
            </div>

            <div className="search-type flex">
                <div className="sources">
                    {source === "netease" ? (
                        <div onClick={() => setSource("qq")} className="source WY">
                            <FingerprintPattern size="2em" />
                            <span className="small-font">WY</span>
                        </div>
                    ) : (
                        <div onClick={() => setSource("netease")} className="source QQ">
                            <Music2 size="2em" />
                            <span className="small-font">QQ</span>
                        </div>
                    )}
                </div>
                <div className="types">
                    {TYPE_MAP.map(t => (
                        <div key={t.key}
                             className={`type flex ${type === t.key ? "type-active" : ""}`}
                             onClick={() => setType(t.key)}>
                            {t.icon}
                            <span className="small-font">{t.label}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* 搜索结果 */}
            <div className="search-results">
                {results.length > 0 ? (
                    <>
                        {results.map((item, i) => (
                            <div key={`${item.platform_id}-${i}`}>
                                {type === "song" || type === "lyric" ? (
                                    <SearchSongItem song={item} onPlay={handlePlay} />
                                ) : type === "artist" ? (
                                    <div className="search-artist">
                                        <img src={item.picture_url} alt="" className="avatar" />
                                        <span>{item.name}</span>
                                    </div>
                                ) : type === "album" ? (
                                    <div className="search-album">
                                        <img src={item.picture_url} alt="" className="cover" />
                                        <div>
                                            <div>{item.name}</div>
                                            <div className="small-font">{item.artist_names}</div>
                                        </div>
                                    </div>
                                ) : null}
                            </div>
                        ))}
                        {/* 底部哨兵 */}
                        <div ref={sentinelRef} style={{height:1}} />
                        {loading && <div className="loading">加载中...</div>}
                        {!hasMore && results.length > 0 && (
                            <div className="empty">— 已加载全部 —</div>
                        )}
                    </>
                ) : keyword && !loading ? (
                    <div className="empty">未找到结果</div>
                ) : null}
            </div>
        </div>
    )
}