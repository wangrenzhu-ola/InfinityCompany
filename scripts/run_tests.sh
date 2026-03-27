#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# InfinityCompany 阶段 6 测试执行脚本
# 覆盖 validation_cases.md 中定义的核心测试用例
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
DEFAULT_ENV_FILE="${ROOT_DIR}/configs/openclaw-target.local.env"
EXAMPLE_ENV_FILE="${ROOT_DIR}/configs/openclaw-target.example.env"

# 支持通过环境变量配置，默认使用 local.env
ENV_FILE="${ENV_FILE:-${DEFAULT_ENV_FILE}}"

# 角色列表
ROLES=(zhangliang xiaohe hanxin chenping zhoubo caocan lishiyi lujia shusuntong xiahouying)

# 测试统计
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0
TOTAL_START_TIME=0

# ============================================================
# 工具函数
# ============================================================

log_info() {
  printf '%s\n' "$*"
}

log_error() {
  printf '%s\n' "$*" >&2
}

# 检查命令是否存在
check_command() {
  command -v "$1" >/dev/null 2>&1
}

# 获取当前时间（秒）
get_time() {
  date +%s.%N
}

# 计算耗时（秒）
calc_duration() {
  local start="$1"
  local end
  end=$(get_time)
  printf '%.1f' "$(echo "${end} - ${start}" | bc)"
}

# 打印测试用例结果
print_test_result() {
  local test_id="$1"
  local test_name="$2"
  local result="$3"
  local duration="$4"
  
  local icon
  case "${result}" in
    PASS)  icon="✓"; ;;
    FAIL)  icon="✗"; ;;
    SKIP)  icon="⊘"; ;;
    *)     icon="?"; ;;
  esac
  
  printf '  %s %-12s %-30s %-6s (%ss)\n' "${icon}" "${test_id}" "${test_name}" "${result}" "${duration}"
}

# 打印分隔线
print_line() {
  printf '%s\n' "───────────────────────────────────────────────────────────────"
}

# 打印双分隔线
print_double_line() {
  printf '%s\n' "═══════════════════════════════════════════════════════════════"
}

# 执行单个测试用例
run_test() {
  local test_id="$1"
  local test_name="$2"
  local test_func="$3"
  
  TOTAL_TESTS=$((TOTAL_TESTS + 1))
  local start_time result duration
  start_time=$(get_time)
  
  if "${test_func}"; then
    result="PASS"
    PASSED_TESTS=$((PASSED_TESTS + 1))
  else
    result="FAIL"
    FAILED_TESTS=$((FAILED_TESTS + 1))
  fi
  
  duration=$(calc_duration "${start_time}")
  print_test_result "${test_id}" "${test_name}" "${result}" "${duration}"
  
  [[ "${result}" == "PASS" ]]
}

# ============================================================
# 测试用例实现
# ============================================================

# TC-ENV-001: 环境变量文件存在性检查
test_env_001() {
  # 检查 example.env 存在
  if [[ ! -f "${EXAMPLE_ENV_FILE}" ]]; then
    log_error "ERROR: ${EXAMPLE_ENV_FILE} 不存在"
    return 1
  fi
  
  # 如果 local.env 不存在，自动从 example.env 复制
  if [[ ! -f "${ENV_FILE}" ]]; then
    if [[ -f "${EXAMPLE_ENV_FILE}" ]]; then
      cp "${EXAMPLE_ENV_FILE}" "${ENV_FILE}"
      log_info "[info] 已从 example.env 创建 ${ENV_FILE}"
    else
      log_error "ERROR: 无法创建 ${ENV_FILE}，缺少 ${EXAMPLE_ENV_FILE}"
      return 1
    fi
  fi
  
  return 0
}

# TC-ENV-002: 必需环境变量完整性验证
test_env_002() {
  local required_vars=(
    OPENCLAW_BASE_DIR
    OPENCLAW_USER_HOME
    OPENCLAW_GATEWAY_URL
    CLAWPANEL_DIR
    OVERLAY_SOURCE_DIR
    RUNTIME_OVERLAY_DIR
    BACKUP_ROOT
  )
  
  # 加载环境变量
  set -a
  # shellcheck source=/dev/null
  source "${ENV_FILE}"
  set +a
  
  local var_name
  for var_name in "${required_vars[@]}"; do
    if [[ -z "${!var_name:-}" ]]; then
      log_error "ERROR: 缺少必需环境变量: ${var_name}"
      return 1
    fi
  done
  
  return 0
}

# TC-ENV-003: 目录结构存在性验证
test_env_003() {
  # 加载环境变量
  set -a
  # shellcheck source=/dev/null
  source "${ENV_FILE}"
  set +a
  
  local dirs=(
    "${CLAWPANEL_DIR}"
    "${OVERLAY_SOURCE_DIR}"
  )
  
  local dir
  for dir in "${dirs[@]}"; do
    if [[ ! -d "${dir}" ]]; then
      log_error "ERROR: 目录不存在: ${dir}"
      return 1
    fi
  done
  
  return 0
}

