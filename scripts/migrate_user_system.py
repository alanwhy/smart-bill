"""用户体系兼容迁移脚本

为已部署的旧版数据库补齐新增列，并将所有现存用户标记为首次登录需强制改密。
本脚本幂等可重入；不会清空任何已有数据。

使用方式（本地）：
    python -m scripts.migrate_user_system            # 实际执行
    python -m scripts.migrate_user_system --dry-run  # 仅打印将执行的 SQL

使用方式（部署后远程容器）：
    docker exec smart-bill-app python -m scripts.migrate_user_system

可通过 ``DATABASE_URL`` 环境变量指定数据库；默认与后端一致：
    sqlite:///./smart_bill.db
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# 允许 ``python scripts/migrate_user_system.py`` 在任意 cwd 下找到 backend 包
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./smart_bill.db")


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------


def _build_engine() -> Engine:
    if DATABASE_URL.startswith("sqlite://"):
        return create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    return create_engine(DATABASE_URL)


def _existing_columns(engine: Engine, table: str) -> list[str]:
    """读取表已有列名（兼容 SQLite / 其他）"""
    if engine.url.drivername.startswith("sqlite"):
        with engine.connect() as conn:
            rows = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
        return [row[1] for row in rows]
    # 通用回退（非 SQLite 场景目前不强制要求）
    from sqlalchemy import inspect

    insp = inspect(engine)
    return [col["name"] for col in insp.get_columns(table)]


# ---------------------------------------------------------------------------
# 迁移步骤
# ---------------------------------------------------------------------------


def run_migration(engine: Engine, dry_run: bool) -> int:
    from datetime import datetime

    # 延迟引入：dry-run 时也不需要实际哈希
    if not dry_run:
        from backend.services.auth_service import hash_password

    columns = _existing_columns(engine, "users")
    if not columns:
        print("[error] users 表不存在；请先运行后端服务以初始化数据库。", file=sys.stderr)
        return 1

    actions = []

    # 1. 补列
    if "role" not in columns:
        actions.append(("add_column", "ALTER TABLE users ADD COLUMN role VARCHAR(16) NOT NULL DEFAULT 'user'", {}))
    else:
        print("[skip] users.role 已存在")

    if "must_change_password" not in columns:
        actions.append(
            ("add_column", "ALTER TABLE users ADD COLUMN must_change_password INTEGER NOT NULL DEFAULT 0", {})
        )
    else:
        print("[skip] users.must_change_password 已存在")

    # 2. 修正 role 空值
    actions.append(("normalize_role", "UPDATE users SET role = 'user' WHERE role IS NULL OR role = ''", {}))

    # 3. 兜底创建 admin（不存在时插入）
    now_iso = datetime.utcnow().isoformat(sep=" ", timespec="seconds")
    if dry_run:
        admin_sql = (
            "INSERT INTO users(username, hashed_password, role, must_change_password, cycle_start_day, created_at, updated_at) "
            "VALUES ('admin', '<hashed-123456>', 'admin', 1, 1, '<utcnow>', '<utcnow>') "
            "WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'admin')"
        )
        actions.append(("ensure_admin", admin_sql, {}))
    else:
        actions.append(
            (
                "ensure_admin",
                "INSERT INTO users(username, hashed_password, role, must_change_password, cycle_start_day, created_at, updated_at) "
                "SELECT 'admin', :hashed, 'admin', 1, 1, :now, :now "
                "WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'admin')",
                {"hashed": hash_password("123456"), "now": now_iso},
            )
        )

    # 4. 仅在 must_change_password 列刚被新建时才批量标记（增量：列已存在说明已迁移过，不重置）
    if "must_change_password" not in columns:
        actions.append(
            (
                "force_change_password",
                "UPDATE users SET must_change_password = 1 WHERE role = 'user'",
                {},
            )
        )

    if dry_run:
        print("\n--- DRY RUN: 将要执行的 SQL ---")
        for label, sql, _ in actions:
            print(f"[{label}]\n  {sql}\n")
        print("--- 没有任何写入实际发生 ---")
        return 0

    print("\n--- 开始执行迁移 ---")
    with engine.begin() as conn:
        for label, sql, params in actions:
            try:
                result = conn.execute(text(sql), params) if params else conn.execute(text(sql))
                rowcount = getattr(result, "rowcount", -1)
                if label.startswith("add_column"):
                    print(f"[ok] {label}")
                else:
                    print(f"[ok] {label}: rowcount={rowcount}")
            except Exception as exc:  # noqa: BLE001
                # ALTER TABLE 重复执行可能抛错——在 add_column 上视为幂等忽略
                if label == "add_column":
                    print(f"[skip] {label}: {exc}")
                    continue
                raise

    print("--- 迁移完成 ---")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Smart Bill 用户体系兼容迁移脚本")
    parser.add_argument("--dry-run", action="store_true", help="仅打印将要执行的 SQL，不实际写入")
    args = parser.parse_args()

    print(f"DATABASE_URL = {DATABASE_URL}")
    engine = _build_engine()

    return run_migration(engine, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
