import {usePlayer} from "../layouts/PlayerContext.jsx";
import {ChevronDown, Heart, Play, Pause, SkipBack, SkipForward, Repeat, Repeat1, Shuffle, ListVideo, EllipsisVertical} from "lucide-react";
import {useState, useEffect, useRef, useCallback, useMemo} from "react";
import './PlayerPage.css';

export default function PlayerPage({onOpenQueue}){

    const {
        currentSong, isPlaying, lyrics, mode, playerOpen,
        closePlayer, pause, resume, next, prev, toggleMode, updateCurrentSong,
        toggleLove, lovedSet, openDetail
    } = usePlayer();

    // 0 = 封面页, 1 = 歌词页
    const [page, setPage] = useState(0);
    const touchStart = useRef(null);
    const isSwitching = useRef(false);

    // 进度条 & 时间
    const [progress, setProgress] = useState(0);
    const [duration, setDuration] = useState(0);
    const progressRef = useRef(null);

    useEffect(() => {
        const el = document.querySelector('audio');
        if (!el) return;
        progressRef.current = el;

        const onTime = () => setProgress(el?.currentTime || 0);
        const onMeta = () => {
            if (el?.duration && isFinite(el.duration)) {
                setDuration(el.duration);
            }
        };
        // 可能 audio 已经有 src 了，主动触发一次
        onMeta();

        el.addEventListener('timeupdate', onTime);
        el.addEventListener('loadedmetadata', onMeta);
        el.addEventListener('durationchange', onMeta);

        return () => {
            el.removeEventListener('timeupdate', onTime);
            el.removeEventListener('loadedmetadata', onMeta);
            el.removeEventListener('durationchange', onMeta);
        };
    }, [currentSong?.song_id]);

    const formatTime = (t) => {
        if (!t || isNaN(t) || !isFinite(t)) return '00:00';
        const m = Math.floor(t / 60);
        const s = Math.floor(t % 60);
        return `${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
    };

    const handleSeek = (e) => {
        const val = Number(e.target.value);
        setProgress(val);
        if (progressRef.current) progressRef.current.currentTime = val;
    };

    const handleLrcClick = (time) => {
        setProgress(time);
        if (progressRef.current) progressRef.current.currentTime = time;
    };

    const modeIcon = mode === 'loop' ? <Repeat size={18}/>
        : mode === 'single' ? <Repeat1 size={18}/>
        : <Shuffle size={18}/>;

    const parseLrc = useCallback((lrcText) => {
        if (!lrcText) return [];
        const parsed = [];
        for (const line of lrcText.split('\n')) {
            const match = line.match(/^\[(\d{2}):(\d{2})(?:\.(\d+))?\](.*)/);
            if (match) {
                const min = parseInt(match[1]);
                const sec = parseInt(match[2]);
                const ms = match[3] ? parseInt(match[3].padEnd(3, '0').slice(0, 3)) : 0;
                parsed.push({ time: min * 60 + sec + ms / 1000, text: match[4].trim() || '...' });
            }
        }
        return parsed;
    }, []);

    const lrcLines = useMemo(() =>
        lyrics?.lyric_text ? parseLrc(lyrics.lyric_text) : [],
    [lyrics?.lyric_text, parseLrc]);
    const plainLines = useMemo(() =>
        !lyrics?.lyric_text && lyrics?.plain_lyric
            ? lyrics.plain_lyric.split('\n').filter(l => l.trim())
            : [],
    [lyrics?.lyric_text, lyrics?.plain_lyric]);

    const activeLrcIndex = useMemo(() =>
        lrcLines.reduce((acc, line, i) => progress >= line.time ? i : acc, -1),
    [lrcLines, progress]);

    const lrcContainerRef = useRef(null);
    useEffect(() => {
        if (page !== 1 || activeLrcIndex < 0 || !lrcContainerRef.current) return;
        const container = lrcContainerRef.current;
        const el = container.querySelector(`[data-lrc="${activeLrcIndex}"]`);
        if (!el) return;
        const cH = container.clientHeight;
        const eTop = el.offsetTop;
        const eH = el.offsetHeight;

        // 当前行理想的居中位置
        const ideal = eTop - cH / 2 + eH / 2;
        // 容器能滚的最大值
        const maxScroll = container.scrollHeight - cH;
        const target = Math.max(0, Math.min(ideal, maxScroll));

        // 只在偏离超过一行时才触发滚动，平滑但不弹跳
        if (Math.abs(container.scrollTop - target) > eH * 0.8) {
            container.scrollTo({top: target, behavior: 'smooth'});
        }
    }, [activeLrcIndex, page]);

    // 滑动切换（阻止冒泡防页面整体滑动）
    const handleTouchStart = (e) => { touchStart.current = e.touches[0].clientY; };
    const handleTouchMove = (e) => {
        if (touchStart.current) e.preventDefault();
    };
    const handleTouchEnd = (e) => {
        if (!touchStart.current || isSwitching.current) return;
        const diff = touchStart.current - e.changedTouches[0].clientY;
        if (Math.abs(diff) > 50) {
            isSwitching.current = true;
            setPage(p => p === 0 ? 1 : 0);
            setTimeout(() => { isSwitching.current = false; }, 300);
        }
        touchStart.current = null;
    };

    if (!currentSong) return null;

    return (
        <>
            <div className={`player-overlay ${playerOpen ? 'show' : ''}`} onClick={closePlayer} />

            <div className={`player-page ${playerOpen ? 'open' : ''}`}
                onTouchStart={handleTouchStart} onTouchEnd={handleTouchEnd}>
                <div className="player-back" style={{backgroundImage:`url(${currentSong?.picture_url || ''})`}}/>
                <div className="player-handle-bar">
                    <ChevronDown size={24} onClick={closePlayer} style={{cursor:'pointer'}} />
                </div>

                {/* 歌名 + 歌手 */}
                <div className="flex" style={{}}>
                    <div style={{flex:1,minWidth:0}}>
                        <div className="player-song-name" style={{whiteSpace:'nowrap',padding:0}}>{currentSong?.song_name || '未在播放'}</div>
                        <div className="player-artist-name" style={{overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{currentSong?.artist_name || ''}</div>
                    </div>

                </div>

                {/* 页面指示器 */}
                <div className="player-page-dots">
                    <span className={page === 0 ? 'active' : ''} onClick={() => setPage(0)} />
                    <span className={page === 1 ? 'active' : ''} onClick={() => setPage(1)} />
                </div>

                <div className="player-pages-wrapper">
                    <div className="player-pages-track" style={{transform: `translateX(-${page * 100}vw)`}}>
                        <div className="player-page-content cover-page">
                            <div className="player-cover-wrap">
                                <img className={`player-cover ${isPlaying ? '' : 'paused'}`}
                                    src={currentSong?.picture_url || null} alt="cover" />
                            </div>
                            <div className="player-lyrics-preview">
                                {lrcLines.length > 0 ? (
                                    (() => {
                                        const start = Math.max(0, activeLrcIndex - 1);
                                        const window = lrcLines.slice(start, start + 3);
                                        return window.map((line, i) => (
                                            <p key={start + i}
                                                onClick={() => handleLrcClick(line.time)}
                                                className={`lrc-line ${(start + i) === activeLrcIndex ? 'active' : ''}`}>
                                                {line.text}
                                            </p>
                                        ));
                                    })()
                                ) : plainLines.length > 0 ? (
                                    plainLines.slice(0, 3).map((line, i) => (
                                        <p key={i} className="lrc-line">{line}</p>
                                    ))
                                ) : (
                                    <p className="lrc-line no-lyric">暂无歌词</p>
                                )}
                            </div>
                        </div>
                        <div className="player-page-content lyrics-page">
                            <div className="player-lyrics" ref={lrcContainerRef}>
                                {lrcLines.length > 0 ? (
                                    lrcLines.map((line, i) => (
                                        <p key={i} data-lrc={i}
                                            onClick={() => handleLrcClick(line.time)}
                                            className={`lrc-line lrc-line-lg ${i === activeLrcIndex ? 'active' : ''}`}>
                                            {line.text}
                                        </p>
                                    ))
                                ) : plainLines.length > 0 ? (
                                    plainLines.map((line, i) => (
                                        <p key={i} className="lrc-line lrc-line-lg">{line}</p>
                                    ))
                                ) : (
                                    <p className="lrc-line no-lyric">暂无歌词</p>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {/* 底部固定区域：进度条 + 控制 */}
                <div className="player-bottom">
                    <div className="player-progress">
                        <span className="player-time">{formatTime(progress)}</span>
                        <input type="range" className="player-slider"
                            style={{background: `linear-gradient(to right, #1db954 ${duration ? (progress/duration*100) : 0}%, #444 ${duration ? (progress/duration*100) : 0}%)`}}
                            min={0} max={duration || 0} value={progress} onChange={handleSeek} />
                        <span className="player-time">{formatTime(duration)}</span>
                    </div>

                    <div className="player-controls">
                        <div onClick={toggleMode} style={{cursor:'pointer', color:'#ccc'}}>{modeIcon}</div>
                        <SkipBack size={28} onClick={prev} style={{cursor:'pointer', color:'#fff'}} />
                        {isPlaying
                            ? <Pause size={44} onClick={pause} style={{cursor:'pointer', color:'#fff'}} />
                            : <Play size={44} onClick={resume} style={{cursor:'pointer', color:'#fff'}} />
                        }
                        <SkipForward size={28} onClick={next} style={{cursor:'pointer', color:'#fff'}} />
                        <ListVideo size={22} color="#ccc" style={{cursor:'pointer'}} onClick={onOpenQueue} />
                    </div>
                </div>
            </div>
        </>
    );
}
