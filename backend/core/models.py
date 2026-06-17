"""Pydantic 数据模型和类型定义"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class CategoryBrief(BaseModel):
    """账单嵌套返回的分类简要信息"""

    id: int = Field(..., description="分类 ID")
    name: str = Field(..., description="分类名称")
    icon: str = Field(default="", description="emoji 图标")
    color: str = Field(default="#6B7280", description="十六进制颜色")

    class Config:
        from_attributes = True


class CategoryInDB(BaseModel):
    """数据库分类记录"""

    id: int = Field(..., description="分类 ID")
    name: str = Field(..., description="分类名称")
    icon: str = Field(default="", description="emoji 图标")
    color: str = Field(..., description="十六进制颜色")
    sort_order: int = Field(..., description="排序权重")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class CreateCategoryRequest(BaseModel):
    """创建分类请求"""

    name: str = Field(..., description="分类名称", min_length=1, max_length=50)
    icon: str = Field(default="", description="emoji 图标", max_length=16)
    color: str = Field(
        default="#6B7280",
        description="十六进制颜色 #RRGGBB",
        pattern=r"^#[0-9A-Fa-f]{6}$",
    )
    sort_order: Optional[int] = Field(default=None, description="排序权重，省略时取末尾", ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "宠物",
                "icon": "🐶",
                "color": "#F59E0B",
                "sort_order": 7,
            }
        }


class UpdateCategoryRequest(BaseModel):
    """更新分类请求"""

    name: Optional[str] = Field(default=None, description="分类名称", min_length=1, max_length=50)
    icon: Optional[str] = Field(default=None, description="emoji 图标", max_length=16)
    color: Optional[str] = Field(
        default=None,
        description="十六进制颜色 #RRGGBB",
        pattern=r"^#[0-9A-Fa-f]{6}$",
    )
    sort_order: Optional[int] = Field(default=None, description="排序权重", ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "宠物用品",
                "color": "#FB923C",
            }
        }


class BillItem(BaseModel):
    """账单项目（API 返回格式）"""

    value: float = Field(..., description="消费金额（元）", gt=0)
    name: str = Field(..., description="商户名称/描述", min_length=1)
    date: str = Field(..., description="消费日期时间（ISO 8601 格式）")
    category_id: int = Field(..., description="分类 ID")
    category: CategoryBrief = Field(..., description="分类详情")

    class Config:
        json_schema_extra = {
            "example": {
                "value": 50.0,
                "name": "麦当劳",
                "date": "2026-06-16 10:00:00",
                "category_id": 1,
                "category": {
                    "id": 1,
                    "name": "餐饮",
                    "icon": "🍽️",
                    "color": "#F97316",
                },
            }
        }


class BillResponse(BaseModel):
    """API 统一响应格式"""

    code: int = Field(..., description="响应码")
    msg: str = Field(..., description="响应消息")
    data: Any = Field(default=None, description="响应数据")


class ErrorResponse(BaseModel):
    """错误响应格式"""

    code: int = Field(..., description="错误码")
    msg: str = Field(..., description="错误消息")
    detail: Optional[str] = Field(default=None, description="错误详情")


class BillRecordInDB(BaseModel):
    """数据库账单记录"""

    id: int = Field(..., description="账单 ID")
    user_id: int = Field(..., description="用户 ID")
    value: float = Field(..., description="消费金额")
    merchant_name: str = Field(..., description="商户名称")
    transaction_date: str = Field(..., description="交易日期")
    category_id: int = Field(..., description="分类 ID")
    category: CategoryBrief = Field(..., description="分类详情")
    image_path: Optional[str] = Field(default=None, description="图片路径")
    description: Optional[str] = Field(default=None, description="账单备注", max_length=100)
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

    value: Optional[float] = Field(default=None, description="消费金额", gt=0)
    merchant_name: Optional[str] = Field(default=None, description="商户名称", min_length=1)
    transaction_date: Optional[str] = Field(default=None, description="交易日期")
    category_id: Optional[int] = Field(default=None, description="分类 ID", ge=1)
    description: Optional[str] = Field(default=None, description="账单备注", max_length=100)

    class Config:
        json_schema_extra = {
            "example": {
                "value": 55.0,
                "merchant_name": "麦当劳",
                "transaction_date": "2026-06-16 10:00:00",
                "category_id": 1,
            }
        }
