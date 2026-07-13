---
name: api-architecture
description: API 设计规范 — 响应格式、分页、认证、端点总览
metadata: 
  node_type: memory
  type: project
  originSessionId: 89731bae-11f2-46cc-bae5-5a7cf7aa54ca
---

# API 架构设计

## 基础 URL

`http://localhost:8000/api/v1`

## 通用响应格式

```json
{
  "code": 0,        // 0=成功，非0=错误码
  "message": "success",
  "data": ...
}
```

## 分页响应

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

## 认证

- 方式：JWT Bearer Token
- Header：`Authorization: Bearer <token>`
- 过期：默认 1440 分钟（24小时）
- 密钥：开发阶段使用 `change-me`（jwt_secret_key）

## 完整端点列表

### Auth（公开 + 需登录）
- `POST /auth/login` — 登录，返回 token + 用户信息
- `POST /auth/register` — 注册，自动创建 UserDetails
- `POST /auth/upload-avatar` — 上传头像（multipart），返回 URL
- `GET /auth/me` — 🔒 获取当前用户信息

### Songs
- `GET /songs` — 列表（分页 + 关键词搜索）
- `GET /songs/{id}` — 详情
- `POST /songs/{id}/play` — 🔒 播放记录（play_count+1, 写 play_history）
- `POST /songs/{id}/download` — 🔒 下载记录（download_count+1）
- `GET /songs/{id}/play-count` — 播放次数
- `GET /songs/{id}/download-count` — 下载次数

### Artists
- `GET /artists` — 列表（分页 + 关键词）
- `GET /artists/{id}` — 详情
- `GET /artists/{id}/songs` — 歌手的歌曲（分页）
- `GET /artists/{id}/albums` — 歌手的专辑（分页）

### Albums
- `GET /albums` — 列表（分页 + 关键词）
- `GET /albums/{id}` — 详情
- `GET /albums/{id}/songs` — 专辑的歌曲（分页）

### Playlists
- `GET /playlists` — 公开歌单列表
- `POST /playlists` — 🔒 创建歌单
- `GET /playlists/my` — 🔒 我的歌单
- `GET /playlists/{id}` — 歌单详情（含歌曲列表）
- `PUT /playlists/{id}` — 🔒 修改（仅创建者）
- `DELETE /playlists/{id}` — 🔒 删除（软删除，仅创建者）

### Search
- `GET /search/song-name?keyword=` — 歌曲名搜索
- `GET /search/artist-name?keyword=` — 歌手名搜索
- `GET /search/album-name?keyword=` — 专辑名搜索
- `GET /search/plain-lyric?keyword=` — 歌词搜索（关联 Songs 表返回 song_name）

### Comments
- `POST /songs/{song_id}/comments` — 🔒 发表评论（支持 parent_id 嵌套）
- `GET /songs/{song_id}/comments` — 评论列表（置顶优先，JOIN users 取 user_name）
- `DELETE /comments/{comment_id}` — 🔒 删除（仅作者）

### Favorites
- `POST /favorites/songs/{song_id}` — 🔒 收藏歌曲
- `POST /favorites/playlists/{playlist_id}` — 🔒 收藏歌单
- `POST /favorites/albums/{album_id}` — 🔒 收藏专辑
- `GET /favorites/list?type=song|album|playlist` — 🔒 收藏列表（分页）
- `DELETE /favorites/songs/{song_id}` — 🔒 取消收藏
- `DELETE /favorites/playlists/{playlist_id}` — 🔒 取消收藏
- `DELETE /favorites/albums/{album_id}` — 🔒 取消收藏

### Follow
- `POST /follow/artist/{artist_id}` — 🔒 关注歌手（fans_count+1, followed_count+1）
- `POST /follow/user/{followed_id}` — 🔒 关注用户（双方计数更新）
- `DELETE /follow/artist/{artist_id}` — 🔒 取关歌手
- `DELETE /follow/user/{followed_id}` — 🔒 取关用户

### Messages
- `POST /message` — 🔒 发送私信
- `GET /message/received` — 🔒 收到的私信
- `GET /message/list` — 🔒 所有私信（发+收）
- `DELETE /message/{message_id}` — 🔒 软删除（区分 sender/receiver 标记）
- `DELETE /message/{message_id}` — 🔒 硬删除（5分钟内，仅发送者）

### Users
- `GET /users/me/info` — 🔒 用户详情 + UserDetails
- `GET /users/me/history` — 🔒 播放历史（分页，JOIN songs）
- `GET /users/me/register-duration` — 🔒 注册天数
- `PUT /users/me` — 🔒 更新用户资料（用户表字段 + 详情表字段）

### Health
- `GET /health` — 健康检查

## 错误处理

- 404：资源不存在
- 400：参数错误 / 重复操作
- 401：未认证 / token 无效
- 403：无权限（不是作者/创建者）
- 通过 `APIResponse(code=N, message="...")` 返回错误
