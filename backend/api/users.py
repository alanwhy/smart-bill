"""管理员用户管理 API 端点（仅 admin 可访问）"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api.auth import require_admin
from backend.core.models import (
    AdminUserBrief,
    BillResponse,
    CreateUserRequest,
    ResetPasswordResponse,
    UpdateUsernameRequest,
)
from backend.database import crud, get_db
from backend.services.auth_service import generate_temp_password, hash_password
from backend.utils import logger

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("", response_model=BillResponse)
def list_users(
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
) -> BillResponse:
    """列出全部用户"""
    try:
        users = crud.list_users(db)
        data = [AdminUserBrief.model_validate(u).model_dump() for u in users]
        return BillResponse(code=0, msg="success", data=data)
    except Exception as e:
        logger.error(f"List users error: {str(e)}")
        return BillResponse(code=getattr(e, "code", 500), msg="error", data={"error": str(e)})


@router.post("", response_model=BillResponse)
def create_user(
    request: CreateUserRequest,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
) -> BillResponse:
    """创建新用户（默认首次登录强制改密）"""
    try:
        user = crud.create_user(
            db,
            username=request.username,
            hashed_password=hash_password(request.password),
            role=request.role,
            must_change_password=True,
        )
        return BillResponse(
            code=0,
            msg="success",
            data=AdminUserBrief.model_validate(user).model_dump(),
        )
    except Exception as e:
        logger.error(f"Create user error: {str(e)}")
        return BillResponse(code=getattr(e, "code", 500), msg="error", data={"error": str(e)})


@router.put("/{user_id}/username", response_model=BillResponse)
def update_username(
    user_id: int,
    request: UpdateUsernameRequest,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
) -> BillResponse:
    """修改用户名（任何人不能修改自己的用户名，含 admin）"""
    try:
        if user_id == admin.id:
            raise HTTPException(status_code=403, detail="不能修改自己的用户名")

        user = crud.update_username(db, user_id, request.username)
        return BillResponse(
            code=0,
            msg="success",
            data=AdminUserBrief.model_validate(user).model_dump(),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update username error: {str(e)}")
        return BillResponse(code=getattr(e, "code", 500), msg="error", data={"error": str(e)})


@router.post("/{user_id}/reset-password", response_model=BillResponse)
def reset_password(
    user_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
) -> BillResponse:
    """管理员重置目标用户密码：生成临时密码并要求其下次登录强制修改"""
    try:
        temp_pw = generate_temp_password(8)
        user = crud.reset_user_password(db, user_id, hash_password(temp_pw))
        data = ResetPasswordResponse(
            user_id=user.id,
            username=user.username,
            temp_password=temp_pw,
        )
        return BillResponse(code=0, msg="success", data=data.model_dump())
    except Exception as e:
        logger.error(f"Reset password error: {str(e)}")
        return BillResponse(code=getattr(e, "code", 500), msg="error", data={"error": str(e)})
