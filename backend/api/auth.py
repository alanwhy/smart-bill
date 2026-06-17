"""认证相关 API 端点"""

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from backend.core.models import BillResponse, ChangePasswordRequest, LoginRequest, LoginResponse, UserInfo
from backend.database import crud, get_db
from backend.services.auth_service import create_access_token, decode_token, hash_password, verify_password
from backend.utils import logger

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def get_current_user(authorization: str = Header(...), db: Session = Depends(get_db)):
    """从 Authorization Bearer token 中提取当前用户"""
    if not authorization.startswith("Bearer "):
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization[7:]
    payload = decode_token(token)
    if payload is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = payload.get("user_id")
    user = crud.get_user_by_id(db, user_id)
    if user is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="User not found")

    return user


@router.post("/login", response_model=BillResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)) -> BillResponse:
    """用户登录，返回 JWT token"""
    try:
        user = crud.get_user_by_username(db, request.username)
        if user is None or not verify_password(request.password, user.hashed_password):
            return BillResponse(code=401, msg="用户名或密码错误")

        token = create_access_token({"user_id": user.id, "username": user.username})
        data = LoginResponse(token=token, user_id=user.id, username=user.username)
        return BillResponse(code=0, msg="success", data=data.model_dump())

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return BillResponse(code=500, msg="服务器错误", data={"error": str(e)})


@router.get("/me", response_model=BillResponse)
def get_me(authorization: str = Header(...), db: Session = Depends(get_db)) -> BillResponse:
    """获取当前登录用户信息"""
    try:
        user = get_current_user(authorization, db)
        data = UserInfo(user_id=user.id, username=user.username)
        return BillResponse(code=0, msg="success", data=data.model_dump())
    except Exception as e:
        return BillResponse(code=401, msg=str(e))


@router.post("/change-password", response_model=BillResponse)
def change_password(
    request: ChangePasswordRequest,
    authorization: str = Header(...),
    db: Session = Depends(get_db),
) -> BillResponse:
    """修改密码"""
    try:
        user = get_current_user(authorization, db)

        if not verify_password(request.old_password, user.hashed_password):
            return BillResponse(code=400, msg="旧密码错误")

        new_hashed = hash_password(request.new_password)
        crud.update_password(db, user.id, new_hashed)
        return BillResponse(code=0, msg="密码修改成功")

    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        return BillResponse(code=500, msg="服务器错误", data={"error": str(e)})
