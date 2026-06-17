"""数据库连接和会话管理"""

import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
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


# SQLite 默认不强制外键约束，需要每个连接显式开启 PRAGMA。
# 如果不开启，ON DELETE RESTRICT 形同虚设，category_id 可能指向不存在的分类。
if DATABASE_URL.startswith("sqlite://"):

    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


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
    """初始化数据库：建表 -> 种子默认分类 -> 迁移历史数据"""
    try:
        from backend.database.models import Base
        from backend.database.seed import (
            backfill_legacy_bill_categories,
            seed_default_categories,
        )

        Base.metadata.create_all(bind=engine)

        db = SessionLocal()
        try:
            seed_default_categories(db)
            backfill_legacy_bill_categories(engine, db)
        finally:
            db.close()

        print("✓ 数据库初始化成功")
    except Exception as e:
        raise DatabaseError(f"Database initialization failed: {str(e)}")
