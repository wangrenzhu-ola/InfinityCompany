#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${1:-}"
SNAPSHOT_DIR="${2:-}"

if [[ -z "${ENV_FILE}" ]]; then
  echo "usage: $0 <env-file> [snapshot-dir]" >&2
  exit 1
fi

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "env file not found: ${ENV_FILE}" >&2
  exit 1
fi

set -a
source "${ENV_FILE}"
set +a

mkdir -p "${BACKUP_ROOT}"
mkdir -p "${RUNTIME_OVERLAY_DIR}"

if [[ -z "${SNAPSHOT_DIR}" ]]; then
  SNAPSHOT_DIR="$(find "${BACKUP_ROOT}" -mindepth 1 -maxdepth 1 -type d | sort | tail -n 1)"
fi

if [[ -z "${SNAPSHOT_DIR}" || ! -d "${SNAPSHOT_DIR}" ]]; then
  echo "snapshot dir not found" >&2
  exit 1
fi

rsync -a --delete "${SNAPSHOT_DIR}/" "${RUNTIME_OVERLAY_DIR}/"

echo "rolled_back_from=${SNAPSHOT_DIR}"
echo "rolled_back_to=${RUNTIME_OVERLAY_DIR}"
