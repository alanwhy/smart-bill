"""Qwen3-VL-Plus 视觉模型调用服务"""

import base64
import os
from typing import Optional

import dashscope
from dashscope import MultiModalConversation

from backend.core.exceptions import FileError, QwenAPIError, ValidationError
from backend.utils import qwen_logger as _log


class QwenVisionService:
    """Qwen3-VL-Plus 服务封装"""

    # 精细化提示词
    SYSTEM_PROMPT = """你是一个专业的账单/收据识别专家。你的任务是从图片中提取账单信息并以 JSON 格式返回。

【输出规则】
- 必须且只能返回一个 JSON 对象，不得包含任何其他文字、解释、markdown 代码块
- 即使图片不清晰或不是标准账单，也必须尝试提取，实在无法识别时返回 {"items": []}

【JSON 结构】
{"items": [{"merchant_name": "商户名", "amount": 金额数字, "date": "YYYY-MM-DD HH:MM:SS", "category": "分类"}]}

【字段说明】
- merchant_name: 商户/店铺名称，字符串
- amount: 消费金额，纯数字（不含¥符号），必须大于0
- date: 交易日期，格式 YYYY-MM-DD HH:MM:SS，无时间信息则用 00:00:00，无日期则用今天
- category: 从以下选项中选择一个：餐饮、交通、购物、娱乐、医疗、住房、其他

【示例输出】
{"items": [{"merchant_name": "麦当劳", "amount": 35.5, "date": "2026-06-17 12:30:00", "category": "餐饮"}]}"""

    SUPPORTED_FORMATS = {"image/jpeg", "image/png"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    def __init__(self):
        """初始化 Qwen 服务"""
        self.api_key = os.getenv("QWEN_API_KEY")
        if not self.api_key:
            raise QwenAPIError("QWEN_API_KEY environment variable not set")

        # 设置 API 密钥
        dashscope.api_key = self.api_key

    def validate_image(self, image_path: str) -> None:
        """验证图片文件"""
        # 检查文件是否存在
        if not os.path.exists(image_path):
            raise FileError(f"Image file not found: {image_path}")

        # 检查文件大小
        file_size = os.path.getsize(image_path)
        if file_size > self.MAX_FILE_SIZE:
            raise FileError(f"Image file too large: {file_size} bytes (max: {self.MAX_FILE_SIZE})")

        # 检查文件格式
        ext = os.path.splitext(image_path)[1].lower()
        if ext not in [".jpg", ".jpeg", ".png"]:
            raise FileError(f"Unsupported image format: {ext} (supported: jpg, png)")

    def _encode_image_to_base64(self, image_path: str) -> str:
        """将图片编码为 base64"""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def call_qwen_vision(self, image_path: str) -> str:
        """调用 Qwen3-VL-Plus 识别账单"""
        try:
            # 验证图片
            self.validate_image(image_path)

            # 获取文件扩展名，确定 MIME 类型
            ext = os.path.splitext(image_path)[1].lower()
            mime_type = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"

            # 编码图片为 base64
            image_base64 = self._encode_image_to_base64(image_path)

            # 调用 Qwen API
            response = MultiModalConversation.call(
                model="qwen3.7-plus",
                messages=[
                    {
                        "role": "system",
                        "content": self.SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "image", "image": f"data:{mime_type};base64,{image_base64}"},
                            {"type": "text", "text": "请识别这张账单/收据图片，直接输出 JSON，需要包含字段商户名称、金额、日期（格式：YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS）、分类（可选）、备注（可选），不要加任何其他文字。"},
                        ],
                    },
                ],
            )

            _log.info(f"[QwenAPI] status_code={response.status_code}")
            _log.info(f"[QwenAPI] raw response={response}")

            if response.status_code != 200:
                _log.error(f"[QwenAPI] FAILED code={getattr(response, 'code', '?')} message={getattr(response, 'message', '?')}")
                raise QwenAPIError(
                    f"Qwen API error: {getattr(response, 'code', response.status_code)}",
                    detail=getattr(response, "message", str(response)),
                )

            # 提取返回内容
            result = response.output.choices[0].message.content[0]["text"]
            _log.info(f"[QwenAPI] model output={result}")
            return result

        except FileError as e:
            raise e
        except QwenAPIError as e:
            raise e
        except Exception as e:
            raise QwenAPIError(f"Failed to call Qwen vision API: {str(e)}", detail=str(e))


# 全局服务实例
_qwen_service: Optional[QwenVisionService] = None


def get_qwen_service() -> QwenVisionService:
    """获取 Qwen 服务单例"""
    global _qwen_service
    if _qwen_service is None:
        _qwen_service = QwenVisionService()
    return _qwen_service
