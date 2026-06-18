# Smart Bill - Claude 开发指南

> 详细文档：[架构设计](docs/ARCHITECTURE.md) · [API](docs/API.md) · [更新日志](docs/CHANGELOG.md) · [环境配置](docs/SETUP.md)

## 项目概览

Qwen3-VL-Plus 智能账单识别服务，供 2 人（用户和媳妇）在本地 NAS 使用。

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

# 生产部署
cp .env.production .env && vi .env   # 填入真实密钥
bash scripts/deploy.sh --init        # 首次初始化服务器
bash scripts/deploy.sh               # 日常更新部署
```

**环境变量**（`.env`）：`QWEN_API_KEY`、`SECRET_KEY`、`DATABASE_URL`、`CORS_ORIGINS` — 参考 `docs/SETUP.md`

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
| POST | `/api/v1/auth/login` | 登录，返回 JWT token |
| GET | `/api/v1/auth/me` | 获取当前用户 |
| POST | `/api/v1/auth/change-password` | 修改密码 |
| GET/PUT | `/api/v1/auth/cycle` | 月度账单周期起始日（1-28） |
| POST | `/api/v1/bills/upload` | 上传图片并发识别（multipart） |
| POST | `/api/v1/bills` | 手动创建账单（JSON） |
| GET | `/api/v1/bills` | 查询列表（user_id, start_date, end_date, category_id, merchant_name） |
| PUT/DELETE | `/api/v1/bills/{id}` | 修改/删除账单 |
| GET/POST/PUT/DELETE | `/api/v1/categories[/{id}]` | 分类 CRUD |

> 完整请求/响应示例见 `docs/API.md`，或访问 http://localhost:8000/docs

## 关键文件

```
backend/services/prompts.py      # LLM system prompt（集中维护，勿内联）
backend/services/qwen_vision.py  # Qwen API 调用
backend/database/crud.py         # 所有数据库操作
frontend/web/src/utils/cycle.ts  # 月度周期日期计算（getCycleDates）
frontend/web/src/stores/         # auth / bills / categories / ui
```

## 待完成（下一阶段）

- [ ] 认证中间件强制校验所有账单端点（当前 user_id 由前端传入）
- [ ] 账单统计分析与趋势图表
- [ ] 报表导出（PDF/Excel）
- [ ] 定时备份脚本

## 已知限制

- `user_id` 未经后端强制校验（安全隐患）
- 无用户注册（仅预设账户）
- SQLite 不适合高并发（小规模无影响）

## 提交规范

`feat|fix|docs|refactor|test|chore: <subject>`

---

**最后更新**: 2026-06-18 · **GitHub**: https://github.com/alanwhy/smart-bill
