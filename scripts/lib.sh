#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
DEFAULT_ENV_FILE="${ROOT_DIR}/configs/openclaw-target.local.env"
EXAMPLE_ENV_FILE="${ROOT_DIR}/configs/openclaw-target.example.env"

info() {
  printf '[info] %s\n' "$*"
}

warn() {
  printf '[warn] %s\n' "$*" >&2
}

success() {
  printf '[ok] %s\n' "$*"
}

fail() {
  printf '[error] %s\n' "$*" >&2
  exit 1
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "缺少命令: $1"
}

resolve_env_file() {
  if [[ -n "${1:-}" ]]; then
    printf '%s\n' "$1"
    return 0
  fi

  if [[ -f "${DEFAULT_ENV_FILE}" ]]; then
    printf '%s\n' "${DEFAULT_ENV_FILE}"
    return 0
  fi

  printf '%s\n' "${DEFAULT_ENV_FILE}"
}

ensure_local_env_file() {
  local env_file="$1"

  if [[ -f "${env_file}" ]]; then
    return 0
  fi

  [[ -f "${EXAMPLE_ENV_FILE}" ]] || fail "缺少示例配置: ${EXAMPLE_ENV_FILE}"
  cp "${EXAMPLE_ENV_FILE}" "${env_file}"
  success "已生成本地配置: ${env_file}"
}

load_env_file() {
  local env_file="$1"
  [[ -f "${env_file}" ]] || fail "配置文件不存在: ${env_file}"

  set -a
  source "${env_file}"
  set +a

  local required_vars=(
    OPENCLAW_BASE_DIR
    OPENCLAW_USER_HOME
    OPENCLAW_GATEWAY_URL
    CLAWPANEL_DIR
    OVERLAY_SOURCE_DIR
    RUNTIME_OVERLAY_DIR
    BACKUP_ROOT
  )

  local var_name
  for var_name in "${required_vars[@]}"; do
    [[ -n "${!var_name:-}" ]] || fail "配置缺失: ${var_name}"
  done
}

gateway_port_from_url() {
  python3 - "$1" <<'PY'
import sys
from urllib.parse import urlparse

url = sys.argv[1]
parsed = urlparse(url)
if parsed.port:
    print(parsed.port)
elif parsed.scheme == "https":
    print(443)
else:
    print(80)
PY
}

clawpanel_url() {
  printf '%s\n' "${CLAWPANEL_URL:-http://127.0.0.1:1420/}"
}

wait_for_http() {
  local url="$1"
  local timeout_seconds="${2:-60}"
  local waited=0

  while (( waited < timeout_seconds )); do
    if curl -fsS "${url}" >/dev/null 2>&1; then
      return 0
    fi
    sleep 2
    waited=$((waited + 2))
  done

  return 1
}

run_command_with_timeout() {
  local timeout_seconds="$1"
  shift

  python3 - "${timeout_seconds}" "$@" <<'PY'
import subprocess
import sys

timeout = int(sys.argv[1])
command = sys.argv[2:]

try:
    result = subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=timeout,
        check=False,
    )
except subprocess.TimeoutExpired:
    raise SystemExit(124)

raise SystemExit(result.returncode)
PY
}

gateway_port_ready() {
  python3 - "${OPENCLAW_GATEWAY_URL}" <<'PY'
import socket
import sys
from urllib.parse import urlparse

parsed = urlparse(sys.argv[1])
host = parsed.hostname or "127.0.0.1"
port = parsed.port or (443 if parsed.scheme == "https" else 80)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(2)
try:
    sock.connect((host, port))
except OSError:
    raise SystemExit(1)
finally:
    sock.close()
PY
}

get_gateway_token() {
  python3 - "${OPENCLAW_USER_HOME}/openclaw.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
if not path.exists():
    raise SystemExit(1)

data = json.loads(path.read_text())
token = (
    data.get("gateway", {})
    .get("auth", {})
    .get("token", "")
)
if token:
    print(token)
PY
}

