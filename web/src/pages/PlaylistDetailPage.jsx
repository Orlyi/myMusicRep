import { useParams, useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { getPlaylist } from "../api/playlists.js";
import { SongItem } from "../components/SongItem.jsx";
import { usePlayer } from "../layouts/PlayerContext.jsx";
import { networkPlayUrl } from "../api/search.js";
import { ChevronLeft, Music } from "lucide-react";

function resolveCover(url) {
    if (!url) return "http://serverIP:8000/static/defaults/photo.jpg"
    if (url.startsWith("/static")) return `http://serverIP:8000${url}`
    return url
}

export default function PlaylistDetailPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { play, addToQueue, toggleLove, lovedSet, openDetail } = usePlayer();

    const [playlist, setPlaylist] = useState(null);
    const [songs, setSongs] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!id) return;
        setLoading(true);
        getPlaylist(id)
            .then((res) => {
                setPlaylist(res.data?.playlist || null);
                setSongs(res.data?.songs || []);
            })
            .catch((err) => console.error("获取歌单详情失败", err))
            .finally(() => setLoading(false));
    }, [id]);

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
    };

    const handleSave = (song) => toggleLove(song);
    const handleAdd = (song) => addToQueue(song);

    if (loading) {
        return (
            <div className="page" style={{ padding: "1em" }}>
                <p>加载中...</p>
            </div>
        );
    }

    if (!playlist) {
        return (
            <div className="page" style={{ padding: "1em" }}>
                <p>歌单不存在</p>
            </div>
        );
    }

    return (
        <div className="page" style={{ display: "flex", flexDirection: "column" }}>

            <div style={{ display: "flex",justifyContent:"center", gap: "0.3em", padding: "0.3em 0", position: "relative", flexShrink: 0 }}>
                <ChevronLeft size={24} onClick={() => navigate(-1)} style={{ cursor: "pointer", left: "5%", position: "fixed" }} />
                <span style={{ fontSize: "1.1em", fontWeight: 600, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {playlist.playlist_name}
                </span>
            </div>


            <div style={{ display: "flex", gap: "1em", marginBottom: "0.5em", flexShrink: 0, padding: "0.5em 1em" }}>
                <img
                    src={resolveCover(playlist.cover_url)}
                    alt={playlist.playlist_name}
                    style={{ width: "35vw", maxWidth: 160, aspectRatio: "1/1", borderRadius: 8, objectFit: "cover", flexShrink: 0 }}
                />
                <div style={{ flex: 1, minWidth: 0, display: "flex", flexDirection: "column", justifyContent: "center" }}>
                    <h2 style={{ margin: "0 0 0.3em 0", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {playlist.playlist_name}
                    </h2>
                    <p style={{ color: "#666", margin: "0.2em 0", fontSize: "0.85em" }}>
                        {playlist.user_name}
                    </p>
                    <div style={{ display: "flex", gap: "0.8em", color: "#999", fontSize: "0.8em" }}>
                        <span style={{ display: "flex", alignItems: "center", gap: "0.2em" }}>
                            <Music size={14} /> {songs.length} 首
                        </span>
                    </div>
                    {playlist.introduction && (
                        <p style={{ color: "#999", fontSize: "0.8em", margin: "0.5em 0 0 0", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                            {playlist.introduction}
                        </p>
                    )}
                </div>
            </div>

            <div style={{ flex: 1, width: "100%", overflow: "auto", minHeight: 0 }}>
                {songs.length === 0 ? (
                    <p style={{ color: "#999", textAlign: "center", padding: "2em 0" }}>暂无歌曲</p>
                ) : (
                    <ul className="song-list" style={{ listStyle: "none", paddingLeft: "4vw", margin: 0, width: "90vw" }}>
                        {songs.map((item) => (
                            <SongItem
                                key={item.song_id}
                                song={{ ...item, is_love: lovedSet.has(item.song_id) }}
                                onPlay={() => handlePlay(item)}
                                onSave={() => handleSave(item)}
                                onAdd={() => handleAdd(item)}
                                onMore={(s) => openDetail(s, null)}
                            />
                        ))}
                    </ul>
                )}
            </div>

            <div style={{ height: "20vh", flexShrink: 0 }} />
        </div>
    );
}
