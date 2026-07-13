---
name: project-overview
description: myMusic 在线音乐平台 — 整体架构、目录结构、技术栈总览
metadata: 
  node_type: memory
  type: project
  originSessionId: 89731bae-11f2-46cc-bae5-5a7cf7aa54ca
---

# myMusic 项目总览

一个在线音乐平台，Web + App 共用一套 React 前端（Capacitor 打包），FastAPI 后端，MySQL 数据库。

## 目录结构

```
D:\myMusic\
├── newMusic/          # 后端 FastAPI（当前活跃）
├── web/               # 前端 React 19 + Vite（当前活跃）
├── spiders/           # 爬虫脚本（调用 yinyueku.cn API）
├── music/             # 本地音乐文件（.mp3）
├── oldMusic/          # 旧版 Java Spring Boot 后端（已废弃）
├── 建模/              # PlantUML 建模图（时序图、状态图、用例图、类图、通信图、部署图）
├── 备份/              # SQL 备份
└── 技术栈.md          # 技术栈文档（中文）
```

## 技术栈

| 层 | 选型 |
|---|---|
| 后端框架 | FastAPI (Python) |
| 数据库 | MySQL + SQLAlchemy 2.0 async + asyncmy 驱动 |
| 迁移 | Alembic |
| 认证 | JWT (python-jose) + bcrypt (passlib) |
| 前端框架 | React 19 + Vite (SPA) |
| 路由 | React Router v7 |
| HTTP | Axios（带拦截器） |
| 样式 | 传统 CSS（不用 Tailwind） |
| 图标 | Lucide React |
| 音频 | Howler.js（已安装，尚未使用） |
| 移动端打包 | Capacitor（规划中） |

## 关键决策

- Web + App 同一套代码，Capacitor 打包
- SPA 非 SSR（音乐 App 不需要 SEO）
- 播放队列放前端状态管理
- JWT 密钥开发阶段用默认值
- 版本管理：GitHub https://github.com/Orlyi/myMusicRep
- 前端开发服务器默认 http://localhost:5173，后端 http://localhost:8000
