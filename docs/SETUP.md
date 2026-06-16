# 本地开发环境配置

## 环境要求

- Python 3.10 或更高版本
- uv（Python 包管理工具）
- SQLite（通常内置）

## 安装 uv

```bash
# macOS
brew install uv

# Linux / WSL
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (如果已安装 Python)
pip install uv
```

## 项目设置

### 1. 克隆项目
```bash
git clone <repository-url>
cd smart-bill
```

### 2. 安装依赖
```bash
make install
# 或直接使用 uv
uv sync
```

### 3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入 QWEN_API_KEY
```

获取 QWEN_API_KEY：
1. 访问 https://dashscope.aliyun.com/
2. 创建或选择项目
3. 在 API-KEY 管理中创建密钥
4. 复制密钥到 .env 文件

### 4. 启动开发服务器
```bash
make dev
```

服务将在 `http://localhost:8000` 运行。

### 5. 查看 API 文档
访问 `http://localhost:8000/docs` 查看 Swagger UI。

## 常用命令

```bash
# 安装依赖
make install

# 启动开发服务器
make dev

# 运行测试
make test

# 代码检查
make lint

# 代码格式化
make format

# 清理临时文件
make clean
```

## 调试

### 启用详细日志
编辑 `.env` 文件：
```
LOG_LEVEL=DEBUG
```

### 查看数据库
SQLite 数据库文件存储在 `smart_bill.db`，可以用任何 SQLite 客户端打开：
```bash
# 使用 sqlite3 命令行
sqlite3 smart_bill.db

# 或使用 VS Code 扩展
# 搜索 "sqlite" 并安装 SQLite 扩展
```

## 测试数据

示例账单图片存储在 `backend/tests/fixtures/` 目录。

## 问题排查

### "QWEN_API_KEY not set"
确保 `.env` 文件存在且包含有效的 QWEN_API_KEY。

### "Database is locked"
SQLite 在高并发下可能出现锁定，重启服务器即可。

### "UnicodeDecodeError"
确保文件使用 UTF-8 编码。
