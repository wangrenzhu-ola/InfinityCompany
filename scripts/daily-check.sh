#!/usr/bin/env bash
#
# daily-check.sh - InfinityCompany 每日运维检查脚本
# 由周勃（运维工程师）每日 18:00 执行
#
# 用法: ./scripts/daily-check.sh [env-file] [--report-only]
#   env-file: 环境配置文件路径 (默认: configs/openclaw-target.local.env)
#   --report-only: 仅生成报告，不执行修复操作
#

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="configs/openclaw-target.local.env"
REPORT_ONLY=false
ENV_FILE_SET=""

# 解析参数
for arg in "$@"; do
  if [[ "$arg" == "--report-only" ]]; then
    REPORT_ONLY=true
  elif [[ "$arg" != --* && -z "${ENV_FILE_SET:-}" ]]; then
    ENV_FILE="$arg"
    ENV_FILE_SET=1
  fi
done

# 报告文件
REPORT_DIR="${REPO_DIR}/logs"
mkdir -p "$REPORT_DIR"
REPORT_FILE="${REPORT_DIR}/daily-check-$(date +"%Y%m%d-%H%M%S").log"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 计数器
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNINGS=0

# 日志函数
log_info() {
  echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$REPORT_FILE"
}

log_ok() {
  echo -e "${GREEN}[PASS]${NC} $1" | tee -a "$REPORT_FILE"
  ((CHECKS_PASSED++))
}

log_error() {
  echo -e "${RED}[FAIL]${NC} $1" | tee -a "$REPORT_FILE"
  ((CHECKS_FAILED++))
}

log_warn() {
  echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$REPORT_FILE"
  ((CHECKS_WARNINGS++))
}

# 初始化报告
init_report() {
  cat > "$REPORT_FILE" << EOF
================================================================================
InfinityCompany 每日运维检查报告
================================================================================
检查时间: $(date '+%Y-%m-%d %H:%M:%S')
检查人员: 周勃 (运维工程师)
配置文件: ${ENV_FILE}
报告文件: ${REPORT_FILE}
================================================================================

EOF
}

# 生成报告摘要
generate_summary() {
  cat >> "$REPORT_FILE" << EOF

================================================================================
检查摘要
================================================================================
通过项:  ${CHECKS_PASSED}
失败项:  ${CHECKS_FAILED}
警告项:  ${CHECKS_WARNINGS}
================================================================================
状态: $([ $CHECKS_FAILED -eq 0 ] && echo "✓ 检查通过" || echo "✗ 存在失败项，需要处理")
================================================================================
EOF

  echo ""
  echo "================================================================================"
  echo "检查报告已保存: $REPORT_FILE"
  echo "================================================================================"
}

# ==================== 检查项 ====================

# 1. 环境配置检查
check_env_config() {
  log_info "【1/8】环境配置检查"
  echo "" >> "$REPORT_FILE"
  
  # 1.1 配置文件存在性
  if [[ -f "${REPO_DIR}/${ENV_FILE}" ]]; then
    log_ok "配置文件存在: ${ENV_FILE}"
  else
    log_error "配置文件不存在: ${ENV_FILE}"
    return 1
  fi
  
  # 1.2 配置验证
  if "${SCRIPT_DIR}/validate-overlay.sh" "${REPO_DIR}/${ENV_FILE}" >/dev/null 2>&1; then
    log_ok "配置验证通过"
  else
    log_error "配置验证失败"
    echo "    修复命令: ./scripts/validate-overlay.sh ${ENV_FILE}" >> "$REPORT_FILE"
  fi
  
  # 加载配置
  set -a
  source "${REPO_DIR}/${ENV_FILE}"
  set +a
}

# 2. 服务健康检查
check_service_health() {
  log_info "【2/8】服务健康检查"
  echo "" >> "$REPORT_FILE"
  
  # 2.1 Gateway 健康检查
  if curl -fsS "${OPENCLAW_GATEWAY_URL}/health" >/dev/null 2>&1; then
    log_ok "Gateway 服务健康: ${OPENCLAW_GATEWAY_URL}"
  else
    log_error "Gateway 服务异常: ${OPENCLAW_GATEWAY_URL}"
    echo "    检查命令: curl -fsS ${OPENCLAW_GATEWAY_URL}/health" >> "$REPORT_FILE"
    echo "    修复命令: openclaw gateway restart" >> "$REPORT_FILE"
  fi
  
  # 2.2 ClawPanel 健康检查
  if curl -fsS "${CLAWPANEL_URL}" >/dev/null 2>&1; then
    log_ok "ClawPanel 服务健康: ${CLAWPANEL_URL}"
  else
    log_error "ClawPanel 服务异常: ${CLAWPANEL_URL}"
    echo "    检查命令: curl -fsS ${CLAWPANEL_URL}" >> "$REPORT_FILE"
    echo "    修复命令: (cd ${CLAWPANEL_DIR} && docker compose up -d)" >> "$REPORT_FILE"
  fi
}

