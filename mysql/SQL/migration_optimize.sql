-- =============================================================
-- myMusic 数据库结构优化迁移
-- 基于 create.sql 评审后的改进
-- 2026-07-14
-- =============================================================

-- 1. VARCHAR 长度扩展
-- -------------------------------------------------------------
SET SQL_SAFE_UPDATES = 0;
-- songs.picture_url: 200 → 500（网易云封面长）
ALTER TABLE songs MODIFY picture_url VARCHAR(500);

-- albums.album_name: 50 → 200
ALTER TABLE albums MODIFY album_name VARCHAR(200);

-- artists.artist_name: 50 → 100
ALTER TABLE artists MODIFY artist_name VARCHAR(100) DEFAULT '群星';

-- playlists.playlist_name: 32 → 100
ALTER TABLE playlists MODIFY playlist_name VARCHAR(100) NOT NULL;

-- search_history.keyword: 32 → 200（搜索句子不截断）
ALTER TABLE search_history MODIFY keyword VARCHAR(200);

-- users.user_name: 20 → 50
ALTER TABLE users MODIFY user_name VARCHAR(50) NOT NULL DEFAULT '默认用户';

-- users.email: 32 → 100, 加 UNIQUE（先清空空串，NULL 不违反 UNIQUE）
ALTER TABLE users MODIFY email VARCHAR(100);
UPDATE users SET email = NULL WHERE email = '';
ALTER TABLE users ADD UNIQUE INDEX uq_email (email);

-- user_details.nick_name: 20 → 50
ALTER TABLE user_details MODIFY nick_name VARCHAR(50);


-- 2. 缺失约束
-- -------------------------------------------------------------

-- lyrics.song_id 加 UNIQUE
ALTER TABLE lyrics ADD UNIQUE INDEX uq_song_id (song_id);

-- songs.platform_id + source 加 UNIQUE（防重复入库）
ALTER TABLE songs ADD UNIQUE INDEX uq_platform_source (platform_id, source);


-- 3. 冗余索引删除
-- -------------------------------------------------------------

-- user_details 的 PK 是 user_id，index_user_id 多余
ALTER TABLE user_details DROP INDEX index_user_id;

-- lyrics 的 PK 是 lyric_id，index_lyric_id 多余
ALTER TABLE lyrics DROP INDEX index_lyric_id;


-- 4. 重复外键约束删除
-- -------------------------------------------------------------

-- user_details 有两个 FK 指向同一字段，删掉重复的（保留 fk_detail_user，名字更清晰）
ALTER TABLE user_details DROP FOREIGN KEY user_details_ibfk_1;


-- 5. search_history 补充 create_time 字段
-- -------------------------------------------------------------

ALTER TABLE search_history ADD COLUMN create_time DATETIME DEFAULT CURRENT_TIMESTAMP AFTER search_type;
ALTER TABLE search_history ADD INDEX index_create_time (create_time);
