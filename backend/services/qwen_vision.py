"""千问模型 视觉模型调用服务"""

import base64
import os
from typing import Iterable, Optional

import dashscope
from dashscope import MultiModalConversation

from backend.config import settings
from backend.core.exceptions import FileError, QwenAPIError, ValidationError
from backend.services.prompts import (
    BILL_RECOGNITION_USER_PROMPT,
    build_bill_recognition_system_prompt,
)
from backend.utils import qwen_logger as _log


class QwenVisionService:
    """千问模型 服务封装"""

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
        if file_size > settings.max_image_size:
            raise FileError(f"Image file too large: {file_size} bytes (max: {settings.max_image_size})")

        # 检查文件格式
        ext = os.path.splitext(image_path)[1].lower()
        if ext not in settings.supported_image_extensions:
            supported = ", ".join(settings.supported_image_extensions)
            raise FileError(f"Unsupported image format: {ext} (supported: {supported})")

    def _encode_image_to_base64(self, image_path: str) -> str:
        """将图片编码为 base64"""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def call_qwen_vision(self, image_path: str, categories: Iterable = ()) -> str:
        """调用 千问模型 识别账单

        Args:
            image_path: 待识别的图片路径
            categories: 当前数据库中可用的分类列表，会注入到 system prompt 中。
                传空时仍会生成 prompt（仅含「其他」），但强烈建议传入实际分类。
        """
        try:
            # 验证图片
            self.validate_image(image_path)

            # 获取文件扩展名，确定 MIME 类型
            ext = os.path.splitext(image_path)[1].lower()
            mime_type = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"

            # 编码图片为 base64
            image_base64 = self._encode_image_to_base64(image_path)

            # 动态构建 system prompt（注入用户当前分类 + 今日日期）
            system_prompt = build_bill_recognition_system_prompt(categories)

            # 调用 Qwen API
            response = MultiModalConversation.call(
                model=settings.qwen_model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "image", "image": f"data:{mime_type};base64,{image_base64}"},
                            {"type": "text", "text": BILL_RECOGNITION_USER_PROMPT},
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
