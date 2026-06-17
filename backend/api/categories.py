"""分类相关 API 端点"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core import (
    BillResponse,
    CategoryInDB,
    CreateCategoryRequest,
    UpdateCategoryRequest,
)
from backend.database import crud, get_db
from backend.utils import logger

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


@router.post("", response_model=BillResponse)
def create_category(
    request: CreateCategoryRequest,
    db: Session = Depends(get_db),
) -> BillResponse:
    """新建分类"""
    try:
        category = crud.create_category(
            db,
            name=request.name,
            icon=request.icon,
            color=request.color,
            sort_order=request.sort_order,
        )
        return BillResponse(code=0, msg="success", data=CategoryInDB.model_validate(category))
    except Exception as e:
        logger.error(f"Error creating category: {str(e)}")
        return BillResponse(code=getattr(e, "code", 500), msg="error", data={"error": str(e)})


@router.get("", response_model=BillResponse)
def list_categories(db: Session = Depends(get_db)) -> BillResponse:
    """查询全部分类"""
    try:
        categories = crud.list_categories(db)
        data: List[CategoryInDB] = [CategoryInDB.model_validate(c) for c in categories]
        return BillResponse(code=0, msg="success", data=data)
    except Exception as e:
        logger.error(f"Error listing categories: {str(e)}")
        return BillResponse(code=getattr(e, "code", 500), msg="error", data={"error": str(e)})


@router.get("/{category_id}", response_model=BillResponse)
def get_category(category_id: int, db: Session = Depends(get_db)) -> BillResponse:
    """获取单个分类"""
    try:
        category = crud.get_category(db, category_id)
        return BillResponse(code=0, msg="success", data=CategoryInDB.model_validate(category))
    except Exception as e:
        logger.error(f"Error getting category {category_id}: {str(e)}")
        return BillResponse(code=getattr(e, "code", 500), msg="error", data={"error": str(e)})


@router.put("/{category_id}", response_model=BillResponse)
def update_category(
    category_id: int,
    request: UpdateCategoryRequest,
    db: Session = Depends(get_db),
) -> BillResponse:
    """更新分类"""
    try:
        category = crud.update_category(
            db,
            category_id,
            name=request.name,
            icon=request.icon,
            color=request.color,
            sort_order=request.sort_order,
        )
        return BillResponse(code=0, msg="success", data=CategoryInDB.model_validate(category))
    except Exception as e:
        logger.error(f"Error updating category {category_id}: {str(e)}")
        return BillResponse(code=getattr(e, "code", 500), msg="error", data={"error": str(e)})


@router.delete("/{category_id}", response_model=BillResponse)
def delete_category(category_id: int, db: Session = Depends(get_db)) -> BillResponse:
    """删除分类（仍被账单引用或最后一个时拒绝）"""
    try:
        crud.delete_category(db, category_id)
        return BillResponse(code=0, msg="success")
    except Exception as e:
        logger.error(f"Error deleting category {category_id}: {str(e)}")
        return BillResponse(code=getattr(e, "code", 500), msg="error", data={"error": str(e)})
