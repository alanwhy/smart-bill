"""账单数据解析服务"""

import json
import re
from typing import List, Optional, Sequence

from backend.core import BillItem, CategoryBrief, ValidationError
from backend.database.models import Category
from backend.utils import logger


class BillParser:
    """账单数据解析器"""

    @staticmethod
    def parse_qwen_output(qwen_response: str, categories: Sequence[Category]) -> List[BillItem]:
        """解析 Qwen 的响应，提取账单项目

        Args:
            qwen_response: Qwen Vision 返回的原始文本
            categories: 当前数据库中的全部分类，用于模糊匹配
        """
        logger.info(f"[BillParser] Qwen 原始返回内容:\n{qwen_response}")
        try:
            return BillParser._parse_json_format(qwen_response, categories)
        except (json.JSONDecodeError, KeyError, ValueError):
            try:
                return BillParser._parse_text_format(qwen_response, categories)
            except Exception as e:
                logger.error("[BillParser] 文本格式解析也失败，原始内容已记录在上方")
                raise ValidationError(f"Failed to parse bill data: {str(e)}")

    @staticmethod
    def _parse_json_format(response: str, categories: Sequence[Category]) -> List[BillItem]:
        """解析 JSON 格式的响应"""
        # 优先尝试 ```json ... ``` 代码块
        json_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1).strip()
        elif response.strip().startswith(("{", "[")):
            json_str = response.strip()
        else:
            # 从文本中提取最外层 JSON 对象
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in response")
            json_str = json_match.group(0)

        data = json.loads(json_str)

        # 兼容直接返回数组的情况
        if isinstance(data, list):
            raw_items = data
        elif isinstance(data, dict):
            if "items" not in data:
                raise ValueError("Invalid JSON structure: missing 'items' key")
            raw_items = data["items"]
        else:
            raise ValueError("Unexpected JSON root type")

        items = []
        for item in raw_items:
            bill_item = BillParser._build_bill_item(item, categories)
            items.append(bill_item)

        if not items:
            raise ValueError("No items found in response")

        return items

    @staticmethod
    def _parse_text_format(response: str, categories: Sequence[Category]) -> List[BillItem]:
        """解析文本格式的响应（备选方案）"""
        items = []
        lines = response.split("\n")
        current_item = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            amount_match = re.search(r"[\¥$￥]?\s*(-?\d+\.?\d*)", line)
            if amount_match:
                amount_val = float(amount_match.group(1))
                # 文本兜底分支无法可靠区分收支，缺省按支出（负数）处理
                if amount_val > 0:
                    amount_val = -amount_val
                current_item["amount"] = amount_val

            date_match = re.search(r"(\d{4}[-/]\d{1,2}[-/]\d{1,2}(?:\s+\d{1,2}:\d{1,2}(?::\d{1,2})?)?)", line)
            if date_match:
                current_item["date"] = BillParser._normalize_date(date_match.group(1))

            if re.search(r"[一-鿿\w]", line):
                if amount_match:
                    merchant = line[: amount_match.start()].strip()
                    if merchant:
                        current_item["merchant_name"] = merchant
                else:
                    if "merchant_name" not in current_item:
                        current_item["merchant_name"] = line

            if all(k in current_item for k in ["merchant_name", "amount", "date"]):
                current_item["category"] = "其他"
                bill_item = BillParser._build_bill_item(current_item, categories)
                items.append(bill_item)
                current_item = {}

        if not items:
            raise ValueError("Unable to parse bill data from text format")

        return items

    @staticmethod
    def _resolve_category(name: Optional[str], categories: Sequence[Category]) -> Category:
        """根据 LLM 返回的分类名做模糊匹配，返回 Category 实体。

        匹配顺序：
        1. 精确同名
        2. 双向 substring 模糊匹配
        3. 名为 "其他" 的兜底分类
        4. 全部分类中 sort_order 最大者（"其他"被改名时的兜底）
        """
        if not categories:
            raise ValidationError("No categories available; database not seeded")

        clean = (name or "").strip()
        if clean:
            for c in categories:
                if c.name == clean:
                    return c
            lower = clean.lower()
            for c in categories:
                cname = c.name.lower()
                if cname in lower or lower in cname:
                    return c

        for c in categories:
            if c.name == "其他":
                return c
        return max(categories, key=lambda c: (c.sort_order, c.id))

    @staticmethod
    def _build_bill_item(item_dict: dict, categories: Sequence[Category]) -> BillItem:
        """从字典构建 BillItem"""
        merchant_name = item_dict.get("merchant_name", "").strip()
        if not merchant_name:
            raise ValueError("Missing merchant_name")

        amount = item_dict.get("amount")
        if amount is None:
            raise ValueError("Missing amount")
        try:
            amount = float(amount)
            if amount == 0:
                raise ValueError("Amount must not be zero")
        except (ValueError, TypeError):
            raise ValueError(f"Invalid amount: {amount}")

        date_str = item_dict.get("date", "").strip()
        if not date_str:
            raise ValueError("Missing date")
        date_str = BillParser._normalize_date(date_str)

        category_str = item_dict.get("category", "其他")
        category = BillParser._resolve_category(category_str, categories)

        return BillItem(
            value=amount,
            name=merchant_name,
            date=date_str,
            category_id=category.id,
            category=CategoryBrief.model_validate(category),
        )

    @staticmethod
    def _normalize_date(date_str: str) -> str:
        """规范化日期格式为 YYYY-MM-DD HH:MM:SS"""
        date_str = date_str.strip()

        patterns = [
            (r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})\s+(\d{1,2}):(\d{1,2})(?::(\d{1,2}))?", "%Y-%m-%d %H:%M:%S"),
            (r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})(?!\d)", "%Y-%m-%d 00:00:00"),
            (r"(?:^|\D)(\d{1,2})[-/](\d{1,2})(?!\d)", ""),
        ]

        for pattern, format_str in patterns:
            match = re.search(pattern, date_str)
            if match:
                if format_str == "":
                    from datetime import datetime

                    month, day = int(match.group(1)), int(match.group(2))
                    year = datetime.now().year
                    return f"{year:04d}-{month:02d}-{day:02d} 00:00:00"

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

        raise ValueError(f"Unable to parse date: {date_str}")
