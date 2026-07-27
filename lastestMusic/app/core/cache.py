"""
通用 Redis 缓存工具
- @cached 装饰器：缓存 GET 接口的返回值
"""
import json
import inspect
from functools import wraps
from typing import Callable, Any

from app.core.redis_client import get_redis

DEFAULT_TTL = 300  # 5 分钟


async def cache_get(key: str) -> Any | None:
    try:
        redis = await get_redis()
        data = await redis.get(key)
        if data:
            return json.loads(data)
    except Exception:
        pass
    return None


async def cache_set(key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:
    try:
        redis = await get_redis()
        await redis.setex(key, ttl, json.dumps(value, default=str))
    except Exception:
        pass


async def cache_delete(pattern: str) -> None:
    try:
        redis = await get_redis()
        keys = await redis.keys(pattern)
        if keys:
            await redis.delete(*keys)
    except Exception:
        pass


def cached(key_prefix: str, ttl: int = DEFAULT_TTL):
    """装饰器：给 GET 端点加 Redis 缓存，保留原始函数签名供 FastAPI 依赖注入"""
    def decorator(func: Callable) -> Callable:
        # 保留原始签名，让 FastAPI 能看到 db=Depends(...) 等参数
        original_sig = inspect.signature(func)

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # 从 kwargs 提取参数造缓存 key
            cache_kwargs = dict(kwargs)
            cache_kwargs.pop("db", None)
            cache_kwargs.pop("self", None)
            if "current_user" in cache_kwargs:
                cu = cache_kwargs.pop("current_user")
                cache_kwargs["uid"] = cu.user_id if cu else "0"
            parts = [key_prefix]
            for k, v in sorted(cache_kwargs.items()):
                parts.append(f"{k}={v}")
            cache_key = ":".join(parts)

            cached_data = await cache_get(cache_key)
            if cached_data is not None:
                return cached_data

            result = await func(*args, **kwargs)

            if hasattr(result, "code") and result.code == 0:
                await cache_set(cache_key, result.model_dump(), ttl)
            return result

        # 把原始签名贴回去，FastAPI 依赖注入靠它
        wrapper.__signature__ = original_sig
        return wrapper
    return decorator
