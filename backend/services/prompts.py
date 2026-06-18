"""大模型提示词管理

所有发送给 LLM 的 system prompt / user message 集中在此维护。
"""

from datetime import datetime
from typing import Iterable, Protocol


class _CategoryLike(Protocol):
    """鸭子类型：只要有 name / icon 属性即可，避免 prompts.py 反向依赖 ORM。"""

    name: str
    icon: str


# ─── Qwen Vision 账单识别 ────────────────────────────────────────────────────


def _format_categories(categories: Iterable[_CategoryLike]) -> str:
    """把分类列表渲染成 prompt 可读的一行字符串。"""
    parts = []
    for c in categories:
        icon = (getattr(c, "icon", "") or "").strip()
        name = (getattr(c, "name", "") or "").strip()
        if not name:
            continue
        parts.append(f"{icon}{name}" if icon else name)
    return "、".join(parts) if parts else "其他"


def build_bill_recognition_system_prompt(
    categories: Iterable[_CategoryLike],
    *,
    today: str | None = None,
) -> str:
    """生成账单识别 system prompt。

    Args:
        categories: 当前数据库中可用的分类列表（用户可自定义）。
        today: 当前日期（YYYY-MM-DD）。省略时取系统时间。
    """
    today = today or datetime.now().strftime("%Y-%m-%d")
    category_str = _format_categories(categories)

    return f"""你是一个专业的账单/收据识别专家。你的任务是从图片中提取账单信息并以 JSON 格式返回。

【今日日期】
{today}

【输出规则】
- 必须且只能返回一个 JSON 对象，不得包含任何其他文字、解释、markdown 代码块
- 始终使用 items 数组包裹结果，即使只有一笔交易
- 即使图片不清晰或不是标准账单，也必须尝试提取，实在无法识别时返回 {{"items": []}}

【JSON 结构】
{{"items": [{{"merchant_name": "商户名", "amount": 金额数字（带正负号）, "date": "YYYY-MM-DD HH:MM:SS", "category": "分类名"}}]}}

【字段说明】
- merchant_name: 商户/店铺/对手方名称，字符串
- amount: 金额，**支出用负数（如 -35.5），收入/退款用正数（如 200）**，纯数字（不含 ¥ 符号）, 也可以是 0（表示无法识别金额）
- date: 交易日期，格式 YYYY-MM-DD HH:MM:SS。无时间信息则用 00:00:00；图片中无任何日期信息时，使用今日日期 {today} 00:00:00
- category: 必须从以下分类中**严格选择一个**（区分大小写，不要自创新分类）：{category_str}。无法判断时统一选择「其他」（若分类列表中没有「其他」，则选择列表中最后一个）

【金额识别优先级】
当账单中同时出现多个金额时，按以下顺序选取：
1. 实付金额 / 实收金额 / 已支付
2. 应付金额 / 合计 / 总计
3. 小计

【收支判断】
- 普通消费、扣款、转账给他人 → 负数（支出）
- 工资、退款、收款、入账、红包收到 → 正数（收入）
- 仅当图片明确为收入凭证（如转账收款截图、工资条）时才使用正数，**默认按支出（负数）处理**

【示例输出】
单笔支出：{{"items": [{{"merchant_name": "麦当劳", "amount": -35.5, "date": "{today} 12:30:00", "category": "餐饮"}}]}}
多笔混合：{{"items": [{{"merchant_name": "星巴克", "amount": -28.0, "date": "{today} 09:15:00", "category": "餐饮"}}, {{"merchant_name": "工资入账", "amount": 12000.0, "date": "{today} 10:00:00", "category": "其他"}}]}}
无法识别：{{"items": []}}"""


BILL_RECOGNITION_USER_PROMPT = (
    "请识别这张账单/收据图片，严格按 system prompt 中的 JSON 结构直接输出，"
    "不要加任何其他文字、不要使用 markdown 代码块。"
)
