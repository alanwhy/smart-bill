"""API 路由总入口"""

from fastapi import APIRouter

from backend.api import auth, bills, categories, users

router = APIRouter()

# 注册所有子路由
router.include_router(auth.router)
router.include_router(bills.router)
router.include_router(categories.router)
router.include_router(users.router)

__all__ = ["router"]
