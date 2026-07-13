import {Heart, Play, Pause, ListVideo} from "lucide-react"
import {usePlayer} from "../layouts/PlayerContext.jsx";
import {saveSong, unsaveSong} from "../api/favorites.js";

export function PlayerBar({onOpenQueue}){
    const {currentSong, isPlaying, openPlayer, pause, resume, updateCurrentSong} = usePlayer()
    if(!currentSong) return null


    const handleSave = async (song) =>{
        try{
            const loved = song.is_love
            loved ? await unsaveSong(song.song_id) : await saveSong(song.song_id)
            updateCurrentSong(song, {is_love: !loved})
        }catch (err){
            console.log(err)
        }
    }

    return(
        <div className="player-bar" style={{display:"flex",justifyContent:"center",alignItems:"center"}}>
            <img src={currentSong.picture_url} style={{height:"2em",aspectRatio:"1/1",cursor:"pointer"}} onClick={openPlayer} />
            <div style={{width:"60vw",overflow:"hidden",flex:1}}>
                {currentSong.song_name}-<span style={{fontSize:"0.8em"}}> {currentSong.artist_name}</span>
            </div>
            <div className="Icon">
                <Heart size={20} fill={currentSong.is_love? "#ff0000": "none"} color={currentSong.is_love? "#ff0000": "currentColor"} onClick={()=>handleSave(currentSong)} ></Heart>
            {isPlaying? <Pause onClick={pause} size={20}></Pause>: <Play onClick={resume} size={20}></Play>}
            <ListVideo onClick={()=>onOpenQueue()} size={20}></ListVideo>
            </div>


        </div>
    )
}
