#!/usr/bin/env bash
# 一键重启 Smart Bill 前后端开发服务器
#
# 用法：
#   ./scripts/restart.sh                # 同时重启前后端 (默认)
#   ./scripts/restart.sh backend        # 只重启后端
#   ./scripts/restart.sh frontend       # 只重启前端
#   ./scripts/restart.sh stop           # 停止前后端，不再启动
#
# 后端日志: logs/backend.log    (默认 http://localhost:8000)
# 前端日志: logs/frontend.log   (默认 http://localhost:5173)
#
# 查看实时日志：
#   tail -f logs/backend.log
#   tail -f logs/frontend.log

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_DIR="$ROOT_DIR/logs"
PID_DIR="$ROOT_DIR/.pids"

BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"
FRONTEND_DIR="$ROOT_DIR/frontend/web"

mkdir -p "$LOG_DIR" "$PID_DIR"

# ---------------------------------------------------------------------------
# 颜色 / 输出
# ---------------------------------------------------------------------------
if [[ -t 1 ]]; then
    C_GREEN=$'\033[0;32m'
    C_YELLOW=$'\033[0;33m'
    C_RED=$'\033[0;31m'
    C_DIM=$'\033[2m'
    C_RESET=$'\033[0m'
else
    C_GREEN=""; C_YELLOW=""; C_RED=""; C_DIM=""; C_RESET=""
fi

info()  { printf "%s▸%s %s\n" "$C_GREEN"  "$C_RESET" "$*"; }
warn()  { printf "%s!%s %s\n" "$C_YELLOW" "$C_RESET" "$*"; }
error() { printf "%s✗%s %s\n" "$C_RED"    "$C_RESET" "$*"; }

# ---------------------------------------------------------------------------
# 工具：根据端口 / pid 文件停服务
# ---------------------------------------------------------------------------
stop_by_port() {
    local port="$1"
    local pids
    pids=$(lsof -nP -iTCP:"$port" -sTCP:LISTEN -t 2>/dev/null || true)
    if [[ -z "$pids" ]]; then
        return 0
    fi
    info "停止占用端口 $port 的进程: $pids"
    # shellcheck disable=SC2086
    kill $pids 2>/dev/null || true

    # 等待最多 5 秒让进程优雅退出
    local i
    for i in 1 2 3 4 5; do
        sleep 1
        pids=$(lsof -nP -iTCP:"$port" -sTCP:LISTEN -t 2>/dev/null || true)
        [[ -z "$pids" ]] && return 0
    done

    warn "端口 $port 仍有进程未退出，发送 SIGKILL"
    # shellcheck disable=SC2086
    kill -9 $pids 2>/dev/null || true
    sleep 1
}

stop_by_pidfile() {
    local pidfile="$1"
    [[ -f "$pidfile" ]] || return 0
    local pid
    pid=$(cat "$pidfile" 2>/dev/null || true)
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
        info "停止进程 $pid (来自 $(basename "$pidfile"))"
        kill "$pid" 2>/dev/null || true
        local i
        for i in 1 2 3 4 5; do
            sleep 1
            kill -0 "$pid" 2>/dev/null || break
        done
        kill -9 "$pid" 2>/dev/null || true
    fi
    rm -f "$pidfile"
}

# ---------------------------------------------------------------------------
# 后端：uv run python -m backend.main
# ---------------------------------------------------------------------------
start_backend() {
    cd "$ROOT_DIR"
    local log="$LOG_DIR/backend.log"
    local pidfile="$PID_DIR/backend.pid"

    info "启动后端 (端口 $BACKEND_PORT)，日志: $log"
    : > "$log"
    nohup uv run python -m backend.main >> "$log" 2>&1 &
    echo $! > "$pidfile"

    # 等待端口起来 (最多 15 秒)
    local i
    for i in $(seq 1 15); do
        if lsof -nP -iTCP:"$BACKEND_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
            info "后端就绪：http://localhost:$BACKEND_PORT (pid $(cat "$pidfile"))"
            return 0
        fi
        sleep 1
    done

    error "后端启动超时，查看 $log"
    return 1
}

stop_backend() {
    stop_by_pidfile "$PID_DIR/backend.pid"
    stop_by_port "$BACKEND_PORT"
}

# ---------------------------------------------------------------------------
# 前端：npm run dev (vite)
# ---------------------------------------------------------------------------
start_frontend() {
    if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
        warn "$FRONTEND_DIR/node_modules 不存在，先运行 npm install"
        (cd "$FRONTEND_DIR" && npm install)
    fi

    cd "$FRONTEND_DIR"
    local log="$LOG_DIR/frontend.log"
    local pidfile="$PID_DIR/frontend.pid"

    info "启动前端 (端口 $FRONTEND_PORT)，日志: $log"
    : > "$log"
    nohup npm run dev -- --port "$FRONTEND_PORT" >> "$log" 2>&1 &
    echo $! > "$pidfile"

    # 等待端口起来 (最多 30 秒，vite 首次启动稍慢)
    local i
    for i in $(seq 1 30); do
        if lsof -nP -iTCP:"$FRONTEND_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
            info "前端就绪：http://localhost:$FRONTEND_PORT (pid $(cat "$pidfile"))"
            return 0
        fi
        sleep 1
    done

    error "前端启动超时，查看 $log"
    return 1
}

stop_frontend() {
    stop_by_pidfile "$PID_DIR/frontend.pid"
    stop_by_port "$FRONTEND_PORT"
}

# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
TARGET="${1:-all}"

case "$TARGET" in
    backend)
        stop_backend
        start_backend
        ;;
    frontend)
        stop_frontend
        start_frontend
        ;;
    stop)
        stop_backend
        stop_frontend
        info "已停止前后端服务"
        ;;
    all|"")
        stop_backend
        stop_frontend
        start_backend
        start_frontend
        ;;
    *)
        error "未知参数: $TARGET"
        echo "用法: $0 [backend|frontend|all|stop]"
        exit 2
        ;;
esac

printf "\n%s完成%s — 查看日志: %stail -f %s/{backend,frontend}.log%s\n" \
    "$C_GREEN" "$C_RESET" "$C_DIM" "$LOG_DIR" "$C_RESET"
