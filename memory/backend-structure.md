---
name: backend-structure
description: FastAPI 后端完整结构 — 路由、模型、schemas、services、数据库配置
metadata: 
  node_type: memory
  type: project
  originSessionId: 89731bae-11f2-46cc-bae5-5a7cf7aa54ca
---

# 后端结构 (newMusic/)

## 入口

- `newMusic/app/main.py` — FastAPI 应用入口。挂载 CORS 中间件、v1 路由、静态文件服务（`/static` → `uploads/`）。lifespan 管理启动/关闭。

## 目录结构

```
newMusic/
├── .env                    # 环境变量（db_host, db_password, jwt_secret_key 等）
├── alembic.ini             # Alembic 配置（连接 mysql+asyncmy://root:sql2008@localhost:3306/myMusic）
├── requirements.txt        # Python 依赖
├── app/
│   ├── main.py             # FastAPI 入口
│   ├── api/v1/             # API 路由（14个模块）
│   │   ├── __init__.py     # 路由汇总，prefix="/api/v1"
│   │   ├── health.py       # GET /health 健康检查
│   │   ├── auth.py         # POST /login, /register, /upload-avatar, GET /me
│   │   ├── users.py        # GET /me/info, /me/history, /me/register-duration, PUT /me
│   │   ├── songs.py        # GET /songs, GET/POST /songs/{id}, /play, /download, /play-count, /download-count
│   │   ├── artists.py      # GET /artists, /artists/{id}, /{id}/songs, /{id}/albums
│   │   ├── albums.py       # GET /albums, /albums/{id}, /{id}/songs
│   │   ├── playlists.py    # CRUD /playlists, GET /my, /{id}
│   │   ├── search.py       # GET /search/song-name, /artist-name, /album-name, /plain-lyric
│   │   ├── comments.py     # POST/GET/DELETE /songs/{id}/comments, DELETE /comments/{id}
│   │   ├── favorites.py    # POST/DELETE /songs/{id}, /playlists/{id}, /albums/{id}, GET /list?type=
│   │   ├── follow.py       # POST/DELETE /follow/artist/{id}, /follow/user/{id}
│   │   ├── message.py      # POST /message, GET /received, /list, DELETE /{id}
│   │   └── lyric.py        # GET /lyric/{song_id}
│   ├── core/
│   │   ├── config.py       # Settings 类（pydantic-settings），从 .env 加载
│   │   ├── database.py     # 异步 SQLAlchemy 引擎 + session factory + get_db 依赖
│   │   └── deps.py         # get_current_user 依赖（HTTPBearer → JWT decode → DB lookup）
│   ├── models/             # SQLAlchemy ORM 模型（21 个表）
│   │   ├── base.py         # DeclarativeBase 基类
│   │   ├── __init__.py     # 导入所有模型（供 Alembic 使用）
│   │   ├── users.py        # Users 表
│   │   ├── user_details.py # UserDetails 表（1:1 Users）
│   │   ├── songs.py        # Songs 表
│   │   ├── artists.py      # Artists 表
│   │   ├── albums.py       # Albums 表
│   │   ├── playlists.py    # Playlists 表
│   │   ├── lyrics.py       # Lyrics 表（LONGTEXT）
│   │   ├── comments.py     # Comments 表（支持嵌套回复：parent_id, root_id）
│   │   ├── messages.py     # Messages 表（双方软删除）
│   │   ├── play_history.py # PlayHistory 表
│   │   ├── search_history.py # SearchHistory 表
│   │   ├── user_follow_artist.py  # 用户关注歌手关联表
│   │   ├── user_follow_user.py    # 用户关注用户关联表（fans_id → followed_id）
│   │   ├── user_save_song.py      # 用户收藏歌曲关联表
│   │   ├── user_save_album.py     # 用户收藏专辑关联表
│   │   ├── user_save_playlist.py  # 用户收藏歌单关联表
│   │   ├── user_like_comment.py   # 用户点赞评论关联表
│   │   ├── artist_sing_song.py    # 歌手-歌曲关联表
│   │   ├── playlist_save_song.py  # 歌单-歌曲关联表
│   │   └── album_save_song.py     # 专辑-歌曲关联表
│   ├── schemas/            # Pydantic 模型（请求/响应）
│   │   ├── common.py       # APIResponse（code/message/data）, PaginatedResponse
│   │   ├── user.py         # UserRegister/Login/Base/Detail req/res
│   │   ├── song.py         # SongBase, SongDetail
│   │   ├── artist.py       # ArtistBase, ArtistDetail
│   │   ├── album.py        # AlbumBase, AlbumDetail
│   │   ├── playlist.py     # PlaylistBase/Create/Update/Detail, SongInPlaylist
│   │   ├── comment.py      # CommentCreateRequest, CommentResponse
│   │   ├── message.py      # MessageSendRequest, MessageResponse
│   │   ├── lyric.py        # LyricResponse
│   │   └── favorite.py     # FavoriteSong/Playlist/AlbumResponse
│   ├── services/           # 业务逻辑层（空目录，尚未实现）
│   └── utils/
│       └── security.py     # bcrypt 密码哈希 + JWT 创建/解码
```

## 数据库关键信息

- 连接：`mysql+asyncmy://root:sql2008@localhost:3306/myMusic`
- 所有表使用 `current_status` 字段做软删除（1=正常）
- 多对多关系通过关联表实现（带复合主键 + create_time）
- Users ↔ UserDetails 是 1:1 关系
- 评论支持嵌套：parent_id 指向直接父评论，root_id 指向根评论