# TC-ENV-004: 环境变量输出格式验证
test_env_004() {
  local output
  
  if ! output=$("${SCRIPT_DIR}/validate-overlay.sh" "${ENV_FILE}" 2>&1); then
    log_error "ERROR: validate-overlay.sh 执行失败"
    return 1
  fi
  
  # 验证输出包含预期的键值对格式
  local expected_keys=(
    "env_file="
    "openclaw_base_dir="
    "openclaw_user_home="
    "openclaw_gateway_url="
    "clawpanel_dir="
    "overlay_source_dir="
    "runtime_overlay_dir="
    "backup_root="
  )
  
  local key
  for key in "${expected_keys[@]}"; do
    if ! echo "${output}" | grep -q "^${key}"; then
      log_error "ERROR: 输出缺少键: ${key}"
      return 1
    fi
  done
  
  return 0
}

# TC-ATT-001: 基础 Attach 流程验证
test_att_001() {
  # 加载环境变量
  set -a
  # shellcheck source=/dev/null
  source "${ENV_FILE}"
  set +a
  
  local output
  if ! output=$("${SCRIPT_DIR}/attach-openclaw.sh" "${ENV_FILE}" 2>&1); then
    log_error "ERROR: attach-openclaw.sh 执行失败"
    return 1
  fi
  
  # 验证输出包含 snapshot 和 attached 信息
  if ! echo "${output}" | grep -q "^snapshot="; then
    log_error "ERROR: attach 输出缺少 snapshot 信息"
    return 1
  fi
  
  if ! echo "${output}" | grep -q "^attached_from="; then
    log_error "ERROR: attach 输出缺少 attached_from 信息"
    return 1
  fi
  
  if ! echo "${output}" | grep -q "^attached_to="; then
    log_error "ERROR: attach 输出缺少 attached_to 信息"
    return 1
  fi
  
  # 验证文件同步 - 检查关键文件是否已同步到运行时目录
  if [[ ! -d "${RUNTIME_OVERLAY_DIR}" ]]; then
    log_error "ERROR: 运行时覆盖目录不存在: ${RUNTIME_OVERLAY_DIR}"
    return 1
  fi
  
  # 检查源目录中的文件是否已同步（如果源目录非空）
  if [[ -n "$(find "${OVERLAY_SOURCE_DIR}" -mindepth 1 -maxdepth 1 2>/dev/null)" ]]; then
    # 源目录非空，验证文件已同步
    if [[ -z "$(find "${RUNTIME_OVERLAY_DIR}" -mindepth 1 -maxdepth 1 2>/dev/null)" ]]; then
      log_error "ERROR: 文件未正确同步到运行时目录"
      return 1
    fi
  fi
  
  return 0
}

# TC-DEP-001: 完整 Deploy 流程验证
test_dep_001() {
  # 加载环境变量
  set -a
  # shellcheck source=/dev/null
  source "${ENV_FILE}"
  set +a
  
  local output
  if ! output=$("${SCRIPT_DIR}/deploy-overlay.sh" "${ENV_FILE}" 2>&1); then
    log_error "ERROR: deploy-overlay.sh 执行失败"
    return 1
  fi
  
  # 验证输出包含部署信息
  if ! echo "${output}" | grep -q "^deployed_overlay="; then
    log_error "ERROR: deploy 输出缺少 deployed_overlay 信息"
    return 1
  fi
  
  if ! echo "${output}" | grep -q "^gateway_url="; then
    log_error "ERROR: deploy 输出缺少 gateway_url 信息"
    return 1
  fi
  
  # 验证 .release 目录和部署标记文件
  local release_dir="${RUNTIME_OVERLAY_DIR}/.release"
  if [[ ! -d "${release_dir}" ]]; then
    log_error "ERROR: release 目录不存在: ${release_dir}"
    return 1
  fi
  
  if [[ ! -f "${release_dir}/last-deploy.txt" ]]; then
    log_error "ERROR: last-deploy.txt 不存在"
    return 1
  fi
  
  if [[ ! -f "${release_dir}/gateway-url.txt" ]]; then
    log_error "ERROR: gateway-url.txt 不存在"
    return 1
  fi
  
  return 0
}

# TC-ROL-005: 角色 IDENTITY 文件存在性验证
test_rol_005() {
  local role
  for role in "${ROLES[@]}"; do
    local identity_file="${ROOT_DIR}/agents/${role}/IDENTITY.md"
    if [[ ! -f "${identity_file}" ]]; then
      log_error "ERROR: IDENTITY.md 不存在: ${identity_file}"
      return 1
    fi
  done
  
  return 0
}

