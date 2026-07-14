import {ListPlus, Heart, CirclePlus, Download, Trash2, DiscAlbum, UserRound, Headphones, X} from "lucide-react";
import {usePlayer} from "../layouts/PlayerContext.jsx";
import {useRef, useEffect} from "react";
import {useLocation, useNavigate} from "react-router-dom";

export function SongDetail({onAdd, onSave, onAddToPlaylist, onDownload}){
    const {closeDetail, addToQueue, toggleLove, lovedSet, detailSong, detailOnDelete, removeFromQueue} = usePlayer();
    const drawerRef = useRef(null);
    const overlayRef = useRef(null);
    const startY = useRef(0);
    const location = useLocation();

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

    if (!effectiveSong) return null;

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
        {key:"onAddToPlaylist",name:"歌单",icon:<CirclePlus />,handler: (s) => { onAddToPlaylist?.(s); handleCloseAnimated(); }},
        {key:"onDownload",name:"下载",icon:<Download />,handler: (s) => { onDownload?.(s); handleCloseAnimated(); }},
        ...(!isSearchPage && detailOnDelete ? [{key:"onDelete",name:"删除",icon:<Trash2 />,handler: handleDelete}] : []),
    
    ];

    const MESSAGE_MAP = [
        {value: effectiveSong.song_name || effectiveSong.name || "未知", name:"歌曲", icon:<Headphones />},
        {value: effectiveSong.album_name || "", name:"专辑", icon:<DiscAlbum />},
        {value: effectiveSong.artist_name || effectiveSong.artist_names || "", name:"歌手", icon:<UserRound />},
    ];

    return (
        <>
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
                                <span className="small-font">{m.name}: {m.value}</span>
                            </div>
                        ))}

                    </div>
                </div>
            </div>
        </>
    );
}
