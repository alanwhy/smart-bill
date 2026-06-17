# Smart Bill - Claude 开发指南

## 项目概览

**Smart Bill** 是一个使用 Qwen3-VL-Plus 视觉模型的智能账单识别服务。

- **用途**: 识别用户上传的账单图片，提取消费信息（金额、日期、商户、分类）
- **用户**: 2 人（用户和媳妇）
- **部署**: 本地 NAS（Docker）
- **开发工具**: Claude Code、Codex
- **起始日期**: 2026-06-16

## 项目架构

### 核心设计原则

1. **模块化分层**
   - API 层 (`backend/api/`) - 路由和请求处理
   - Service 层 (`backend/services/`) - 业务逻辑
   - Database 层 (`backend/database/`) - 数据持久化
   - Core 层 (`backend/core/`) - 数据模型和类型
   - Utils 层 (`backend/utils/`) - 工具函数

2. **前后端分离**
   - 后端: Python + FastAPI（http://localhost:8000）
   - 前端: Vue 3 + TypeScript + Vite + Tailwind CSS + Pinia（http://localhost:5173）
   - 通过 REST API 通信，Vite 代理处理跨域

3. **数据库设计**
   - SQLite 轻量级存储（本地 NAS 部署）
   - `bill_records` 表：id、user_id、merchant_name、value、transaction_date、category、notes、image_path、created_at、updated_at
   - `categories` 表：id、name、icon、color、sort_order、created_at
   - 索引: (user_id, created_at) 复合索引

### 关键技术决策

