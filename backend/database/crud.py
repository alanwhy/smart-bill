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
    parent_id: Optional[int] = None,
) -> Category:
    """创建分类"""
    try:
        existing = db.query(Category).filter(Category.name == name).first()
        if existing:
            raise ValidationError(
                "Category name already exists",
                detail=f"Category with name '{name}' already exists",
            )

        if parent_id is not None:
            parent = db.query(Category).filter(Category.id == parent_id).first()
            if not parent:
                raise ValidationError(
                    "Parent category not found",
                    detail=f"父分类 ID {parent_id} 不存在",
                )

        if sort_order is None:
            current_max = db.query(func.max(Category.sort_order)).scalar()
            sort_order = (current_max + 1) if current_max is not None else 0

        category = Category(name=name, icon=icon, color=color, sort_order=sort_order, parent_id=parent_id)
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


def list_categories_tree(db: Session) -> List[Category]:
    """返回树形分类列表（仅根节点，子节点通迁 children 嵌套）"""
    try:
        return (
            db.query(Category)
            .filter(Category.parent_id.is_(None))
            .order_by(Category.sort_order.asc(), Category.id.asc())
            .all()
        )
    except Exception as e:
        raise DatabaseError(f"Failed to list categories tree: {str(e)}")


def get_descendant_ids(db: Session, category_id: int) -> List[int]:
    """返回该分类及所有后代分类的 id 列表（递归遍历）"""
    result: List[int] = [category_id]
    queue = [category_id]
    while queue:
        current_ids = queue
        children = db.query(Category.id).filter(Category.parent_id.in_(current_ids)).all()
        child_ids = [c.id for c in children]
        result.extend(child_ids)
        queue = child_ids
    return result


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
    parent_id: Optional[int] = None,
    clear_parent: bool = False,
) -> Category:
    """更新分类，clear_parent=True 时将分类提升为根节点"""
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
        if clear_parent:
            category.parent_id = None
        elif parent_id is not None:
            if parent_id == category_id:
                raise ValidationError(
                    "Cannot set category as its own parent",
                    detail="分类不能将自身设为父分类",
                )
            # 防循环引用：新父节点不能是当前节点的后代
            descendant_ids = get_descendant_ids(db, category_id)
            if parent_id in descendant_ids:
                raise ValidationError(
                    "Circular reference detected",
                    detail="不能将分类的后代设为其父分类（循环引用）",
                )
            parent = db.query(Category).filter(Category.id == parent_id).first()
            if not parent:
                raise ValidationError(
                    "Parent category not found",
                    detail=f"父分类 ID {parent_id} 不存在",
                )
            category.parent_id = parent_id

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
    """删除分类（仍被账单引用、最后一个或有子分类时拒绝）"""
    try:
        category = get_category(db, category_id)

        child_count = db.query(Category).filter(Category.parent_id == category_id).count()
        if child_count > 0:
            raise ValidationError(
                "Cannot delete category with subcategories",
                detail=f"分类「{category.name}」下还有子分类，请先删除或迁移子分类",
            )

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
    category_ids: Optional[List[int]] = None,
    merchant_name: Optional[str] = None,
) -> List[BillRecord]:
    """查询账单列表"""
    try:
        query = db.query(BillRecord).filter(BillRecord.user_id == user_id)

        if start_date:
            query = query.filter(BillRecord.transaction_date >= start_date)

        if end_date:
            query = query.filter(BillRecord.transaction_date <= end_date + "T23:59:59")

        if category_ids:
            # 按分类筛选时，自动展开每个分类的所有后代
            all_ids: List[int] = []
            for cid in category_ids:
                all_ids.extend(get_descendant_ids(db, cid))
            query = query.filter(BillRecord.category_id.in_(all_ids))

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


def batch_create_bills(
    db: Session,
    user_id: int,
    items: list,
) -> int:
    """批量创建账单，在单事务内完成，任一失败则全部回滚，返回创建数量"""
    try:
        records = []
        for item in items:
            # 校验分类存在
            get_category(db, item.category_id)
            bill = BillRecord(
                user_id=user_id,
                merchant_name=item.merchant_name,
                value=item.value,
                transaction_date=item.transaction_date,
                category_id=item.category_id,
                description=item.description,
            )
            records.append(bill)

        db.add_all(records)
        db.commit()
        return len(records)
    except (ResourceNotFoundError, DatabaseError):
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Failed to batch create bills: {str(e)}")


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


def create_user(
    db: Session,
    username: str,
    hashed_password: str,
    role: str = "user",
    must_change_password: bool = True,
) -> User:
    """创建用户。默认新用户首次登录需强制修改密码。"""
    try:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            raise ValidationError(
                "Username already exists",
                detail=f"用户名「{username}」已存在",
            )
        if role not in ("admin", "user"):
            raise ValidationError("Invalid role", detail="role 必须为 admin 或 user")

        user = User(
            username=username,
            hashed_password=hashed_password,
            role=role,
            must_change_password=must_change_password,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except ValidationError:
        raise
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Failed to create user: {str(e)}")


def list_users(db: Session) -> List[User]:
    """列出所有用户（按 id 升序）"""
    try:
        return db.query(User).order_by(User.id.asc()).all()
    except Exception as e:
        raise DatabaseError(f"Failed to list users: {str(e)}")


def update_username(db: Session, user_id: int, new_username: str) -> User:
    """修改用户名（用户名唯一）"""
    try:
        new_username = (new_username or "").strip()
        if not new_username:
            raise ValidationError("Invalid username", detail="用户名不能为空")
        if len(new_username) > 50:
            raise ValidationError("Invalid username", detail="用户名长度不能超过 50 字符")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ResourceNotFoundError("User", user_id)

        if new_username == user.username:
            return user

        duplicate = (
            db.query(User)
            .filter(User.username == new_username, User.id != user_id)
            .first()
        )
        if duplicate:
            raise ValidationError(
                "Username already exists",
                detail=f"用户名「{new_username}」已存在",
            )

        user.username = new_username
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user
    except (ResourceNotFoundError, ValidationError):
        raise
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Failed to update username: {str(e)}")


def update_password(db: Session, user_id: int, new_hashed_password: str) -> User:
    """更新用户密码；任何成功改密都会清除 must_change_password 旗标。"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ResourceNotFoundError("User", user_id)
        user.hashed_password = new_hashed_password
        user.must_change_password = False
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user
    except ResourceNotFoundError:
        raise
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Failed to update password: {str(e)}")


def reset_user_password(db: Session, user_id: int, new_hashed_password: str) -> User:
    """管理员重置用户密码：写入新哈希并标记为需强制修改。"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ResourceNotFoundError("User", user_id)
        user.hashed_password = new_hashed_password
        user.must_change_password = True
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user
    except ResourceNotFoundError:
        raise
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Failed to reset user password: {str(e)}")


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
