-- =============================================================
-- myMusic 完整建表脚本（生产环境用）
-- 基于 SQLAlchemy ORM 模型 + 优化迁移
-- 2026-07-26
-- =============================================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ========================
-- 1. 用户表
-- ========================
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `user_name` varchar(50) NOT NULL DEFAULT '默认用户',
  `password` varchar(60) NOT NULL,
  `email` varchar(100) DEFAULT '',
  `avatar_url` varchar(256) DEFAULT '',
  `roles` varchar(20) DEFAULT 'user',
  `current_status` tinyint DEFAULT '1',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  KEY `index_name` (`user_name`),
  KEY `index_current_status` (`current_status`),
  UNIQUE INDEX `uq_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ========================
-- 2. 用户详情表（1:1 users）
-- ========================
DROP TABLE IF EXISTS `user_details`;
CREATE TABLE `user_details` (
  `user_id` int NOT NULL,
  `nick_name` varchar(50) DEFAULT '',
  `gender` enum('男','女','其他') DEFAULT '其他',
  `birthdate` date DEFAULT '2026-05-20',
  `phone_number` varchar(20) DEFAULT '',
  `real_name` varchar(20) DEFAULT '',
  `city` varchar(20) DEFAULT '',
  `fans_count` int DEFAULT '0',
  `followed_count` int DEFAULT '0',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  KEY `index_city` (`city`),
  CONSTRAINT `fk_detail_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ========================
