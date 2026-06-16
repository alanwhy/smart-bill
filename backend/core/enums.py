"""枚举类型定义"""

from enum import Enum


class BillCategory(str, Enum):
    """账单分类枚举"""

    DINING = "餐饮"
    TRANSPORT = "交通"
    SHOPPING = "购物"
    ENTERTAINMENT = "娱乐"
    HEALTHCARE = "医疗"
    HOUSING = "住房"
    OTHER = "其他"

    @classmethod
    def get_all_names(cls) -> list[str]:
        """获取所有分类名称"""
        return [item.value for item in cls]

    @classmethod
    def from_name(cls, name: str) -> "BillCategory":
        """根据名称获取分类，支持模糊匹配"""
        name = name.strip()

        # 精确匹配
        for item in cls:
            if item.value == name:
                return item

        # 模糊匹配
        name_lower = name.lower()
        for item in cls:
            if item.value.lower() in name_lower or name_lower in item.value.lower():
                return item

        # 默认返回其他
        return cls.OTHER
