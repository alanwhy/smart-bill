"""数据库初始化数据（默认分类）和遗留数据迁移"""

from typing import Sequence, Tuple

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from backend.database.models import Category
from backend.utils import logger

# (name, icon, color, sort_order)
DEFAULT_CATEGORIES: Sequence[Tuple[str, str, str, int]] = (
    ("餐饮", "🍽️", "#F97316", 0),
    ("交通", "🚗", "#3B82F6", 1),
    ("购物", "🛍️", "#EC4899", 2),
    ("娱乐", "🎬", "#A855F7", 3),
    ("医疗", "🏥", "#EF4444", 4),
    ("住房", "🏠", "#10B981", 5),
    ("其他", "📦", "#6B7280", 6),
)


def seed_default_categories(db: Session) -> None:
    """如果分类表为空，则插入默认分类。"""
    if db.query(Category).count() > 0:
        return

    for name, icon, color, sort_order in DEFAULT_CATEGORIES:
        db.add(Category(name=name, icon=icon, color=color, sort_order=sort_order))
    db.commit()
    logger.info(f"Seeded {len(DEFAULT_CATEGORIES)} default categories")


def backfill_legacy_bill_categories(engine: Engine, db: Session) -> None:
    """旧表 bill_records 仍有 category 字符串列时，迁移到 category_id 外键。

    SQLite 限制：无法直接 ALTER COLUMN，所以使用
    "新建表 -> INSERT SELECT -> DROP -> RENAME" 的标准做法。
    """
    if not engine.url.drivername.startswith("sqlite"):
        # 其他数据库目前无需自动迁移，保留位以便后续扩展
        return

    with engine.connect() as conn:
        rows = conn.execute(text("PRAGMA table_info(bill_records)")).fetchall()

    if not rows:
        # 全新数据库（create_all 之后表已经是新版结构），无需迁移
        return

    columns = {row[1] for row in rows}

    # 没有旧 category 列，且新 category_id 列已存在 -> 已是新结构
    if "category" not in columns:
        return

    logger.info("Detected legacy bill_records.category column, starting backfill")

    # 准备 fallback 分类（"其他"），若被改名则取 sort_order 最大者
    fallback = (
        db.query(Category).filter(Category.name == "其他").first()
        or db.query(Category).order_by(Category.sort_order.desc(), Category.id.desc()).first()
    )
    if fallback is None:
        raise RuntimeError("No category available as fallback during backfill")

    # 一次性把所有分类装载为 dict
    name_to_id = {c.name: c.id for c in db.query(Category).all()}

    has_new_column = "category_id" in columns
    fallback_count = 0

    if has_new_column:
        # 同时存在 category 和 category_id：仅回填 category_id 为空的行
        legacy_rows = db.execute(
            text("SELECT id, category FROM bill_records WHERE category_id IS NULL")
        ).fetchall()
        for bill_id, cat_name in legacy_rows:
            cid = name_to_id.get(cat_name)
            if cid is None:
                cid = fallback.id
                fallback_count += 1
            db.execute(
                text("UPDATE bill_records SET category_id = :cid WHERE id = :bid"),
                {"cid": cid, "bid": bill_id},
            )
        db.execute(text("ALTER TABLE bill_records DROP COLUMN category"))
        db.commit()
        logger.info(f"Backfill complete: {len(legacy_rows)} rows updated, {fallback_count} fallbacks")
        return

    # 旧版只有 category 字符串列，需要重建表
    db.execute(
        text(
            """
            CREATE TABLE bill_records_new (
                id INTEGER NOT NULL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                merchant_name VARCHAR(255) NOT NULL,
                value FLOAT NOT NULL,
                transaction_date VARCHAR(50) NOT NULL,
                category_id INTEGER NOT NULL,
                image_path TEXT,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE RESTRICT
            )
            """
        )
    )

    legacy_rows = db.execute(
        text(
            "SELECT id, user_id, merchant_name, value, transaction_date, category, image_path, created_at, updated_at "
            "FROM bill_records"
        )
    ).fetchall()

    for row in legacy_rows:
        cat_name = row[5]
        cid = name_to_id.get(cat_name)
        if cid is None:
            cid = fallback.id
            fallback_count += 1
        db.execute(
            text(
                "INSERT INTO bill_records_new (id, user_id, merchant_name, value, transaction_date, "
                "category_id, image_path, created_at, updated_at) "
                "VALUES (:id, :user_id, :merchant_name, :value, :transaction_date, "
                ":category_id, :image_path, :created_at, :updated_at)"
            ),
            {
                "id": row[0],
                "user_id": row[1],
                "merchant_name": row[2],
                "value": row[3],
                "transaction_date": row[4],
                "category_id": cid,
                "image_path": row[6],
                "created_at": row[7],
                "updated_at": row[8],
            },
        )

    db.execute(text("DROP TABLE bill_records"))
    db.execute(text("ALTER TABLE bill_records_new RENAME TO bill_records"))
    db.execute(text("CREATE INDEX IF NOT EXISTS ix_bill_records_id ON bill_records (id)"))
    db.execute(text("CREATE INDEX IF NOT EXISTS ix_bill_records_user_id ON bill_records (user_id)"))
    db.execute(text("CREATE INDEX IF NOT EXISTS ix_bill_records_category_id ON bill_records (category_id)"))
    db.execute(text("CREATE INDEX IF NOT EXISTS ix_bill_records_created_at ON bill_records (created_at)"))
    db.execute(text("CREATE INDEX IF NOT EXISTS idx_user_created ON bill_records (user_id, created_at)"))
    db.commit()
    logger.info(
        f"Migrated bill_records to category_id FK: {len(legacy_rows)} rows, {fallback_count} fallbacks"
    )
