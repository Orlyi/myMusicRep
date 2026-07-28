import {useOutletContext, useNavigate} from "react-router-dom";
import {useEffect, useState} from "react";
import {getMyInfo, getRecentListens} from "../api/users.js";
import {listFavorites} from "../api/favorites.js";
import {myPlaylists, createPlaylist, deletePlaylist} from "../api/playlists.js";
import {networkPlayUrl} from "../api/search.js";
import useAuth from "../hooks/useAuth.js";
import {SongItem} from "../components/SongItem.jsx";
import {SearchSongItem} from "../components/SearchSongItem.jsx";
import {PlaylistItem} from "../components/PlaylistItem.jsx";
import "./ProfilePage.css"
import {usePlayer} from "../layouts/PlayerContext.jsx";
import {STATIC_BASE} from "../config.js";

export default function ProfilePage(){
    const {setHeaderContent} = useOutletContext()
    const navigate = useNavigate()
    const {logout} = useAuth()
    const [acting, setActing] = useState(1)
    const [userInfo, setUserInfo] = useState(null)
    const [loading, setLoading] = useState(true)
    const [favorites, setFavorites] = useState([])
    const [history, setHistory] = useState([])
    const [playlists, setPlaylists] = useState([])
    const [showCreate, setShowCreate] = useState(false)
    const [createName, setCreateName] = useState("")
    const [createIntro, setCreateIntro] = useState("")
    const {play, addToQueue, toggleLove, lovedSet, initLoveState, openDetail}= usePlayer()

    // 统一播放逻辑：干净本地路径直接播，脏 CDN 走 network/play-url 刷新
    const handlePlay = async (song) => {
        try {
            if (song.download_url && song.download_url.startsWith("/static/music")) {
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
            console.log(err);
        }
    };

    const handleSave = (song) => toggleLove(song)

    // "听过"的删除：从当前列表和 Redis 移除
    const handleHistoryDelete = (song) => {
        setHistory(prev => prev.filter(item => item.song_id !== song.song_id))
    }

    // 创建歌单
    const handleCreatePlaylist = async () => {
        if (!createName.trim()) return
        try {
            await createPlaylist({ playlist_name: createName.trim(), introduction: createIntro.trim() })
            setCreateName("")
            setCreateIntro("")
            setShowCreate(false)
            const res = await myPlaylists({ page: 1, page_size: 20 })
            setPlaylists(res.data?.items || [])
        } catch (err) {
            console.log("创建歌单失败", err)
        }
    }

    // 删除歌单
    const handleDeletePlaylist = async (pl) => {
        if (!window.confirm(`删除歌单「${pl.playlist_name}」？`)) return
        try {
            await deletePlaylist(pl.playlist_id)
            setPlaylists(prev => prev.filter(p => p.playlist_id !== pl.playlist_id))
        } catch (err) {
            console.log("删除歌单失败", err)
        }
    }

    useEffect(() => {
        setHeaderContent(
            <>
            <div className="top-nav-tab" onClick={()=>setActing(1)}><div className={`top-nav-tab-item ${acting=== 1? "larger_fontsize": ""}`}>我的</div><div className={`underline tab ${acting=== 1? "width_zero": ""}`}></div></div>
            <div className="top-nav-tab" onClick={()=>setActing(2)}><div className={`top-nav-tab-item ${acting=== 2? "larger_fontsize": ""}`}>听过</div><div className={`underline tab ${acting=== 2? "width_zero": ""}`}></div></div>
            <div className="top-nav-tab" onClick={()=>setActing(3)}><div className={`top-nav-tab-item ${acting=== 3? "larger_fontsize": ""}`}>歌单</div><div className={`underline tab ${acting=== 3? "width_zero": ""}`}></div></div>
            </>
        )
        return ()=>setHeaderContent(null)
    }, [acting, setHeaderContent]);

    const fetchInfo = async () => {
        try{
            const res = await getMyInfo()
            console.log('[ProfilePage] getMyInfo result:', res)
            setUserInfo(res.data)
            setLoading(false)
        } catch(err){
            console.log("获取用户信息失败", err)
            setLoading(false)
        }
    }

    useEffect(()=>{
        fetchInfo()
    }, [])

    useEffect(()=>{
        if(acting === 1){
            listFavorites({type:"song", page:1, page_size:20}).then(res=>{
                const items = res.data?.items || []
                setFavorites(items)
                // 同步到全局 lovedSet
                initLoveState(items.map(i => i.song_id))
            }).catch(err=>{console.log("获取收藏失败", err)})
        }
        if(acting === 2){
            getRecentListens({page:1, page_size:20}).then(res=>{
                setHistory(res.data?.items || [])
            }).catch(err=>{console.log("获取最近播放失败", err)})
        }
        if(acting === 3){
            myPlaylists({page:1, page_size:20}).then(res=>{
                setPlaylists(res.data?.items || [])
            }).catch(err=>{console.log("获取歌单失败", err)})
        }
    }, [acting])

    if(loading){
        return <div className="profile-loading"><span>加载中...</span></div>
    }

    const user = userInfo?.user
    const details = userInfo?.details

    const renderContent = () => {
        switch(acting){
            case 1:
                return favorites.length === 0 ? (
                    <span className="empty-hint">还没有收藏歌曲</span>
                ) : (
                    <ul className="song-list">
                        {favorites.map(item=>(
                            <SongItem
                                key={item.song_id}
                                song={{...item, is_love: lovedSet.has(item.song_id)}}
                                onSave={()=> handleSave(item)}
                                onPlay={()=>handlePlay(item)}
                                onAdd={() => addToQueue(item)}
                                onMore={(s) => openDetail(s, null)}
                            />
                        ))}
                    </ul>
                )
            case 2:
                return history.length === 0 ? (
                    <span className="empty-hint">还没有播放记录</span>
                ) : (
                    <ul className="song-list">
                        {history.map(item=>(
                            <SearchSongItem
                                key={item.song_id}
                                song={{...item, is_love: lovedSet.has(item.song_id)}}
                                onPlay={() => handlePlay(item)}
                                onAdd={() => addToQueue(item)}
                                onSave={() => handleSave(item)}
                                onMore={(s) => openDetail(s, handleHistoryDelete)}
                            />
                        ))}
                    </ul>
                )
            case 3:
                return (
                    <>
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.5em 0.8em" }}>
                            <span style={{ fontSize: "0.85em", color: "#999" }}>共 {playlists.length} 个歌单</span>
                            <button
                                onClick={() => setShowCreate(true)}
                                style={{
                                    background: "#333", color: "#fff", border: "none", borderRadius: "1.5em",
                                    padding: "0.3em 0.8em", fontSize: "0.8em", cursor: "pointer",
                                }}
                            >+ 创建歌单</button>
                        </div>

                        {playlists.length === 0 ? (
                            <span className="empty-hint">还没有歌单</span>
                        ) : (
                            <ul className="song-list">
                                {playlists.map(item=>(
                                    <PlaylistItem
                                        key={item.playlist_id}
                                        list={item}
                                        onOpen={(id) => navigate(`/playlist/${id}`)}
                                        onDelete={handleDeletePlaylist}
                                    />
                                ))}
                            </ul>
                        )}
                    </>
                )
        }
    }

    return (
        <div className="profile-page">
            <section className="profile-info" onClick={()=>navigate("/profile/detail")}>
                <div className="avatar">
                    {user?.avatar_url ? (
                        <img src={`${STATIC_BASE}${user.avatar_url}`} alt="头像" style={{width:"100%",height:"100%",borderRadius:"50%",objectFit:"cover"}} />
                    ) : (
                        user?.user_name?.[0]?.toUpperCase() || "?"
                    )}
                </div>
                <div className="info-text">
                    <h3>{user?.user_name || "..."}</h3>
                </div>
                <div className="info-stats">
                    <div className="stat"><span className="num">{details?.followed_count ?? 0}</span><span className="label">关注</span></div>
                    <div className="stat"><span className="num">{details?.fans_count ?? 0}</span><span className="label">粉丝</span></div>
                </div>
            </section>

            <section className="profile-content">
                {renderContent()}
            </section>

            {/* 创建歌单弹窗 */}
            {showCreate && (
                <div
                    style={{
                        position: "fixed", inset: 0, zIndex: 1000,
                        display: "flex", alignItems: "center", justifyContent: "center",
                        background: "rgba(0,0,0,0.4)",
                    }}
                    onClick={() => setShowCreate(false)}
                >
                    <div
                        style={{
                            background: "#fff", borderRadius: 12, padding: "1.2em", width: "75vw", maxWidth: 300,
                            display: "flex", flexDirection: "column", gap: "0.8em",
                        }}
                        onClick={e => e.stopPropagation()}
                    >
                        <h3 style={{ margin: 0, fontSize: "1em" }}>创建歌单</h3>
                        <input
                            placeholder="歌单名称"
                            value={createName}
                            onChange={e => setCreateName(e.target.value)}
                            style={{
                                border: "1px solid #ddd", borderRadius: 8, padding: "0.6em", fontSize: "0.9em",
                                outline: "none", width: "100%", boxSizing: "border-box",
                            }}
                            autoFocus
                        />
                        <input
                            placeholder="简介（可选）"
                            value={createIntro}
                            onChange={e => setCreateIntro(e.target.value)}
                            style={{
                                border: "1px solid #ddd", borderRadius: 8, padding: "0.6em", fontSize: "0.9em",
                                outline: "none", width: "100%", boxSizing: "border-box",
                            }}
                        />
                        <div style={{ display: "flex", gap: "0.6em", justifyContent: "flex-end" }}>
                            <button
                                onClick={() => setShowCreate(false)}
                                style={{
                                    border: "1px solid #ddd", borderRadius: "1.5em", padding: "0.4em 1em",
                                    background: "#fff", cursor: "pointer", fontSize: "0.85em",
                                }}
                            >取消</button>
                            <button
                                onClick={handleCreatePlaylist}
                                style={{
                                    background: "#333", color: "#fff", border: "none", borderRadius: "1.5em",
                                    padding: "0.4em 1em", cursor: "pointer", fontSize: "0.85em",
                                }}
                            >创建</button>
                        </div>
                    </div>
                </div>
            )}

            <div style={{height:"10vh"}}></div>
        </div>
    )
}
