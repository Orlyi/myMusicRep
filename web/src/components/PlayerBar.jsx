import {Heart, Play, Pause, ListVideo, EllipsisVertical} from "lucide-react"
import {usePlayer} from "../layouts/PlayerContext.jsx";

export function PlayerBar({onOpenQueue}){
    const {currentSong, isPlaying, openPlayer, pause, resume, toggleLove, openDetail} = usePlayer()
    if(!currentSong) return null

    const handleSave = () => toggleLove(currentSong)

    return(
        <div className="player-bar" style={{display:"flex",justifyContent:"center",alignItems:"center"}}>
            <img src={currentSong?.picture_url || null} style={{height:"2em",aspectRatio:"1/1",cursor:"pointer",borderRadius:"0.2em"}} onClick={openPlayer} />
            <div style={{width:"50vw",overflow:"hidden",whiteSpace:"nowrap",display:"flex",alignItems:"center",paddingLeft:"0.3em"}}>
                <div className="marquee-wrap">
                    <span className="marquee-text">
                        {currentSong?.song_name || "未播放"} <span className="small-font">- {currentSong?.artist_name || ""}</span>
                        <span style={{display:"inline-block",width:"4em"}} />
                        {currentSong?.song_name || "未播放"} <span className="small-font">- {currentSong?.artist_name || ""}</span>
                    </span>
                </div>
            </div>
            <div className="Icon">
                <Heart size={20} fill={currentSong.is_love? "#ff0000": "none"} color={currentSong.is_love? "#ff0000": "currentColor"} onClick={handleSave} ></Heart>
            {isPlaying? <Pause onClick={pause} size={20}></Pause>: <Play onClick={resume} size={20}></Play>}
            <EllipsisVertical size={20} onClick={() => openDetail(currentSong)} />
            <ListVideo onClick={()=>onOpenQueue()} size={20}></ListVideo>
            </div>



        </div>
    )
}
