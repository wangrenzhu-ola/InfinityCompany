#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${1:-}"

if [[ -z "${ENV_FILE}" ]]; then
  echo "usage: $0 <env-file>" >&2
  exit 1
fi

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "env file not found: ${ENV_FILE}" >&2
  exit 1
fi

set -a
source "${ENV_FILE}"
set +a

required_vars=(
  OPENCLAW_BASE_DIR
  OPENCLAW_USER_HOME
  OPENCLAW_GATEWAY_URL
  CLAWPANEL_DIR
  OVERLAY_SOURCE_DIR
  RUNTIME_OVERLAY_DIR
  BACKUP_ROOT
)

for var_name in "${required_vars[@]}"; do
  if [[ -z "${!var_name:-}" ]]; then
    echo "missing required variable: ${var_name}" >&2
    exit 1
  fi
done

if [[ ! -d "${CLAWPANEL_DIR}" ]]; then
  echo "clawpanel dir not found: ${CLAWPANEL_DIR}" >&2
  exit 1
fi

if [[ ! -d "${OVERLAY_SOURCE_DIR}" ]]; then
  echo "overlay source dir not found: ${OVERLAY_SOURCE_DIR}" >&2
  exit 1
fi

mkdir -p "${BACKUP_ROOT}"

echo "env_file=${ENV_FILE}"
echo "openclaw_base_dir=${OPENCLAW_BASE_DIR}"
echo "openclaw_user_home=${OPENCLAW_USER_HOME}"
echo "openclaw_gateway_url=${OPENCLAW_GATEWAY_URL}"
echo "clawpanel_dir=${CLAWPANEL_DIR}"
echo "overlay_source_dir=${OVERLAY_SOURCE_DIR}"
echo "runtime_overlay_dir=${RUNTIME_OVERLAY_DIR}"
echo "backup_root=${BACKUP_ROOT}"
