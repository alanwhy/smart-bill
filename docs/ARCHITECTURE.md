# 架构设计文档

## 系统分层

### 后端分层

#### 1. API 层 (`backend/api/`)
- 处理 HTTP 请求/响应
- 参数验证和错误处理
- CORS 和中间件配置
- 文件：`bills.py`、`categories.py`、`auth.py`、`routes.py`

#### 2. Service 层 (`backend/services/`)
- 核心业务逻辑
- Qwen API 调用
- 账单数据解析
- 用户认证服务
- 文件：`qwen_vision.py`、`bill_parser.py`、`bill_processor.py`、`auth_service.py`

#### 3. Database 层 (`backend/database/`)
- SQLAlchemy ORM 模型
- CRUD 操作
- 数据持久化
- 文件：`models.py`、`crud.py`、`db.py`、`seed.py`

#### 4. Core 层 (`backend/core/`)
- 数据模型和 Pydantic schema
- 枚举类型
- 自定义异常
- 文件：`models.py`、`enums.py`、`exceptions.py`

#### 5. Utils 层 (`backend/utils/`)
- 数据验证
- 数据转换
- 日志管理
- 文件：`validators.py`、`converters.py`、`logger.py`

### 前端架构 (`frontend/web/`)

技术栈：**Vue 3 + TypeScript + Vite + Tailwind CSS + Pinia**

- **pages/** - 页面组件：DashboardPage、LoginPage、CategoriesPage、SettingsPage、UserPage
- **components/bills/** - 账单相关组件：BillCard、BillEditModal、BillFilters、BillUploadModal
- **components/common/** - 通用组件：Toast（通知）、ConfirmDialog（确认框）
- **stores/** - Pinia 状态管理：auth.ts、bills.ts、categories.ts、ui.ts
- **api/** - axios 请求封装，Vite 代理到 http://localhost:8000
- **router/** - Vue Router，含受保护路由（需登录）

响应式设计：PC 侧边栏导航 / 移动端底部导航

## 数据模型

### BillRecord（账单数据库表）
```python
BillRecord(
  id: int,
  user_id: int,
  merchant_name: str,
  value: float,               # 负数=支出，正数=收入
  transaction_date: str,
  category_id: int,           # 外键关联 categories.id
  category: CategoryBrief,    # lazy="joined" 自动加载
  description: str | None,    # 账单备注（max 100 字）
  image_path: str | None,     # 识别图片路径（手动创建时为 null）
  created_at: datetime,
  updated_at: datetime
)
```

### User（用户表）
```python
User(
  id: int,
  username: str,
  hashed_password: str,
  cycle_start_day: int,       # 月度账单周期起始日（1-28，默认 1）
  created_at: datetime,
  updated_at: datetime
)
```

### Category（分类数据库表）
```python
Category(
  id: int,
  name: str,
  icon: str,
  color: str,
  sort_order: int,
  created_at: datetime
)
```

## 数据流

### 账单上传流程（并发处理）
```
上传多张图片
  ↓
API 路由 (bills.py) - 保存所有临时文件
  ↓
asyncio.gather() 并发执行
  ├─ _process_single_bill(img1) 独立线程 + DB session
  ├─ _process_single_bill(img2) 独立线程 + DB session
  └─ _process_single_bill(imgN) ...
  ↓
每个线程内：
  ├─ BillProcessor.process_bill_image()
  ├─ prompts.py 动态构建 system prompt
  ├─ qwen_vision.py 调用 Qwen API
  ├─ bill_parser.py 解析 JSON
  └─ crud.py 保存数据库
  ↓
合并结果返回
```

### 手动创建账单流程
```
POST /bills (JSON body)
  ↓
API 路由 (bills.py)
  ↓
crud.create_bill() 直接写入数据库
  ↓
返回 BillRecordInDB（含嵌套 CategoryBrief）
```

### 认证流程
```
前端 Login 页
  ↓
POST /auth/login → auth_service.py 验证用户密码
  ↓
返回 JWT token → 存储在 Pinia auth store
  ↓
后续请求携带 Authorization: Bearer <token>
  ↓
get_current_user() 解码 token，注入用户信息
```

## 文件组织

```
smart-bill/
├── backend/
│   ├── api/
│   │   ├── auth.py          # 认证路由（登录/获取用户/改密码）
│   │   ├── bills.py         # 账单路由（主入口）
│   │   ├── categories.py    # 分类路由（CRUD）
│   │   └── routes.py        # 路由聚合
│   ├── services/
│   │   ├── auth_service.py  # 用户认证逻辑
│   │   ├── qwen_vision.py   # Qwen API 调用
│   │   ├── bill_parser.py   # 数据解析（JSON/文本）
   │   ├── bill_processor.py # 流程编排
   │   └── prompts.py       # LLM 提示词管理（system prompt 集中维护）
│   ├── database/
│   │   ├── models.py        # SQLAlchemy 模型（BillRecord, Category）
│   │   ├── db.py            # 数据库连接
│   │   ├── crud.py          # CRUD 操作
│   │   └── seed.py          # 初始分类种子数据
│   ├── core/
│   │   ├── models.py        # Pydantic 模型
│   │   ├── enums.py         # 分类枚举
│   │   └── exceptions.py    # 异常定义
│   └── utils/
│       ├── validators.py    # 验证器
│       ├── converters.py    # 数据转换
│       └── logger.py        # 日志管理
├── frontend/
│   └── web/
│       ├── src/
│       │   ├── pages/       # 页面组件
│       │   ├── components/  # 通用/业务组件
│       │   ├── stores/      # Pinia 状态管理
│       │   ├── api/         # axios 请求封装
│       │   ├── router/      # 路由配置       │   ├── utils/
       │   │   └── cycle.ts # 月度周期日期计算工具│       │   └── types/       # TypeScript 类型
│       ├── package.json
│       └── vite.config.ts   # Vite 配置（含后端代理）
├── scripts/
│   └── restart.sh           # 一键重启前后端脚本
└── docs/
    ├── API.md
    ├── ARCHITECTURE.md
    ├── CHANGELOG.md
    └── SETUP.md
```

## 关键设计决策

### 为什么使用 FastAPI？
- 高性能异步框架
- 自动 OpenAPI 文档
- 原生支持文件上传
- Pydantic 集成

### 为什么分离 services 层？
- 业务逻辑独立于 HTTP 层
- 便于单元测试
- 未来可转换为其他传输协议

### 为什么使用 SQLite？
- 轻量级数据库
- 无需单独部署
- 本地 NAS 部署方便

### 为什么选择 Vue 3 + Vite？
- TypeScript 原生支持
- Pinia 状态管理简洁
- Vite 代理无需跨域配置
- Tailwind CSS 快速响应式开发
