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

# SYNC AGENTS TO OPENCLAW
# This ensures that all 10 agents from InfinityCompany/agents/ are registered in OpenClaw's user home.
AGENTS_SRC_DIR="/Users/wangrenzhu/work/MetaClaw/InfinityCompany/agents"
AGENTS_DST_DIR="${OPENCLAW_USER_HOME}/agents"

echo "Syncing agents from ${AGENTS_SRC_DIR} to ${AGENTS_DST_DIR}..."
mkdir -p "${AGENTS_DST_DIR}"

for agent_dir in "${AGENTS_SRC_DIR}"/*; do
  if [[ -d "$agent_dir" ]]; then
    agent_name=$(basename "$agent_dir")
    
    # We need to map the agent name to the correct directory structure expected by OpenClaw
    # OpenClaw expects: ~/.openclaw/agents/<agent_name>/agent/
    target_agent_dir="${AGENTS_DST_DIR}/${agent_name}/agent"
    mkdir -p "${target_agent_dir}"
    
    # Copy all markdown files (IDENTITY.md, TOOLS.md, etc.)
    cp "${agent_dir}"/*.md "${target_agent_dir}/" 2>/dev/null || true
    echo "  Synced ${agent_name}"
  fi
done

# If main agent is caocan, we should also copy caocan's files to main
echo "Syncing caocan to main agent..."
mkdir -p "${AGENTS_DST_DIR}/main/agent"
cp "${AGENTS_SRC_DIR}/caocan"/*.md "${AGENTS_DST_DIR}/main/agent/" 2>/dev/null || true

release_dir="${RUNTIME_OVERLAY_DIR}/.release"
mkdir -p "${release_dir}"

printf '%s\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" > "${release_dir}/last-deploy.txt"
printf '%s\n' "${OPENCLAW_GATEWAY_URL}" > "${release_dir}/gateway-url.txt"

echo "deployed_overlay=${RUNTIME_OVERLAY_DIR}"
echo "gateway_url=${OPENCLAW_GATEWAY_URL}"
