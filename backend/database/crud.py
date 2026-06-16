"""数据库 CRUD 操作"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from backend.core.exceptions import DatabaseError, ResourceNotFoundError
from backend.database.models import BillRecord


def create_bill(
    db: Session,
    user_id: int,
    merchant_name: str,
    value: float,
    transaction_date: str,
    category: str,
    image_path: Optional[str] = None,
) -> BillRecord:
    """创建账单记录"""
    try:
        bill = BillRecord(
            user_id=user_id,
            merchant_name=merchant_name,
            value=value,
            transaction_date=transaction_date,
            category=category,
            image_path=image_path,
        )
        db.add(bill)
        db.commit()
        db.refresh(bill)
        return bill
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Failed to create bill: {str(e)}")


def list_bills(
    db: Session,
    user_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
) -> List[BillRecord]:
    """查询账单列表"""
    try:
        query = db.query(BillRecord).filter(BillRecord.user_id == user_id)

        if start_date:
            query = query.filter(BillRecord.transaction_date >= start_date)

        if end_date:
            query = query.filter(BillRecord.transaction_date <= end_date)

        if category:
            query = query.filter(BillRecord.category == category)

        return query.order_by(BillRecord.transaction_date.desc()).all()
    except Exception as e:
        raise DatabaseError(f"Failed to list bills: {str(e)}")


def get_bill(db: Session, bill_id: int) -> BillRecord:
    """获取单个账单"""
    try:
        bill = db.query(BillRecord).filter(BillRecord.id == bill_id).first()
        if not bill:
            raise ResourceNotFoundError("Bill", bill_id)
        return bill
    except ResourceNotFoundError:
        raise
    except Exception as e:
        raise DatabaseError(f"Failed to get bill: {str(e)}")


def update_bill(
    db: Session,
    bill_id: int,
    merchant_name: Optional[str] = None,
    value: Optional[float] = None,
    transaction_date: Optional[str] = None,
    category: Optional[str] = None,
) -> BillRecord:
    """更新账单"""
    try:
        bill = get_bill(db, bill_id)

        if merchant_name is not None:
            bill.merchant_name = merchant_name
        if value is not None:
            bill.value = value
        if transaction_date is not None:
            bill.transaction_date = transaction_date
        if category is not None:
            bill.category = category

        bill.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(bill)
        return bill
    except (ResourceNotFoundError, DatabaseError):
        raise
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Failed to update bill: {str(e)}")


def delete_bill(db: Session, bill_id: int) -> bool:
    """删除账单"""
    try:
        bill = get_bill(db, bill_id)
        db.delete(bill)
        db.commit()
        return True
    except (ResourceNotFoundError, DatabaseError):
        raise
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Failed to delete bill: {str(e)}")
