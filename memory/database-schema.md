---
name: database-schema
description: 数据库表结构概览 — 实体表、关联表、关键字段
metadata: 
  node_type: memory
  type: project
  originSessionId: 89731bae-11f2-46cc-bae5-5a7cf7aa54ca
---

# 数据库表结构

## 实体表

| 表名 | 主键 | 关键字段 |
|------|------|----------|
| `users` | user_id | user_name(20), password(60), email(32), avatar_url(256), roles(20), current_status, create_time |
| `user_details` | user_id (FK→users) | nick_name(20), gender(Enum:男/女/其他), birthdate, phone_number, real_name, city, fans_count, followed_count |
| `songs` | song_id | platform_id, song_name(200), artist_id, album_id, lyric_id, picture_id, picture_url, sources, url_id, introduction(TEXT), download_url(500), download_count, play_count, current_status |
| `artists` | artist_id | platform_id, artist_name(50), songs_count, album_count, fans_count, introduction(TEXT), current_status |
| `albums` | album_id | platform_id, artist_id(FK→artists), album_name(50), songs_count, current_status |
| `playlists` | playlist_id | playlist_name(32), user_id(FK→users), introduction(200), cover_url(500), songs_count, play_count, save_count, is_public, current_status |
| `lyrics` | lyric_id | song_id(FK→songs), platform_id, lyric_text(LONGTEXT), plain_lyric(TEXT) |
| `comments` | comment_id | song_id(FK→songs), user_id(FK→users), content(1000), parent_id(FK→self), root_id, like_count, reply_count, is_top, current_status |
| `messages` | message_id | sender_id(FK→users), receiver_id(FK→users), content(1000), is_read, is_deleted_sender, is_deleted_receiver, sent_time, read_time |
| `play_history` | play_id | user_id, song_id, artist_id, playlist_id, playlist_duration, is_completed, create_time |
| `search_history` | search_id | user_id, keyword(32), search_type(Enum: artist/song/lyric/album/playlist/user/other) |

## 多对多关联表（复合主键 + create_time）

| 表名 | 复合主键 | 说明 |
|------|----------|------|
| `user_follow_artist` | (user_id, artist_id) | 用户关注歌手 |
| `user_follow_user` | (fans_id, followed_id) | 用户关注用户 |
| `user_save_song` | (user_id, song_id) | 用户收藏歌曲 |
| `user_save_album` | (user_id, album_id) | 用户收藏专辑 |
| `user_save_playlist` | (user_id, playlist_id) | 用户收藏歌单 |
| `user_like_comment` | (user_id, comment_id) | 用户点赞评论 |
| `artist_sing_song` | (artist_id, song_id) | 歌手演唱歌曲 |
| `playlist_save_song` | (playlist_id, song_id) | 歌单包含歌曲 |
| `album_save_song` | (album_id, song_id) | 专辑包含歌曲 |

## 关系说明

- Users ↔ UserDetails：1:1（user_detail 关系，uselist=False）
- Songs → Lyrics：1:1（song.lyric 关系，uselist=False）
- Songs → Artists：多对1（通过 artist_id）
- Songs → Albums：多对1（通过 album_id）
- 评论嵌套：parent_id 指向直接父评论，root_id 指向根评论（0=顶级评论）
- 删略策略：users 和 songs 对关联表用 CASCADE 删除
