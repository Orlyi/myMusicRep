
export function PlaylistItem({list,onOpen}){
    return(
        <div style={{display:"flex",justifyContent:"center",alignItems:"center"}}>

            <img src={list?.cover_url} alt="?" style={{height:"2.5em", borderRadius:"4px", aspectRatio:"1/1", objectFit: "cover"}}></img>

            <div className="list-item-content" onClick={()=>onOpen?.(list.playlist_id)} style={{flex:1,marginLeft:"0.5em"}}>
                <div>
                    {list?.playlist_name || "未知"}
                </div>
                <div style={{fontSize:"0.8em",color:"#727272"}}>
                    {list?.songs_count || 0}首-
                </div>
            </div>
        </div>
    )
}
