"""SQLAlchemy 数据库模型"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Index, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class BillRecord(Base):
    """账单记录表"""

    __tablename__ = "bill_records"

    id = Column(Integer, primary_key=True, index=True, comment="账单 ID")
    user_id = Column(Integer, nullable=False, index=True, comment="用户 ID")
    merchant_name = Column(String(255), nullable=False, comment="商户名称")
    value = Column(Float, nullable=False, comment="消费金额")
    transaction_date = Column(String(50), nullable=False, comment="交易日期时间")
    category = Column(String(50), nullable=False, index=True, comment="分类")
    image_path = Column(Text, nullable=True, comment="原始图片路径")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False, comment="更新时间")

    # 创建复合索引以支持按用户和时间范围查询
    __table_args__ = (Index("idx_user_created", "user_id", "created_at"),)

    def __repr__(self):
        return f"<BillRecord(id={self.id}, user_id={self.user_id}, merchant_name={self.merchant_name}, value={self.value})>"