- **FastAPI** - 高性能异步框架，自动 OpenAPI 文档
- **SQLAlchemy + SQLite** - 轻量级 ORM + 数据库
- **Pydantic** - 数据验证和序列化
- **uv** - Python 依赖管理（替代 pip）
- **Vue 3 + Vite** - 前端框架，TypeScript 支持，Vite proxy 处理跨域
- **Pinia** - Vue 3 状态管理（auth/bills/categories/ui store）
- **Tailwind CSS** - 响应式样式，深色主题，金色 primary (#F59E0B)
- **python-jose + passlib** - JWT 认证
- **Docker Compose** - 容器化部署

## 开发规范

### 代码风格

```python
# 导入顺序: 标准库 → 第三方 → 本地
import os
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core import BillCategory
from backend.database import crud, get_db
```

### 命名约定

- **文件**: snake_case (e.g., `bill_parser.py`)
- **类**: PascalCase (e.g., `BillProcessor`)
- **函数/变量**: snake_case (e.g., `get_bill_list`)
- **常量**: UPPER_SNAKE_CASE (e.g., `MAX_FILE_SIZE`)

### 错误处理

使用自定义异常（`backend/core/exceptions.py`）：

```python
from backend.core import ValidationError, QwenAPIError, DatabaseError

# 而不是 raise Exception()
raise ValidationError("Invalid input", detail="详细错误信息")
```

### 日志

使用统一的日志记录器：

```python
from backend.utils import logger

logger.info("Operation succeeded")
logger.error(f"Error: {str(e)}")
```

## 常用命令

```bash
# 依赖管理
make install          # 使用 uv 安装后端依赖
uv pip list          # 列出所有依赖

# 后端开发
make dev             # 启动后端开发服务器 (http://localhost:8000)
make test            # 运行测试
make lint            # 代码检查
make format          # 代码格式化
make clean           # 清理临时文件

# 前端开发
cd frontend/web
npm install          # 安装前端依赖
npm run dev          # 启动前端开发服务器 (http://localhost:5173)
npm run build        # 构建前端

# 一键重启
bash scripts/restart.sh   # 同时重启前后端开发服务器

# Docker
make build-docker    # 构建 Docker 镜像
make run-docker      # 运行 Docker 容器

# 其他
make help            # 显示所有命令
make docs            # 查看文档
```

## API 文档

### 主要端点

**认证**
- `POST /api/v1/auth/login` - 登录获取 JWT token
- `GET /api/v1/auth/me` - 获取当前用户（Bearer token）
- `POST /api/v1/auth/change-password` - 修改密码

**账单**
- `POST /api/v1/bills/upload` - 上传图片识别账单
  - 参数: files (UploadFile), user_id (int)
  - 返回: List[BillItem]

- `GET /api/v1/bills` - 查询账单列表
  - 参数: user_id, start_date?, end_date?, category?
  - 返回: List[BillRecordInDB]

- `PUT /api/v1/bills/{bill_id}` - 修改账单（支持 notes 备注字段）
- `DELETE /api/v1/bills/{bill_id}` - 删除账单

**分类**
- `GET/POST /api/v1/categories` - 列出/创建分类
- `GET/PUT/DELETE /api/v1/categories/{id}` - 查询/更新/删除分类

- `GET /docs` - Swagger UI
- `GET /health` - 健康检查

完整 API 文档见 `docs/API.md`

## 数据模型

### BillItem (API 响应)
```python
{
  "value": 50.0,              # 金额
  "name": "麦当劳",           # 商户名
  "date": "2026-06-16 10:00:00",  # 日期
  "category": "餐饮"          # 分类
}
```

### BillRecord (数据库)
```python
BillRecord(
  id: int,
  user_id: int,               # 谁创建的
  merchant_name: str,
  value: float,
  transaction_date: str,
  category: str,              # 分类名称（来自 categories 表）
  notes: str | None,          # 账单备注
  image_path: str,            # 原始图片路径
  created_at: datetime,
  updated_at: datetime
)
```

### Category (分类数据库)
```python
Category(
  id: int,
  name: str,                  # 分类名称
  icon: str,                  # emoji 图标
  color: str,                 # 颜色（hex）
  sort_order: int,            # 排序
  created_at: datetime
)
```

### 默认分类（种子数据）
- 餐饮 🍽️ / 交通 🚗 / 购物 🛍️ / 娱乐 🎮
- 医疗 🏥 / 住房 🏠 / 其他 📦

## 文件组织

```
backend/
├── api/
│   ├── auth.py          # 认证路由（登录/获取用户/改密码）
│   ├── bills.py         # 账单路由（主入口）
│   ├── categories.py    # 分类路由（CRUD）
│   └── routes.py        # 路由聚合
├── services/
│   ├── auth_service.py  # 用户认证逻辑
│   ├── qwen_vision.py  # Qwen API 调用
│   ├── bill_parser.py  # 数据解析（JSON/文本）
│   └── bill_processor.py # 流程编排
├── database/
│   ├── models.py        # SQLAlchemy 模型（BillRecord, Category）
│   ├── db.py           # 数据库连接
│   ├── crud.py         # CRUD 操作
│   └── seed.py         # 初始分类种子数据
├── core/
│   ├── models.py        # Pydantic 模型
│   ├── enums.py        # 分类枚举
│   └── exceptions.py    # 异常定义
└── utils/
    ├── validators.py   # 验证器
    ├── converters.py   # 数据转换
    └── logger.py       # 日志管理

frontend/web/src/
├── pages/              # DashboardPage, LoginPage, CategoriesPage...
├── components/
│   ├── bills/          # BillCard, BillEditModal, BillFilters, BillUploadModal
│   └── common/         # Toast, ConfirmDialog
├── stores/             # auth.ts, bills.ts, categories.ts, ui.ts
├── api/                # axios 请求封装
├── router/             # 路由（含受保护路由）
└── types/              # TypeScript 类型定义

scripts/
└── restart.sh          # 一键重启前后端开发服务器
```

## 环境变量

```bash
# .env 文件配置
QWEN_API_KEY=your-api-key              # 阿里云 DashScope API 密钥
LOG_LEVEL=INFO                         # 日志级别
DATABASE_URL=sqlite:///./smart_bill.db # 数据库 URL
HOST=0.0.0.0                          # 服务器地址
PORT=8000                             # 服务器端口
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"] # CORS 允许源
SECRET_KEY=your-secret-key            # JWT 签名密钥
```

## 开发流程

### 新增功能

1. **设计**: 在 plan 文件中描述设计
2. **实现**: 按模块顺序实现（测试 → 代码 → 集成）
3. **测试**: `make test` 运行测试
4. **提交**: `git commit -m "feat: 简洁描述"` 并说明改动

### 提交消息规范

```
<type>: <subject>

<body>

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
```

类型:
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档
- `refactor`: 代码重构
- `test`: 测试
- `chore`: 杂务

## 后续优先级

### Phase 12: 用户认证与授权（已完成 ✅）
- [x] JWT token 登录认证
- [x] `POST /api/v1/auth/login`、`GET /api/v1/auth/me`
- [x] auth service + 前端登录页
- [ ] 中间件强制验证所有 bill 端点（当前 user_id 仍由前端传入）
- [ ] 用户注册功能（当前仅支持预设账户）

### Phase 13: 分类管理服务（已完成 ✅）
- [x] Category 数据库表
- [x] CRUD API 端点（`GET/POST/PUT/DELETE /api/v1/categories`）
- [x] 自定义分类支持 + 种子数据
- [x] 前端分类管理页面

### Phase 14: 前端应用开发（已完成 ✅）
- [x] 响应式 Web 应用（Vue 3 + TypeScript + Vite + Tailwind）
- [x] 图片上传界面（BillUploadModal）
- [x] 账单列表展示（DashboardPage + BillFilters）
- [x] 分类管理界面（CategoriesPage）
- [x] Toast 通知组件 + ConfirmDialog 确认框
- [x] 账单备注字段

### Phase 15: 高级功能（第一优先级）
- [ ] 账单统计分析（月度消费、分类占比）
- [ ] 报表导出（PDF/Excel）
- [ ] 消费趋势图表（echarts/chart.js）
- [ ] 定期提醒功能

### Phase 16: 部署优化（第二优先级）
- [ ] NAS 部署指南
- [ ] Docker 镜像优化（前端 nginx + 后端 uvicorn）
- [ ] 本地存储配置（规范化图片存储路径）
- [ ] 定时备份脚本

## 已知问题 & 限制

1. **用户标识**: user_id 仍由前端传入，auth 中间件尚未强制校验所有账单端点
2. **用户注册**: 当前仅支持预设账户登录，暂无注册功能
3. **图片存储**: 临时文件存储在系统 temp 目录，后续需要规范化存储
4. **并发**: SQLite 在高并发下可能出现锁定，小规模使用无问题

## 持续维护

### 文档更新

- 每个阶段完成后更新 `docs/CHANGELOG.md`
- API 变更后更新 `docs/API.md`
- 架构调整后更新 `docs/ARCHITECTURE.md`

### 代码审查

- 每个 PR 检查：类型注解、错误处理、文档注释
- 确保模块间低耦合、高内聚
- 避免循环导入

### 性能监控

- 监控 Qwen API 调用耗时
- 数据库查询性能
- 内存使用情况

## 快速参考

### 启动项目
```bash
cd smart-bill
make install
cp .env.example .env
# 编辑 .env 填入 QWEN_API_KEY 和 SECRET_KEY
make dev
# 后端: http://localhost:8000/docs

# 前端（另开终端）
cd frontend/web && npm install && npm run dev
# 前端: http://localhost:5173

# 或者一键重启
bash scripts/restart.sh
```

### 查看文档
```bash
# 架构设计
cat docs/ARCHITECTURE.md

# API 文档
cat docs/API.md

# 开发配置
cat docs/SETUP.md

# 更新日志
cat docs/CHANGELOG.md

# 项目总结
cat IMPLEMENTATION_SUMMARY.md
```

### 常见操作

```bash
# 安装新依赖
uv pip install package_name

# 更新 pyproject.toml
# 手动编辑后运行:
make install

# 添加测试
# 在 backend/tests/ 中创建 test_xxx.py

# 提交代码
git add -A
git commit -m "type: description"
git push origin main
```

## GitHub 仓库

- **地址**: https://github.com/alanwhy/smart-bill
- **分支**: main
- **开发规范**: 直接在 main 分支开发（小团队）

## 联系与问题

如有问题或需要调整开发流程，请：
1. 更新这个 CLAUDE.md 文件
2. 在 CHANGELOG.md 中记录
3. 提交 git commit

---

**最后更新**: 2026-06-17  
**由 Claude Code 维护**
