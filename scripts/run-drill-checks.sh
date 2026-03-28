#!/usr/bin/env bash
#
# InfinityCompany 恢复能力演练检查脚本
# 用于验证演练前环境、演练中检查点和演练后状态
#
# 用法:
#   ./run-drill-checks.sh [mode] [config_file]
#
# 模式:
#   all      - 执行所有检查（默认）
#   env      - 检查环境变量和目录结构
#   service  - 检查服务可用性
#   integrity- 检查文件完整性
#   snapshot - 检查快照可用性
#   config   - 检查配置正确性
#   quick    - 快速检查关键检查点
#   pre      - 演练前检查（P-01 到 P-10）
#   post     - 演练后验证（V-01 到 V-08）

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFINITYCOMPANY_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# 默认配置
MODE="${1:-all}"
CONFIG_FILE="${2:-${INFINITYCOMPANY_ROOT}/configs/openclaw-target.local.env}"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 计数器
PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

# 打印带颜色的消息
print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASS_COUNT++))
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAIL_COUNT++))
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    ((WARN_COUNT++))
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# 加载配置文件
load_config() {
    if [[ ! -f "${CONFIG_FILE}" ]]; then
        print_fail "配置文件不存在: ${CONFIG_FILE}"
        return 1
    fi
    
    set -a
    source "${CONFIG_FILE}"
    set +a
    return 0
}

