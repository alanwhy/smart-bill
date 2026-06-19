# Smart Bill - Claude 开发指南

> 详细文档：[架构设计](docs/ARCHITECTURE.md) · [API](docs/API.md) · [更新日志](docs/CHANGELOG.md) · [环境配置](docs/SETUP.md)

## 项目概览

基于千问大模型智能账单识别服务，供 2 人（用户和媳妇）在本地 NAS 使用。

- **后端**: Python + FastAPI（http://localhost:8000）
- **前端**: Vue 3 + TypeScript + Vite + Tailwind CSS + Pinia（http://localhost:5173）
- **数据库**: SQLite（`bill_records` + `categories` + `users` 三张表）

## 快速启动

```bash
# 一键重启前后端（开发环境）
bash scripts/restart.sh

# 分步启动
make install && make dev          # 后端
cd frontend/web && npm run dev    # 前端（新终端）

# 生产部署（需提前 export 生产密钥）
export QWEN_API_KEY_PROD=your-prod-key
export SECRET_KEY_PROD=$(openssl rand -hex 32)
bash scripts/deploy.sh --init        # 首次初始化服务器
bash scripts/deploy.sh               # 后端日常更新部署
bash scripts/deploy_frontend.sh      # 前端独立部署（19284 端口）
```

**环境变量**（`.env`）：本地开发用，`cp .env.example .env` 后填入 `QWEN_API_KEY`、`SECRET_KEY` — 参考 `docs/SETUP.md`。部署时生产密钥通过 shell 环境变量 `QWEN_API_KEY_PROD` / `SECRET_KEY_PROD` 传入，不依赖本地 `.env`。

## 关键约定

- **金额符号**：`value` 负数=支出，正数=收入，禁止为 0
- **备注字段**：`description`（max 100 字），非 `notes`
- **分类存储**：`category_id` 外键，不存分类名字符串；响应含嵌套 `CategoryBrief`
- **错误处理**：使用 `backend/core/exceptions.py` 中的自定义异常，不抛裸 `Exception`
- **日志**：`from backend.utils import logger`
- **导入顺序**：标准库 → 第三方 → 本地

## API 端点速查

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/v1/auth/login` | 登录，返回 JWT token（含 role/must_change_password） |
| GET | `/api/v1/auth/me` | 获取当前用户 |
| POST | `/api/v1/auth/change-password` | 修改密码 |
| GET/PUT | `/api/v1/auth/cycle` | 月度账单周期起始日（1-28） |
| POST | `/api/v1/bills/upload` | 上传图片并发识别（multipart） |
| POST | `/api/v1/bills` | 手动创建账单（JSON） |
| POST | `/api/v1/bills/batch` | 批量导入账单（JSON 数组） |
| GET | `/api/v1/bills` | 查询列表（user_id, start_date, end_date, category_id, merchant_name） |
| PUT/DELETE | `/api/v1/bills/{id}` | 修改/删除账单 |
| GET/POST/PUT/DELETE | `/api/v1/categories[/{id}]` | 分类 CRUD（含 parent_id 支持层级结构） |
| GET | `/api/v1/categories/tree` | 树形分类列表（根节点 + 嵌套 children） |
| GET | `/api/v1/users` | 用户列表（仅 admin） |
| POST | `/api/v1/users` | 创建用户（仅 admin） |
| PUT | `/api/v1/users/{id}/username` | 修改用户名（仅 admin，不能改自己） |
| POST | `/api/v1/users/{id}/reset-password` | 重置用户密码（仅 admin） |

> 完整请求/响应示例见 `docs/API.md`，或访问 http://localhost:8000/docs

## 关键文件

```
backend/services/prompts.py      # LLM system prompt（集中维护，勿内联）
backend/services/qwen_vision.py  # Qwen API 调用
backend/database/crud.py         # 所有数据库操作
backend/api/users.py             # 用户管理 API（仅 admin）
frontend/web/src/utils/cycle.ts  # 月度周期日期计算（getCycleDates）
frontend/web/src/utils/excel.ts  # Excel 导入/导出工具
frontend/web/src/utils/useDevice.ts  # 设备检测工具
frontend/web/src/stores/         # auth / bills / categories / ui
frontend/web/src/components/categories/CategoryDrillDown.vue  # 钒取式分类选择器
frontend/web/src/components/categories/CategoryNodeRow.vue    # 树形节点行组件
frontend/web/src/pages/UsersAdminPage.vue        # 用户管理页
frontend/web/src/pages/ForceChangePasswordPage.vue  # 强制改密页
scripts/migrate_user_system.py   # 存量用户数据迁移脚本
scripts/migrate_categories_tree.py  # 分类树存量数据迁移脚本（添加 parent_id 列）
```

## 待完成（下一阶段）

- [ ] 认证中间件强制校验所有账单端点（当前 user_id 由前端传入）
- [ ] 账单统计分析与趋势图表
- [ ] 定时备份脚本

## 已知限制

- `user_id` 未经后端强制校验（安全隐患）
- 无用户注册（仅预设账户 + admin 创建）
- SQLite 不适合高并发（小规模无影响）

## 提交规范

`feat|fix|docs|refactor|test|chore: <subject>`

---

**最后更新**: 2026-06-19 · **GitHub**: https://github.com/alanwhy/smart-bill
