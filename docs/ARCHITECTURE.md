# 架构设计文档

## 系统分层

### 1. API 层 (`backend/api/`)
- 处理 HTTP 请求/响应
- 参数验证和错误处理
- CORS 和中间件配置

### 2. Service 层 (`backend/services/`)
- 核心业务逻辑
- Qwen API 调用
- 账单数据解析
- 流程编排

### 3. Database 层 (`backend/database/`)
- SQLAlchemy ORM 模型
- CRUD 操作
- 数据持久化

### 4. Core 层 (`backend/core/`)
- 数据模型和 Pydantic schema
- 枚举类型
- 自定义异常

### 5. Utils 层 (`backend/utils/`)
- 数据验证
- 数据转换
- 日志管理

## 数据流

```
上传图片
  ↓
API 路由 (bills.py)
  ↓
BillProcessor.process_bill_image()
  ├─ 图片验证 (validators.py)
  ├─ 调用 Qwen (qwen_vision.py)
  ├─ 解析数据 (bill_parser.py)
  ├─ 保存数据库 (crud.py)
  └─ 返回结果
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
