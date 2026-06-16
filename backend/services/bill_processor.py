"""业务流程编排 - 账单处理整体流程"""

import os
import shutil
import tempfile
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
        self.qwen_service = get_qwen_service()
        self.bill_parser = BillParser()

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
        temp_file_path = None

        try:
            # Step 1: 验证文件
            validate_image_file(file_path)

            # Step 2: 复制文件到临时目录（保存原始图片）
            temp_dir = tempfile.gettempdir()
            temp_file_name = f"bill_{os.urandom(8).hex()}_{os.path.basename(file_path)}"
            temp_file_path = os.path.join(temp_dir, temp_file_name)
            shutil.copy2(file_path, temp_file_path)

            # Step 3: 调用 Qwen 识别
            qwen_response = self.qwen_service.call_qwen_vision(temp_file_path)

            # Step 4: 解析响应
            bill_items = self.bill_parser.parse_qwen_output(qwen_response)

            # Step 5: 保存到数据库
            for bill_item in bill_items:
                crud.create_bill(
                    db=db,
                    user_id=user_id,
                    merchant_name=bill_item.name,
                    value=bill_item.value,
                    transaction_date=bill_item.date,
                    category=bill_item.category,
                    image_path=temp_file_path,
                )

            return bill_items

        except (FileError, ValidationError):
            raise
        except Exception as e:
            raise ValidationError(f"Failed to process bill image: {str(e)}")
        finally:
            # 清理临时文件
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception:
                    pass
