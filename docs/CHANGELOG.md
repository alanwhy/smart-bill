# Changelog

所有前端版本变更记录。格式遵循 [Conventional Commits](https://conventionalcommits.org/)。

## [0.7.0] - 2026-06-19

### 已实现

- [x] Phase 24：分类层级结构（树形分类）
  - **数据库层**：`categories` 表新增 `parent_id` 自引用外键（`ON DELETE RESTRICT`，防止有子分类的分类被删除），支持无限层级嵌套
  - **`GET /api/v1/categories/tree`**：新增树形端点，仅返回根节点，子节点递归嵌套在 `children` 数组中；`CategoryTree` Pydantic 模型支持递归自引用
  - **`GET /api/v1/categories`**：平铺列表已增加 `parent_id` 字段
  - **创建/更新分类**：校验父分类是否存在、防止循环引用；`UpdateCategoryRequest` 支持明确传 `null` 将分类提升为根节点
  - **删除分类**：有子分类时返回 400，禁止删除
  - **账单列表过滤**：`category_id` 过滤时自动展开后代分类，查询某个父分类时同时返回所有子分类账单
  - **`scripts/migrate_categories_tree.py`**：为存量数据库添加 `parent_id` 列的迁移脚本
  - **前端 `CategoryTree` 类型**：`bill.ts` 新增 `CategoryTree` 接口（含 `children: CategoryTree[]`）
  - **`categoryApi.listTree()`**：`api/categories.ts` 新增调用树形端点的方法
  - **`categories` store 扩展**：`rootCategories`（根节点列表）、`childrenOf(id)`（子节点）、`buildTree()`、`byId(id)` 计算属性
  - **`CategoryDrillDown.vue`**：新增钻取式分类选择组件（逐级展开，支持选中任意层级），用于账单编辑和筛选
  - **`CategoryNodeRow.vue`**：新增树形节点行组件，递归渲染分类树，支持展开/折叠
  - **`CategoriesPage.vue`** 重设计：树形视图展示，支持展开/折叠节点，新增/编辑时可选择父分类
  - **`BillEditModal.vue`** / **`BillFilters.vue`**：分类选择器替换为 `CategoryDrillDown` 钻取组件
  - **`BillCard.vue`**：展示完整分类路径（如 `餐饮 / 午餐`）
  - **`SettingsPage.vue`**：同步更新分类相关展示逻辑
  - 前端自定义数字输入框滚轮样式（隐藏默认 spinner，CSS 自定义）
  - 全局滚动条样式优化（`main.css`）

_last commit: `17b7ba8263de7c533b135f56414a1f295b0ee1b8`_

---

## [0.6.0](https://github.com/alanwhy/smart-bill/compare/v0.5.0...v0.6.0) (2026-06-19)


### ✨ 新功能

* 优化配置管理，支持 CORS 和图片扩展名的字符串解析；更新 Docker Compose 配置以简化环境变量设置 ([e33bb47](https://github.com/alanwhy/smart-bill/commit/e33bb4722305fed9dd9d5fb5026bcb3ef8ba8e4f))
* 更新应用名称为“爱理财”，优化页面标题和描述；调整样式和动画效果 ([5138825](https://github.com/alanwhy/smart-bill/commit/5138825095eaa079b4617bc51de86c5b9ea60540))
* 添加用户角色与权限系统，支持用户管理和强制改密功能；实现批量导入账单功能，优化移动端体验 ([e85c844](https://github.com/alanwhy/smart-bill/commit/e85c844232a349abe17949b18c7885bc4f245d59))


### 🐛 Bug 修复

* 优化 401 错误处理逻辑，仅在已登录状态下清除 token 并跳转登录页 ([58f82c9](https://github.com/alanwhy/smart-bill/commit/58f82c9e05abd84ef391e3c0522106224e006860))

## [0.6.0] - 2026-06-19

### 已实现

- [x] Phase 21：用户角色与权限系统
  - **`role` 字段**：`users` 表新增 `role`（`admin` / `user`，默认 `user`）和 `must_change_password`（布尔，默认 `false`）列
  - **`ForceChangePasswordPage.vue`**：首次登录（或被管理员重置密码后）强制改密页面，改密成功后自动跳转
  - **`UsersAdminPage.vue`**：管理员专属用户管理页，支持新增用户、修改用户名（不能改自己）、重置密码（生成临时密码）
  - **后端 `backend/api/users.py`**：`GET /api/v1/users`、`POST /api/v1/users`、`PUT /api/v1/users/{id}/username`、`POST /api/v1/users/{id}/reset-password`，均需 `admin` 角色
  - **`require_admin` 依赖**：`auth.py` 新增，自动校验当前用户 role
  - **`auth_service.generate_temp_password()`**：生成临时密码工具函数
  - **路由守卫扩展**：`router/index.ts` 新增 `/users/admin`（需 admin）和 `/force-change-password` 路由，登录后自动检测 `must_change_password`
  - **`scripts/migrate_user_system.py`**：存量用户数据迁移脚本（添加 role/must_change_password 列，设置种子 admin 账号）
  - `seed.py` 新增预设 admin 用户（首次启动强制改密）

- [x] Phase 22：批量导入账单（Excel）
  - **`frontend/web/src/utils/excel.ts`**：完整 Excel 工具库，含 `downloadTemplate()`（带示例数据和字段说明的模板下载）、`exportBillsToExcel()`（账单导出）、`parseBillsFromExcel()`（Excel 解析与字段校验）
  - **`POST /api/v1/bills/batch`**：批量创建账单端点（`BatchCreateBillRequest`，接受账单数组，事务性写入）
  - **`UserPage.vue`** 数据管理区域：导出全部账单为 Excel、上传 Excel 导入、模板下载，新增专属样式布局
  - `frontend/web/package.json` 新增 `xlsx` 依赖
  - Excel 列定义：金额 | 商家名称 | 交易日期 | 分类名称 | 备注
  - 导入时匹配分类名称（须与系统分类完全一致），校验金额非零、商户名不空、日期格式 `YYYY-MM-DD`

- [x] Phase 23：移动端体验优化
  - **左滑操作按钮**：`BillCard.vue` 支持移动端左滑显示编辑/删除按钮，touch 事件精准计算滑动距离
  - **窄屏提示 Banner**：`DashboardPage.vue` 屏幕宽度 < 375px 时展示引导提示
  - **`useDevice.ts`**：设备检测工具（`isMobile`、`isNarrow`、视口宽度响应式），供组件按需调用
  - 下滑关闭模态框：移动端模态框支持 touch 拖动和下滑手势关闭
  - 视口优化：`index.html` 禁止用户缩放，`main.css` 优化主内容区滚动

_last commit: `9c90330b97f8e8104d5acefae15ea9cd0c408293`_

---

## [0.5.0] - 2026-06-19


### ✨ 新功能

* add category management feature ([7cc2e0d](https://github.com/alanwhy/smart-bill/commit/7cc2e0d45b701e42cdf8b4afd383745be8208ad6))
* add user role and password change requirements ([9353812](https://github.com/alanwhy/smart-bill/commit/9353812bca254ed0632f4bed435b10e2e34040bd))
* 优化模态框和过渡效果，提升用户体验 ([5cf0859](https://github.com/alanwhy/smart-bill/commit/5cf08592a46ef691193358978eb1b09b1ec2d8f8))
* 优化用户页面数据管理区域的样式和布局，提升导入导出功能的用户体验 ([0b04cc2](https://github.com/alanwhy/smart-bill/commit/0b04cc2c0a9d4b57eeb93c7050ba30b97df5041e))
* 优化视口设置和主内容区域样式，增强移动端适配性 ([7337e1e](https://github.com/alanwhy/smart-bill/commit/7337e1ebe0ea6a0b35633ff15ef4139f3e651b63))
* 优化移动端和桌面端的用户体验，添加左滑操作按钮和窄屏提示 Banner ([112c394](https://github.com/alanwhy/smart-bill/commit/112c3944dd34c369d95507d95059e85988025b1b))
* 优化移动端模态框样式和交互，支持下滑关闭和拖动关闭功能 ([4925fd8](https://github.com/alanwhy/smart-bill/commit/4925fd84605c20a8f1caa4e51e6130654efc968b))
* 初始化 Vue 3 前端项目 - Smart Bill Web 应用 ([9a07793](https://github.com/alanwhy/smart-bill/commit/9a07793ea427562f947f4f40fe89d7d6f305e779))
* 实现 Smart Bill 核心后端服务 ([fa51093](https://github.com/alanwhy/smart-bill/commit/fa51093b8f54c8f31e3bd16f13ed5437ecfc9583))
* 实现账单上传并发处理，添加占位符功能以优化用户体验 ([74faaf8](https://github.com/alanwhy/smart-bill/commit/74faaf89027d9684c23ee757f04c1bf9b0297383))
* 将标题链接化，增强用户导航体验 ([a02dfef](https://github.com/alanwhy/smart-bill/commit/a02dfefff230a916fdc331d93e8bde6cf116cb09))
* 更新文档，添加前端 README 和架构设计说明，优化部署脚本和环境变量配置 ([f48562c](https://github.com/alanwhy/smart-bill/commit/f48562ca8c295c81f7cf6e6fdb2787ec3ab3570c))
* 更新文档，添加手动创建账单和月度账单周期设置功能说明 ([ae162c6](https://github.com/alanwhy/smart-bill/commit/ae162c6ee47b0832f61f828dda3be9009b44bbb3))
* 更新文档，添加生产环境部署说明，简化数据模型，移除账单记录中的图片路径字段 ([5890c3b](https://github.com/alanwhy/smart-bill/commit/5890c3befe359aff17dcb49747a5c496657df8e2))
* 更新文档，添加用户认证和分类管理API说明，优化架构设计描述 ([2c54bee](https://github.com/alanwhy/smart-bill/commit/2c54beee8bf6bad9ceea7205dbb258b6a3e572e8))
* 更新文档，统一使用“千问模型”描述，优化相关文件中的模型名称 ([d273ffa](https://github.com/alanwhy/smart-bill/commit/d273ffacbe2a51f7786f8d7b838aa3527fdd52bc))
* 更新环境变量配置，移除 .env.production，优化生产部署流程 ([908158a](https://github.com/alanwhy/smart-bill/commit/908158a9e9dc94d82c4feaa3631f7235ffb58034))
* 更新账单模型和解析逻辑，支持收支类型区分，优化用户体验 ([54f77bd](https://github.com/alanwhy/smart-bill/commit/54f77bda258eaf2d2519d910f1aaf8bde822787c))
* 添加 Docker 配置和完成文档 ([a24c5ff](https://github.com/alanwhy/smart-bill/commit/a24c5ff3e2cc80cee4527b2f9aedaef577676f1f))
* 添加 Qwen API 配置和提示词管理，优化账单识别功能 ([8efae57](https://github.com/alanwhy/smart-bill/commit/8efae571ba10bdc2d3c429b4067dd091bcc1edff))
* 添加 Toast 组件以显示错误提示，优化用户体验 ([76f2ffe](https://github.com/alanwhy/smart-bill/commit/76f2ffe345f991cdebe5e2d6d873aed20427c26d))
* 添加一键重启 Smart Bill 前后端开发服务器脚本 ([2e108a7](https://github.com/alanwhy/smart-bill/commit/2e108a7e0d8a6baaea41018db97aab9fe9264d82))
* 添加前端 Dockerfile、Nginx 配置和一键部署脚本，优化前端部署流程 ([71f692b](https://github.com/alanwhy/smart-bill/commit/71f692bfd951ea40634a32de90580466c866a6cf))
* 添加手动创建账单功能，更新相关数据模型和 API 接口 ([4f1618e](https://github.com/alanwhy/smart-bill/commit/4f1618e9224bf6ca63894f92bf41e00a9987beae))
* 添加批量导入账单功能，更新相关数据模型和接口，优化导入导出 Excel 的工具函数 ([63d6387](https://github.com/alanwhy/smart-bill/commit/63d63878a7106b9f67d1d6f4dd63fdd5188adf20))
* 添加更新文档技能，支持自动同步文档与代码变更 ([7feed81](https://github.com/alanwhy/smart-bill/commit/7feed81f056f1f88a19b2f3912b1ccf9f160b7a3))
* 添加生产环境变量配置，更新 Docker 和部署脚本，优化开发和部署流程 ([5280657](https://github.com/alanwhy/smart-bill/commit/528065773467cf436c258a9134c1de787aaeaa70))
* 添加用户月度账单周期设置功能，支持获取和更新周期起始日 ([25f3b8d](https://github.com/alanwhy/smart-bill/commit/25f3b8d1809d0965d26a58e2873f184ea6a2edd3))
* 添加账单备注功能，支持在账单中记录描述信息 ([94c31d7](https://github.com/alanwhy/smart-bill/commit/94c31d79c6151fa9a8ebbb06862f48cf821e8aea))
* 移除账单记录和创建账单接口中的图片路径字段，简化数据模型 ([952f931](https://github.com/alanwhy/smart-bill/commit/952f9315d7b37036909b9118b6f9ce26f937acc1))


### 🐛 Bug 修复

* 删除不再需要的设置文件，清理项目结构 ([ffe9957](https://github.com/alanwhy/smart-bill/commit/ffe99576f6b691aeef9b53da58ccac4011aa972b))
* 改进前端上传错误提示，显示详细错误信息 ([c2d5590](https://github.com/alanwhy/smart-bill/commit/c2d5590524b0cacacbbd3f32926ceeedaec2c212))
* 更新删除分类时的错误提示信息，支持中文显示 ([994ac50](https://github.com/alanwhy/smart-bill/commit/994ac503ff5a905319096c8f9ae405d43a210fef))
* 更新账单解析器以记录 Qwen 响应和解析错误，优化用户调试体验 ([85d536c](https://github.com/alanwhy/smart-bill/commit/85d536c6a21a15ecb27052fda0c16d7d636bde56))

## [0.5.0] - 2026-06-18

### 已实现

- [x] Phase 19：前端独立容器化部署
  - **前端 Dockerfile** `docker/Dockerfile.frontend`：基于 `nginx:alpine`，将预构建 dist 复制到 Nginx 静态目录
  - **Nginx 配置** `docker/nginx.conf`：gzip 压缩、静态资源长效缓存、`/api` 反向代理到后端容器、SPA 路由回退
  - **前端一键部署脚本** `scripts/deploy_frontend.sh`：本地构建 → rsync 同步产物 → 远程构建并启动 frontend 容器 → 健康检查（端口 19284）
  - **Docker Compose 扩展**：`docker/docker-compose.yml` 新增 `frontend` service（19284:80），depends_on 后端

- [x] Phase 20：环境变量配置优化
  - 移除 `.env.production` 文件，改为通过 shell 环境变量 `QWEN_API_KEY_PROD` / `SECRET_KEY_PROD` 传入生产密钥，避免敏感信息落盘
  - `scripts/deploy.sh` 优化：部署前检查生产密钥环境变量是否已 export，动态生成临时 `.env` 文件部署完成后自动删除
  - `.env.example` 精简：移除生产相关字段，专注本地开发必要配置（`QWEN_API_KEY`、`SECRET_KEY`、`LOG_LEVEL`、`HOST`、`PORT`、`DATABASE_URL`、`CORS_ORIGINS`）
  - `docs/SETUP.md` 新增完整生产部署说明（密钥管理、两阶段部署流程）

_last commit: `908158a9e9dc94d82c4feaa3631f7235ffb58034`_

---

## [0.4.0] - 2026-06-18

### 已实现

- [x] Phase 17：生产环境部署
  - **一键部署脚本** `scripts/deploy.sh`：支持 `--init`（首次初始化服务器）和日常更新部署两种模式
  - **生产环境变量模板** `.env.production`（已于 v0.5.0 移除，改为 shell 环境变量方式）：原含 `QWEN_API_KEY`、`SECRET_KEY`、`CORS_ORIGINS` 等配置项
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

- [x] Phase 4：千问模型 集成
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
