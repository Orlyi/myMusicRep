import {useNavigate} from "react-router-dom";
import {useState, useCallback, useRef, useEffect} from "react";
import "./SearchPage.css"
import {FingerprintPattern, Music2, Search, DiscAlbum, UserRound, FileText, Headphones, Loader, X} from "lucide-react"
import {networkSearch, networkPlayUrl, fetchAlbumDetail} from "../api/search.js"
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
    const {play, addToQueue, toggleLove, lovedSet, openDetail} = usePlayer()
    const [source, setSource] = useState("netease")
    const [type, setType] = useState("song")
    const [keyword, setKeyword] = useState("")
    const [loading, setLoading] = useState(false)
    const [albumLoading, setAlbumLoading] = useState(false)  // 专辑拉取中
    const [results, setResults] = useState([])
    const [page, setPage] = useState(1)
    const [hasMore, setHasMore] = useState(true)
    const sentinelRef = useRef(null)
    const pageRef = useRef(1)
    // 搜索结果解析后记录 platform_id → song_id 映射，用于渲染爱心
    const platformSongId = useRef({})
    // Toast 提示
    const [toast, setToast] = useState(null)
    const toastTimer = useRef(null)
    const showToast = useCallback((msg, icon) => {
        setToast({ msg, icon })
        clearTimeout(toastTimer.current)
        toastTimer.current = setTimeout(() => setToast(null), 3000)
    }, [])

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
            platformSongId.current = {}
            setHasMore(items.length >= 30)
        } catch (e) {
            console.error("搜索失败", e)
        } finally {
            setLoading(false)
        }
    }, [keyword, source, type])

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
        const song = await resolveSong(platformId)
        if (song?.url) {
            play(song, song.url)
        }
    }


    const resolveSong = async (platformId) => {
        const song = results.find(r => r.platform_id === platformId)
        if (!song) return null

        try {
            const res = await networkPlayUrl({
                platform_id: platformId,
                source,
                song_name: song.name,
                artist_names: song.artist_names,
                album_name: song.album_name,
                picture_url: song.picture_url,
            })
            if (res.data?.url) {
                const sid = res.data.song_id
                if (sid) platformSongId.current[song.platform_id] = sid
                return {
                    ...song,
                    song_id: sid,
                    song_name: song.name,
                    artist_name: song.artist_names,
                    picture_url: res.data.picture_url || song.picture_url || '',
                    url: res.data.url,
                    download_url: res.data.url,
                }
            }

            const failReason = res.data?.fail_reason || res.message
            if (failReason) {
                console.warn(` ${song.name} - ${failReason}`)
                showToast(failReason, song.picture_url || song.artist_names)
            }
        } catch (e) {
            console.error("获取播放地址失败", e)
        }
        return null
    }

    const handleAdd = async (song) => {
        const enriched = await resolveSong(song.platform_id)
        if (enriched) addToQueue(enriched)
    }

    const handleSave = async (song) => {
        const enriched = await resolveSong(song.platform_id)
        if (enriched) toggleLove(enriched)
    }

    const handleMore = async (s) => {
        const enriched = await resolveSong(s.platform_id)
        if (enriched) openDetail(enriched, null)
    }

    const handleAlbumClick = async (item) => {
        setAlbumLoading(true)
        try {
            const res = await fetchAlbumDetail({
                platform_id: item.platform_id,
                source,
            })
            if (res.data?.album_id) {
                navigate(`/album/${res.data.album_id}`)
            }
        } catch (e) {
            console.error("获取专辑详情失败", e)
        } finally {
            setAlbumLoading(false)
        }
    }

    return (
        <div className="page column " style={{overflow:"auto"}}>
            <div className="search-bar">
                <div className="search" style={{margin:"0 0 0 5vw"}}>
                    <Search onClick={handleSearch} />
                    <input className="search-content"
                           placeholder="喵"
                           value={keyword}
                           onChange={e => setKeyword(e.target.value)}
                           onKeyDown={handleKeyDown}
                            autoFocus
                    />
                </div>
                <button style={{marginRight:"1em"}} className="cancel" onClick={() => navigate(-1)}>取消</button>
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


            <div className="search-results" style={{}}>
                {results.length > 0 ? (
                    <>
                        {results.map((item, i) => (
                            <div key={`${item.platform_id}-${i}`}>
                                {type === "song" || type === "lyric" ? (
                                    <SearchSongItem song={{...item, is_love: lovedSet.has(platformSongId.current[item.platform_id])}} onPlay={handlePlay} onSave={handleSave} onAdd={handleAdd} onMore={handleMore} />
                                ) : type === "artist" ? (
                                    <div className="search-artist">
                                        <img src={item.picture_url} alt="" className="avatar" />
                                        <span>{item.name}</span>
                                    </div>
                                ) : type === "album" ? (
                                    <div className="search-album" onClick={() => handleAlbumClick(item)} style={{cursor:"pointer"}}>
                                        <img src={item.picture_url} alt="" className="cover" />
                                        <div>
                                            <div>{item.name}</div>
                                            <div className="small-font" style={{textAlign:"left"}}>{item.artist_names}</div>
                                        </div>
                                    </div>
                                ) : null}
                            </div>
                        ))}

                        <div ref={sentinelRef} style={{height:1}} />
                        {loading && <div className="loading">加载中...</div>}
                        {albumLoading && <div className="loading"><Loader size={16} style={{animation:"spin 1s linear infinite"}} /> 正在拉取专辑...</div>}
                        {!hasMore && results.length > 0 && (
                            <div className="empty">— 已加载全部 —</div>
                        )}
                    </>
                ) : keyword && !loading ? (
                    <div className="empty">未找到结果</div>
                ) : null}

                {toast && (
                    <div className="toast-overlay">
                        <div className="toast-content">
                            <span className="toast-text">{toast.msg}</span>
                            <X size={16} onClick={() => setToast(null)} style={{cursor:"pointer", flexShrink:0}} />
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}