# 3. 运行时目录检查
check_runtime_dir() {
  log_info "【3/8】运行时目录检查"
  echo "" >> "$REPORT_FILE"
  
  # 3.1 运行时目录存在性
  if [[ -d "${RUNTIME_OVERLAY_DIR}" ]]; then
    log_ok "运行时目录存在: ${RUNTIME_OVERLAY_DIR}"
  else
    log_error "运行时目录不存在: ${RUNTIME_OVERLAY_DIR}"
    echo "    修复命令: ./scripts/deploy-overlay.sh ${ENV_FILE}" >> "$REPORT_FILE"
    return 1
  fi
  
  # 3.2 部署标记检查
  if [[ -f "${RUNTIME_OVERLAY_DIR}/.release/last-deploy.txt" ]]; then
    local last_deploy
    last_deploy=$(cat "${RUNTIME_OVERLAY_DIR}/.release/last-deploy.txt")
    log_ok "部署标记存在，最后部署: ${last_deploy}"
  else
    log_warn "部署标记不存在，可能未执行过正式部署"
    echo "    修复命令: ./scripts/deploy-overlay.sh ${ENV_FILE}" >> "$REPORT_FILE"
  fi
  
  # 3.3 目录内容检查
  local file_count
  file_count=$(find "${RUNTIME_OVERLAY_DIR}" -type f 2>/dev/null | wc -l)
  if [[ $file_count -gt 0 ]]; then
    log_ok "运行时目录包含 ${file_count} 个文件"
  else
    log_warn "运行时目录为空"
  fi
}

# 4. 快照数量检查
check_snapshots() {
  log_info "【4/8】快照数量检查"
  echo "" >> "$REPORT_FILE"
  
  # 4.1 快照目录存在性
  if [[ -d "${BACKUP_ROOT}" ]]; then
    log_ok "快照目录存在: ${BACKUP_ROOT}"
  else
    log_warn "快照目录不存在: ${BACKUP_ROOT}"
    mkdir -p "${BACKUP_ROOT}"
    log_info "已创建快照目录"
  fi
  
  # 4.2 快照数量统计
  local snapshot_count
  snapshot_count=$(find "${BACKUP_ROOT}" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l)
  
  if [[ $snapshot_count -eq 0 ]]; then
    log_warn "警告: 无可用回滚快照"
    echo "    建议执行: ./scripts/attach-openclaw.sh ${ENV_FILE} 创建初始快照" >> "$REPORT_FILE"
  elif [[ $snapshot_count -lt 3 ]]; then
    log_warn "快照数量较少: ${snapshot_count} 个 (建议至少保留 3 个)"
  else
    log_ok "可用快照数量: ${snapshot_count} 个"
  fi
  
  # 4.3 显示最近快照
  echo "" >> "$REPORT_FILE"
  echo "最近 3 个快照:" >> "$REPORT_FILE"
  find "${BACKUP_ROOT}" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort | tail -n 3 | while read -r snapshot; do
    echo "    - $(basename "$snapshot")" >> "$REPORT_FILE"
  done
}

# 5. Git 工作区检查
check_git_status() {
  log_info "【5/8】Git 工作区检查"
  echo "" >> "$REPORT_FILE"
  
  # 5.1 检查 overlay/ 目录变更
  local overlay_changes
  overlay_changes=$(git -C "${REPO_DIR}" status --porcelain overlay/ 2>/dev/null | wc -l)
  
  if [[ $overlay_changes -eq 0 ]]; then
    log_ok "overlay/ 目录无未提交变更"
  else
    log_warn "overlay/ 目录有 ${overlay_changes} 个未提交变更"
    echo "    查看变更: git -C ${REPO_DIR} status overlay/" >> "$REPORT_FILE"
    echo "    提交变更: git -C ${REPO_DIR} add overlay/ && git commit -m '...'" >> "$REPORT_FILE"
  fi
  
  # 5.2 检查是否有未推送的提交
  local unpushed_commits
  unpushed_commits=$(git -C "${REPO_DIR}" log --oneline @{u}.. 2>/dev/null | wc -l)
  if [[ $unpushed_commits -gt 0 ]]; then
    log_warn "有 ${unpushed_commits} 个未推送的提交"
    echo "    推送命令: git -C ${REPO_DIR} push" >> "$REPORT_FILE"
  else
    log_ok "所有提交已推送"
  fi
}