# 检查环境变量
check_env_variables() {
    print_info "检查环境变量..."
    
    local required_vars=(
        "OPENCLAW_BASE_DIR"
        "OPENCLAW_USER_HOME"
        "OPENCLAW_GATEWAY_URL"
        "CLAWPANEL_DIR"
        "OVERLAY_SOURCE_DIR"
        "RUNTIME_OVERLAY_DIR"
        "BACKUP_ROOT"
    )
    
    local missing=()
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            missing+=("${var}")
        fi
    done
    
    if [[ ${#missing[@]} -eq 0 ]]; then
        print_pass "所有必需环境变量已设置"
        return 0
    else
        print_fail "缺失环境变量: ${missing[*]}"
        return 1
    fi
}

# 检查目录结构
check_directory_structure() {
    print_info "检查目录结构..."
    
    local errors=0
    
    # 检查 OpenClaw 基座目录
    if [[ -d "${OPENCLAW_BASE_DIR}" ]]; then
        print_pass "OpenClaw 基座目录存在: ${OPENCLAW_BASE_DIR}"
    else
        print_fail "OpenClaw 基座目录不存在: ${OPENCLAW_BASE_DIR}"
        ((errors++))
    fi
    
    # 检查 ClawPanel 目录
    if [[ -d "${CLAWPANEL_DIR}" ]]; then
        print_pass "ClawPanel 目录存在: ${CLAWPANEL_DIR}"
    else
        print_fail "ClawPanel 目录不存在: ${CLAWPANEL_DIR}"
        ((errors++))
    fi
    
    # 检查 Overlay 源目录
    if [[ -d "${OVERLAY_SOURCE_DIR}" ]]; then
        print_pass "Overlay 源目录存在: ${OVERLAY_SOURCE_DIR}"
    else
        print_fail "Overlay 源目录不存在: ${OVERLAY_SOURCE_DIR}"
        ((errors++))
    fi
    
    # 检查快照目录可写
    if mkdir -p "${BACKUP_ROOT}" 2>/dev/null; then
        print_pass "快照目录可写: ${BACKUP_ROOT}"
    else
        print_fail "快照目录不可写: ${BACKUP_ROOT}"
        ((errors++))
    fi
    
    return ${errors}
}

# 检查依赖工具
check_dependencies() {
    print_info "检查依赖工具..."
    
    local errors=0
    
    # 检查 rsync
    if command -v rsync >/dev/null 2>&1; then
        print_pass "rsync 已安装"
    else
        print_fail "rsync 未安装"
        ((errors++))
    fi
    
    # 检查 curl
    if command -v curl >/dev/null 2>&1; then
        print_pass "curl 已安装"
    else
        print_fail "curl 未安装"
        ((errors++))
    fi
    
    # 检查 jq（可选）
    if command -v jq >/dev/null 2>&1; then
        print_pass "jq 已安装（可选）"
    else
        print_warn "jq 未安装（可选，用于 JSON 输出）"
    fi
    
    return ${errors}
}

# 检查脚本可执行性
check_scripts_executable() {
    print_info "检查脚本可执行性..."
    
    local errors=0
    local scripts=("validate-overlay.sh" "attach-openclaw.sh" "deploy-overlay.sh" "rollback-overlay.sh")
    
    for script in "${scripts[@]}"; do
        if [[ -x "${SCRIPT_DIR}/${script}" ]]; then
            print_pass "脚本可执行: ${script}"
        else
            print_fail "脚本不可执行: ${script}"
            ((errors++))
        fi
    done
    
    return ${errors}
}

# 检查服务可用性
check_service_availability() {
    print_info "检查服务可用性..."
    
    local errors=0
    
    # 检查 Gateway（添加超时参数）
    if curl -fsS --max-time 3 "${OPENCLAW_GATEWAY_URL}" >/dev/null 2>&1; then
        print_pass "Gateway 服务正常 (${OPENCLAW_GATEWAY_URL})"
    else
        print_fail "Gateway 服务异常 (${OPENCLAW_GATEWAY_URL})"
        ((errors++))
    fi
    
    # 检查 ClawPanel（添加超时参数）
    local clawpanel_url="${CLAWPANEL_URL:-http://127.0.0.1:1420/}"
    if curl -fsS --max-time 3 "${clawpanel_url}" >/dev/null 2>&1; then
        print_pass "ClawPanel 服务正常 (${clawpanel_url})"
    else
        print_fail "ClawPanel 服务异常 (${clawpanel_url})"
        ((errors++))
    fi
    
    return ${errors}
}

# 检查文件完整性
check_file_integrity() {
    print_info "检查文件完整性..."
    
    if [[ ! -d "${OVERLAY_SOURCE_DIR}" ]]; then
        print_fail "Overlay 源目录不存在"
        return 1
    fi
    
    if [[ ! -d "${RUNTIME_OVERLAY_DIR}" ]]; then
        print_warn "运行时目录不存在，可能是首次部署"
        return 0
    fi
    
    local missing_count=0
    local mismatch_count=0
    
    # 检查源目录所有文件是否都在目标目录
    while IFS= read -r -d '' src_file; do
        rel_path="${src_file#${OVERLAY_SOURCE_DIR}/}"
        dst_file="${RUNTIME_OVERLAY_DIR}/${rel_path}"
        
        if [[ ! -f "${dst_file}" ]]; then
            ((missing_count++))
        else
            # 比较文件内容（如果 md5sum 可用）
            if command -v md5sum >/dev/null 2>&1; then
                src_hash=$(md5sum "${src_file}" | awk '{print $1}')
                dst_hash=$(md5sum "${dst_file}" | awk '{print $1}')
                if [[ "${src_hash}" != "${dst_hash}" ]]; then
                    ((mismatch_count++))
                fi
            fi
        fi
    done < <(find "${OVERLAY_SOURCE_DIR}" -type f -print0 2>/dev/null)
    
    if [[ ${missing_count} -eq 0 && ${mismatch_count} -eq 0 ]]; then
        print_pass "文件完整性检查通过"
        return 0
    else
        if [[ ${missing_count} -gt 0 ]]; then
            print_fail "发现 ${missing_count} 个缺失文件"
        fi
        if [[ ${mismatch_count} -gt 0 ]]; then
            print_fail "发现 ${mismatch_count} 个文件内容不一致"
        fi
        return 1
    fi
}

# 检查快照可用性
check_snapshot_availability() {
    print_info "检查快照可用性..."
    
    local snapshot_count
    snapshot_count=$(find "${BACKUP_ROOT}" -name "attach-*" -type d 2>/dev/null | wc -l)
    
    if [[ ${snapshot_count} -gt 0 ]]; then
        print_pass "找到 ${snapshot_count} 个可用快照"
        
        # 显示最新快照
        local latest
        latest=$(ls -1td "${BACKUP_ROOT}"/attach-* 2>/dev/null | head -1)
        if [[ -n "${latest}" ]]; then
            print_info "最新快照: $(basename "${latest}")"
        fi
        return 0
    else
        print_warn "未找到任何快照（首次部署前为正常状态）"
        return 0
    fi
}

# 检查配置正确性
check_config_validation() {
    print_info "检查配置正确性..."
    
    if "${SCRIPT_DIR}/validate-overlay.sh" "${CONFIG_FILE}" >/dev/null 2>&1; then
        print_pass "配置验证通过"
        return 0
    else
        print_fail "配置验证失败"
        return 1
    fi
}

# 演练前检查（P-01 到 P-10）
run_pre_drill_checks() {
    print_info "============================================"
    print_info "        演练前准备检查 (Pre-Drill)"
    print_info "============================================"
    echo ""
    
    load_config || return 1
    
    check_dependencies
    check_scripts_executable
    check_env_variables
    check_directory_structure
    check_snapshot_availability
    
    echo ""
    print_summary
}

# 演练后验证（V-01 到 V-08）
run_post_drill_checks() {
    print_info "============================================"
    print_info "        演练后状态验证 (Post-Drill)"
    print_info "============================================"
    echo ""
    
    load_config || return 1
    
    check_service_availability
    check_file_integrity
    check_config_validation
    check_snapshot_availability
    
    # 检查部署元数据
    print_info "检查部署元数据..."
    if [[ -f "${RUNTIME_OVERLAY_DIR}/.release/last-deploy.txt" ]]; then
        local deploy_time
        deploy_time=$(cat "${RUNTIME_OVERLAY_DIR}/.release/last-deploy.txt")
        print_pass "部署记录存在: ${deploy_time}"
    else
        print_warn "未找到部署记录"
    fi
    
    # 检查演练日志
    print_info "检查演练日志..."
    local latest_log
    latest_log=$(ls -1t "${BACKUP_ROOT}"/drill-*/drill-log.txt 2>/dev/null | head -1)
    if [[ -n "${latest_log}" ]]; then
        print_pass "演练日志存在: ${latest_log}"
    else
        print_warn "未找到演练日志"
    fi
    
    echo ""
    print_summary
}

# 快速检查所有关键检查点
run_quick_checks() {
    print_info "============================================"
    print_info "          快速检查 (Quick Check)"
    print_info "============================================"
    echo ""
    
    load_config || return 1
    
    # 关键检查点
    check_env_variables
    check_directory_structure
    check_service_availability
    check_file_integrity
    check_snapshot_availability
    
    echo ""
    print_summary
}

# 打印汇总
print_summary() {
    print_info "============================================"
    print_info "              检查汇总"
    print_info "============================================"
    echo -e "  ${GREEN}通过: ${PASS_COUNT}${NC}"
    echo -e "  ${RED}失败: ${FAIL_COUNT}${NC}"
    echo -e "  ${YELLOW}警告: ${WARN_COUNT}${NC}"
    print_info "============================================"
    
    if [[ ${FAIL_COUNT} -eq 0 ]]; then
        print_pass "所有检查通过！"
        return 0
    else
        print_fail "存在 ${FAIL_COUNT} 个失败的检查项"
        return 1
    fi
}

# 主函数
main() {
    echo ""
    print_info "InfinityCompany 恢复能力演练检查脚本"
    print_info "模式: ${MODE}"
    print_info "配置: ${CONFIG_FILE}"
    echo ""
    
    case "${MODE}" in
        env)
            load_config && check_env_variables && check_directory_structure
            ;;
        service)
            load_config && check_service_availability
            ;;
        integrity)
            load_config && check_file_integrity
            ;;
        snapshot)
            load_config && check_snapshot_availability
            ;;
        config)
            load_config && check_config_validation
            ;;
        quick)
            run_quick_checks
            ;;
        pre)
            run_pre_drill_checks
            ;;
        post)
            run_post_drill_checks
            ;;
        all)
            print_info "============================================"
            print_info "      执行完整检查 (Full Check)"
            print_info "============================================"
            echo ""
            load_config || exit 1
            check_dependencies
            check_scripts_executable
            check_env_variables
            check_directory_structure
            check_config_validation
            check_service_availability
            check_file_integrity
            check_snapshot_availability
            echo ""
            print_summary
            ;;
        help|--help|-h)
            echo "用法: $0 [mode] [config_file]"
            echo ""
            echo "模式:"
            echo "  all      - 执行所有检查（默认）"
            echo "  env      - 检查环境变量和目录结构"
            echo "  service  - 检查服务可用性"
            echo "  integrity- 检查文件完整性"
            echo "  snapshot - 检查快照可用性"
            echo "  config   - 检查配置正确性"
            echo "  quick    - 快速检查关键检查点"
            echo "  pre      - 演练前检查"
            echo "  post     - 演练后验证"
            echo "  help     - 显示此帮助信息"
            echo ""
            echo "示例:"
            echo "  $0                                    # 执行所有检查"
            echo "  $0 quick                              # 快速检查"
            echo "  $0 pre                                # 演练前检查"
            echo "  $0 post                               # 演练后验证"
            echo "  $0 service                            # 只检查服务"
            echo "  $0 all configs/my-config.env          # 使用指定配置"
            exit 0
            ;;
        *)
            print_fail "未知模式: ${MODE}"
            echo "使用 '$0 help' 查看可用模式"
            exit 1
            ;;
    esac
}

main "$@"
