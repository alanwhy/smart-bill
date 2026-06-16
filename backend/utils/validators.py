"""数据和文件验证工具"""

import os

from backend.core import FileError


def validate_image_file(file_path: str, max_size: int = 10 * 1024 * 1024) -> None:
    """验证图片文件

    Args:
        file_path: 文件路径
        max_size: 最大文件大小（字节），默认 10MB

    Raises:
        FileError: 验证失败
    """
    # 检查文件存在
    if not os.path.exists(file_path):
        raise FileError(f"Image file not found: {file_path}")

    # 检查文件大小
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        raise FileError("Image file is empty")

    if file_size > max_size:
        raise FileError(f"Image file too large: {file_size} bytes (max: {max_size})")

    # 检查文件格式
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    if ext not in [".jpg", ".jpeg", ".png"]:
        raise FileError(f"Unsupported image format: {ext} (supported: .jpg, .jpeg, .png)")


def validate_user_id(user_id: int) -> None:
    """验证用户 ID

    Args:
        user_id: 用户 ID

    Raises:
        ValueError: 验证失败
    """
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError(f"Invalid user_id: {user_id}")


def validate_date_range(start_date: str = None, end_date: str = None) -> None:
    """验证日期范围

    Args:
        start_date: 开始日期（YYYY-MM-DD 格式）
        end_date: 结束日期（YYYY-MM-DD 格式）

    Raises:
        ValueError: 验证失败
    """
    import re

    date_pattern = r"^\d{4}-\d{2}-\d{2}$"

    if start_date and not re.match(date_pattern, start_date):
        raise ValueError(f"Invalid start_date format: {start_date} (expected YYYY-MM-DD)")

    if end_date and not re.match(date_pattern, end_date):
        raise ValueError(f"Invalid end_date format: {end_date} (expected YYYY-MM-DD)")

    if start_date and end_date and start_date > end_date:
        raise ValueError(f"start_date cannot be later than end_date")
