#!/usr/bin/env bash
# =============================================================
# Smart Bill — 前端一键部署脚本
# 用法：
#   首次部署（开放防火墙端口）：./scripts/deploy_frontend.sh --init
#   日常更新部署：               ./scripts/deploy_frontend.sh
# =============================================================

set -euo pipefail

# ---- 配置 ----
SERVER_IP="8.141.99.198"
SERVER_USER="root"
SERVER_PORT="22"
SSH_KEY="$HOME/.ssh/smart_bill_deploy"
REMOTE_DIR="/opt/smart-bill"
COMPOSE_FILE="docker/docker-compose.yml"
FRONTEND_PORT="19284"

# ---- 颜色输出 ----
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# ---- SSH / SCP 快捷函数 ----
SSHOPTS="-i $SSH_KEY -o StrictHostKeyChecking=accept-new -o ConnectTimeout=15"
ssh_cmd() { ssh $SSHOPTS -p "$SERVER_PORT" "${SERVER_USER}@${SERVER_IP}" "$@"; }

# ---- 前置检查 ----
[[ -f "$SSH_KEY" ]] || error "SSH 私钥不存在：$SSH_KEY"

# =========================================================
# --init：首次部署初始化（仅需执行一次）
# =========================================================
if [[ "${1:-}" == "--init" ]]; then
  info "=== 开放防火墙端口 ${FRONTEND_PORT} ==="
  ssh_cmd "ufw allow ${FRONTEND_PORT}/tcp 2>/dev/null || \
    iptables -A INPUT -p tcp --dport ${FRONTEND_PORT} -j ACCEPT 2>/dev/null || true"
  info "端口 ${FRONTEND_PORT} 已开放"
fi

# =========================================================
# 前端部署流程
# =========================================================
info "=== 开始部署 Smart Bill 前端 ==="

# Step 1：本地构建（生产产物）
info "本地构建前端..."
(cd frontend/web && npx vite build) || error "前端构建失败，请检查 vite build 的输出"

# Step 2：同步构建产物 + docker 配置
info "同步 dist 产物到服务器..."
rsync -az --delete \
  -e "ssh $SSHOPTS -p $SERVER_PORT" \
  frontend/web/dist/ "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/frontend/web/dist/"

info "同步 Docker 配置..."
rsync -az \
  -e "ssh $SSHOPTS -p $SERVER_PORT" \
  docker/ "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/docker/"

# Step 2：构建并启动前端容器
info "构建前端镜像并启动容器..."
ssh_cmd "cd $REMOTE_DIR && \
  (docker compose -f $COMPOSE_FILE stop frontend 2>/dev/null || \
   docker-compose -f $COMPOSE_FILE stop frontend 2>/dev/null || true) && \
  (docker compose -f $COMPOSE_FILE build frontend || \
   docker-compose -f $COMPOSE_FILE build frontend) && \
  (docker compose -f $COMPOSE_FILE up -d frontend || \
   docker-compose -f $COMPOSE_FILE up -d frontend)"

# Step 3：健康检查（等待最多 60 秒）
info "等待前端服务启动（最多 60 秒）..."
for i in $(seq 1 12); do
  if ssh_cmd "curl -sf http://localhost:${FRONTEND_PORT}/" >/dev/null 2>&1; then
    info "=== 前端部署成功！==="
    echo ""
    echo "  前端地址：http://${SERVER_IP}:${FRONTEND_PORT}"
    echo ""
    info "查看日志：ssh -i $SSH_KEY ${SERVER_USER}@${SERVER_IP} 'docker logs -f smart-bill-frontend'"
    exit 0
  fi
  warn "等待中... ($((i * 5))s)"
  sleep 5
done

error "前端服务启动超时，请查看容器日志：\n  ssh -i $SSH_KEY ${SERVER_USER}@${SERVER_IP} 'docker logs smart-bill-frontend'"