# TC-ROL-006: 角色 IDENTITY 文件格式验证（YAML Frontmatter）
test_rol_006() {
  local role
  for role in "${ROLES[@]}"; do
    local identity_file="${ROOT_DIR}/agents/${role}/IDENTITY.md"
    
    # 检查文件是否以 --- 开头（YAML Frontmatter）
    if ! head -n 1 "${identity_file}" | grep -q '^---$'; then
      log_error "ERROR: ${identity_file} 缺少 YAML Frontmatter 开始标记"
      return 1
    fi
    
    # 检查是否有结束的 ---
    if ! grep -n '^---$' "${identity_file}" | head -n 2 | tail -n 1 | grep -q '^2:'; then
      # 检查第二行或后续行是否有结束的 ---
      local line_count
      line_count=$(grep -n '^---$' "${identity_file}" | wc -l)
      if [[ "${line_count}" -lt 2 ]]; then
        log_error "ERROR: ${identity_file} 缺少 YAML Frontmatter 结束标记"
        return 1
      fi
    fi
    
    # 检查是否包含 name 字段
    if ! grep -q '^name:' "${identity_file}"; then
      log_error "ERROR: ${identity_file} 缺少 name 字段"
      return 1
    fi
    
    # 检查是否包含 description 字段
    if ! grep -q '^description:' "${identity_file}"; then
      log_error "ERROR: ${identity_file} 缺少 description 字段"
      return 1
    fi
  done
  
  return 0
}

# TC-ROL-007: 角色信息可解析性验证（使用 Python）
test_rol_007() {
  local python_script
  python_script=$(cat <<'PYTHON'
import sys
import re

def parse_identity(content):
    """解析 IDENTITY.md 文件的 YAML Frontmatter"""
    # 匹配 YAML Frontmatter
    pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        return None
    
    yaml_content = match.group(1)
    result = {}
    
    # 解析简单的键值对
    for line in yaml_content.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            result[key] = value
    
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: parse_identity.py <file>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    parsed = parse_identity(content)
    if parsed is None:
        print("ERROR: Failed to parse YAML Frontmatter")
        sys.exit(1)
    
    # 验证必需字段
    required_fields = ['name', 'description']
    for field in required_fields:
        if field not in parsed:
            print(f"ERROR: Missing required field: {field}")
            sys.exit(1)
    
    print(f"Parsed successfully: name={parsed.get('name')}")
    sys.exit(0)

if __name__ == '__main__':
    main()
PYTHON
)

  local role
  for role in "${ROLES[@]}"; do
    local identity_file="${ROOT_DIR}/agents/${role}/IDENTITY.md"
    
    if ! echo "${python_script}" | python3 - "${identity_file}" 2>&1; then
      log_error "ERROR: 无法解析 ${identity_file}"
      return 1
    fi
  done
  
  return 0
}

# ============================================================
# 主程序
# ============================================================

main() {
  TOTAL_START_TIME=$(get_time)
  
  # 检查依赖命令
  if ! check_command bc; then
    log_error "ERROR: 缺少必需的命令: bc"
    exit 1
  fi
  
  if ! check_command python3; then
    log_error "ERROR: 缺少必需的命令: python3"
    exit 1
  fi
  
  # 打印标题
  print_double_line
  log_info "   InfinityCompany 阶段 6 测试执行"
  print_double_line
  log_info ""
  log_info "配置文件: ${ENV_FILE}"
  log_info ""
  
  # Phase 1: 环境配置测试
  log_info "[Phase 1/3] 环境配置测试"
  print_line
  run_test "TC-ENV-001" "环境变量文件存在性检查" test_env_001 || true
  run_test "TC-ENV-002" "必需环境变量完整性检查" test_env_002 || true
  run_test "TC-ENV-003" "目录结构存在性验证" test_env_003 || true
  run_test "TC-ENV-004" "环境变量输出格式验证" test_env_004 || true
  log_info ""
  
  # Phase 2: 部署流程测试
  log_info "[Phase 2/3] 部署流程测试"
  print_line
  run_test "TC-ATT-001" "基础 Attach 流程验证" test_att_001 || true
  run_test "TC-DEP-001" "完整 Deploy 流程验证" test_dep_001 || true
  log_info ""
  
  # Phase 3: 角色验证测试
  log_info "[Phase 3/3] 角色验证测试"
  print_line
  run_test "TC-ROL-005" "角色 IDENTITY 文件存在性验证" test_rol_005 || true
  run_test "TC-ROL-006" "角色 IDENTITY 文件格式验证" test_rol_006 || true
  run_test "TC-ROL-007" "角色信息可解析性验证" test_rol_007 || true
  log_info ""
  
  # 计算总耗时
  local total_duration
  total_duration=$(calc_duration "${TOTAL_START_TIME}")
  
  # 计算通过率
  local pass_rate=0
  if [[ ${TOTAL_TESTS} -gt 0 ]]; then
    pass_rate=$((PASSED_TESTS * 100 / TOTAL_TESTS))
  fi
  
  # 打印汇总
  print_double_line
  log_info "                         测试汇总"
  print_double_line
  log_info "  总用例数: ${TOTAL_TESTS}"
  log_info "  通过:     ${PASSED_TESTS}"
  log_info "  失败:     ${FAILED_TESTS}"
  log_info "  跳过:     ${SKIPPED_TESTS}"
  log_info "  通过率:   ${pass_rate}%"
  log_info "  总耗时:   ${total_duration}s"
  print_double_line
  
  # 返回状态
  if [[ ${FAILED_TESTS} -gt 0 ]]; then
    exit 1
  fi
  
  exit 0
}

main "$@"
