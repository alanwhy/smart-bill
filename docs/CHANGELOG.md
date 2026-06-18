# 更新日志

## [0.4.0] - 2026-06-18

### 已实现

- [x] Phase 17：生产环境部署
  - **一键部署脚本** `scripts/deploy.sh`：支持 `--init`（首次初始化服务器）和日常更新部署两种模式
  - **生产环境变量模板** `.env.production`：含 `QWEN_API_KEY`、`SECRET_KEY`、`CORS_ORIGINS` 等配置项
  - **前端远程环境配置** `frontend/web/.env.remote`：生产环境 API 地址设置
  - **Docker Compose 优化**：端口改为 19283:8000，持久化数据卷（`smart-bill-data`），healthcheck 配置
  - **Dockerfile 优化**：构建流程精简
  - `frontend/web/package.json` 新增 `build:remote` 脚本，`vite.config.ts` 支持多环境代理

- [x] Phase 18：UI 精细化优化
  - **模态框动效**：BillUploadModal、BillEditModal、ConfirmDialog 添加淡入/滑入过渡动画
  - **全局样式扩展** `main.css`：大量 Tailwind 自定义组件类（`.modal-overlay`、`.card-hover`、`.btn-*` 等）
  - **DashboardPage**、**LoginPage** 细节样式调整

- [x] 数据模型简化
  - 移除 `BillRecord.image_path` 字段（数据库、`crud.py`、`bill_processor.py`、Pydantic 模型及前端 `bill.ts` 全链路清理）
  - 账单不再存储图片路径，简化数据结构

_last commit: `528065773467cf436c258a9134c1de787aaeaa70`_

---

## [0.3.0] - 2026-06-18

### 已实现

- [x] Phase 15：账单高级功能
  - **收支类型区分**：`value` 字段约定负数=支出、正数=收入，前端 BillCard/BillEditModal 同步展示
  - **手动创建账单**：`POST /api/v1/bills`，无需上传图片即可创建账单（`CreateBillRequest`）
  - **并发图片上传**：多张图片并发调用 Qwen API（`asyncio.gather` + `run_in_executor`），每张图片独立线程和独立 DB session
  - **上传占位符**：前端上传中实时显示骨架占位卡，提升用户体验

- [x] Phase 16（部分）：用户个性化设置
  - **月度账单周期设置**：用户可自定义周期起始日（1-28），如每月 15 日到次月 14 日为一个周期
  - `GET /api/v1/auth/cycle` - 获取当前用户周期起始日
  - `PUT /api/v1/auth/cycle` - 更新周期起始日（1-28）
  - `frontend/web/src/utils/cycle.ts` - 周期日期计算工具库（`getCycleDates`）
  - `SettingsPage.vue` 新增周期起始日设置 UI
  - `DashboardPage.vue` 支持按自定义周期筛选账单（本周期 / 上周期）

- [x] 账单识别提示词工程（prompts.py）
  - 将 system prompt 从 `qwen_vision.py` 中提取，集中到 `backend/services/prompts.py` 独立管理
  - `build_bill_recognition_system_prompt(categories)` - 动态注入当前分类列表
  - Qwen API 配置项（model、max_tokens 等）统一到 `backend/config.py`

- [x] 数据模型升级
  - `BillRecord.description` 替代原 `notes`（数据库字段重命名，max_length=100）
  - `BillRecord.category_id` 外键关联 `categories` 表（原来存 `category` 字符串）
  - `BillRecordInDB` 新增嵌套 `CategoryBrief` 返回分类详情（id、name、icon、color）
  - `User` 表新增 `cycle_start_day` 字段（默认 1）
  - API 查询账单支持 `merchant_name` 模糊搜索过滤

---

## [0.2.0] - 2026-06-17

### 已实现

- [x] Phase 12：用户认证与授权
  - JWT token 登录认证（python-jose + passlib/bcrypt）
  - `POST /api/v1/auth/login` - 用户登录，返回 JWT token
  - `GET /api/v1/auth/me` - 获取当前登录用户信息（Bearer token）
  - `POST /api/v1/auth/change-password` - 修改密码
  - Auth service（`backend/services/auth_service.py`）
  - 前端登录页面（`LoginPage.vue`）和认证状态管理（Pinia auth store）
  - 受保护路由（需登录后访问）

