#!/usr/bin/env python3
"""
迁移脚本：为 categories 表添加 parent_id 字段，支持无限层级分类树。

安全性：
- 使用 ALTER TABLE ADD COLUMN，SQLite 原生支持（3.1.3+）
- 若字段已存在，脚本幂等退出，不会报错
- 存量数据 parent_id 全为 NULL（根分类），无需更新任何行

用法：
    python scripts/migrate_categories_tree.py
    python scripts/migrate_categories_tree.py --db /custom/path/to/smart_bill.db
"""

import argparse
import os
import sqlite3
import sys


def get_default_db_path() -> str:
    """根据项目根目录查找默认数据库路径"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    # 按优先级查找
    candidates = [
        os.path.join(project_root, "smart_bill.db"),
        os.path.join(project_root, "data", "smart_bill.db"),
        os.path.join(project_root, "backend", "smart_bill.db"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return candidates[0]  # 返回默认位置（即使不存在，让后续报错更清晰）


def migrate(db_path: str) -> None:
    if not os.path.exists(db_path):
        print(f"[ERROR] 数据库文件不存在：{db_path}", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] 连接数据库：{db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 检查字段是否已存在（幂等）
        cursor.execute("PRAGMA table_info(categories)")
        columns = [row[1] for row in cursor.fetchall()]
        if "parent_id" in columns:
            print("[INFO] parent_id 字段已存在，跳过迁移（幂等）")
            return

        # 添加 parent_id 字段（NULL = 根分类）
        print("[INFO] 执行：ALTER TABLE categories ADD COLUMN parent_id INTEGER REFERENCES categories(id) ON DELETE RESTRICT")
        cursor.execute(
            "ALTER TABLE categories ADD COLUMN parent_id INTEGER REFERENCES categories(id) ON DELETE RESTRICT"
        )

        # 创建索引
        print("[INFO] 执行：CREATE INDEX IF NOT EXISTS idx_category_parent ON categories(parent_id)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_category_parent ON categories(parent_id)"
        )

        conn.commit()

        # 验证
        cursor.execute("PRAGMA table_info(categories)")
        cols_after = [row[1] for row in cursor.fetchall()]
        assert "parent_id" in cols_after, "迁移后字段验证失败！"

        cursor.execute("SELECT COUNT(*) FROM categories WHERE parent_id IS NOT NULL")
        non_null = cursor.fetchone()[0]
        assert non_null == 0, f"存量数据 parent_id 应全为 NULL，但发现 {non_null} 条非 NULL 数据"

        print(f"[OK] 迁移成功！categories 表现在包含 parent_id 字段（存量数据全为 NULL）")

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] 迁移失败：{e}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="为 categories 表添加 parent_id 字段")
    parser.add_argument(
        "--db",
        default=None,
        help="数据库文件路径（默认自动查找项目根目录下的 smart_bill.db）",
    )
    args = parser.parse_args()

    db_path = args.db or get_default_db_path()
    migrate(db_path)