-- 3. 歌手表
-- ========================
DROP TABLE IF EXISTS `artists`;
CREATE TABLE `artists` (
  `artist_id` int NOT NULL AUTO_INCREMENT,
  `platform_id` varchar(50) DEFAULT NULL,
  `artist_name` varchar(100) NOT NULL DEFAULT '群星',
  `avartar_url` varchar(200) DEFAULT NULL,
  `source` varchar(50) DEFAULT NULL,
  `songs_count` int DEFAULT '0',
  `album_count` int DEFAULT '0',
  `fans_count` int DEFAULT '0',
  `introduction` text,
  `current_status` tinyint DEFAULT '1',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`artist_id`),
  KEY `index_artist_name` (`artist_name`),
  KEY `index_artist_status` (`current_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ========================
-- 4. 专辑表
-- ========================
DROP TABLE IF EXISTS `albums`;
CREATE TABLE `albums` (
  `album_id` int NOT NULL AUTO_INCREMENT,
  `platform_id` varchar(50) DEFAULT NULL,
  `artist_id` int DEFAULT NULL,
  `album_name` varchar(200) NOT NULL DEFAULT '',
  `cover_url` varchar(500) DEFAULT NULL,
  `source` varchar(50) DEFAULT NULL,
  `songs_count` int DEFAULT '0',
  `current_status` tinyint DEFAULT '1',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`album_id`),
  KEY `index_album_name` (`album_name`),
  KEY `index_album_status` (`current_status`),
  KEY `index_album_artist` (`artist_id`),
  CONSTRAINT `fk_album_artist` FOREIGN KEY (`artist_id`) REFERENCES `artists` (`artist_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ========================
-- 5. 歌曲表
-- ========================
DROP TABLE IF EXISTS `songs`;
CREATE TABLE `songs` (
  `song_id` int NOT NULL AUTO_INCREMENT,
  `platform_id` varchar(200) DEFAULT NULL,
  `song_name` varchar(200) NOT NULL,
  `artist_id` int DEFAULT NULL,
  `album_id` int DEFAULT NULL,
  `lyric_id` int DEFAULT NULL,
  `picture_url` varchar(500) DEFAULT NULL,
  `source` varchar(50) DEFAULT NULL,
  `introduction` text,
  `download_url` varchar(1000) DEFAULT NULL,
  `download_count` int DEFAULT '0',
  `play_count` int DEFAULT '0',
  `current_status` tinyint DEFAULT '1',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`song_id`),
  KEY `index_song_name` (`song_name`),
  KEY `index_song_status` (`current_status`),
  KEY `index_song_artist` (`artist_id`),
  UNIQUE INDEX `uq_platform_source` (`platform_id`, `source`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ========================
-- 6. 歌词表（1:1 songs）
-- ========================
DROP TABLE IF EXISTS `lyrics`;
CREATE TABLE `lyrics` (
  `lyric_id` int NOT NULL AUTO_INCREMENT,
  `song_id` int NOT NULL,
  `lyric_text` longtext,
  `plain_lyric` text COMMENT '纯文本歌词',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`lyric_id`),
  KEY `index_lyric_song` (`song_id`),
  UNIQUE INDEX `uq_lyric_song_id` (`song_id`),
  CONSTRAINT `fk_lyric_song` FOREIGN KEY (`song_id`) REFERENCES `songs` (`song_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ========================
-- 7. 歌单表
-- ========================
DROP TABLE IF EXISTS `playlists`;
CREATE TABLE `playlists` (
  `playlist_id` int NOT NULL AUTO_INCREMENT,
  `playlist_name` varchar(100) NOT NULL,
  `user_id` int DEFAULT NULL,
  `introduction` varchar(200) DEFAULT '',
  `cover_url` varchar(500) DEFAULT '',
  `songs_count` int DEFAULT '0',
  `play_count` int DEFAULT '0',
  `save_count` int DEFAULT '0',
  `is_public` tinyint(1) DEFAULT '0',
  `current_status` tinyint DEFAULT '1',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`playlist_id`),
  KEY `index_playlist_name` (`playlist_name`),
  KEY `index_playlist_status` (`current_status`),
  KEY `index_playlist_user` (`user_id`),
  CONSTRAINT `fk_playlist_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ========================
-- 8. 评论表（支持嵌套回复）
-- ========================
DROP TABLE IF EXISTS `comments`;
CREATE TABLE `comments` (
  `comment_id` int NOT NULL AUTO_INCREMENT,
  `song_id` int DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  `content` varchar(1000) DEFAULT NULL,
  `parent_id` int DEFAULT NULL,
  `root_id` int DEFAULT '0',
  `like_count` int DEFAULT '0',
  `reply_count` int DEFAULT '0',
  `is_top` tinyint(1) DEFAULT '0',
  `current_status` tinyint DEFAULT '1',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`comment_id`),
  KEY `index_comment_song` (`song_id`),
  KEY `index_comment_user` (`user_id`),
  KEY `index_comment_status` (`current_status`),
  KEY `index_comment_top` (`is_top`),
  KEY `index_comment_time` (`create_time`),
  CONSTRAINT `fk_comment_song` FOREIGN KEY (`song_id`) REFERENCES `songs` (`song_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_comment_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_comment_parent` FOREIGN KEY (`parent_id`) REFERENCES `comments` (`comment_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ========================
-- 9. 私信表（双方软删除）
-- ========================
DROP TABLE IF EXISTS `messages`;
CREATE TABLE `messages` (
  `message_id` int NOT NULL AUTO_INCREMENT,
  `sender_id` int DEFAULT NULL,
  `receiver_id` int DEFAULT NULL,
  `content` varchar(1000) NOT NULL,
  `is_read` tinyint(1) DEFAULT '0',
  `is_deleted_sender` tinyint(1) DEFAULT '0',
  `is_deleted_receiver` tinyint(1) DEFAULT '0',
  `sent_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `read_time` datetime DEFAULT NULL,
  `current_status` tinyint DEFAULT '1',
  PRIMARY KEY (`message_id`),
  KEY `index_message_sender` (`sender_id`),
  KEY `index_message_receiver` (`receiver_id`),
  KEY `index_message_time` (`sent_time`),
  KEY `index_message_status` (`current_status`),
  CONSTRAINT `fk_message_sender` FOREIGN KEY (`sender_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_message_receiver` FOREIGN KEY (`receiver_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ========================
-- 10. 播放历史表
-- ========================
DROP TABLE IF EXISTS `play_history`;
CREATE TABLE `play_history` (
  `play_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `song_id` int DEFAULT NULL,
  `artist_id` int DEFAULT NULL,
  `playlist_id` int DEFAULT NULL,
  `playlist_duration` int DEFAULT '0' COMMENT '已播时长(秒)',
  `is_completed` tinyint(1) DEFAULT '1',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`play_id`),
  KEY `index_play_user` (`user_id`),
  KEY `index_play_song` (`song_id`),
  KEY `index_play_playlist` (`playlist_id`),
  KEY `index_play_time` (`create_time`),
  CONSTRAINT `fk_play_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_play_song` FOREIGN KEY (`song_id`) REFERENCES `songs` (`song_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_play_artist` FOREIGN KEY (`artist_id`) REFERENCES `artists` (`artist_id`) ON DELETE SET NULL,
  CONSTRAINT `fk_play_playlist` FOREIGN KEY (`playlist_id`) REFERENCES `playlists` (`playlist_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ========================
-- 11. 搜索历史表
-- ========================
DROP TABLE IF EXISTS `search_history`;
CREATE TABLE `search_history` (
  `search_id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `keyword` varchar(200) DEFAULT NULL,
  `search_type` enum('artist','song','lyric','album','playlist','user','other') DEFAULT 'song',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`search_id`),
  KEY `index_search_user` (`user_id`),
  KEY `index_search_keyword` (`keyword`),
  KEY `index_search_type` (`search_type`),
  KEY `index_search_time` (`create_time`),
  CONSTRAINT `fk_search_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ============================================
-- 12-21. 多对多关联表（复合主键）
-- ============================================

-- 12. 用户关注歌手
DROP TABLE IF EXISTS `user_follow_artist`;
CREATE TABLE `user_follow_artist` (
  `user_id` int NOT NULL,
  `artist_id` int NOT NULL,
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`, `artist_id`),
  KEY `index_ufa_user` (`user_id`),
  KEY `index_ufa_artist` (`artist_id`),
  CONSTRAINT `fk_ufa_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_ufa_artist` FOREIGN KEY (`artist_id`) REFERENCES `artists` (`artist_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 13. 用户关注用户
DROP TABLE IF EXISTS `user_follow_user`;
CREATE TABLE `user_follow_user` (
  `fans_id` int NOT NULL,
  `followed_id` int NOT NULL,
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`fans_id`, `followed_id`),
  KEY `index_ufu_fans` (`fans_id`),
  KEY `index_ufu_followed` (`followed_id`),
  CONSTRAINT `fk_ufu_fans` FOREIGN KEY (`fans_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_ufu_followed` FOREIGN KEY (`followed_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 14. 用户收藏歌曲
DROP TABLE IF EXISTS `user_save_song`;
CREATE TABLE `user_save_song` (
  `user_id` int NOT NULL,
  `song_id` int NOT NULL,
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`, `song_id`),
  KEY `index_uss_user` (`user_id`),
  KEY `index_uss_song` (`song_id`),
  CONSTRAINT `fk_uss_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_uss_song` FOREIGN KEY (`song_id`) REFERENCES `songs` (`song_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 15. 用户收藏专辑
DROP TABLE IF EXISTS `user_save_album`;
CREATE TABLE `user_save_album` (
  `user_id` int NOT NULL,
  `album_id` int NOT NULL,
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`, `album_id`),
  KEY `index_usa_user` (`user_id`),
  KEY `index_usa_album` (`album_id`),
  CONSTRAINT `fk_usa_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_usa_album` FOREIGN KEY (`album_id`) REFERENCES `albums` (`album_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 16. 用户收藏歌单
DROP TABLE IF EXISTS `user_save_playlist`;
CREATE TABLE `user_save_playlist` (
  `user_id` int NOT NULL,
  `playlist_id` int NOT NULL,
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`, `playlist_id`),
  KEY `index_usp_user` (`user_id`),
  KEY `index_usp_playlist` (`playlist_id`),
  CONSTRAINT `fk_usp_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_usp_playlist` FOREIGN KEY (`playlist_id`) REFERENCES `playlists` (`playlist_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 17. 用户点赞评论
DROP TABLE IF EXISTS `user_like_comment`;
CREATE TABLE `user_like_comment` (
  `user_id` int NOT NULL,
  `comment_id` int NOT NULL,
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`, `comment_id`),
  KEY `index_ulc_user` (`user_id`),
  KEY `index_ulc_comment` (`comment_id`),
  CONSTRAINT `fk_ulc_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_ulc_comment` FOREIGN KEY (`comment_id`) REFERENCES `comments` (`comment_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 18. 歌手-歌曲多对多
DROP TABLE IF EXISTS `artist_sing_song`;
CREATE TABLE `artist_sing_song` (
  `artist_id` int NOT NULL,
  `song_id` int NOT NULL,
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`artist_id`, `song_id`),
  KEY `index_ass_artist` (`artist_id`),
  KEY `index_ass_song` (`song_id`),
  CONSTRAINT `fk_ass_artist` FOREIGN KEY (`artist_id`) REFERENCES `artists` (`artist_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_ass_song` FOREIGN KEY (`song_id`) REFERENCES `songs` (`song_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 19. 歌单-歌曲多对多
DROP TABLE IF EXISTS `playlist_save_song`;
CREATE TABLE `playlist_save_song` (
  `playlist_id` int NOT NULL,
  `song_id` int NOT NULL,
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`playlist_id`, `song_id`),
  KEY `index_pss_playlist` (`playlist_id`),
  KEY `index_pss_song` (`song_id`),
  CONSTRAINT `fk_pss_playlist` FOREIGN KEY (`playlist_id`) REFERENCES `playlists` (`playlist_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_pss_song` FOREIGN KEY (`song_id`) REFERENCES `songs` (`song_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 20. 专辑-歌曲（旧表，已弃用，保留兼容）
DROP TABLE IF EXISTS `album_save_song`;
CREATE TABLE `album_save_song` (
  `album_id` int NOT NULL,
  `song_id` int NOT NULL,
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`album_id`, `song_id`),
  KEY `index_ass_al_album` (`album_id`),
  KEY `index_ass_al_song` (`song_id`),
  CONSTRAINT `fk_ass_al_album` FOREIGN KEY (`album_id`) REFERENCES `albums` (`album_id`) ON DELETE CASCADE,
  CONSTRAINT `fk_ass_al_song` FOREIGN KEY (`song_id`) REFERENCES `songs` (`song_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

SET FOREIGN_KEY_CHECKS = 1;
