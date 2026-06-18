"""业务流程编排 - 账单处理整体流程"""

import os
from typing import List

from sqlalchemy.orm import Session

from backend.core import BillItem, FileError, ValidationError
from backend.database import crud
from backend.services.bill_parser import BillParser
from backend.services.qwen_vision import get_qwen_service
from backend.utils.validators import validate_image_file


class BillProcessor:
    """账单处理器 - 协调整个处理流程"""

    def __init__(self):
        """初始化处理器"""
        self.qwen_service = None
        self.bill_parser = BillParser()

    def _get_qwen_service(self):
        """延迟加载 Qwen 服务"""
        if self.qwen_service is None:
            self.qwen_service = get_qwen_service()
        return self.qwen_service

    def process_bill_image(self, file_path: str, user_id: int, db: Session) -> List[BillItem]:
        """处理单个账单图片的完整流程

        Args:
            file_path: 上传的图片文件路径
            user_id: 用户 ID
            db: 数据库会话

        Returns:
            识别到的账单项目列表

        Raises:
            FileError: 文件处理错误
            ValidationError: 验证错误
        """
        try:
            # Step 1: 验证文件
            validate_image_file(file_path)

            # Step 2: 调用 Qwen 识别（直接使用传入的 file_path，无需二次复制）
            qwen_response = self._get_qwen_service().call_qwen_vision(file_path)

            # Step 4: 加载分类用于模糊匹配，再解析响应
            categories = crud.list_categories(db)
            bill_items = self.bill_parser.parse_qwen_output(qwen_response, categories)

            # Step 5: 保存到数据库
            for bill_item in bill_items:
                crud.create_bill(
                    db=db,
                    user_id=user_id,
                    merchant_name=bill_item.name,
                    value=bill_item.value,
                    transaction_date=bill_item.date,
                    category_id=bill_item.category_id,
                    image_path=file_path,
                )

            return bill_items

        except (FileError, ValidationError):
            raise
        except Exception as e:
            raise ValidationError(f"Failed to process bill image: {str(e)}")
