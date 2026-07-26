import {useEffect, useState} from "react";
import {useNavigate, useOutletContext} from "react-router-dom";
import "./HomePage.css"
import TopBar from "../components/TopBar.jsx";
import {SongItem} from "../components/SongItem.jsx";
import {Search, Sparkles, ListMusic, ChevronRight} from "lucide-react"
import {networkPlayUrl} from "../api/search.js";
import {recommend, recommendPlaylists} from "../api/recommend.js";
import {usePlayer} from "../layouts/PlayerContext.jsx";

export default function HomePage(){
    const navigate = useNavigate()
    const {setHeaderContent} = useOutletContext()
    const {play, addToQueue, toggleLove, lovedSet, openDetail} = usePlayer()
    const [items, setItems] = useState([])
    const [playlists, setPlaylists] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        setHeaderContent(
            <TopBar from="/" path="/">
                <div className="S" onClick={()=>navigate("/search")}>
                    <Search></Search>
                    <div className="search-for"></div>
                </div>
            </TopBar>
        )
        return () => setHeaderContent(null)
    }, [setHeaderContent])

    useEffect(() => {
        setLoading(true)
        Promise.all([
            recommend({limit: 20}),
            recommendPlaylists({limit: 6}),
        ])
            .then(([songRes, plRes]) => {
                setItems(songRes.data?.items || [])
                setPlaylists(plRes.data?.items || [])
            })
            .catch(err => console.log("获取推荐失败", err))
            .finally(() => setLoading(false))
    }, [])

    function resolveCover(url) {
        if (!url) return null
        if (url.startsWith("/static")) return `http://localhost:8000${url}`
        return url
    }

    const handlePlay = async (song) => {
        try {
            if (song.download_url?.startsWith("/static/music")) {
                play(song, song.download_url);
                return;
            }
            if (song.platform_id) {
                const playRes = await networkPlayUrl({
                    platform_id: song.platform_id,
                    source: song.source || 'netease',
                });
                if (playRes.data?.url) {
                    play(song, playRes.data.url);
                    return;
                }
                if (playRes.data?.fail_reason) {
                    console.warn(`⚠️ ${song.song_name} - ${playRes.data.fail_reason}`);
                    return;
                }
            }
            if (song.download_url) {
                play(song, song.download_url);
            }
        } catch (err) {
            console.error(err);
        }
    }

    return (
        <div className="page" style={{display:"flex",flexDirection:"column",overflow:"auto"}}>
            {/* 猜你喜欢 */}
            <div style={{display:"flex",alignItems:"center",gap:"0.4em",padding:"0.8em",flexShrink:0}}>
                <Sparkles size={20} color="#ff8c00" />
                <span style={{fontSize:"1.1em",fontWeight:600}}>猜你喜欢</span>
            </div>

            {loading ? (
                <p style={{textAlign:"center",color:"#999",padding:"2em"}}>加载中...</p>
            ) : (
                <div style={{flex:1,width:"100%",overflow:"auto",minHeight:0}}>
                    {/* 推荐歌曲 */}
                    {items.length > 0 && (
                        <ul className="song-list" style={{listStyle:"none",paddingLeft:"4vw",margin:0,width:"88vw"}}>
                            {items.map((item) => (
                                <SongItem
                                    key={item.song_id}
                                    song={{...item, is_love: lovedSet.has(item.song_id)}}
                                    onPlay={() => handlePlay(item)}
                                    onSave={() => toggleLove(item)}
                                    onAdd={() => addToQueue(item)}
                                    onMore={(s) => openDetail(s, null)}
                                />
                            ))}
                        </ul>
                    )}

                    {/* 推荐歌单 */}
                    {playlists.length > 0 && (
                        <>
                            <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",padding:"0.8em 0.8em 0.4em"}}>
                                <div style={{display:"flex",alignItems:"center",gap:"0.3em"}}>
                                    <ListMusic size={18} />
                                    <span style={{fontSize:"1em",fontWeight:600}}>推荐歌单</span>
                                </div>
                                <div style={{display:"flex",alignItems:"center",gap:"0.2em",color:"#999",fontSize:"0.8em",cursor:"pointer"}}
                                    onClick={() => navigate("/library")}>
                                    更多 <ChevronRight size={14} />
                                </div>
                            </div>

                            <div style={{display:"flex",flexWrap:"wrap",gap:"0.8em",padding:"0 0.8em 0.8em"}}>
                                {playlists.map(pl => (
                                    <div key={pl.playlist_id}
                                        onClick={() => navigate(`/playlist/${pl.playlist_id}`)}
                                        style={{width:"calc(50% - 0.4em)",cursor:"pointer"}}>
                                        <img
                                            src={resolveCover(pl.cover_url)}
                                            alt={pl.playlist_name}
                                            style={{width:"100%",aspectRatio:"1/1",borderRadius:8,objectFit:"cover"}}
                                        />
                                        <div style={{fontSize:"0.8em",marginTop:"0.3em",overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>
                                            {pl.playlist_name}
                                        </div>
                                        <div style={{fontSize:"0.7em",color:"#999"}}>{pl.songs_count} 首</div>
                                    </div>
                                ))}
                            </div>
                        </>
                    )}

                    {items.length === 0 && playlists.length === 0 && (
                        <p style={{textAlign:"center",color:"#999",padding:"3em"}}>先去听几首歌吧</p>
                    )}
                </div>
            )}

            <div style={{height:"20vh",flexShrink:0}} />
        </div>
    )
}
