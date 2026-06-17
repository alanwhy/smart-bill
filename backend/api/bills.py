"""账单相关 API 端点"""

from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from backend.core import BillRecordInDB, BillResponse, UpdateBillRequest
from backend.database import crud, get_db
from backend.services import BillProcessor
from backend.utils import logger, validate_date_range, validate_user_id

router = APIRouter(prefix="/api/v1/bills", tags=["bills"])
processor = BillProcessor()


@router.post("/upload", response_model=BillResponse)
async def upload_bill(
    files: List[UploadFile] = File(...),
    user_id: int = Form(...),
    db: Session = Depends(get_db),
) -> BillResponse:
    """上传账单图片并识别"""
    try:
        validate_user_id(user_id)

        if not files:
            return BillResponse(code=400, msg="No files provided")

        all_bills = []

        for file in files:
            import tempfile

            with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
                content = await file.read()
                tmp.write(content)
                tmp_path = tmp.name

            try:
                bills = processor.process_bill_image(tmp_path, user_id, db)
                all_bills.extend(bills)
                logger.info(f"Successfully processed {file.filename} for user {user_id}, found {len(bills)} bills")
            finally:
                import os

                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

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
    db: Session = Depends(get_db),
) -> BillResponse:
    """查询账单列表"""
    try:
        validate_user_id(user_id)
        validate_date_range(start_date, end_date)

        bills = crud.list_bills(db, user_id, start_date, end_date, category_id)
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
