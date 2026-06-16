"""API 路由总入口"""

from fastapi import APIRouter

from backend.api import bills

router = APIRouter()

# 注册所有子路由
router.include_router(bills.router)

__all__ = ["router"]
