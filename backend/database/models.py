"""SQLAlchemy 数据库模型"""

from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    """用户表"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment="用户 ID")
    username = Column(String(50), nullable=False, unique=True, index=True, comment="用户名")
    hashed_password = Column(String(255), nullable=False, comment="哈希密码")
    cycle_start_day = Column(Integer, nullable=False, default=1, comment="月度账单周期起始日（1-28）")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"


class Category(Base):
    """账单分类表（全局共享，两位用户共用）"""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, comment="分类 ID")
    name = Column(String(50), nullable=False, unique=True, index=True, comment="分类名称")
    icon = Column(String(16), nullable=False, default="", comment="emoji 图标")
    color = Column(String(7), nullable=False, default="#6B7280", comment="十六进制颜色 #RRGGBB")
    sort_order = Column(Integer, nullable=False, default=0, index=True, comment="排序权重，数值小的在前")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")

    __table_args__ = (Index("idx_category_sort", "sort_order", "id"),)

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"


class BillRecord(Base):
    """账单记录表"""

    __tablename__ = "bill_records"

    id = Column(Integer, primary_key=True, index=True, comment="账单 ID")
    user_id = Column(Integer, nullable=False, index=True, comment="用户 ID")
    merchant_name = Column(String(255), nullable=False, comment="商户名称")
    value = Column(Float, nullable=False, comment="消费金额")
    transaction_date = Column(String(50), nullable=False, comment="交易日期时间")
    category_id = Column(
        Integer,
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="分类 ID（外键）",
    )
    image_path = Column(Text, nullable=True, comment="原始图片路径")
    description = Column(String(100), nullable=True, default="", comment="账单备注")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")

    # lazy="joined" 让 BillRecordInDB.model_validate(bill) 可直接序列化嵌套 category；
    # 改为 "select" 时调用方需在 session 关闭前完成序列化或显式 joinedload。
    category = relationship("Category", lazy="joined")

    # 创建复合索引以支持按用户和时间范围查询
    __table_args__ = (Index("idx_user_created", "user_id", "created_at"),)

    def __repr__(self):
        return f"<BillRecord(id={self.id}, user_id={self.user_id}, merchant_name={self.merchant_name}, value={self.value})>"
