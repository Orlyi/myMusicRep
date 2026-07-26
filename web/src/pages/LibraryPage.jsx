import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { topSongs, topAlbums, topArtists } from "../api/ranking.js";
import { networkPlayUrl } from "../api/search.js";
import { SongItem } from "../components/SongItem.jsx";
import { usePlayer } from "../layouts/PlayerContext.jsx";
import { Headphones, DiscAlbum, UserRound, Trophy } from "lucide-react";

const TABS = [
    { key: "songs", label: "歌曲", icon: <Headphones size={16} /> },
    { key: "albums", label: "专辑", icon: <DiscAlbum size={16} /> },
    { key: "artists", label: "歌手", icon: <UserRound size={16} /> },
];

export default function LibraryPage() {
    const navigate = useNavigate();
    const { play, addToQueue, toggleLove, lovedSet, openDetail } = usePlayer();
    const [activeTab, setActiveTab] = useState("songs");
    const [data, setData] = useState({ songs: [], albums: [], artists: [] });
    const [loading, setLoading] = useState(true);

    const fetchData = async (tab) => {
        setLoading(true);
        try {
            if (tab === "songs") {
                const res = await topSongs({ limit: 30 });
                setData(prev => ({ ...prev, songs: res.data?.items || [] }));
            } else if (tab === "albums") {
                const res = await topAlbums({ limit: 30 });
                setData(prev => ({ ...prev, albums: res.data?.items || [] }));
            } else if (tab === "artists") {
                const res = await topArtists({ limit: 30 });
                setData(prev => ({ ...prev, artists: res.data?.items || [] }));
            }
        } catch (err) {
            console.error("获取排行榜失败", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { fetchData(activeTab); }, [activeTab]);

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

    return (
        <div className="page" style={{ display: "flex", flexDirection: "column" }}>
            {/* 标题 */}
            <div style={{ display: "flex", alignItems: "center", gap: "0.3em", padding: "0.5em 0.8em", flexShrink: 0 }}>
                <Trophy size={20} />
                <span style={{ fontSize: "1.1em", fontWeight: 600 }}>排行榜</span>
            </div>

            {/* Tab */}
            <div style={{ display: "flex", flexShrink: 0, borderBottom: "1px solid #eee" }}>
                {TABS.map(t => (
                    <div key={t.key}
                        onClick={() => setActiveTab(t.key)}
                        style={{
                            flex: 1, textAlign: "center", padding: "0.6em 0", cursor: "pointer",
                            display: "flex", alignItems: "center", justifyContent: "center", gap: "0.3em",
                            borderBottom: activeTab === t.key ? "2px solid #333" : "2px solid transparent",
                            fontWeight: activeTab === t.key ? 600 : 400,
                            color: activeTab === t.key ? "#333" : "#999",
                        }}>
                        {t.icon}
                        <span>{t.label}</span>
                    </div>
                ))}
            </div>

            {/* 内容 */}
            <div style={{ flex: 1, width: "100%", overflow: "auto", minHeight: 0 }}>
                {loading ? (
                    <p style={{ textAlign: "center", color: "#999", padding: "2em 0" }}>加载中...</p>
                ) : activeTab === "songs" ? (
                    data.songs.length === 0 ? (
                        <p style={{ textAlign: "center", color: "#999", padding: "2em 0" }}>暂无歌曲</p>
                    ) : (
                        <ul className="song-list" style={{ listStyle: "none", paddingLeft: "4vw", margin: 0, width: "88vw" }}>
                            {data.songs.map((item, i) => (
                                <div key={item.song_id} style={{ display: "flex", alignItems: "center", gap: "0.5em"}}>
                                    <span style={{
                                        width: "1.5em", textAlign: "center", fontWeight: 700,
                                        color: i < 3 ? ["#ff4545", "#ff8c00", "#ffc107"][i] : "#999",
                                        fontSize: i < 3 ? "1.1em" : "0.9em", flexShrink: 0,
                                    }}>{i + 1}</span>
                                    <div style={{ flex: 1, minWidth: 0 }}>
                                        <SongItem
                                            song={{ ...item, is_love: lovedSet.has(item.song_id) }}
                                            onPlay={() => handlePlay(item)}
                                            onSave={() => toggleLove(item)}
                                            onAdd={() => addToQueue(item)}
                                            onMore={(s) => openDetail(s, null)}
                                        />
                                    </div>
                                </div>
                            ))}
                        </ul>
                    )
                ) : activeTab === "albums" ? (
                    data.albums.length === 0 ? (
                        <p style={{ textAlign: "center", color: "#999", padding: "2em 0" }}>暂无专辑</p>
                    ) : (
                        <div style={{ padding: "0 1em" }}>
                            {data.albums.map((item, i) => (
                                <div key={item.album_id}
                                    onClick={() => navigate(`/album/${item.album_id}`)}
                                    style={{ display: "flex", alignItems: "center", gap: "0.8em", padding: "0.7em 0", borderBottom: "1px solid #f5f5f5", cursor: "pointer" }}>
                                    <span style={{
                                        width: "1.5em", textAlign: "center", fontWeight: 700,
                                        color: i < 3 ? ["#ff4545", "#ff8c00", "#ffc107"][i] : "#999",
                                        fontSize: i < 3 ? "1.1em" : "0.9em", flexShrink: 0,
                                    }}>{i + 1}</span>
                                    <img src={item.cover_url || ""} alt=""
                                        style={{ width: "3.5em", height: "3.5em", borderRadius: 6, objectFit: "cover", flexShrink: 0 }} />
                                    <div style={{ flex: 1, minWidth: 0 }}>
                                        <div style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", fontSize: "0.95em" }}>
                                            {item.album_name}
                                        </div>
                                        <div style={{ fontSize: "0.8em", color: "#999", marginTop: "0.2em" }}>{item.songs_count} 首</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )
                ) : (
                    data.artists.length === 0 ? (
                        <p style={{ textAlign: "center", color: "#999", padding: "2em 0" }}>暂无歌手</p>
                    ) : (
                        <div style={{ padding: "0 1em" }}>
                            {data.artists.map((item, i) => (
                                <div key={item.artist_id}
                                    onClick={() => navigate(`/artist/${item.artist_id}`)}
                                    style={{ display: "flex", alignItems: "center", gap: "0.8em", padding: "0.7em 0", borderBottom: "1px solid #f5f5f5", cursor: "pointer" }}>
                                    <span style={{
                                        width: "1.5em", textAlign: "center", fontWeight: 700,
                                        color: i < 3 ? ["#ff4545", "#ff8c00", "#ffc107"][i] : "#999",
                                        fontSize: i < 3 ? "1.1em" : "0.9em", flexShrink: 0,
                                    }}>{i + 1}</span>
                                    <img src={item.avartar_url || ""} alt=""
                                        style={{ width: "3.5em", height: "3.5em", borderRadius: "50%", objectFit: "cover", flexShrink: 0 }} />
                                    <div style={{ flex: 1, minWidth: 0 }}>
                                        <div style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", fontSize: "0.95em" }}>
                                            {item.artist_name}
                                        </div>
                                        <div style={{ fontSize: "0.8em", color: "#999", marginTop: "0.2em" }}>
                                            {item.songs_count} 首歌 · {item.fans_count} 粉丝
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )
                )}
            </div>

            <div style={{ height: "20vh", flexShrink: 0 }} />
        </div>
    );
}
