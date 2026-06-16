"""日志管理"""

import logging
import os
import sys

# 获取日志级别
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


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


# 全局记录器
logger = setup_logger("smart-bill")
