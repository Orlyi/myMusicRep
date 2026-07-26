import { Trash2 } from "lucide-react";

function resolveCover(url) {
    if (!url) return "http://localhost:8000/static/defaults/photo.jpg"
    if (url.startsWith("/static")) return `http://localhost:8000${url}`
    return url
}

export function PlaylistItem({list, onOpen, onDelete}){
    return(
        <div style={{display:"flex",justifyContent:"center",alignItems:"center"}}>
            <img
                src={resolveCover(list?.cover_url)}
                alt=""
                style={{height:"2.5em", borderRadius:"4px", aspectRatio:"1/1", objectFit: "cover", cursor:"pointer"}}
                onClick={()=>onOpen?.(list.playlist_id)}
            />

            <div className="list-item-content" onClick={()=>onOpen?.(list.playlist_id)} style={{flex:1,marginLeft:"0.5em"}}>
                <div>{list?.playlist_name || "未知"}</div>
                <div style={{fontSize:"0.8em",color:"#727272"}}>{list?.songs_count || 0}首</div>
            </div>

            {onDelete && (
                <Trash2 size={18} color="#999" style={{cursor:"pointer", flexShrink:0, marginRight:"0.5em"}}
                    onClick={(e) => { e.stopPropagation(); onDelete(list); }}
                />
            )}
        </div>
    )
}
