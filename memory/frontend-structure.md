---
name: frontend-structure
description: React 前端完整结构 — 页面、组件、路由、API 层、hooks
metadata: 
  node_type: memory
  type: project
  originSessionId: 89731bae-11f2-46cc-bae5-5a7cf7aa54ca
---

# 前端结构 (web/)

## 入口

- `web/src/main.jsx` — React 入口，挂载 BrowserRouter + App
- `web/src/App.jsx` — 路由配置，分为 MainLayout 内路由和独立路由

## 目录结构

```
web/src/
├── main.jsx              # 入口文件
├── App.jsx               # 路由配置
├── App.css               # 全局样式
├── index.css             # 基础样式
├── api/                  # API 请求层（axios）
│   ├── client.js         # Axios 实例，baseURL=http://localhost:8000/api/v1
│   │                     # 请求拦截器：自动注入 Bearer token
│   │                     # 响应拦截器：401 时清空 token 跳转 /login
│   ├── auth.js           # login, register, getMe, uploadAvatar
│   ├── songs.js          # listSongs, getSong, playSong, downloadSong, playCount, downloadCount
│   ├── artists.js        # 歌手 API
│   ├── albums.js         # 专辑 API
│   ├── playlists.js      # 歌单 API
│   ├── search.js         # searchSongName, searchArtistName, searchAlbumName, searchPlainLyric
│   ├── comments.js       # 评论 API
│   ├── favorites.js      # 收藏 API
│   ├── follow.js         # 关注 API
│   ├── messages.js       # 私信 API
│   ├── lyric.js          # 歌词 API
│   └── users.js          # 用户 API
├── components/           # 公共组件
│   ├── Sidebar.jsx       # 侧边栏（含退出登录按钮 + 插槽 children）
│   ├── Sidebar.css
│   ├── SidebarItem.jsx   # 侧边栏菜单项（含导航跳转）
│   ├── SidebarItem.css
│   ├── TopBar.jsx        # 顶部导航栏（含返回按钮 GoBack）
│   ├── GoBack.jsx        # 返回按钮
│   ├── DetailItem.jsx    # 详情项展示组件
│   └── Navigate.js       # 导航工具
├── hooks/
│   └── useAuth.js        # 认证 hook：检查 token，非公开页面自动跳转 /login
│                         # 公开路径：["/", "/register"]
│                         # 提供 logout() 方法
├── layouts/
│   └── MainLayout.jsx    # 主布局：顶部汉堡菜单 + 侧边栏 + 底部 4 标签导航（首页/消息/列表/我的）+ <Outlet>
├── pages/                # 页面组件（12 个）
│   ├── index.js          # 统一导出
│   ├── HomePage.jsx      # 首页（占位中）
│   ├── HomePage.css
│   ├── LoginPage.jsx     # 登录页：用户名/密码、记住密码、自动登录、错误提示
│   ├── LoginPage.css
│   ├── RegisterPage.jsx  # 注册页：头像上传、用户名、密码、确认密码、邮箱
│   ├── RegisterPage.css
│   ├── SearchPage.jsx    # 搜索页（占位中）
│   ├── SongDetailPage.jsx     # 歌曲详情页
│   ├── ArtistDetailPage.jsx   # 歌手详情页
│   ├── AlbumDetailPage.jsx    # 专辑详情页
│   ├── PlaylistDetailPage.jsx # 歌单详情页
│   ├── LibraryPage.jsx   # 我的收藏/列表
│   ├── MessagesPage.jsx  # 私信页
│   ├── ProfilePage.jsx   # 个人信息页
│   ├── ProfilePage.css
│   └── ProfileDetailPage.jsx  # 个人信息详情页
```

## 路由表

| 路由 | 页面 | 布局 |
|------|------|------|
| `/` | HomePage | MainLayout（底部导航） |
| `/library` | LibraryPage | MainLayout |
| `/messages` | MessagesPage | MainLayout |
| `/profile` | ProfilePage | MainLayout |
| `/profile/detail` | ProfileDetailPage | 独立（无底部导航） |
| `/search` | SearchPage | 独立 |
| `/song/:id` | SongDetailPage | 独立 |
| `/artist/:id` | ArtistDetailPage | 独立 |
| `/album/:id` | AlbumDetailPage | 独立 |
| `/playlist/:id` | PlaylistDetailPage | 独立 |
| `/login` | LoginPage | 独立 |
| `/register` | RegisterPage | 独立 |

## 认证流程

1. 登录成功 → token 存 localStorage（自动登录）或 sessionStorage
2. Axios 拦截器自动在每个请求头加 `Authorization: Bearer <token>`
3. 401 响应 → 清空 token，跳转 `/login`
4. useAuth hook 在页面加载时检查 token，非公开路径无 token → 跳转登录

## 依赖版本

- React 19.2.6, React Router 7.18.0, Axios 1.18.0
- Howler.js 2.2.4（已安装，尚未实际使用）
- Lucide React 1.21.0（图标库）
- Vite 8.0.12
