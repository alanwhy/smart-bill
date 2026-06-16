# 更新日志

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
- [ ] 用户认证与授权
- [ ] 分类管理服务
- [ ] 前端应用开发
- [ ] Docker 部署配置

### 已知问题
- 无

### 优化建议
- 暂无
