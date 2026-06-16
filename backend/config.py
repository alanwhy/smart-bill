"""应用配置"""

import os
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 应用信息
    app_name: str = "Smart Bill"
    app_version: str = "0.1.0"

    # 服务配置
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))

    # 数据库配置
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./smart_bill.db")

    # Qwen API 配置
    qwen_api_key: str = os.getenv("QWEN_API_KEY", "")

    # 日志配置
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # CORS 配置
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost",
        "http://127.0.0.1",
    ]

    class Config:
        case_sensitive = False
        env_file = ".env"


# 全局设置实例
settings = Settings()
