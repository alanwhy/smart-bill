"""数据库 CRUD 操作"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.core.exceptions import DatabaseError, ResourceNotFoundError, ValidationError
from backend.database.models import BillRecord, Category, User


# ---------------------------------------------------------------------------
# Category CRUD
# ---------------------------------------------------------------------------


def create_category(
    db: Session,
    name: str,
    icon: str = "",
    color: str = "#6B7280",
    sort_order: Optional[int] = None,
) -> Category:
    """创建分类"""
    try:
        existing = db.query(Category).filter(Category.name == name).first()
        if existing:
            raise ValidationError(
                "Category name already exists",
                detail=f"Category with name '{name}' already exists",
            )

        if sort_order is None:
            current_max = db.query(func.max(Category.sort_order)).scalar()
            sort_order = (current_max + 1) if current_max is not None else 0

        category = Category(name=name, icon=icon, color=color, sort_order=sort_order)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category
    except ValidationError:
        raise
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Failed to create category: {str(e)}")


def list_categories(db: Session) -> List[Category]:
    """查询全部分类，按 sort_order/id 升序"""
    try:
        return db.query(Category).order_by(Category.sort_order.asc(), Category.id.asc()).all()
    except Exception as e:
        raise DatabaseError(f"Failed to list categories: {str(e)}")


def get_category(db: Session, category_id: int) -> Category:
    """获取单个分类"""
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise ResourceNotFoundError("Category", category_id)
        return category
    except ResourceNotFoundError:
        raise
    except Exception as e:
        raise DatabaseError(f"Failed to get category: {str(e)}")


def get_category_by_name(db: Session, name: str) -> Optional[Category]:
    """根据名称获取分类（精确匹配，未找到返回 None）"""
    try:
        return db.query(Category).filter(Category.name == name).first()
    except Exception as e:
        raise DatabaseError(f"Failed to query category by name: {str(e)}")


def update_category(
    db: Session,
    category_id: int,
    name: Optional[str] = None,
    icon: Optional[str] = None,
    color: Optional[str] = None,
    sort_order: Optional[int] = None,
) -> Category:
    """更新分类"""
    try:
        category = get_category(db, category_id)

        if name is not None and name != category.name:
            duplicate = db.query(Category).filter(Category.name == name, Category.id != category_id).first()
            if duplicate:
                raise ValidationError(
                    "Category name already exists",
                    detail=f"Category with name '{name}' already exists",
                )
            category.name = name
        if icon is not None:
            category.icon = icon
        if color is not None:
            category.color = color
        if sort_order is not None:
            category.sort_order = sort_order

        category.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(category)
        return category
    except (ResourceNotFoundError, ValidationError):
        raise
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Failed to update category: {str(e)}")


def delete_category(db: Session, category_id: int) -> bool:
    """删除分类（仍被账单引用或最后一个时拒绝）"""
    try:
        category = get_category(db, category_id)

        ref_count = db.query(BillRecord).filter(BillRecord.category_id == category_id).count()
        if ref_count > 0:
            raise ValidationError(
                "Cannot delete category with bills",
                detail=f"分类「{category.name}」下还有账单，请先修改这些账单的分类后再删除",
            )

        total = db.query(Category).count()
        if total <= 1:
            raise ValidationError(
                "Cannot delete the last category",
                detail="至少保留一个分类，无法删除",
            )

        db.delete(category)
        db.commit()
        return True
    except (ResourceNotFoundError, ValidationError):
        raise
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Failed to delete category: {str(e)}")


# ---------------------------------------------------------------------------
# Bill CRUD
# ---------------------------------------------------------------------------


def create_bill(
    db: Session,
    user_id: int,
    merchant_name: str,
    value: float,
    transaction_date: str,
    category_id: int,
    description: Optional[str] = None,
) -> BillRecord:
    """创建账单记录"""
    try:
        # 校验分类存在
        get_category(db, category_id)

        bill = BillRecord(
            user_id=user_id,
            merchant_name=merchant_name,
            value=value,
            transaction_date=transaction_date,
            category_id=category_id,
            description=description,
        )
        db.add(bill)
        db.commit()
        db.refresh(bill)
        return bill
    except (ResourceNotFoundError, DatabaseError):
        raise
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Failed to create bill: {str(e)}")


def list_bills(
    db: Session,
    user_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category_id: Optional[int] = None,
    merchant_name: Optional[str] = None,
) -> List[BillRecord]:
    """查询账单列表"""
    try:
        query = db.query(BillRecord).filter(BillRecord.user_id == user_id)

        if start_date:
            query = query.filter(BillRecord.transaction_date >= start_date)

        if end_date:
            query = query.filter(BillRecord.transaction_date <= end_date + "T23:59:59")

        if category_id:
            query = query.filter(BillRecord.category_id == category_id)

        if merchant_name:
            query = query.filter(BillRecord.merchant_name.ilike(f"%{merchant_name}%"))

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
    category_id: Optional[int] = None,
    description: Optional[str] = None,
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
        if category_id is not None:
            # 校验分类存在
            get_category(db, category_id)
            bill.category_id = category_id
        if description is not None:
            bill.description = description

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


# ---------------------------------------------------------------------------
# User CRUD
# ---------------------------------------------------------------------------


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名查找用户"""
    try:
        return db.query(User).filter(User.username == username).first()
    except Exception as e:
        raise DatabaseError(f"Failed to query user: {str(e)}")


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """根据 ID 查找用户"""
    try:
        return db.query(User).filter(User.id == user_id).first()
    except Exception as e:
        raise DatabaseError(f"Failed to query user: {str(e)}")


def create_user(db: Session, username: str, hashed_password: str) -> User:
    """创建用户"""
    try:
        user = User(username=username, hashed_password=hashed_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Failed to create user: {str(e)}")


def update_password(db: Session, user_id: int, new_hashed_password: str) -> User:
    """更新用户密码"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ResourceNotFoundError("User", user_id)
        user.hashed_password = new_hashed_password
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user
    except ResourceNotFoundError:
        raise
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Failed to update password: {str(e)}")


def get_user_cycle(db: Session, user_id: int) -> int:
    """获取用户的月度账单周期起始日（1-28，默认 1）"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ResourceNotFoundError("User", user_id)
        return user.cycle_start_day if user.cycle_start_day is not None else 1
    except ResourceNotFoundError:
        raise
    except Exception as e:
        raise DatabaseError(f"Failed to get user cycle: {str(e)}")


def update_user_cycle(db: Session, user_id: int, cycle_start_day: int) -> User:
    """更新用户的月度账单周期起始日（1-28）"""
    try:
        if not (1 <= cycle_start_day <= 28):
            raise ValidationError("Invalid cycle_start_day", detail="起始日必须在 1 到 28 之间")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ResourceNotFoundError("User", user_id)
        user.cycle_start_day = cycle_start_day
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user
    except (ResourceNotFoundError, ValidationError):
        raise
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Failed to update user cycle: {str(e)}")
