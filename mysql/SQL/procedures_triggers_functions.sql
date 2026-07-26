-- =============================================================
-- myMusic 存储过程 / 触发器 / 函数
-- 2026-07-26
-- =============================================================

-- ========================
-- 函数
-- ========================

-- 获取歌曲的所有歌手名（拼接）
DROP FUNCTION IF EXISTS `fn_get_song_artists`;
DELIMITER ;;
CREATE FUNCTION `fn_get_song_artists`(p_song_id INT) RETURNS VARCHAR(500)
    DETERMINISTIC
    READS SQL DATA
BEGIN
    DECLARE v_names VARCHAR(500);
    SELECT GROUP_CONCAT(a.artist_name SEPARATOR '、') INTO v_names
    FROM artist_sing_song ass
    JOIN artists a ON ass.artist_id = a.artist_id
    WHERE ass.song_id = p_song_id;
    RETURN v_names;
END;;
DELIMITER ;

-- 格式化毫秒为 mm:ss
DROP FUNCTION IF EXISTS `fn_format_duration`;
DELIMITER ;;
CREATE FUNCTION `fn_format_duration`(ms INT) RETURNS VARCHAR(10)
    DETERMINISTIC
    READS SQL DATA
BEGIN
    DECLARE total_sec INT;
    DECLARE min INT;
    DECLARE sec INT;
    SET total_sec = ms / 1000;
    SET min = FLOOR(total_sec / 60);
    SET sec = total_sec % 60;
    RETURN CONCAT(min, ':', LPAD(sec, 2, '0'));
END;;
DELIMITER ;

-- 获取搜索热词（按搜索次数排序）
DROP FUNCTION IF EXISTS `fn_get_search_hot`;
DELIMITER ;;
CREATE FUNCTION `fn_get_search_hot`(p_keyword VARCHAR(200)) RETURNS INT
    DETERMINISTIC
    READS SQL DATA
BEGIN
    DECLARE v_count INT;
    SELECT COUNT(*) INTO v_count
    FROM search_history
    WHERE keyword = p_keyword;
    RETURN v_count;
END;;
DELIMITER ;


-- ========================
-- 触发器
-- ========================

-- 1. 收藏歌曲 → user_save_song.songs_count + 1（已由后端逻辑维护，不需要触发器）
--    改用触发器维护 songs.play_count（当 play_history 插入时）

-- 给 lyrics 插入时自动提取纯文本歌词
DROP TRIGGER IF EXISTS `trg_lyrics_insert`;
DELIMITER ;;
CREATE TRIGGER `trg_lyrics_insert`
    BEFORE INSERT ON `lyrics`
    FOR EACH ROW
BEGIN
    IF NEW.lyric_text IS NOT NULL THEN
        SET NEW.plain_lyric = REGEXP_REPLACE(NEW.lyric_text, '\\[[0-9.:]+\\]', '');
    END IF;
END;;
DELIMITER ;

-- 给 lyrics 更新时同样提取
DROP TRIGGER IF EXISTS `trg_lyrics_update`;
DELIMITER ;;
CREATE TRIGGER `trg_lyrics_update`
    BEFORE UPDATE ON `lyrics`
    FOR EACH ROW
BEGIN
    IF NEW.lyric_text IS NOT NULL THEN
        SET NEW.plain_lyric = REGEXP_REPLACE(NEW.lyric_text, '\\[[0-9.:]+\\]', '');
    END IF;
END;;
DELIMITER ;

-- 收藏歌曲时更新 songs_count（实际上由后端维护，备用）
DROP TRIGGER IF EXISTS `trg_user_save_song_insert`;
DELIMITER ;;
CREATE TRIGGER `trg_user_save_song_insert`
    AFTER INSERT ON `user_save_song`
    FOR EACH ROW
BEGIN
    UPDATE songs SET download_count = download_count + 1 WHERE song_id = NEW.song_id;
END;;
DELIMITER ;

-- 取消收藏时回滚
DROP TRIGGER IF EXISTS `trg_user_save_song_delete`;
DELIMITER ;;
CREATE TRIGGER `trg_user_save_song_delete`
    AFTER DELETE ON `user_save_song`
    FOR EACH ROW
BEGIN
    UPDATE songs SET download_count = GREATEST(download_count - 1, 0) WHERE song_id = OLD.song_id;
END;;
DELIMITER ;


-- ========================
-- 存储过程
-- ========================

-- 重新计算所有计数（用于数据修复）
DROP PROCEDURE IF EXISTS `sp_recalculate_all_counts`;
DELIMITER ;;
CREATE PROCEDURE `sp_recalculate_all_counts`()
BEGIN
    -- 歌曲播放次数（从 play_history 重新统计）
    UPDATE songs s
    SET s.play_count = (
        SELECT COUNT(*) FROM play_history ph WHERE ph.song_id = s.song_id
    );

    -- 歌曲下载/收藏次数
    UPDATE songs s
    SET s.download_count = (
        SELECT COUNT(*) FROM user_save_song uss WHERE uss.song_id = s.song_id
    );

    -- 歌手歌曲数
    UPDATE artists a
    SET a.songs_count = (
        SELECT COUNT(*) FROM artist_sing_song ass WHERE ass.artist_id = a.artist_id
    );

    -- 歌手专辑数
    UPDATE artists a
    SET a.album_count = (
        SELECT COUNT(*) FROM albums alb WHERE alb.artist_id = a.artist_id
    );

    -- 专辑歌曲数
    UPDATE albums a
    SET a.songs_count = (
        SELECT COUNT(*) FROM songs s WHERE s.album_id = a.album_id
    );

    -- 歌单歌曲数
    UPDATE playlists p
    SET p.songs_count = (
        SELECT COUNT(*) FROM playlist_save_song pss WHERE pss.playlist_id = p.playlist_id
    );
END;;
DELIMITER ;

-- 清理过期/脏数据
DROP PROCEDURE IF EXISTS `sp_cleanup_stale_songs`;
DELIMITER ;;
CREATE PROCEDURE `sp_cleanup_stale_songs`()
BEGIN
    -- 标记 download_url 是已过期 CDN 链接的歌曲为 current_status=0（软删除）
    UPDATE songs
    SET current_status = 0
    WHERE download_url LIKE '%music.126.net%'
       OR download_url LIKE '%126.net%'
       OR (download_url IS NOT NULL AND download_url NOT LIKE '/static/music/%');
END;;
DELIMITER ;
