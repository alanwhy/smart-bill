.PHONY: help install dev test lint format clean build-docker run-docker docs

help:
	@echo "Smart Bill - 账单识别服务"
	@echo ""
	@echo "可用命令："
	@echo "  make install      - 使用 uv 安装依赖"
	@echo "  make dev          - 启动开发服务器"
	@echo "  make test         - 运行测试"
	@echo "  make lint         - 代码检查"
	@echo "  make format       - 代码格式化"
	@echo "  make clean        - 清理临时文件"
	@echo "  make build-docker - 构建 Docker 镜像"
	@echo "  make run-docker   - 运行 Docker 容器"
	@echo "  make docs         - 查看文档"

install:
	uv sync

dev:
	uv run python -m backend.main

test:
	uv run pytest backend/tests/ -v --tb=short

lint:
	uv run ruff check backend/
	uv run mypy backend/

format:
	uv run black backend/
	uv run ruff check --fix backend/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/ .mypy_cache/ build/ dist/ *.egg-info/ .coverage htmlcov/
	rm -f smart_bill.db

build-docker:
	docker build -f docker/Dockerfile -t smart-bill:latest .

run-docker:
	docker-compose -f docker/docker-compose.yml up

docs:
	@echo "查看文档请打开: file://$(PWD)/docs"
	@echo ""
	@echo "主要文档："
	@echo "- ARCHITECTURE.md  - 架构设计"
	@echo "- API.md          - API 文档"
	@echo "- SETUP.md        - 开发配置"
	@echo "- CHANGELOG.md    - 更新日志"
