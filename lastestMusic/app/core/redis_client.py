"""
全局异步 Redis 客户端
在应用启动时初始化连接池，关闭时释放。
"""
import importlib

from app.core.config import settings

# 懒加载，只有真正用了 Redis 才导入
_redis_module = None
_pool = None


def _lazy_import():
    """延迟导入 redis 包，以免没装 redis 时影响启动"""
    global _redis_module
    if _redis_module is None:
        _redis_module = importlib.import_module("redis.asyncio")
    return _redis_module


async def get_redis():
    """获取 Redis 连接（从连接池自动获取）"""
    r = _lazy_import()
    global _pool
    if _pool is None:
        _pool = r.ConnectionPool(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            username=settings.redis_user or None,
            password=settings.redis_password or None,
            decode_responses=True,   # 自动返回 str 而不是 bytes
            max_connections=20,
        )
    return r.Redis(connection_pool=_pool)


async def close_redis():
    """关闭 Redis 连接池（应用关闭时调用）"""
    global _pool
    if _pool:
        await _pool.aclose()
        _pool = None
