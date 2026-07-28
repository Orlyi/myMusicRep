import {usePlayer} from "../layouts/PlayerContext.jsx";
import {SongList} from "./SongList.jsx";
import {Repeat,Repeat1,Shuffle,Trash2} from "lucide-react"

export function QueueDrawer({open, onClose}){
    const {queue, currentIndex, mode, toggleMode, playIndex, removeFromQueue, clearQueue, toggleLove, lovedSet} = usePlayer()

    const handlePlay = (song) => {
        const idx = queue.findIndex(s => s.song_id === song.song_id)
        playIndex(idx)
    }

    const handleSave = (song) => toggleLove(song)

    const modeIcon = mode === 'loop' ? <Repeat size={16}/>
        : mode === 'single' ? <Repeat1 size={16}/>
        : <Shuffle size={16}/>

    const modeLabel = mode === 'loop' ? '列表循环'
        : mode === 'single' ? '单曲循环'
        : '随机播放'

    return(
        <>
        {open && (<div className="queue-overlay" onClick={onClose} />)}
        <div className={`queue-drawer ${open ? 'openY' : ''}`} onClick={e => e.stopPropagation()}>
            <div className="queue-handle" />

            <h4 style={{fontWeight:"500"}}>正在播放 <span style={{fontSize:"0.6em",color:"rgb(114,114,114)"}}> {queue.length}</span></h4>

            <div style={{display:"flex", paddingBottom:"3vh", justifyContent:"space-between", alignItems:"center"}}>
                <div style={{display:"flex", alignItems:"center", gap:"0.3em",color:"rgb(114,114,114)"}} onClick={toggleMode}>
                    {modeIcon}
                    <span style={{fontSize:"0.8em",color:"rgb(114,114,114)"}}>{modeLabel}</span>
                </div>
                <Trash2 size={16} style={{color:"rgb(114,114,114)"}} onClick={clearQueue} />
            </div>
            <div className="queue-list">
                {queue.map((song, i) => (
                    <SongList
                        key={song.song_id + '-' + i}
                        song={{...song, is_love: lovedSet.has(song.song_id)}}
                        isActive={i === currentIndex}
                        onPlay={handlePlay}
                        onSave={handleSave}
                        onRemove={() => removeFromQueue(song)}
                    />
                ))}
            </div>
        </div>
        </>
    )
}
