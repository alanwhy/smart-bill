# Smart Bill - 智能账单识别服务

使用 Qwen3-VL-Plus 视觉模型识别账单图片，提取结构化账单数据。

## 功能

- 上传账单图片（JPG/PNG），支持多张并发识别
- **手动创建账单**，无需上传图片
- **收支类型区分**（负数=支出，正数=收入）
- 账单数据保存到 SQLite，支持查询/编辑/删除
- 自定义分类管理（CRUD）
- 账单备注功能
- 用户认证（JWT）
- **月度账单周期自定义**（起始日 1-28 可配置）
- 响应式 Web 前端（PC 侧边栏 / 移动端底部导航）

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.10+ · FastAPI · SQLAlchemy · SQLite · uv |
| AI | 阿里云 DashScope Qwen3-VL-Plus |
| 前端 | Vue 3 · TypeScript · Vite · Tailwind CSS · Pinia |
| 部署 | Docker Compose · Nginx · 本地 NAS / 服务器 |

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- uv（Python 包管理工具）

### 安装与启动（本地开发）

**方式一：一键启动（推荐）**

```bash
cd smart-bill
cp .env.example .env
# 编辑 .env，填入 QWEN_API_KEY
bash scripts/restart.sh
```

**方式二：分步启动**

```bash
# 后端
make install
make dev
# 访问 http://localhost:8000/docs

# 前端（新终端）
cd frontend/web
npm install
npm run dev
# 访问 http://localhost:5173
```

### 生产环境部署（服务器 / NAS）

```bash
# 首次初始化服务器（仅需执行一次）
# 先 export 生产密钥（不依赖 .env 文件）
export QWEN_API_KEY_PROD=your-production-key
export SECRET_KEY_PROD=$(openssl rand -hex 32)
bash scripts/deploy.sh --init

# 日常更新部署（每次发布前 export 密钥即可）
export QWEN_API_KEY_PROD=your-production-key
export SECRET_KEY_PROD=your-production-secret
bash scripts/deploy.sh

# 前端独立部署（可选，单独更新前端）
bash scripts/deploy_frontend.sh
```

> 后端监听端口 `19283`，前端 Nginx 容器监听端口 `19284`。

### 访问地址

| 服务 | 本地开发 | 生产环境 |
|---|---|---|
| 前端应用 | http://localhost:5173 | http://server:19284 |
| 后端 API | http://localhost:8000 | http://server:19283 |
| Swagger 文档 | http://localhost:8000/docs | — |
| 健康检查 | http://localhost:8000/health | — |

## 项目结构

```
smart-bill/
├── backend/          # FastAPI 后端
│   ├── api/          # 路由（bills, categories, auth）
│   ├── services/     # 业务逻辑（qwen, parser, auth, prompts）
│   ├── database/     # ORM 模型和 CRUD
│   ├── core/         # Pydantic 模型和枚举
│   └── utils/        # 工具函数和日志
├── frontend/web/     # Vue 3 前端
│   └── src/
│       ├── pages/    # 页面（Dashboard, Login, Categories, Settings...）
│       ├── components/  # 组件（BillCard, Toast, ConfirmDialog...）
│       ├── stores/   # Pinia 状态（auth, bills, categories）
│       ├── utils/    # 工具（cycle.ts 周期日期计算）
│       └── api/      # axios 请求封装
├── docker/           # Docker 配置（生产环境）
│   ├── Dockerfile          # 后端镜像
│   ├── Dockerfile.frontend # 前端 Nginx 镜像
│   ├── docker-compose.yml  # 编排（后端:19283 + 前端:19284）
│   └── nginx.conf          # 前端 Nginx 配置（SPA + API 代理）
├── scripts/
│   ├── restart.sh          # 一键重启（开发环境）
│   ├── deploy.sh           # 后端一键部署（生产环境）
│   └── deploy_frontend.sh  # 前端一键部署（生产环境）
└── docs/             # 文档
```

## 文档

- [API 文档](docs/API.md)
- [架构设计](docs/ARCHITECTURE.md)
- [开发配置](docs/SETUP.md)
- [更新日志](docs/CHANGELOG.md)
- [前端开发](frontend/web/README.md)

## 开发工具

- Claude Code
- Codex

## 后续计划

- [ ] 账单统计分析与趋势图表
- [ ] 报表导出（PDF/Excel）
- [ ] 定时备份脚本
- [ ] 认证中间件强制校验所有账单端点

## 许可证

MIT
