from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.v1 import router as v1_router
from app.core.config import settings
from app.core.redis_client import close_redis



@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print(f"🎵 {settings.app_name} 启动中...")
    yield
    # 关闭时
    print("🔌 关闭 Redis 连接...")
    await close_redis()
    print(f"🎵 {settings.app_name} 已关闭")

app = FastAPI(
    title=settings.app_name,
    description="在线音乐平台 API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)



# CORS 配置（允许前端跨域）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(v1_router)

# 静态文件（头像等上传资源）
app.mount("/static", StaticFiles(directory="uploads"), name="static")


if __name__ == "__main__":
    import uvicorn
    print("正在启动")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.server_port,
        reload=settings.debug,
    )
