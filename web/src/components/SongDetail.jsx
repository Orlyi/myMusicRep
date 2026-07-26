import {ListPlus, Heart, CirclePlus, Download, Trash2, DiscAlbum, UserRound, Headphones, X, Check} from "lucide-react";
import {usePlayer} from "../layouts/PlayerContext.jsx";
import {useRef, useEffect, useState} from "react";
import {useLocation, useNavigate} from "react-router-dom";
import {myPlaylists, addSongToPlaylist} from "../api/playlists.js";

export function SongDetail({onAdd, onSave, onAddToPlaylist, onDownload}){
    const {closeDetail, addToQueue, toggleLove, lovedSet, detailSong, detailOnDelete} = usePlayer();
    const drawerRef = useRef(null);
    const overlayRef = useRef(null);
    const startY = useRef(0);
    const location = useLocation();
    const navigate = useNavigate();

    const [showPlaylistPicker, setShowPlaylistPicker] = useState(false);
    const [userPlaylists, setUserPlaylists] = useState([]);

    const effectiveSong = detailSong;
    const isLoved = effectiveSong ? lovedSet.has(effectiveSong.song_id) : false;

    // 判断当前页面：搜索页不显示删除，其他页面都显示
    const isSearchPage = location.pathname === '/search';

    const handleDelete = () => {
        if (isSearchPage) return;
        if (detailOnDelete) detailOnDelete(effectiveSong);
        handleCloseAnimated();
    };

    const handleClose = () => closeDetail?.();

    // 打开动画
    useEffect(() => {
        if (!effectiveSong) return;
        requestAnimationFrame(() => {
            if (drawerRef.current) drawerRef.current.classList.add('open');
            if (overlayRef.current) overlayRef.current.classList.add('show');
        });
    }, [effectiveSong]);

    const handleCloseAnimated = () => {
        if (drawerRef.current) drawerRef.current.classList.remove('open');
        if (overlayRef.current) overlayRef.current.classList.remove('show');
        setTimeout(() => handleClose(), 250);
    };

    // 触摸关闭
    const handleTouchStart = (e) => { startY.current = e.touches[0].clientY; };
    const handleTouchMove = (e) => {
        if (!drawerRef.current) return;
        const dy = e.touches[0].clientY - startY.current;
        if (dy > 0) drawerRef.current.style.transform = `translateY(${dy}px)`;
    };
    const handleTouchEnd = (e) => {
        if (!drawerRef.current) return;
        const dy = e.changedTouches[0].clientY - startY.current;
        if (dy > 80) handleCloseAnimated();
        drawerRef.current.style.transform = "";
    };

    // 打开"加入歌单"面板 → 拉取我的歌单
    const handleOpenPlaylistPicker = async () => {
        try {
            const res = await myPlaylists({ page: 1, page_size: 50 });
            setUserPlaylists(res.data?.items || []);
            setShowPlaylistPicker(true);
        } catch (err) {
            console.log("获取歌单失败", err);
        }
    };

    // 加入指定歌单
    const handleAddToPlaylist = async (pl) => {
        if (!effectiveSong?.song_id) return;
        try {
            await addSongToPlaylist(pl.playlist_id, effectiveSong.song_id);
            setShowPlaylistPicker(false);
            handleCloseAnimated();
        } catch (err) {
            console.log("加入歌单失败", err);
        }
    };

    if (!effectiveSong || isSearchPage) return null;

    const handleAdd = () => {
        addToQueue(effectiveSong);
        onAdd?.(effectiveSong);
        handleCloseAnimated();
    };

    const handleSave = () => {
        toggleLove(effectiveSong);
        onSave?.(effectiveSong);
    };

    const HANDLE_MAP = [
        {key:"onAdd",name:"添加",icon:<ListPlus />,handler: handleAdd},
        {key:"onSave",name:"收藏",icon:<Heart fill={isLoved ? "#ff0000" : "none"} color={isLoved ? "#ff0000" : "currentColor"} />,handler: handleSave},
        {key:"onAddToPlaylist",name:"歌单",icon:<CirclePlus />,handler: handleOpenPlaylistPicker},
        {key:"onDownload",name:"下载",icon:<Download />,handler: (s) => { onDownload?.(s); handleCloseAnimated(); }},
        ...(!isSearchPage && detailOnDelete ? [{key:"onDelete",name:"删除",icon:<Trash2 />,handler: handleDelete}] : []),
    ];

    const MESSAGE_MAP = [
        {key:"song", value: effectiveSong.song_name || effectiveSong.name || "未知", name:"歌曲", icon:<Headphones />},
        {key:"album", value: effectiveSong.album_name || "", name:"专辑", icon:<DiscAlbum />},
        {key:"artist", value: effectiveSong.artist_name || effectiveSong.artist_names || "", name:"歌手", icon:<UserRound />},
    ];

    return (
        <>
            {/* 歌单选择器（覆盖在抽屉之上） */}
            {showPlaylistPicker && (
                <div
                    style={{
                        position:"fixed", inset:0, zIndex:2000,
                        display:"flex", alignItems:"center", justifyContent:"center",
                        background:"rgba(0,0,0,0.4)",
                    }}
                    onClick={() => setShowPlaylistPicker(false)}
                >
                    <div
                        style={{
                            background:"#fff", borderRadius:12, width:"75vw", maxWidth:320, maxHeight:"60vh",
                            display:"flex", flexDirection:"column", overflow:"hidden",
                        }}
                        onClick={e => e.stopPropagation()}
                    >
                        <div style={{display:"flex", justifyContent:"space-between", alignItems:"center", padding:"1em 1em 0.5em"}}>
                            <span style={{fontWeight:600, fontSize:"0.95em"}}>加入歌单</span>
                            <X size={18} style={{cursor:"pointer"}} onClick={() => setShowPlaylistPicker(false)} />
                        </div>
                        <div style={{overflow:"auto", padding:"0 0.5em 0.5em"}}>
                            {userPlaylists.length === 0 ? (
                                <p style={{textAlign:"center", color:"#999", fontSize:"0.85em", padding:"1em 0"}}>还没有歌单</p>
                            ) : (
                                userPlaylists.map(pl => (
                                    <div
                                        key={pl.playlist_id}
                                        onClick={() => handleAddToPlaylist(pl)}
                                        style={{
                                            display:"flex", alignItems:"center", gap:"0.6em", padding:"0.6em",
                                            borderRadius:8, cursor:"pointer",
                                        }}
                                        onMouseEnter={e => e.currentTarget.style.background="#f5f5f5"}
                                        onMouseLeave={e => e.currentTarget.style.background="transparent"}
                                    >
                                        <img
                                            src={pl.cover_url ? (pl.cover_url.startsWith("/static") ? `http://localhost:8000${pl.cover_url}` : pl.cover_url) : ""}
                                            alt=""
                                            style={{width:"2.5em", height:"2.5em", borderRadius:6, objectFit:"cover", background:"#eee"}}
                                        />
                                        <div style={{flex:1, minWidth:0}}>
                                            <div style={{fontSize:"0.9em", overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap"}}>
                                                {pl.playlist_name}
                                            </div>
                                            <div style={{fontSize:"0.75em", color:"#999"}}>{pl.songs_count || 0}首</div>
                                        </div>
                                        <Check size={16} color="#999" />
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                </div>
            )}

            <div className="bottom-drawer-overlay" ref={overlayRef} onClick={handleCloseAnimated} />
            <div className="bottom-drawer"
                ref={drawerRef}
                onTouchStart={handleTouchStart}
                onTouchMove={handleTouchMove}
                onTouchEnd={handleTouchEnd}>
                <div className="drawer-handle" />
                <button className="drawer-close" onClick={handleCloseAnimated}>
                    <X size={20} />
                </button>

                <div className="song-detail flex column" style={{paddingTop:"1em"}}>
                    <div className="song-detail-handle flex" style={{width:"100%",gap:"5%",height:"auto",justifyContent:"space-between",marginBottom:"1em"}}>
                        {HANDLE_MAP.map((t) => (
                            <div key={t.key} className="detail-item flex column" onClick={() => t.handler(effectiveSong)} style={{width:"20%",alignItems:"center",gap:"0.3em"}}>
                                <div>{t.icon}</div>
                                <span className="small-font">{t.name}</span>
                            </div>
                        ))}
                    </div>
                    <div className="flex column" style={{width:"100%",overflow:"auto",paddingBottom:"1em",paddingLeft:"1em",boxSizing:"border-box"}}>
                        {MESSAGE_MAP.map((m, i) => (
                            <div key={i} className="flex" style={{width:"100%",height:"5vh",justifyContent:"flex-start",gap:"0.5em"}}>
                                {m.icon}
                                {m.key === 'album' && effectiveSong.album_id ? (
                                    <span className="small-font" style={{cursor:"pointer",color:"#1db954"}} onClick={() => handleCloseAnimated() || navigate(`/album/${effectiveSong.album_id}`)}>
                                        {m.name}: {m.value}
                                    </span>
                                ) : m.key === 'artist' && effectiveSong.artist_id ? (
                                    <span className="small-font" style={{cursor:"pointer",color:"#1db954"}} onClick={() => handleCloseAnimated() || navigate(`/artist/${effectiveSong.artist_id}`)}>
                                        {m.name}: {m.value}
                                    </span>
                                ) : (
                                    <span className="small-font">{m.name}: {m.value}</span>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </>
    );
}
