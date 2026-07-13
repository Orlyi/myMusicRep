---
name: spiders-and-data
description: 爬虫脚本说明 — 数据来源、API 调用方式
metadata: 
  node_type: memory
  type: project
  originSessionId: 89731bae-11f2-46cc-bae5-5a7cf7aa54ca
---

# 爬虫与数据来源

## 数据源

所有爬虫调用 `http://www.yinyueku.cn/api.php` 这个第三方音乐 API。

## 爬虫文件

### `spiders/music_spider.py`
- 调用 API `types=url` 获取歌曲播放/下载 URL
- 通过 requests 下载 .mp3 文件到 `./music/` 目录
- 当前是硬编码示例（id=2661558787, source=netease）

### `spiders/lyric_spider.py`
- 调用 API `types=lyric` 获取歌词
- 当前是硬编码示例（id=1381755293, source=netease）

### `spiders/search_sprider.py`
- 搜索 + 获取 URL + 下载的完整流程
- 包含三个类：
  - `Search(search, headers, keyword)` — 搜索歌曲，返回歌曲列表（id, name, author 等）
  - `UrlSpider(search, headers, id, source, sign)` — 获取歌曲播放 URL
  - `SongSpider(url, headers, songname)` — 下载歌曲文件
- 当前硬编码搜索 "慢慢喜欢你"

## API 参数说明

搜索请求参数：
- types: "search" | "url" | "lyric"
- id: 歌曲 ID
- source: "netease"（网易云音乐）
- name: 搜索关键词
- count: 返回数量
- pages: 页码
- sign: 签名（搜索返回结果中包含）
- song: 歌曲 ID（歌词请求时用）

## 当前状态

爬虫目前是独立的脚本，尚未集成到 FastAPI 后端。将来可能需要：
- 将爬虫逻辑封装成 Service
- 通过后端 API 触发爬取任务
- 存入 MySQL 数据库
