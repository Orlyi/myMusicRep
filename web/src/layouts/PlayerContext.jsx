
import {useState, useRef, useMemo, useCallback, createContext, useContext, useEffect} from "react";
import {getLyrics} from "../api/lyric.js";

const PlayerContext = createContext()

export function usePlayer(){
    return useContext(PlayerContext)
}

const MODE = { LOOP: 'loop', SINGLE: 'single', SHUFFLE: 'shuffle' }
const MODE_ORDER = [MODE.LOOP, MODE.SINGLE, MODE.SHUFFLE]

function generateShuffled(len) {
    const arr = Array.from({length: len}, (_, i) => i)
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]]
    }
    return arr
}

export function PlayerProvider({ children }){
    const [playerOpen, setPlayerOpen] = useState(false)
    const openPlayer = () => setPlayerOpen(true)
    const closePlayer = () => setPlayerOpen(false)

    const [queue, setQueue] = useState([])
    const [currentIndex, setCurrentIndex] = useState(-1)
    const [isPlaying, setIsPlaying] = useState(false)
    const [mode, setMode] = useState(MODE.LOOP)
    const [shuffledOrder, setShuffledOrder] = useState([])
    const audioRef = useRef(null)

    const [lyrics, setLyrics] = useState(null)

    const currentSong = useMemo(() => {
        if (currentIndex < 0 || queue.length === 0) return null
        const idx = mode === MODE.SHUFFLE
            ? (shuffledOrder[currentIndex] ?? currentIndex)
            : currentIndex
        return queue[idx] ?? null
    }, [queue, currentIndex, mode, shuffledOrder])

    // 当前歌曲切换时自动拉歌词
    useEffect(() => {
        if (!currentSong?.song_id) {
            setLyrics(null)
            return
        }
        setLyrics(null)
        getLyrics(currentSong.song_id)
            .then(res => setLyrics(res.data))
            .catch(() => setLyrics(null))
    }, [currentSong?.song_id])

    const resolveUrl = (url) => url?.startsWith("http") ? url : `http://localhost:8000${url}`

    const playIndex = useCallback((index) => {
        if (index < 0 || index >= queue.length) return
        setCurrentIndex(index)
        setIsPlaying(true)
        const song = queue[index]
        if (song && audioRef.current) {
            const newUrl = resolveUrl(song.url || song.download_url)
            if (audioRef.current.src !== newUrl) {
                audioRef.current.src = newUrl
            }
            audioRef.current.play().catch(err => {
                if (err.name !== 'AbortError') console.log('播放失败:', err)
            })
        }
    }, [queue])

    const play = useCallback((song, url) => {
        const item = { ...song, url: resolveUrl(url || song.download_url) }
        const existingIdx = queue.findIndex(s => s.song_id === song.song_id)
        if (existingIdx >= 0) {
            setQueue(prev => prev.map((s, i) => i === existingIdx ? item : s))
            playIndex(existingIdx)
        } else {
            setQueue(prev => [...prev, item])
            setTimeout(() => {
                setCurrentIndex(queue.length)
                setIsPlaying(true)
                if (audioRef.current) {
                    audioRef.current.src = item.url
                    audioRef.current.play().catch(err => {
                        if (err.name !== 'AbortError') console.log('播放失败:', err)
                    })
                }
            }, 0)
        }
    }, [queue, playIndex])

    const addToQueue = useCallback((song) => {
        const item = { ...song, url: resolveUrl(song.url || song.download_url) }
        setQueue(prev => {
            const exists = prev.some(s => s.song_id === song.song_id)
            if (exists) return prev
            return [...prev, item]
        })
    }, [])

    const playQueue = useCallback((list, startIndex = 0) => {
        setQueue(list)
        setShuffledOrder(generateShuffled(list.length))
        setTimeout(() => {
            if (startIndex < 0 || startIndex >= list.length) return
            setCurrentIndex(startIndex)
            setIsPlaying(true)
            const song = list[startIndex]
            if (song && audioRef.current) {
                audioRef.current.src = resolveUrl(song.url || song.download_url)
                audioRef.current.play().catch(err => {
                    if (err.name !== 'AbortError') console.log('播放失败:', err)
                })
            }
        }, 0)
    }, [])

    const next = useCallback(() => {
        if (queue.length === 0) return
        if (mode === MODE.SINGLE) {
            audioRef.current.currentTime = 0
            audioRef.current?.play()
            return
        }
        const nextIdx = currentIndex + 1 >= queue.length ? 0 : currentIndex + 1
        playIndex(nextIdx)
    }, [queue, currentIndex, mode, playIndex])

    const prev = useCallback(() => {
        if (queue.length === 0) return
        if (audioRef.current?.currentTime > 3) {
            audioRef.current.currentTime = 0
            return
        }
        const prevIdx = currentIndex - 1 < 0 ? queue.length - 1 : currentIndex - 1
        playIndex(prevIdx)
    }, [queue, currentIndex, playIndex])

    const toggleMode = useCallback(() => {
        setMode(prev => {
            const cur = MODE_ORDER.indexOf(prev)
            return MODE_ORDER[(cur + 1) % MODE_ORDER.length]
        })
    }, [])

    const pause = () => {
        setIsPlaying(false)
        audioRef.current?.pause()
    }

    const resume = () => {
        audioRef.current?.play()
        setIsPlaying(true)
    }

    const updateCurrentSong = useCallback((song, update) => {
        setQueue(prev => prev.map(s =>
            s.song_id === song.song_id ? { ...s, ...update } : s
        ))
    }, [])

    const removeFromQueue = useCallback((song) => {
        setQueue(prev => {
            const idx = prev.findIndex(s => s.song_id === song.song_id)
            if (idx < 0) return prev
            const next = prev.filter((_, i) => i !== idx)
            setTimeout(() => {
                setCurrentIndex(ci => {
                    if (ci === idx) {
                        const newIdx = ci >= next.length ? Math.max(0, next.length - 1) : ci
                        const nextSong = next[newIdx]
                        if (nextSong && audioRef.current) {
                            audioRef.current.src = resolveUrl(nextSong.url || nextSong.download_url)
                            audioRef.current.play().catch(err => {
                                if (err.name !== 'AbortError') console.log('播放失败:', err)
                            })
                        }
                        setIsPlaying(true)
                        return newIdx
                    }
                    if (ci > idx) return ci - 1
                    return ci
                })
            }, 0)
            return next
        })
    }, [])

    const clearQueue = useCallback(() => {
        setQueue([])
        setCurrentIndex(-1)
        setIsPlaying(false)
        if (audioRef.current) {
            audioRef.current.pause()
            audioRef.current.src = ''
        }
    }, [])

    const handleEnded = () => {
        if (mode === MODE.SINGLE) {
            audioRef.current.currentTime = 0
            audioRef.current?.play()
        } else {
            next()
        }
    }

    return(
        <PlayerContext.Provider value={{
            currentSong, isPlaying, lyrics, queue, currentIndex, mode,
            playerOpen, openPlayer, closePlayer,
            play, playQueue, playIndex, next, prev, removeFromQueue, addToQueue, clearQueue,
            pause, resume, toggleMode, updateCurrentSong, audioRef
        }}>
            {children}
            <audio ref={audioRef} onEnded={handleEnded} />
        </PlayerContext.Provider>
    )
}
