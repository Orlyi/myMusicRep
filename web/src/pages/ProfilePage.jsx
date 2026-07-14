import {useOutletContext, useNavigate} from "react-router-dom";
import {useEffect, useState} from "react";
import {getMyInfo, getRecentListens} from "../api/users.js";
import {listFavorites} from "../api/favorites.js";
import {myPlaylists} from "../api/playlists.js";
import useAuth from "../hooks/useAuth.js";
import {SongItem} from "../components/SongItem.jsx";
import {PlaylistItem} from "../components/PlaylistItem.jsx";
import "./ProfilePage.css"
import {usePlayer} from "../layouts/PlayerContext.jsx";
import {downloadSong} from "../api/songs.js";
import {SearchSongItem} from "../components/SearchSongItem.jsx";

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
    const {play, addToQueue, toggleLove, lovedSet, initLoveState, openDetail}= usePlayer()

    const handlePlay = async (song) =>{
        try{
            const res = await downloadSong(song.song_id)
            if(res.data?.download_url){
                play(res.data, res.data.download_url)
            }
        }catch (err){
            console.log(err)
        }
    }

    const handleSave = (song) => toggleLove(song)

    // "听过"的删除：从当前列表和 Redis 移除
    const handleHistoryDelete = (song) => {
        setHistory(prev => prev.filter(item => item.song_id !== song.song_id))
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
                                onClick={()=>handlePlay(item)}
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
                return playlists.length === 0 ? (
                    <span className="empty-hint">还没有歌单</span>
                ) : (
                    <ul className="song-list">
                        {playlists.map(item=>(
                            <PlaylistItem
                                key={item.playlist_id}
                                list={item}
                                onOpen={(id) => navigate(`/playlist/${id}`)}
                            />
                        ))}
                    </ul>
                )
        }
    }

    return (
        <div className="profile-page">
            <section className="profile-info" onClick={()=>navigate("/profile/detail")}>
                <div className="avatar">
                    {user?.avatar_url ? (
                        <img src={`http://localhost:8000${user.avatar_url}`} alt="头像" style={{width:"100%",height:"100%",borderRadius:"50%",objectFit:"cover"}} />
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
            
        </div>
    )
}