"""日志管理"""

import logging
import os
import sys

# 获取日志级别
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# 日志目录（相对于项目根目录）
_LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")


def _ensure_log_dir() -> str:
    os.makedirs(_LOG_DIR, exist_ok=True)
    return _LOG_DIR


def setup_logger(name: str = __name__) -> logging.Logger:
    """设置日志记录器

    Args:
        name: 记录器名称

    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, LOG_LEVEL))

    # 创建格式化器
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台 handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def setup_qwen_logger() -> logging.Logger:
    """专用 Qwen API 日志记录器，同时写入控制台和 log/qwen.log"""
    qwen_log = logging.getLogger("smart-bill.qwen")

    if qwen_log.handlers:
        return qwen_log

    qwen_log.setLevel(logging.DEBUG)
    qwen_log.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    qwen_log.addHandler(console_handler)

    try:
        log_dir = _ensure_log_dir()
        file_handler = logging.FileHandler(
            os.path.join(log_dir, "qwen.log"), encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        qwen_log.addHandler(file_handler)
    except OSError:
        pass  # 文件系统不可写时静默降级到控制台

    return qwen_log


# 全局记录器
logger = setup_logger("smart-bill")
qwen_logger = setup_qwen_logger()
