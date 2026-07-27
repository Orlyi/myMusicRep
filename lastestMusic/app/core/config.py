from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置，自动从 .env 文件加载"""

    # 应用
    app_name: str = "myMusic"
    debug: bool = False
    server_port: int = 8000

    # 数据库
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = Field(..., alias="DB_PASSWORD")
    db_name: str = "myMusic"
    db_pool_size: int = 10
    db_max_overflow: int = 20

    # JWT
    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    netease_cookie: str = Field(..., alias="NETEASE_COOKIE")

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_user: str = ""
    redis_password: str = ""

    @property
    def database_url(self) -> str:
        """构建异步 MySQL 连接字符串"""
        return (
            f"mysql+asyncmy://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
            f"?charset=utf8mb4"
        )

    model_config = {"env_file": [".env", ".env.prod"], "env_file_encoding": "utf-8"}


settings = Settings()
