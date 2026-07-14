"""
Redis 键名和 TTL 常量管理
所有 key 统一在这定义，避免散落在各处。
"""

# ── 网易云 CDN 缓存（短 TTL，匹配 CDN 有效期） ──
CDN_URL_PREFIX = "netease:cdn_url:"
CDN_URL_TTL = 600  # 10 分钟

# ── 下载任务去重 ──
PENDING_DOWNLOAD_PREFIX = "netease:pending:"
PENDING_DOWNLOAD_TTL = 120  # 2 分钟，超时自动释放

# ── 下载任务队列（由 Worker 消费） ──
DOWNLOAD_QUEUE_KEY = "netease:dl_queue"
DOWNLOAD_TASK_TTL = 86400  # 24 小时，防止堆积

# ── 用户最近播放（听过） ──
RECENT_LISTEN_PREFIX = "user:listen:"
RECENT_LISTEN_MAX = 50       # 最多保留50首
RECENT_LISTEN_TTL = 604800   # 7天

# ── 通用 ──
TASK_LOCK_PREFIX = "lock:"
TASK_LOCK_TTL = 30  # 秒
