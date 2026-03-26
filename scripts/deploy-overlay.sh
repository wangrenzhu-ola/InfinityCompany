#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${1:-}"

if [[ -z "${ENV_FILE}" ]]; then
  echo "usage: $0 <env-file>" >&2
  exit 1
fi

"${SCRIPT_DIR}/validate-overlay.sh" "${ENV_FILE}" >/dev/null
"${SCRIPT_DIR}/attach-openclaw.sh" "${ENV_FILE}" >/dev/null

set -a
source "${ENV_FILE}"
set +a

release_dir="${RUNTIME_OVERLAY_DIR}/.release"
mkdir -p "${release_dir}"

printf '%s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" > "${release_dir}/last-deploy.txt"
printf '%s\n' "${OPENCLAW_GATEWAY_URL}" > "${release_dir}/gateway-url.txt"

echo "deployed_overlay=${RUNTIME_OVERLAY_DIR}"
echo "gateway_url=${OPENCLAW_GATEWAY_URL}"
