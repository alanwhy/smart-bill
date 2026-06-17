# Smart Bill - 智能账单识别服务

使用 Qwen3-VL-Plus 视觉模型识别账单图片，提取结构化账单数据。

## 功能

- 上传账单图片（JPG/PNG），Qwen3-VL-Plus 自动识别账单信息
- 账单数据保存到 SQLite，支持查询/编辑/删除
- 自定义分类管理（CRUD）
- 账单备注功能
- 用户认证（JWT）
- 响应式 Web 前端（PC 侧边栏 / 移动端底部导航）

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.10+ · FastAPI · SQLAlchemy · SQLite · uv |
| AI | 阿里云 DashScope Qwen3-VL-Plus |
| 前端 | Vue 3 · TypeScript · Vite · Tailwind CSS · Pinia |
| 部署 | Docker Compose · 本地 NAS |

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- uv（Python 包管理工具）

### 安装与启动

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

### 访问地址

| 服务 | 地址 |
|---|---|
| 前端应用 | http://localhost:5173 |
| 后端 API | http://localhost:8000 |
| Swagger 文档 | http://localhost:8000/docs |
| 健康检查 | http://localhost:8000/health |

## 项目结构

```
smart-bill/
├── backend/          # FastAPI 后端
│   ├── api/          # 路由（bills, categories, auth）
│   ├── services/     # 业务逻辑（qwen, parser, auth）
│   ├── database/     # ORM 模型和 CRUD
│   ├── core/         # Pydantic 模型和枚举
│   └── utils/        # 工具函数和日志
├── frontend/web/     # Vue 3 前端
│   └── src/
│       ├── pages/    # 页面（Dashboard, Login, Categories...）
│       ├── components/  # 组件（BillCard, Toast, ConfirmDialog...）
│       ├── stores/   # Pinia 状态（auth, bills, categories）
│       └── api/      # axios 请求封装
├── scripts/
│   └── restart.sh    # 一键重启脚本
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
- [ ] Docker NAS 部署优化
- [ ] 定时备份脚本

## 许可证

MIT
