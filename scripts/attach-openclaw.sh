#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${1:-}"

if [[ -z "${ENV_FILE}" ]]; then
  echo "usage: $0 <env-file>" >&2
  exit 1
fi

"${SCRIPT_DIR}/validate-overlay.sh" "${ENV_FILE}" >/dev/null

set -a
source "${ENV_FILE}"
set +a

timestamp="$(date +"%Y%m%d-%H%M%S")"
snapshot_dir="${BACKUP_ROOT}/attach-${timestamp}"

mkdir -p "${BACKUP_ROOT}"
mkdir -p "${RUNTIME_OVERLAY_DIR}"
mkdir -p "${snapshot_dir}"

if [[ -n "$(find "${RUNTIME_OVERLAY_DIR}" -mindepth 1 -maxdepth 1 2>/dev/null)" ]]; then
  rsync -a "${RUNTIME_OVERLAY_DIR}/" "${snapshot_dir}/"
fi

echo "snapshot=${snapshot_dir}"

rsync -a --delete "${OVERLAY_SOURCE_DIR}/" "${RUNTIME_OVERLAY_DIR}/"

echo "attached_from=${OVERLAY_SOURCE_DIR}"
echo "attached_to=${RUNTIME_OVERLAY_DIR}"
