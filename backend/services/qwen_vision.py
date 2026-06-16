"""Qwen3-VL-Plus 视觉模型调用服务"""

import base64
import os
from typing import Optional

import dashscope
from dashscope import MultiModalConversation

from backend.core.exceptions import FileError, QwenAPIError, ValidationError


class QwenVisionService:
    """Qwen3-VL-Plus 服务封装"""

    # 精细化提示词
    SYSTEM_PROMPT = """你是一个专业的账单/收据识别专家。
请分析这张账单/收据图片，提取其中的所有消费项目信息。

返回格式必须是有效的 JSON，包含以下结构：
{
  "items": [
    {
      "merchant_name": "商户名称",
      "amount": 金额数字（仅数字，不含符号），
      "date": "YYYY-MM-DD HH:MM:SS 格式的日期（如果没有时间则使用 00:00:00）",
      "category": "分类（从以下选项中选择：餐饮、交通、购物、娱乐、医疗、住房、其他）"
    }
  ]
}

重要说明：
1. 如果图片中有多个消费项目，请全部提取
2. 日期格式必须是 YYYY-MM-DD HH:MM:SS
3. 金额必须是数字格式
4. 只返回 JSON，不要添加其他文字"""

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
                model="qwen-vl-plus",
                messages=[
                    {
                        "role": "system",
                        "content": self.SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "image", "image": f"data:{mime_type};base64,{image_base64}"},
                            {"type": "text", "text": "请识别这张账单/收据，提取所有消费项目信息。"},
                        ],
                    },
                ],
            )

            if response.status_code != 200:
                raise QwenAPIError(
                    f"Qwen API error: {response.code}",
                    detail=response.message if hasattr(response, "message") else str(response),
                )

            # 提取返回内容
            result = response.output.choices[0].message.content[0]["text"]
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
