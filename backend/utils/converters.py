"""数据转换工具"""

from datetime import datetime


def convert_amount(amount: str | float) -> float:
    """转换金额格式为浮点数

    Args:
        amount: 金额（可能包含 ¥、$、￥、逗号等符号）

    Returns:
        浮点数金额

    Raises:
        ValueError: 转换失败
    """
    if isinstance(amount, (int, float)):
        return float(amount)

    if not isinstance(amount, str):
        raise ValueError(f"Invalid amount type: {type(amount)}")

    # 移除货币符号
    amount_str = amount.replace("¥", "").replace("$", "").replace("￥", "").strip()

    # 移除逗号（千位分隔符）
    amount_str = amount_str.replace(",", "")

    try:
        return float(amount_str)
    except ValueError:
        raise ValueError(f"Cannot convert amount to float: {amount}")


def convert_date_to_iso8601(date_str: str) -> str:
    """转换日期为 ISO 8601 格式 (YYYY-MM-DD HH:MM:SS)

    Args:
        date_str: 日期字符串

    Returns:
        ISO 8601 格式的日期字符串

    Raises:
        ValueError: 转换失败
    """
    import re

    # 尝试多种格式
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%m-%d %H:%M:%S",
        "%m/%d %H:%M:%S",
        "%m-%d",
        "%m/%d",
    ]

    date_str = date_str.strip()

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)

            # 如果年份缺失，补充当前年份
            if "%Y" not in fmt:
                dt = dt.replace(year=datetime.now().year)

            # 如果时间缺失，补充 00:00:00
            if "%H" not in fmt:
                dt = dt.replace(hour=0, minute=0, second=0)

            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue

    raise ValueError(f"Unable to parse date: {date_str}")


def normalize_merchant_name(name: str) -> str:
    """规范化商户名称

    Args:
        name: 商户名称

    Returns:
        规范化后的商户名称
    """
    # 移除首尾空格
    name = name.strip()

    # 移除多余空格
    name = " ".join(name.split())

    return name
