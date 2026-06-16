# Smart Bill - 智能账单识别服务

使用 Qwen3-VL-Plus 视觉模型识别账单图片，提取结构化账单数据。

## 功能

- 🖼️ 上传账单图片（JPG/PNG）
- 🤖 使用 Qwen3-VL-Plus 自动识别账单信息
- 💾 保存账单数据到 SQLite 数据库
- 🔍 查询和管理账单数据

## 快速开始

### 环境要求

- Python 3.10+
- uv（Python 包管理工具）

### 安装

1. 克隆项目并进入目录
   ```bash
   cd smart-bill
   ```

2. 安装依赖
   ```bash
   uv sync
   ```

3. 配置环境变量
   ```bash
   cp .env.example .env
   # 编辑 .env，填入 QWEN_API_KEY
   ```

4. 启动开发服务器
   ```bash
   make dev
   ```

服务将在 `http://localhost:8000` 运行。

### 使用

访问 `http://localhost:8000/docs` 查看 API 文档。

## 项目结构

见 [ARCHITECTURE.md](docs/ARCHITECTURE.md)

## 文档

- [API 文档](docs/API.md)
- [架构设计](docs/ARCHITECTURE.md)
- [开发配置](docs/SETUP.md)
- [更新日志](docs/CHANGELOG.md)

## 开发工具

- Claude Code
- Codex

## 后续计划

- [ ] 用户认证与授权
- [ ] 分类管理服务
- [ ] 前端应用（响应式 Web）
- [ ] Docker 部署配置

## 许可证

MIT
