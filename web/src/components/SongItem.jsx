
import {Heart, ListPlus, EllipsisVertical} from "lucide-react"


export function SongItem({song, onPlay, onSave, onAdd, onMore}){
    return(
        <div style={{display:"flex",justifyContent:"center",alignItems:"center",height:"10vh" }} className="active">

            <img src={song?.picture_url} alt="?" style={{height:"2.5em", borderRadius:"4px", aspectRatio:"1/1", objectFit: "cover"}}></img>

            <div className="song-item-content" onClick={()=>onPlay?.(song.song_id)} style={{width:"60%",marginLeft:"0.5em",overflow:"hidden"}}>
                <div style={{overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>
                    {song?.song_name || "未知"}
                </div>
                <div style={{fontSize:"0.8em",color:"#727272",overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>
                    {song?.artist_name || "未知"}
                </div>
            </div>
            <div className="Icon">
                <Heart size={20} fill={song.is_love? "#ff0000": "none"} color={song.is_love? "#ff0000": "currentColor"} onClick={(e) => { e.stopPropagation(); onSave?.(song); }}></Heart>
            <ListPlus size={20}  onClick={(e) => { e.stopPropagation(); onAdd?.(song); }}></ListPlus>
            <EllipsisVertical size={20} onClick={(e) => { e.stopPropagation(); onMore?.(song); }}></EllipsisVertical>
            </div>

        </div>
    )
}
