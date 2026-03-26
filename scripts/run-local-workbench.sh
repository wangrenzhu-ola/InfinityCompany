#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib.sh"

ENV_FILE="$(resolve_env_file "${1:-}")"
ensure_local_env_file "${ENV_FILE}"
load_env_file "${ENV_FILE}"
ENV_FILE_IN_USE="${ENV_FILE}"

require_command python3
require_command curl
require_command docker
require_command openclaw

info "使用配置: ${ENV_FILE}"
"${SCRIPT_DIR}/validate-overlay.sh" "${ENV_FILE}" >/dev/null

ensure_gateway_running
ensure_clawpanel_running

TOKEN="$(get_gateway_token)"
[[ -n "${TOKEN}" ]] || fail "无法读取 gateway token"

DASHBOARD_URL="$(get_dashboard_url)"
CLAWPANEL_URL="$(clawpanel_url)"

print_access_summary "${DASHBOARD_URL}" "${CLAWPANEL_URL}" "${TOKEN}"
show_access_dialog "${DASHBOARD_URL}" "${CLAWPANEL_URL}" "${TOKEN}"
