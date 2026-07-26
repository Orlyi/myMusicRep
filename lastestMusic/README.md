# myMusic Backend Server

在线音乐平台后端 API 服务。

## 环境要求

- **Python** 3.10+
- **MySQL** 8.0
- **Node.js** 18+（用于网易云音乐播放地址解密）
- **Redis**（可选，推荐用于缓存）

## 快速部署

```bash
# 1. 安装 Python 依赖
pip install -r requirements.txt

# 2. 创建并初始化数据库
# 先登录 MySQL 创建数据库：
mysql -u root -p
CREATE DATABASE myMusic CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
exit

# 然后导入建表脚本：
mysql -u root -p myMusic < init_db.sql

# （可选）导入存储过程和触发器：
mysql -u root -p myMusic < mysql/procedures_triggers_functions.sql

# 3. 配置环境变量
mv .env.prod .env
# 编辑 .env，填入你的数据库密码、JWT密钥等

# 4. 启动服务
python app/main.py
```

服务默认运行在 `http://0.0.0.0:8000`，API 文档访问 `http://localhost:8000/docs`。

## 环境变量说明（.env）

| 变量 | 说明 | 示例 |
|------|------|------|
| `DB_HOST` | MySQL 地址 | `localhost` |
| `DB_PASSWORD` | MySQL 密码 | `your_password` |
| `JWT_SECRET_KEY` | JWT 签名密钥（随机字符串） | `random-string` |
| `NETEASE_COOKIE` | 网易云音乐 Cookie（登录后 F12 获取） | 见 .env.prod 模板 |

## 项目结构

```
lastMusic/
├── app/                # 后端核心代码
│   ├── api/v1/         # API 路由（15+ 接口模块）
│   ├── core/           # 配置、数据库、Redis 连接
│   ├── models/         # SQLAlchemy ORM 模型（21 张表）
│   ├── schemas/        # Pydantic 数据校验
│   ├── services/       # 业务逻辑
│   └── utils/          # JWT、密码加密工具
├── spiders/            # 网易云加密模块
│   ├── encrypt.py      # AES+RSA 加密破解
│   └── RSA.js          # RSA 加密（Node.js）
├── alembic/            # 数据库迁移
├── init_db.sql         # 建表脚本
├── requirements.txt    # Python 依赖
└── .env.prod           # 环境变量模板
```
