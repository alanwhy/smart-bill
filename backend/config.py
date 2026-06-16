"""应用配置"""

from typing import List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """应用配置"""

    # 应用信息
    app_name: str = "Smart Bill"
    app_version: str = "0.1.0"

    # 服务配置
    host: str = "0.0.0.0"
    port: int = 8000

    # 数据库配置
    database_url: str = "sqlite:///./smart_bill.db"

    # Qwen API 配置
    qwen_api_key: str = ""

    # 日志配置
    log_level: str = "INFO"

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
