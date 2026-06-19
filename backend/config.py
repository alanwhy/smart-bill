"""应用配置"""

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
    qwen_model: str = "qwen3.7-plus"

    # 图片上传限制
    max_image_size: int = 10 * 1024 * 1024  # 10MB
    supported_image_extensions: str = ".jpg,.jpeg,.png"

    # 日志配置
    log_level: str = "INFO"

    # CORS 配置（逗号分隔字符串，应用层解析为列表）
    cors_origins: str = "http://localhost:3000,http://localhost:8080,http://localhost,http://127.0.0.1"

    @property
    def cors_origins_list(self) -> list:
        import json
        v = self.cors_origins.strip()
        if v.startswith("["):
            try:
                return json.loads(v)
            except Exception:
                v = v.strip("[]")
        return [item.strip().strip('"\'') for item in v.split(",") if item.strip()]

    @property
    def supported_extensions_list(self) -> list:
        return [item.strip() for item in self.supported_image_extensions.split(",") if item.strip()]

    class Config:
        case_sensitive = False
        env_file = ".env"
        extra = "ignore"


# 全局设置实例
settings = Settings()


# 全局设置实例
settings = Settings()
