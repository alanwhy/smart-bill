"""数据库连接和会话管理"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from backend.core.exceptions import DatabaseError

# 获取数据库 URL，默认为 SQLite
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./smart_bill.db")

# SQLite 特殊配置
engine_kwargs = {}
if DATABASE_URL.startswith("sqlite://"):
    engine_kwargs = {
        "connect_args": {"check_same_thread": False},
        "poolclass": StaticPool,
    }

try:
    engine = create_engine(DATABASE_URL, **engine_kwargs)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    raise DatabaseError(f"Failed to create database engine: {str(e)}")


def get_db() -> Session:
    """获取数据库会话，用于依赖注入"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise DatabaseError(f"Database session error: {str(e)}")
    finally:
        db.close()


def init_db():
    """初始化数据库，创建所有表"""
    try:
        # 导入所有模型，确保 SQLAlchemy 能识别它们
        from backend.database.models import Base

        Base.metadata.create_all(bind=engine)
        print("✓ 数据库初始化成功")
    except Exception as e:
        raise DatabaseError(f"Database initialization failed: {str(e)}")
