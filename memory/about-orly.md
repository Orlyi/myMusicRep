---
name: about-orly
description: "Who Orly is — role, expertise, preferences, and working style"
metadata: 
  node_type: memory
  type: user
  originSessionId: 7903812b-da46-47ac-9ec7-40c461deb913
---

# About Orly

**Who**: Solo developer of the myMusic full-stack music platform project. GitHub handle: Orlyi.

**Code name**: `Orly` (git user name)

**Tech stack & preferences**:
- Backend: FastAPI + SQLAlchemy 2.0 async + MySQL + Alembic, strongly typed with Pydantic v2
- Frontend: React 19 + Vite + React Router v7 + Axios
- Styling: Plain CSS — explicitly avoided TailwindCSS v4. CSS files co-located with components.
- State management: Currently using React's built-in state + hooks; Zustand planned but not yet adopted
- Mobile: Plans to use Capacitor to wrap web build into Android APK (no separate mobile codebase)
- Audio: Howler.js
- Icons: Lucide React
- Auth: JWT + bcrypt, localStorage/sessionStorage based on "auto login" checkbox

**Working style**:
- Prefers thorough planning before execution — asked for UML modeling (sequence, communication, class, state, deployment diagrams) before diving deeper into code
- Uses PlantUML for architecting/visualizing system design
- Self-documents in `技术栈.md` — a comprehensive tech-stack doc in Chinese
- Keeps old versions: `oldMusic/` (deprecated), `备份/` (backups)
- IDE: JetBrains (`.idea/` tracked in gitignore but present)

**Current project phase**: Early development — data models (22 tables) and API routers (13 modules) are scaffolded, frontend pages are being built out. Many uncommitted changes in working tree (29 files, +880/-57).

**Platform**: Windows 11 Home China, using Git Bash for shell commands.

**Why**: Knowing Orly's full-stack inclinations, tech choices, and documentation habits means:
- Prefer structured, planned approaches before coding
- Match code style to existing patterns in the repo
- Chinese comments/docs are acceptable
- Don't suggest Tailwind or CSS frameworks — he deliberately chose plain CSS
- Don't suggest a separate mobile project — he's committed to Capacitor/web-reuse
