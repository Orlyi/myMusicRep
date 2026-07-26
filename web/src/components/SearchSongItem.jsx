import {Heart, ListPlus, EllipsisVertical} from "lucide-react";

export function SearchSongItem({song, onPlay, onSave, onAdd, onMore}){

    return(
        <div className="search-song-item flex" style={{height:"8vh",width:"100%"}} onClick={() => onPlay?.(song.platform_id)}>
            <div className="search-song-content" style={{flex:"1", minWidth:0,paddingLeft:"1em"}}>
                <div style={{
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                }}>{song?.name || song?.song_name}</div>
                <div className="small-font" style={{
                    textAlign:"left",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                }}>
                    {song?.artist_names || song?.artist_name}
                    {song?.album_name && ` · ${song.album_name}`}
                </div>
            </div>

            <div className="search-song-actions" style={{display:"flex",gap:"0.6em"}}>
                <Heart size="1em" fill={song.is_love? "#ff0000": "none"} color={song.is_love? "#ff0000": "currentColor"} onClick={(e) => { e.stopPropagation(); onSave?.(song); }}></Heart>
                <ListPlus size="1em" onClick={(e) => { e.stopPropagation(); onAdd?.(song); }}></ListPlus>
                {onMore && <EllipsisVertical size="1em" onClick={(e) => { e.stopPropagation(); onMore?.(song); }} />}
            </div>
        </div>
    )
}