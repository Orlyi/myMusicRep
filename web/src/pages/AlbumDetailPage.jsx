import { useParams, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { getAlbum, getSongs } from "../api/albums.js";
import { SongItem } from "../components/SongItem.jsx";
import { usePlayer } from "../layouts/PlayerContext.jsx";
import { downloadSong } from "../api/songs.js";
import { networkPlayUrl } from "../api/search.js";
import {ChevronLeft} from "lucide-react";

export default function AlbumDetailPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { play, addToQueue, toggleLove, lovedSet, openDetail } = usePlayer();

    const [album, setAlbum] = useState(null);
    const [songs, setSongs] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!id) return;
        setLoading(true);
        Promise.all([
            getAlbum(id),
            getSongs(id, { page: 1, page_size: 100 }),
        ])
            .then(([albumRes, songsRes]) => {
                setAlbum(albumRes.data);
                setSongs(songsRes.data?.items || []);
            })
            .catch((err) => console.error("获取专辑详情失败", err))
            .finally(() => setLoading(false));
    }, [id]);

    const handlePlay = async (song) => {
        try {
            const res = await downloadSong(song.song_id);
            if (res.data?.download_url) {
                const url = res.data.download_url;
                // 只有 /static/music 开头的才是已下载的干净地址 → 直接播
                if (url.startsWith("/static/music")) {
                    play(res.data, url);
                    return;
                }
                // 否则是脏地址（CDN/过期/临时）→ 走 play-url 刷新+下载覆盖
                if (song.platform_id) {
                    const playRes = await networkPlayUrl({
                        platform_id: song.platform_id,
                        source: song.source || 'netease',
                    });
                    if (playRes.data?.url) {
                        play(res.data, playRes.data.url);
                        return;
                    }
                    if (playRes.data?.fail_reason) {
                        console.warn(`⚠️ ${song.song_name} - ${playRes.data.fail_reason}`);
                        return;
                    }
                }
                // 兜底直接播（可能还是脏的，但试了）
                play(res.data, url);
            }
        } catch (err) {
            console.error(err);
        }
    };

    const handleSave = (song) => toggleLove(song);
    const handleAdd = (song) => addToQueue(song);

    if (loading) {
        return (
            <div className="page" style={{padding:"1em"}}>
                <p>加载中...</p>
            </div>
        );
    }

    if (!album) {
        return (
            <div className="page" style={{padding:"1em"}}>
                <p>专辑不存在</p>
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
                    {album.album_name}
                </span>
            </div>

            <div style={{display:"flex",gap:"1em",marginBottom:"1em",flexShrink:0}}>
                {album.cover_url && (
                    <img
                        src={album.cover_url}
                        alt={album.album_name}
                        style={{
                            width:"40vw",maxWidth:200,aspectRatio:"1/1",
                            borderRadius:8,objectFit:"cover",flexShrink:0,
                        }}
                    />
                )}
                <div style={{flex:1,minWidth:0,display:"flex",flexDirection:"column",justifyContent:"flex-end"}}>
                    <h2 style={{margin:0,
                        overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>
                        {album.album_name}
                    </h2>
                    <p style={{color:"#666",margin:"0.3em 0",fontSize:"0.9em",
                        overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>
                        {album.artist_name ? `歌手: ${album.artist_name}` : ""}
                    </p>
                    <p style={{color:"#999",fontSize:"0.8em",margin:0}}>
                        {album.songs_count || songs.length} 首
                    </p>
                </div>
            </div>

            {/* 歌曲列表（可滚动） */}
            <div style={{flex:1,width:"100%",overflow:"auto",minHeight:0}}>
                {songs.length === 0 ? (
                    <p style={{color:"#999",textAlign:"center"}}>暂无歌曲</p>
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
                )}
            </div>

            <div style={{height:"20vh",flexShrink:0}} />
        </div>
    );
}
