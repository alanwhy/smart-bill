"""账单数据解析服务"""

import json
import re
from typing import List

from backend.core import BillCategory, BillItem, ValidationError


class BillParser:
    """账单数据解析器"""

    @staticmethod
    def parse_qwen_output(qwen_response: str) -> List[BillItem]:
        """解析 Qwen 的响应，提取账单项目"""
        try:
            # 尝试 JSON 格式解析
            return BillParser._parse_json_format(qwen_response)
        except (json.JSONDecodeError, KeyError, ValueError):
            # 如果 JSON 解析失败，尝试文本格式解析
            try:
                return BillParser._parse_text_format(qwen_response)
            except Exception as e:
                raise ValidationError(f"Failed to parse bill data: {str(e)}")

    @staticmethod
    def _parse_json_format(response: str) -> List[BillItem]:
        """解析 JSON 格式的响应"""
        # 尝试提取 JSON 块
        # 处理可能的 markdown 代码块格式
        json_match = re.search(r"```json\n(.*?)\n```", response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        elif response.strip().startswith("{"):
            json_str = response.strip()
        else:
            # 尝试找到 JSON 对象
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in response")
            json_str = json_match.group(0)

        data = json.loads(json_str)

        if not isinstance(data, dict) or "items" not in data:
            raise ValueError("Invalid JSON structure: missing 'items' key")

        items = []
        for item in data["items"]:
            bill_item = BillParser._build_bill_item(item)
            items.append(bill_item)

        if not items:
            raise ValueError("No items found in response")

        return items

    @staticmethod
    def _parse_text_format(response: str) -> List[BillItem]:
        """解析文本格式的响应（备选方案）"""
        items = []

        # 按行处理，查找包含金额和商户的行
        lines = response.split("\n")

        current_item = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 尝试提取金额
            amount_match = re.search(r"[\¥$￥]?\s*(\d+\.?\d*)", line)
            if amount_match:
                current_item["amount"] = float(amount_match.group(1))

            # 尝试提取日期
            date_match = re.search(r"(\d{4}[-/]\d{1,2}[-/]\d{1,2}(?:\s+\d{1,2}:\d{1,2}(?::\d{1,2})?)?)", line)
            if date_match:
                current_item["date"] = BillParser._normalize_date(date_match.group(1))

            # 尝试提取商户名称（如果行中有中文或字母）
            if re.search(r"[一-鿿\w]", line):
                if amount_match:
                    # 金额前的内容视为商户名
                    merchant = line[: amount_match.start()].strip()
                    if merchant:
                        current_item["merchant_name"] = merchant
                else:
                    # 如果没有金额，整行视为商户名
                    if "merchant_name" not in current_item:
                        current_item["merchant_name"] = line

            # 如果已经收集到足够信息，创建项目
            if all(k in current_item for k in ["merchant_name", "amount", "date"]):
                current_item["category"] = "其他"  # 文本格式中无法确定分类
                bill_item = BillParser._build_bill_item(current_item)
                items.append(bill_item)
                current_item = {}

        if not items:
            raise ValueError("Unable to parse bill data from text format")

        return items

    @staticmethod
    def _build_bill_item(item_dict: dict) -> BillItem:
        """从字典构建 BillItem"""
        # 提取必要字段
        merchant_name = item_dict.get("merchant_name", "").strip()
        if not merchant_name:
            raise ValueError("Missing merchant_name")

        amount = item_dict.get("amount")
        if amount is None:
            raise ValueError("Missing amount")
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except (ValueError, TypeError):
            raise ValueError(f"Invalid amount: {amount}")

        date_str = item_dict.get("date", "").strip()
        if not date_str:
            raise ValueError("Missing date")
        date_str = BillParser._normalize_date(date_str)

        # 分类映射
        category_str = item_dict.get("category", "其他").strip()
        category_enum = BillCategory.from_name(category_str)

        return BillItem(
            value=amount,
            name=merchant_name,
            date=date_str,
            category=category_enum.value,
        )

    @staticmethod
    def _normalize_date(date_str: str) -> str:
        """规范化日期格式为 YYYY-MM-DD HH:MM:SS"""
        date_str = date_str.strip()

        # 尝试各种常见日期格式
        patterns = [
            # YYYY-MM-DD HH:MM:SS
            (r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})\s+(\d{1,2}):(\d{1,2})(?::(\d{1,2}))?", "%Y-%m-%d %H:%M:%S"),
            # YYYY-MM-DD
            (r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})(?!\d)", "%Y-%m-%d 00:00:00"),
            # MM-DD (假设当前年)
            (r"(?:^|\D)(\d{1,2})[-/](\d{1,2})(?!\d)", ""),
        ]

        for pattern, format_str in patterns:
            match = re.search(pattern, date_str)
            if match:
                if format_str == "":
                    # MM-DD 格式，需要补充年份
                    from datetime import datetime

                    month, day = int(match.group(1)), int(match.group(2))
                    year = datetime.now().year
                    return f"{year:04d}-{month:02d}-{day:02d} 00:00:00"

                # 标准化月日和小时分秒
                groups = match.groups()
                year = int(groups[0])
                month = int(groups[1])
                day = int(groups[2])

                if len(groups) >= 4:
                    hour = int(groups[3])
                    minute = int(groups[4]) if len(groups) >= 5 else 0
                    second = int(groups[5]) if len(groups) >= 6 else 0
                else:
                    hour = minute = second = 0

                return f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"

        # 如果无法识别日期格式，返回原始字符串
        raise ValueError(f"Unable to parse date: {date_str}")
