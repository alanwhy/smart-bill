# 使用 Python 3.11 官方镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 换用阿里云 apt 镜像源，加速国内下载
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制 pyproject.toml 和安装依赖
COPY pyproject.toml .
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ uv && \
    uv export --no-hashes --format requirements-txt -o /tmp/requirements.txt && \
    pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r /tmp/requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# 启动命令
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
