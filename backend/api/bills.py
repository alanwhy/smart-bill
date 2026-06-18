"""账单相关 API 端点"""

import asyncio
import os
import tempfile
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from backend.core import BillRecordInDB, BillResponse, UpdateBillRequest
from backend.database import crud, get_db
from backend.database.db import SessionLocal
from backend.services import BillProcessor
from backend.utils import logger, validate_date_range, validate_user_id

router = APIRouter(prefix="/api/v1/bills", tags=["bills"])
processor = BillProcessor()


def _process_single_bill(tmp_path: str, filename: str, user_id: int) -> list:
    """在独立线程中处理单张账单（每次创建独立 db session，SQLAlchemy session 不能跨线程共享）"""
    db = SessionLocal()
    try:
        bills = processor.process_bill_image(tmp_path, user_id, db)
        logger.info(f"Successfully processed {filename} for user {user_id}, found {len(bills)} bills")
        return bills
    except Exception as e:
        logger.error(f"Failed to process {filename}: {str(e)}")
        return []
    finally:
        db.close()
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


@router.post("/upload", response_model=BillResponse)
async def upload_bill(
    files: List[UploadFile] = File(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db),
) -> BillResponse:
    """上传账单图片并识别（多张图片并发处理）"""
    try:
        validate_user_id(user_id)

        if not files:
            return BillResponse(code=400, msg="No files provided")

        # 1. 先将所有文件写入临时目录（串行，<5ms，非瓶颈）
        tmp_paths: List[tuple[str, str]] = []
        for file in files:
            ext = os.path.splitext(file.filename or "")[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                content = await file.read()
                tmp.write(content)
                tmp_paths.append((tmp.name, file.filename or "unknown"))

        # 2. 并发调用 Qwen API（每张图片独立线程 + 独立 db session）
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(None, _process_single_bill, tmp_path, filename, user_id)
            for tmp_path, filename in tmp_paths
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 3. 合并结果，跳过失败项
        all_bills = []
        for r in results:
            if isinstance(r, list):
                all_bills.extend(r)
            elif isinstance(r, Exception):
                logger.error(f"Bill processing task raised exception: {str(r)}")

        return BillResponse(code=0, msg="success", data=all_bills)

    except Exception as e:
        logger.error(f"Error processing bill upload: {str(e)}")
        return BillResponse(code=getattr(e, "code", 500), msg="error", data={"error": str(e)})


@router.get("", response_model=BillResponse)
def list_bills(
    user_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category_id: Optional[int] = None,
    merchant_name: Optional[str] = None,
    db: Session = Depends(get_db),
) -> BillResponse:
    """查询账单列表"""
    try:
        validate_user_id(user_id)
        validate_date_range(start_date, end_date)

        bills = crud.list_bills(db, user_id, start_date, end_date, category_id, merchant_name)
        bill_records = [BillRecordInDB.model_validate(bill) for bill in bills]
        return BillResponse(code=0, msg="success", data=bill_records)

    except Exception as e:
        logger.error(f"Error listing bills: {str(e)}")
        return BillResponse(code=getattr(e, "code", 500), msg="error", data={"error": str(e)})


@router.put("/{bill_id}", response_model=BillResponse)
def update_bill(
    bill_id: int,
    request: UpdateBillRequest,
    db: Session = Depends(get_db),
) -> BillResponse:
    """修改账单"""
    try:
        bill = crud.update_bill(
            db,
            bill_id,
            merchant_name=request.merchant_name,
            value=request.value,
            transaction_date=request.transaction_date,
            category_id=request.category_id,
            description=request.description,
        )
        return BillResponse(code=0, msg="success", data=BillRecordInDB.model_validate(bill))

    except Exception as e:
        logger.error(f"Error updating bill: {str(e)}")
        return BillResponse(code=getattr(e, "code", 500), msg="error", data={"error": str(e)})


@router.delete("/{bill_id}", response_model=BillResponse)
def delete_bill(
    bill_id: int,
    db: Session = Depends(get_db),
) -> BillResponse:
    """删除账单"""
    try:
        crud.delete_bill(db, bill_id)
        return BillResponse(code=0, msg="success")

    except Exception as e:
        logger.error(f"Error deleting bill: {str(e)}")
        return BillResponse(code=getattr(e, "code", 500), msg="error", data={"error": str(e)})
