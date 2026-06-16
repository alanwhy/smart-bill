"""Pydantic 数据模型和类型定义"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from .enums import BillCategory


class BillItem(BaseModel):
    """账单项目（API 返回格式）"""

    value: float = Field(..., description="消费金额（元）", gt=0)
    name: str = Field(..., description="商户名称/描述", min_length=1)
    date: str = Field(..., description="消费日期时间（ISO 8601 格式）")
    category: str = Field(..., description="消费分类")

    class Config:
        json_schema_extra = {
            "example": {
                "value": 50.0,
                "name": "麦当劳",
                "date": "2026-06-16 10:00:00",
                "category": "餐饮",
            }
        }


class BillResponse(BaseModel):
    """API 统一响应格式"""

    code: int = Field(..., description="响应码")
    msg: str = Field(..., description="响应消息")
    data: any = Field(default=None, description="响应数据")


class ErrorResponse(BaseModel):
    """错误响应格式"""

    code: int = Field(..., description="错误码")
    msg: str = Field(..., description="错误消息")
    detail: str = Field(default=None, description="错误详情")


class BillRecordInDB(BaseModel):
    """数据库账单记录"""

    id: int = Field(..., description="账单 ID")
    user_id: int = Field(..., description="用户 ID")
    value: float = Field(..., description="消费金额")
    merchant_name: str = Field(..., description="商户名称")
    transaction_date: str = Field(..., description="交易日期")
    category: str = Field(..., description="分类")
    image_path: str = Field(default=None, description="图片路径")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class UploadRequest(BaseModel):
    """上传请求模型"""

    user_id: int = Field(..., description="用户 ID", ge=1)

    class Config:
        json_schema_extra = {"example": {"user_id": 1}}


class UpdateBillRequest(BaseModel):
    """修改账单请求模型"""

    value: float = Field(default=None, description="消费金额", gt=0)
    merchant_name: str = Field(default=None, description="商户名称", min_length=1)
    transaction_date: str = Field(default=None, description="交易日期")
    category: str = Field(default=None, description="分类")

    class Config:
        json_schema_extra = {
            "example": {
                "value": 55.0,
                "merchant_name": "麦当劳",
                "transaction_date": "2026-06-16 10:00:00",
                "category": "餐饮",
            }
        }