# 6. 磁盘空间检查
check_disk_space() {
  log_info "【6/8】磁盘空间检查"
  echo "" >> "$REPORT_FILE"
  
  # 6.1 检查快照目录磁盘使用
  local snapshot_size
  snapshot_size=$(du -sh "${BACKUP_ROOT}" 2>/dev/null | cut -f1)
  log_ok "快照目录大小: ${snapshot_size}"
  
  # 6.2 检查运行时目录磁盘使用
  local runtime_size
  runtime_size=$(du -sh "${RUNTIME_OVERLAY_DIR}" 2>/dev/null | cut -f1)
  log_ok "运行时目录大小: ${runtime_size}"
  
  # 6.3 检查磁盘可用空间
  local available_pct
  available_pct=$(df -h "${REPO_DIR}" | awk 'NR==2 {print $5}' | tr -d '%')
  local used_pct=$((100 - available_pct))
  
  if [[ $used_pct -gt 90 ]]; then
    log_error "磁盘使用率过高: ${used_pct}%"
    echo "    清理命令: find ${BACKUP_ROOT} -mindepth 1 -maxdepth 1 -type d -mtime +30 -exec rm -rf {} \;" >> "$REPORT_FILE"
  elif [[ $used_pct -gt 80 ]]; then
    log_warn "磁盘使用率较高: ${used_pct}%"
  else
    log_ok "磁盘使用率正常: ${used_pct}%"
  fi
}

# 7. Docker 状态检查
check_docker_status() {
  log_info "【7/8】Docker 状态检查"
  echo "" >> "$REPORT_FILE"
  
  # 7.1 Docker 服务状态
  if docker info >/dev/null 2>&1; then
    log_ok "Docker 服务运行中"
  else
    log_error "Docker 服务未运行"
    return 1
  fi
  
  # 7.2 ClawPanel 容器状态
  if docker ps --format "table {{.Names}}" | grep -q "clawpanel"; then
    log_ok "ClawPanel 容器运行中"
  else
    log_warn "ClawPanel 容器未运行"
    echo "    启动命令: (cd ${CLAWPANEL_DIR} && docker compose up -d)" >> "$REPORT_FILE"
  fi
}

# 8. 发布准备检查
check_release_readiness() {
  log_info "【8/8】发布准备检查"
  echo "" >> "$REPORT_FILE"
  
  local ready=true
  
  # 8.1 Gateway 健康
  if ! curl -fsS "${OPENCLAW_GATEWAY_URL}/health" >/dev/null 2>&1; then
    log_error "Gateway 未就绪，无法发布"
    ready=false
  fi
  
  # 8.2 ClawPanel 健康
  if ! curl -fsS "${CLAWPANEL_URL}" >/dev/null 2>&1; then
    log_error "ClawPanel 未就绪，无法发布"
    ready=false
  fi
  
  # 8.3 快照可用
  local snapshot_count
  snapshot_count=$(find "${BACKUP_ROOT}" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | wc -l)
  if [[ $snapshot_count -eq 0 ]]; then
    log_warn "无可用快照，建议先创建快照"
  fi
  
  if [[ "$ready" == true ]]; then
    log_ok "发布准备就绪"
    echo "" >> "$REPORT_FILE"
    echo "发布命令:" >> "$REPORT_FILE"
    echo "    ./scripts/deploy-overlay.sh ${ENV_FILE}" >> "$REPORT_FILE"
  else
    log_error "发布准备未完成，请修复上述问题"
  fi
}

# 清理旧快照（可选）
cleanup_old_snapshots() {
  log_info "【可选】清理超过 30 天的旧快照"
  
  local old_count
  old_count=$(find "${BACKUP_ROOT}" -mindepth 1 -maxdepth 1 -type d -mtime +30 2>/dev/null | wc -l)
  
  if [[ $old_count -gt 0 ]]; then
    if [[ "$REPORT_ONLY" == false ]]; then
      find "${BACKUP_ROOT}" -mindepth 1 -maxdepth 1 -type d -mtime +30 -exec rm -rf {} \; 2>/dev/null
      log_ok "已清理 ${old_count} 个超过 30 天的旧快照"
    else
      log_info "发现 ${old_count} 个超过 30 天的旧快照 (仅报告模式，未清理)"
    fi
  else
    log_ok "无超过 30 天的旧快照需要清理"
  fi
}

# ==================== 主流程 ====================

main() {
  # 切换到仓库目录
  cd "${REPO_DIR}"
  
  # 显示标题
  echo "================================================================================"
  echo "              InfinityCompany 每日运维检查"
  echo "================================================================================"
  echo "检查时间: $(date '+%Y-%m-%d %H:%M:%S')"
  echo "检查人员: 周勃 (运维工程师)"
  echo "配置文件: ${ENV_FILE}"
  [[ "$REPORT_ONLY" == true ]] && echo "模式: 仅报告 (不执行修复)"
  echo "================================================================================"
  echo ""
  
  # 初始化报告
  init_report
  
  # 执行检查
  check_env_config && {
    check_service_health
    check_runtime_dir
    check_snapshots
    check_git_status
    check_disk_space
    check_docker_status
    check_release_readiness
    cleanup_old_snapshots
  }
  
  # 生成报告摘要
  generate_summary
  
  # 返回状态
  if [[ $CHECKS_FAILED -eq 0 ]]; then
    echo -e "\n${GREEN}✓ 所有关键检查通过${NC}"
    exit 0
  else
    echo -e "\n${RED}✗ 存在 ${CHECKS_FAILED} 个失败项，请查看报告并处理${NC}"
    exit 1
  fi
}

# 执行主流程
main "$@"
