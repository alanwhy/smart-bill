"""API 路由总入口"""

from fastapi import APIRouter

from backend.api import bills, categories

router = APIRouter()

# 注册所有子路由
router.include_router(bills.router)
router.include_router(categories.router)

__all__ = ["router"]