get_dashboard_url() {
  local dashboard_url
  dashboard_url="$(openclaw dashboard --no-open 2>/dev/null | awk -F': ' '/Dashboard URL:/ {print $2}' | tail -n 1 || true)"

  if [[ -n "${dashboard_url}" ]]; then
    printf '%s\n' "${dashboard_url}"
    return 0
  fi

  local token
  token="$(get_gateway_token)"
  [[ -n "${token}" ]] || fail "无法读取 gateway token"
  printf '%s/#token=%s\n' "${OPENCLAW_GATEWAY_URL%/}" "${token}"
}

ensure_gateway_running() {
  info "检查 OpenClaw Gateway"

  if gateway_port_ready; then
    success "OpenClaw Gateway 已可用"
    return 0
  fi

  local quick_retry=0
  while (( quick_retry < 3 )); do
    sleep 2
    if gateway_port_ready; then
      success "OpenClaw Gateway 已可用"
      return 0
    fi
    quick_retry=$((quick_retry + 1))
  done

  local port
  port="$(gateway_port_from_url "${OPENCLAW_GATEWAY_URL}")"

  warn "OpenClaw Gateway 未就绪，尝试拉起"

  if ! run_command_with_timeout 20 openclaw gateway start; then
    warn "Gateway service 未安装，尝试重新安装"
    run_command_with_timeout 40 openclaw gateway install --force --port "${port}" || true
    run_command_with_timeout 20 openclaw gateway start || true
  fi

  local waited=0
  while (( waited < 60 )); do
    if gateway_port_ready; then
      success "OpenClaw Gateway 已启动"
      return 0
    fi
    sleep 2
    waited=$((waited + 2))
  done

  fail "OpenClaw Gateway 启动失败"
}

ensure_clawpanel_running() {
  local url
  url="$(clawpanel_url)"

  info "检查 ClawPanel"

  if wait_for_http "${url}" 4; then
    success "ClawPanel 已可用"
    return 0
  fi

  warn "ClawPanel 未就绪，尝试重建并启动"
  (
    cd "${CLAWPANEL_DIR}"
    docker compose up -d --build
  )

  wait_for_http "${url}" 90 || fail "ClawPanel 启动失败: ${url}"
  success "ClawPanel 已启动"
}

copy_to_clipboard() {
  local value="$1"

  if command -v pbcopy >/dev/null 2>&1; then
    printf '%s' "${value}" | pbcopy
  fi
}

print_access_summary() {
  local dashboard_url="$1"
  local clawpanel_url="$2"
  local token="$3"

  printf '\n'
  printf 'InfinityCompany 已就绪\n'
  printf 'ClawPanel: %s\n' "${clawpanel_url}"
  printf 'Gateway:   %s\n' "${OPENCLAW_GATEWAY_URL}"
  printf 'Dashboard: %s\n' "${dashboard_url}"
  printf 'Token:     %s\n' "${token}"
  printf '配置:      %s\n' "${ENV_FILE_IN_USE:-未记录}"
  printf '\n'
}

show_access_dialog() {
  local dashboard_url="$1"
  local clawpanel_url="$2"
  local token="$3"

  copy_to_clipboard "${token}"

  if [[ "${INFINITYCOMPANY_NO_DIALOG:-0}" == "1" ]]; then
    return 0
  fi

  if ! command -v osascript >/dev/null 2>&1; then
    return 0
  fi

  local choice
  choice="$(osascript - "${clawpanel_url}" "${dashboard_url}" "${token}" <<'APPLESCRIPT'
on run argv
  set clawpanelUrl to item 1 of argv
  set dashboardUrl to item 2 of argv
  set gatewayToken to item 3 of argv
  set messageText to "ClawPanel: " & clawpanelUrl & return & return & "Gateway Dashboard: " & dashboardUrl & return & return & "Token 已复制到剪贴板：" & return & gatewayToken
  set dialogResult to display dialog messageText buttons {"关闭", "打开网关", "打开 ClawPanel"} default button "打开 ClawPanel" with title "InfinityCompany 已就绪"
  return button returned of dialogResult
end run
APPLESCRIPT
)"

  case "${choice}" in
    "打开 ClawPanel")
      open "${clawpanel_url}" >/dev/null 2>&1 || true
      ;;
    "打开网关")
      open "${dashboard_url}" >/dev/null 2>&1 || true
      ;;
  esac
}
