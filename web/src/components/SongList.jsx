  import {Heart, X, GripVertical} from "lucide-react"

  export function SongList({song, isActive, onPlay, onSave, onRemove}){
      return(
          <div className={`song-list-item ${isActive ? 'active' : ''}`}
               style={{
                   display:"flex", alignItems:"center", gap:8, padding:"0.5em",
                   background: isActive ? '#1db95420' : 'transparent',
                   borderRadius: 8,
               }}
               onClick={() => onPlay?.(song)}>

              <GripVertical size={16} color="#999" style={{flexShrink:0}} />


              <div style={{flex:1, minWidth:0, overflow:"hidden"}}>
                  <div style={{fontWeight: isActive ? 600 : 400,
                               color: isActive ? '#1db954' : undefined,
                               overflow:"hidden", whiteSpace:"nowrap"}}>
                      {isActive ? (
                          <div className="marquee-wrap" style={{display:"inline-block",verticalAlign:"bottom",width:"auto",maxWidth:"100%"}}>
                              <span className="marquee-text" style={{verticalAlign:"bottom"}}>
                                  {song?.song_name || "未知"} <span style={{fontSize:"0.7em"}}>- {song?.artist_name || "未知"}</span>
                                  <span style={{display:"inline-block",width:"3em"}} />
                                  {song?.song_name || "未知"} <span style={{fontSize:"0.7em"}}>- {song?.artist_name || "未知"}</span>
                              </span>
                          </div>
                      ) : (
                          <span style={{overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap",display:"inline-block",maxWidth:"100%"}}>
                              {song?.song_name || "未知"} - <span style={{fontSize:"0.6em",color: "rgb(114,114,114)"}}>{song?.artist_name || "未知"}</span>
                          </span>
                      )}
                  </div>

              </div>

              <Heart size={16}
                     fill={song?.is_love ? "#ff0000" : "none"}
                     color={song?.is_love ? "#ff0000" : "#999"}
                     onClick={(e) => { e.stopPropagation(); onSave?.(song); }} />

              <X size={16} color="#999"
                 onClick={(e) => { e.stopPropagation(); onRemove?.(song); }} />
          </div>
      )
  }