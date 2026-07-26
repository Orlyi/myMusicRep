import { useParams, useNavigate } from "react-router-dom";
import { useState, useEffect, useCallback } from "react";
import { getArtist, artistSongs, artistAlbums } from "../api/artists.js";
import { networkPlayUrl } from "../api/search.js";
import { SongItem } from "../components/SongItem.jsx";
import { usePlayer } from "../layouts/PlayerContext.jsx";
import {ChevronLeft, Headphones, DiscAlbum, Users} from "lucide-react";

export default function ArtistDetailPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { play, addToQueue, toggleLove, lovedSet, openDetail } = usePlayer();

    const [artist, setArtist] = useState(null);
    const [songs, setSongs] = useState([]);
    const [albums, setAlbums] = useState([]);
    const [activeTab, setActiveTab] = useState("songs");
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!id) return;
        setLoading(true);
        Promise.all([
            getArtist(id),
            artistSongs(id, { page: 1, page_size: 50 }),
            artistAlbums(id, { page: 1, page_size: 50 }),
        ])
            .then(([artistRes, songsRes, albumsRes]) => {
                setArtist(artistRes.data);
                setSongs(songsRes.data?.items || []);
                setAlbums(albumsRes.data?.items || []);
            })
            .catch((err) => console.error("获取歌手详情失败", err))
            .finally(() => setLoading(false));
    }, [id]);

    const handlePlay = useCallback(async (song) => {
        try {
            // 只有 /static/music 开头的才是已下载的干净地址 → 直接播
            if (song.download_url && song.download_url.startsWith("/static/music")) {
                play(song, song.download_url);
                return;
            }
            // 否则走 network/play-url 刷新+下载覆盖
            if (song.platform_id) {
                const playRes = await networkPlayUrl({
                    platform_id: song.platform_id,
                    source: song.source || 'netease',
                    song_name: song.song_name,
                    artist_names: song.artist_name,
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
            // 兜底
            if (song.download_url) {
                play(song, song.download_url);
            }
        } catch (err) {
            console.error(err);
        }
    }, [play]);

    const handleSave = useCallback((song) => toggleLove(song), [toggleLove]);
    const handleAdd = useCallback((song) => addToQueue(song), [addToQueue]);

    if (loading) {
        return (
            <div className="page" style={{padding:"1em"}}>
                <p>加载中...</p>
            </div>
        );
    }

    if (!artist) {
        return (
            <div className="page" style={{padding:"1em"}}>
                <p>歌手不存在</p>
            </div>
        );
    }

    return (
        <div className="page" style={{display:"flex",flexDirection:"column"}}>
            {/* 顶部返回 */}
            <div style={{display:"flex",alignItems:"center",gap:"0.3em",padding:"0.3em 0",position:"relative",flexShrink:0}}>
                <ChevronLeft size={24} onClick={() => navigate(-1)} style={{cursor:"pointer",left:"5%",position:"fixed"}} />
                <span style={{fontSize:"1.1em",fontWeight:600,
                    overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>
                    {artist.artist_name}
                </span>
            </div>

            {/* 歌手头部信息 */}
            <div style={{display:"flex",gap:"1em",marginBottom:"0.5em",flexShrink:0, padding:"0.5em 1em"}}>
                <img
                    src={artist.avartar_url || ""}
                    alt={artist.artist_name}
                    style={{
                        width:"30vw",maxWidth:140,aspectRatio:"1/1",
                        borderRadius:"50%",objectFit:"cover",flexShrink:0,
                    }}
                />
                <div style={{flex:1,minWidth:0,display:"flex",flexDirection:"column",justifyContent:"center"}}>
                    <h2 style={{margin:"0 0 0.3em 0",
                        overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>
                        {artist.artist_name}
                    </h2>
                    <div style={{display:"flex",gap:"0.8em",color:"#666",fontSize:"0.85em"}}>
                        <span style={{display:"flex",alignItems:"center",gap:"0.2em"}}>
                            <Headphones size={14} /> {artist.songs_count || 0}
                        </span>

                        <span style={{display:"flex",alignItems:"center",gap:"0.2em"}}>
                            <Users size={14} /> {artist.fans_count || 0}
                        </span>
                    </div>
                    {artist.introduction && (
                        <p style={{color:"#999",fontSize:"0.8em",margin:"0.5em 0 0 0",
                            overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>
                            {artist.introduction}
                        </p>
                    )}
                </div>
            </div>

            {/* Tab 切换 */}
            <div style={{display:"flex",flexShrink:0,borderBottom:"1px solid #eee"}}>
                <div
                    onClick={() => setActiveTab("songs")}
                    style={{
                        textAlign:"center",cursor:"pointer",
                        borderBottom: activeTab === "songs" ? "2px solid #333" : "2px solid transparent",
                        fontWeight: activeTab === "songs" ? 600 : 400,
                        color: activeTab === "songs" ? "#333" : "#999",
                    }}
                >
                    歌曲 ({songs.length})
                </div>
                <div
                    onClick={() => setActiveTab("albums")}
                    style={{
                        textAlign:"center",cursor:"pointer",
                        borderBottom: activeTab === "albums" ? "2px solid #333" : "2px solid transparent",
                        fontWeight: activeTab === "albums" ? 600 : 400,
                        color: activeTab === "albums" ? "#333" : "#999",width:"20vw"
                    }}
                >
                    专辑 ({albums.length})
                </div>
            </div>

            {/* Tab 内容 */}
            <div style={{flex:1,width:"100%",overflow:"auto",minHeight:0}}>
                {activeTab === "songs" ? (
                    songs.length === 0 ? (
                        <p style={{color:"#999",textAlign:"center",padding:"2em 0"}}>暂无歌曲</p>
                    ) : (
                        <ul className="song-list" style={{listStyle:"none",paddingLeft:"4vw",margin:0,width:"88vw"}}>
                            {songs.map((item) => (
                                <SongItem
                                    key={item.song_id}
                                    song={{...item, is_love: lovedSet.has(item.song_id)}}
                                    onPlay={() => handlePlay(item)}
                                    onSave={() => handleSave(item)}
                                    onAdd={() => handleAdd(item)}
                                    onMore={(s) => openDetail(s, null)}
                                />
                            ))}
                        </ul>
                    )
                ) : (
                    albums.length === 0 ? (
                        <p style={{color:"#999",textAlign:"center",padding:"2em 0"}}>暂无专辑</p>
                    ) : (
                        <div style={{padding:"0 1em"}}>
                            {albums.map((album) => (
                                <div
                                    key={album.album_id}
                                    onClick={() => navigate(`/album/${album.album_id}`)}
                                    style={{
                                        display:"flex",alignItems:"center",gap:"0.8em",
                                        padding:"0.7em 0",borderBottom:"1px solid #f5f5f5",cursor:"pointer",
                                    }}
                                >
                                    <img
                                        src={album.cover_url || ""}
                                        alt={album.album_name}
                                        style={{
                                            width:"3.5em",height:"3.5em",borderRadius:"6px",objectFit:"cover",flexShrink:0,
                                        }}
                                    />
                                    <div style={{flex:1,minWidth:0}}>
                                        <div style={{
                                            overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap",
                                            fontSize:"0.95em",
                                        }}>
                                            {album.album_name}
                                        </div>
                                        <div style={{fontSize:"0.8em",color:"#999",marginTop:"0.2em"}}>
                                            {album.songs_count || 0} 首
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )
                )}
            </div>

            <div style={{height:"20vh",flexShrink:0}} />
        </div>
    );
}
