#!/usr/bin/env bash
# =============================================================
# Smart Bill — 一键部署脚本
# 用法：
#   首次部署（含服务器初始化）：./scripts/deploy.sh --init
#   日常更新部署：               ./scripts/deploy.sh
# =============================================================

set -euo pipefail

# ---- 配置 ----
SERVER_IP="8.141.99.198"
SERVER_USER="root"
SERVER_PORT="22"
SSH_KEY="$HOME/.ssh/smart_bill_deploy"
REMOTE_DIR="/opt/smart-bill"
COMPOSE_FILE="docker/docker-compose.yml"
ENV_FILE=".env"           # 本地 .env 文件（填好真实值后使用）

# ---- 颜色输出 ----
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# ---- SSH / SCP 快捷函数 ----
SSHOPTS="-i $SSH_KEY -o StrictHostKeyChecking=accept-new -o ConnectTimeout=15"
ssh_cmd() { ssh $SSHOPTS -p "$SERVER_PORT" "${SERVER_USER}@${SERVER_IP}" "$@"; }
scp_cmd() { scp $SSHOPTS -P "$SERVER_PORT" "$@"; }

# ---- 前置检查 ----
[[ -f "$SSH_KEY" ]] || error "SSH 私钥不存在：$SSH_KEY\n  请先运行：ssh-keygen -t ed25519 -f $SSH_KEY"
[[ -f "$ENV_FILE" ]] || error ".env 文件不存在。\n  请复制 .env.production 为 .env 并填入真实值：\n  cp .env.production .env && vi .env"

grep -q "your_qwen_api_key_here" "$ENV_FILE" && \
  error ".env 中 QWEN_API_KEY 仍为占位符，请填入真实值后再部署"
grep -q "your_secret_key_here" "$ENV_FILE" && \
  error ".env 中 SECRET_KEY 仍为占位符，请运行：openssl rand -hex 32"

# =========================================================
# --init：首次服务器初始化（仅需执行一次）
# =========================================================
if [[ "${1:-}" == "--init" ]]; then
  info "=== Phase 1：初始化服务器 ==="

  info "安装 Docker..."
  ssh_cmd "bash -c 'curl -fsSL https://get.docker.com | bash && \
    systemctl enable docker && systemctl start docker'"

  info "安装 Docker Compose plugin..."
  ssh_cmd "apt-get install -y docker-compose-plugin 2>/dev/null || \
    apt-get install -y docker-compose 2>/dev/null || true"

  info "开放防火墙端口 19283..."
  ssh_cmd "ufw allow 19283/tcp 2>/dev/null || iptables -A INPUT -p tcp --dport 19283 -j ACCEPT 2>/dev/null || true"

  info "创建应用目录..."
  ssh_cmd "mkdir -p $REMOTE_DIR"

  info "配置 SSH 公钥（无密码登录）..."
  PUB_KEY=$(cat "${SSH_KEY}.pub")
  ssh_cmd "mkdir -p ~/.ssh && chmod 700 ~/.ssh && \
    grep -qF '${PUB_KEY}' ~/.ssh/authorized_keys 2>/dev/null || \
    echo '${PUB_KEY}' >> ~/.ssh/authorized_keys && \
    chmod 600 ~/.ssh/authorized_keys"

  info "=== 服务器初始化完成 ==="
fi

# =========================================================
# 日常部署流程
# =========================================================
info "=== 开始部署 Smart Bill 后端 ==="

# Step 1：同步代码
info "同步代码到服务器..."
rsync -az --delete \
  --exclude='.git' \
  --exclude='.env' \
  --exclude='.env.production' \
  --exclude='*.db' \
  --exclude='__pycache__' \
  --exclude='.venv' \
  --exclude='node_modules' \
  --exclude='logs/*' \
  --exclude='.pytest_cache' \
  -e "ssh $SSHOPTS -p $SERVER_PORT" \
  ./ "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/"

# Step 2：上传 .env
info "上传 .env 文件..."
scp_cmd "$ENV_FILE" "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/.env"

# Step 3：构建并启动容器
info "构建 Docker 镜像并启动容器..."
ssh_cmd "cd $REMOTE_DIR && \
  (docker compose -f $COMPOSE_FILE --env-file .env down --remove-orphans 2>/dev/null || \
   docker-compose -f $COMPOSE_FILE down --remove-orphans 2>/dev/null || true) && \
  (docker compose -f $COMPOSE_FILE --env-file .env up -d --build || \
   docker-compose -f $COMPOSE_FILE up -d --build)"

# Step 4：健康检查（等待最多 60 秒）
info "等待服务启动（最多 60 秒）..."
for i in $(seq 1 12); do
  if ssh_cmd "curl -sf http://localhost:19283/health" >/dev/null 2>&1; then
    info "=== 部署成功！==="
    echo ""
    echo "  API 地址：http://${SERVER_IP}:19283"
    echo "  Swagger：  http://${SERVER_IP}:19283/docs"
    echo ""
    info "查看日志：ssh -i $SSH_KEY ${SERVER_USER}@${SERVER_IP} 'docker logs -f smart-bill-app'"
    exit 0
  fi
  warn "等待中... ($((i * 5))s)"
  sleep 5
done

# 健康检查失败，打印日志辅助排查
error "服务启动超时，请查看容器日志：\n  ssh -i $SSH_KEY ${SERVER_USER}@${SERVER_IP} 'docker logs smart-bill-app'"