- [x] Phase 13：分类管理服务
  - Category 数据库表（`backend/database/models.py`）
  - `POST /api/v1/categories` - 创建自定义分类
  - `GET /api/v1/categories` - 列出所有分类
  - `GET /api/v1/categories/{id}` - 查询单个分类
  - `PUT /api/v1/categories/{id}` - 更新分类
  - `DELETE /api/v1/categories/{id}` - 删除分类（含安全检查）
  - 分类种子数据（`backend/database/seed.py`）
  - 前端分类管理页面（`CategoriesPage.vue`）和 Pinia categories store

- [x] Phase 14：Vue 3 前端应用
  - Vue 3 + TypeScript + Vite + Tailwind CSS + Pinia 完整技术栈
  - 响应式设计：PC 侧边栏导航、移动端底部导航
  - 账单上传界面（`BillUploadModal.vue`）
  - 账单列表与筛选（`DashboardPage.vue`、`BillFilters.vue`）
  - 账单编辑/删除（`BillEditModal.vue`、`BillCard.vue`）
  - 分类管理界面（`CategoriesPage.vue`）
  - 用户设置页面（`SettingsPage.vue`、`UserPage.vue`）
  - Vite 代理配置（前端 http://localhost:5173 → 后端 http://localhost:8000）

- [x] Phase 15（部分）：前端增强与账单备注
  - Toast 通知组件（`components/common/Toast.vue`）- error/success/info 三种类型，自动消失
  - ConfirmDialog 确认对话框组件
  - 账单备注（notes）字段 - 数据库、API、前端全链路支持
  - 删除操作错误提示中文化（"分类「x」下还有账单，请先修改..."）

- [x] 其他改进
  - `scripts/restart.sh` - 一键重启前后端开发服务器脚本
  - 优化 Qwen API 响应日志记录，方便调试
  - 前端 README（`frontend/web/README.md`）- 技术栈、设计系统、开发规范

### 已知问题
- 无

---

## [0.1.0] - 2026-06-16

### 已实现
- [x] Phase 1：项目环境初始化
  - Git 仓库初始化
  - 使用 uv 的依赖管理配置 (pyproject.toml)
  - 环境变量模板 (.env.example)
  - Makefile 便捷命令
  - 文档框架初始化

- [x] Phase 2：数据模型和核心类型
  - Pydantic 数据模型 (BillItem, BillResponse 等)
  - 账单分类枚举 (餐饮、交通、购物等)
  - 自定义异常类

- [x] Phase 3：数据库层实现
  - SQLAlchemy ORM 模型 (BillRecord)
  - CRUD 操作（创建、查询、更新、删除）
  - SQLite 数据库连接和会话管理

- [x] Phase 4：Qwen3-VL-Plus 集成
  - 阿里云 DashScope API 调用
  - 图片验证和 base64 编码
  - 精细化系统提示词设计
  - 支持 JPG/PNG 格式

- [x] Phase 5：账单数据解析
  - JSON 格式解析（优先）
  - 文本格式解析（备选）
  - 日期格式规范化
  - 分类名称自动映射

- [x] Phase 6：业务流程编排
  - 端到端流程协调
  - 图片验证 → Qwen 调用 → 数据解析 → 数据库保存

- [x] Phase 7：API 路由实现
  - POST /api/v1/bills/upload - 上传并识别账单
  - GET /api/v1/bills - 查询账单列表
  - PUT /api/v1/bills/{id} - 修改账单
  - DELETE /api/v1/bills/{id} - 删除账单
  - 健康检查端点

- [x] Phase 8-11：工具函数、配置、测试、Docker
  - 数据验证工具 (validators.py)
  - 数据转换工具 (converters.py)
  - 日志管理 (logger.py)
  - FastAPI 应用配置 (main.py, config.py)
  - Docker 和 Docker Compose 配置

### 进行中
- [ ] 单元测试编写
- [ ] 集成测试编写

### 待实现
- [ ] 账单统计分析与报表导出
- [ ] Docker NAS 部署优化
- [ ] 消费趋势分析

### 已知问题
- 无

### 优化建议
- 暂无
