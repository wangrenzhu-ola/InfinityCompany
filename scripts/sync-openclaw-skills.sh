#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
SOURCE_BASE_DEFAULT="${ROOT_DIR}/skills"
TARGET_BASE_DEFAULT="${HOME}/.openclaw/workspace/skills"

MODE="sync"
DRY_RUN=0
SYNC_ALL=1
SOURCE_BASE="${SOURCE_BASE_DEFAULT}"
TARGET_BASE="${TARGET_BASE_DEFAULT}"
SKILLS=()

usage() {
  cat <<'EOF'
用法:
  sync-openclaw-skills.sh [--all] [--skill <name> ...] [--check] [--dry-run]
                          [--source-base <dir>] [--target-base <dir>]

参数:
  --all                 同步 source-base 下所有包含 SKILL.md 的技能目录（默认）
  --skill <name>        仅同步指定技能，可重复使用
  --check               只检查差异，不执行写入；有差异时返回非 0
  --dry-run             预演模式，显示将变更的内容
  --source-base <dir>   源技能目录，默认 InfinityCompany/skills
  --target-base <dir>   目标技能目录，默认 ~/.openclaw/workspace/skills
  -h, --help            显示帮助
EOF
}

info() {
  printf '[info] %s\n' "$*"
}

ok() {
  printf '[ok] %s\n' "$*"
}

err() {
  printf '[error] %s\n' "$*" >&2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all)
      SYNC_ALL=1
      shift
      ;;
    --skill)
      [[ $# -ge 2 ]] || { err "--skill 需要参数"; exit 2; }
      SKILLS+=("$2")
      SYNC_ALL=0
      shift 2
      ;;
    --check)
      MODE="check"
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --source-base)
      [[ $# -ge 2 ]] || { err "--source-base 需要参数"; exit 2; }
      SOURCE_BASE="$2"
      shift 2
      ;;
    --target-base)
      [[ $# -ge 2 ]] || { err "--target-base 需要参数"; exit 2; }
      TARGET_BASE="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      err "未知参数: $1"
      usage
      exit 2
      ;;
  esac
done

command -v rsync >/dev/null 2>&1 || { err "缺少命令: rsync"; exit 2; }
[[ -d "${SOURCE_BASE}" ]] || { err "源目录不存在: ${SOURCE_BASE}"; exit 2; }

if [[ ${SYNC_ALL} -eq 1 ]]; then
  while IFS= read -r -d '' skill_dir; do
    SKILLS+=("$(basename "${skill_dir}")")
  done < <(find "${SOURCE_BASE}" -mindepth 1 -maxdepth 1 -type d -print0 | sort -z)
fi

FILTERED_SKILLS=()
for skill in "${SKILLS[@]}"; do
  [[ -f "${SOURCE_BASE}/${skill}/SKILL.md" ]] || continue
  FILTERED_SKILLS+=("${skill}")
done
SKILLS=("${FILTERED_SKILLS[@]}")

[[ ${#SKILLS[@]} -gt 0 ]] || { err "未找到可同步技能（需包含 SKILL.md）"; exit 2; }

RSYNC_EXCLUDES=(
  --exclude=".venv/"
  --exclude="__pycache__/"
  --exclude=".pytest_cache/"
  --exclude="*.pyc"
  --exclude=".DS_Store"
)

mkdir -p "${TARGET_BASE}"

info "模式: ${MODE}"
info "源目录: ${SOURCE_BASE}"
info "目标目录: ${TARGET_BASE}"
info "技能: ${SKILLS[*]}"

DRIFT_COUNT=0

for skill in "${SKILLS[@]}"; do
  src="${SOURCE_BASE}/${skill}/"
  dst="${TARGET_BASE}/${skill}/"

  if [[ "${MODE}" == "sync" ]]; then
    mkdir -p "${dst}"
    RSYNC_FLAGS=(-a --delete "${RSYNC_EXCLUDES[@]}")
    [[ ${DRY_RUN} -eq 1 ]] && RSYNC_FLAGS=(-ani --delete "${RSYNC_EXCLUDES[@]}")
    output="$(rsync "${RSYNC_FLAGS[@]}" "${src}" "${dst}")"
    if [[ -n "${output}" ]]; then
      printf '%s\n' "${output}"
    fi
    if [[ ${DRY_RUN} -eq 1 ]]; then
      if [[ -n "${output}" ]]; then
        info "预演差异: ${skill}"
      else
        ok "预演无差异: ${skill}"
      fi
    else
      ok "已同步: ${skill}"
    fi
    continue
  fi

  check_output="$(rsync -ani --delete "${RSYNC_EXCLUDES[@]}" "${src}" "${dst}")"
  if [[ -n "${check_output}" ]]; then
    DRIFT_COUNT=$((DRIFT_COUNT + 1))
    err "发现漂移: ${skill}"
    printf '%s\n' "${check_output}" | head -n 40
  else
    ok "无漂移: ${skill}"
  fi
done

if [[ "${MODE}" == "check" ]]; then
  if [[ ${DRIFT_COUNT} -gt 0 ]]; then
    err "检查结束，存在 ${DRIFT_COUNT} 个技能漂移"
    exit 1
  fi
  ok "检查结束，所有技能一致"
  exit 0
fi

ok "同步完成"
