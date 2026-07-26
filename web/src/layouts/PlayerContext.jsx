import {useState, useRef, useMemo, useCallback, createContext, useContext, useEffect} from "react";
import {getLyrics} from "../api/lyric.js";
import {saveSong, unsaveSong} from "../api/favorites.js";

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

// 最近播放记录（fire-and-forget，不阻塞播放）
function recordListen(songId) {
    if (!songId) return
    const token = localStorage.getItem('token') || sessionStorage.getItem('token')
    if (!token) return
    fetch(`http://localhost:8000/api/v1/songs/${songId}/listen`, {
        method: 'POST',
        headers: {'Authorization': `Bearer ${token}`}
    }).catch(() => {})
}

export function PlayerProvider({ children }){
    const [playerOpen, setPlayerOpen] = useState(false)
    const openPlayer = () => setPlayerOpen(true)
    const closePlayer = () => setPlayerOpen(false)

    const [detailSong, setDetailSong] = useState(null)
    const [detailOnDelete, setDetailOnDelete] = useState(null)
    const openDetail = useCallback((song, onDeleteCb) => {
        setDetailSong(song)
        setDetailOnDelete(() => onDeleteCb || null)
    }, [])
    const closeDetail = useCallback(() => {
        setDetailSong(null)
        setDetailOnDelete(null)
    }, [])

    const [queue, setQueue] = useState([])
    const [currentIndex, setCurrentIndex] = useState(-1)
    const [isPlaying, setIsPlaying] = useState(false)
    const [mode, setMode] = useState(MODE.LOOP)
    const [shuffledOrder, setShuffledOrder] = useState([])
    const [lovedSet, setLovedSet] = useState(new Set())
    const [onDeleteSong, setOnDeleteSong] = useState(null)
    const audioRef = useRef(null)
    const toggleLock = useRef(false)  // 防重复点击

    const [lyrics, setLyrics] = useState(null)

    const currentSong = useMemo(() => {
        if (currentIndex < 0 || queue.length === 0) return null
        const idx = mode === MODE.SHUFFLE
            ? (shuffledOrder[currentIndex] ?? currentIndex)
            : currentIndex
        const song = queue[idx] ?? null
        if (song) {
            song.is_love = lovedSet.has(song.song_id)
        }
        return song
    }, [queue, currentIndex, mode, shuffledOrder, lovedSet])

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

    // 同步 audio src —— currentSong 变化时保证 audio 有有效源
    useEffect(() => {
        if (!currentSong || !audioRef.current) return
        const newUrl = resolveUrl(currentSong.url || currentSong.download_url || '')
        if (newUrl && audioRef.current.src !== newUrl) {
            audioRef.current.src = newUrl
        }
    }, [currentSong])

    const is_cdn_domain = (url) =>
        url && typeof url === 'string' && (
            url.includes('music.126.net') ||
            url.includes('126.net') ||
            (url.startsWith('http') && !url.includes('localhost'))
        )

    const resolveUrl = (url) => {
        if (!url) return ''
        if (is_cdn_domain(url)) {
            return `http://localhost:8000/api/v1/network/audio-proxy?url=${encodeURIComponent(url)}`
        }
        return url.startsWith('http') ? url : `http://localhost:8000${url}`
    }

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
            // 记录最近播放
            recordListen(song.song_id)
        }
    }, [queue])

    const play = useCallback((song, url) => {
        const item = { ...song, url: resolveUrl(url || song.download_url) }
        const existingIdx = queue.findIndex(s => s.song_id === song.song_id)
        if (existingIdx >= 0) {
            setQueue(prev => prev.map((s, i) => i === existingIdx ? item : s))
            playIndex(existingIdx)
        } else {
            const newIdx = queue.length
            setQueue(prev => [...prev, item])
            setCurrentIndex(newIdx)
            setIsPlaying(true)
            if (audioRef.current) {
                audioRef.current.src = item.url
                audioRef.current.play().catch(err => {
                    if (err.name !== 'AbortError') console.log('播放失败:', err)
                })
            }
            recordListen(song.song_id || item.song_id)
        }
    }, [queue, playIndex])

    const addToQueue = useCallback((song, url) => {
        const item = { ...song, url: resolveUrl(url || song.url || song.download_url) }
        setQueue(prev => {
            const exists = prev.some(s => s.song_id === song.song_id)
            if (exists) return prev
            return [...prev, item]
        })
        // 第一次加歌时设 currentIndex，让 PlayerBar 出现
        if (queue.length === 0) {
            setCurrentIndex(0)
        }
    }, [queue])

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
        setIsPlaying(true)
        audioRef.current?.play().catch(err => {
            if (err.name !== 'AbortError') console.log('播放失败:', err)
        })
    }

    const updateCurrentSong = useCallback((song, update) => {
        setQueue(prev => prev.map(s =>
            s.song_id === song.song_id ? { ...s, ...update } : s
        ))
    }, [])

    const toggleLove = useCallback(async (song) => {
        if (!song?.song_id || toggleLock.current) return
        toggleLock.current = true
        try {
            const loved = lovedSet.has(song.song_id)
            if (loved) {
                await unsaveSong(song.song_id)
            } else {
                await saveSong(song.song_id)
            }
            setLovedSet(prev => {
                const next = new Set(prev)
                if (loved) next.delete(song.song_id)
                else next.add(song.song_id)
                return next
            })
        } catch (err) {
            console.log('收藏操作失败:', err)
        } finally {
            toggleLock.current = false
        }
    }, [lovedSet])

    // 初始化 lovedSet 用的——播放时如果歌曲已经在收藏列表里
    const initLoveState = useCallback((songIds) => {
        if (songIds.length === 0) return
        setLovedSet(prev => {
            const next = new Set(prev)
            songIds.forEach(id => next.add(id))
            return next
        })
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
            playerOpen, openPlayer, closePlayer, detailSong, detailOnDelete, openDetail, closeDetail,
            play, playQueue, playIndex, next, prev, removeFromQueue, addToQueue, clearQueue,
            pause, resume, toggleMode, updateCurrentSong, toggleLove, initLoveState, lovedSet, audioRef
        }}>
            {children}
            <audio ref={audioRef} onEnded={handleEnded} />
        </PlayerContext.Provider>
    )
}
