#!/bin/bash
#
# InfinityCompany 留痕校验脚本
# 用途: 验证代码提交、文档更新、看板更新与复盘同步的协作留痕
# 维护者: 周勃(运维工程师) / 陆贾(知识库管理员)
# 版本: v1.0.0
#

set -e

# ============================================
# 配置变量
# ============================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPORT_DIR="$PROJECT_ROOT/reports/traceability"
LOG_FILE="$REPORT_DIR/check_$(date +%Y%m%d_%H%M%S).log"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 计数器
ERRORS=0
WARNINGS=0
INFO=0
PASSED=0

# ============================================
# 工具函数
# ============================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
    INFO=$((INFO + 1))
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
    WARNINGS=$((WARNINGS + 1))
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    ERRORS=$((ERRORS + 1))
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1" | tee -a "$LOG_FILE"
    PASSED=$((PASSED + 1))
}

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_section() {
    echo -e "\n${YELLOW}▶ $1${NC}"
    echo -e "${YELLOW}────────────────────────────────────────${NC}"
}

# 初始化报告目录
init_report_dir() {
    mkdir -p "$REPORT_DIR"
    echo "# 留痕校验报告 - $(date '+%Y-%m-%d %H:%M:%S')" > "$LOG_FILE"
    echo "" >> "$LOG_FILE"
}

# ============================================
# Git 提交规范检查
# ============================================

check_git_commits() {
    print_section "Git 提交规范检查"
    
    local since_date="${1:-7 days ago}"
    log_info "检查时间范围: $since_date 至今"
    
    # 获取提交列表
    local commits
    commits=$(git -C "$PROJECT_ROOT" log --since="$since_date" --pretty=format:"%H|%an|%ae|%at|%s" 2>/dev/null || true)
    
    if [ -z "$commits" ]; then
        log_warn "指定时间范围内没有提交记录"
        return
    fi
    
    local total_commits=0
    local valid_commits=0
    local invalid_commits=0
    
    # Conventional Commits 正则
    local commit_pattern='^(feat|fix|docs|style|refactor|test|chore|design|workflow|agent)(\([a-zA-Z0-9_/:-]+\))?!?: .+'
    
    while IFS='|' read -r hash author email timestamp subject; do
        ((total_commits++))
        
        # 检查提交信息格式
        if [[ "$subject" =~ $commit_pattern ]]; then
            ((valid_commits++))
            
            # 检查主题长度
            local subject_length=${#subject}
            if [ "$subject_length" -gt 72 ]; then
                log_warn "[$hash] 提交主题过长 (${subject_length}字符): ${subject:0:50}..."
            fi
            
            # 检查是否关联任务ID
            if ! [[ "$subject" =~ (#[0-9]+|\[NOTION-[A-Z0-9-]+\]) ]]; then
                log_warn "[$hash] 建议关联 Story/Task ID: ${subject:0:50}"
            fi
        else
            ((invalid_commits++))
            log_error "[$hash] 提交信息格式不符合 Conventional Commits: $subject"
        fi
    done <<< "$commits"
    
    echo ""
    log_info "Git 提交统计: 总计=$total_commits 合规=$valid_commits 不合规=$invalid_commits"
    
    if [ "$invalid_commits" -eq 0 ]; then
        log_success "所有提交信息格式符合规范"
    fi
}

# ============================================
# Git 分支策略检查
# ============================================

check_git_branches() {
    print_section "Git 分支策略检查"
    
    local branches
    branches=$(git -C "$PROJECT_ROOT" branch -a 2>/dev/null | sed 's/^[* ]*//' || true)
    
    local valid_patterns=(
        '^main$'
        '^develop$'
        '^feature/[a-z0-9-]+$'
        '^hotfix/[a-z0-9-]+$'
        '^release/v[0-9]+\.[0-9]+\.[0-9]+$'
        '^remotes/origin/main$'
        '^remotes/origin/develop$'
        '^remotes/origin/feature/[a-z0-9-]+$'
        '^remotes/origin/hotfix/[a-z0-9-]+$'
        '^remotes/origin/release/v[0-9]+\.[0-9]+\.[0-9]+$'
    )
    
    local invalid_branches=()
    
    while IFS= read -r branch; do
        [ -z "$branch" ] && continue
        
        local is_valid=false
        for pattern in "${valid_patterns[@]}"; do
            if [[ "$branch" =~ $pattern ]]; then
                is_valid=true
                break
            fi
        done
        
        if [ "$is_valid" = false ]; then
            invalid_branches+=("$branch")
            log_error "分支命名不符合规范: $branch"
        fi
    done <<< "$branches"
    
    if [ ${#invalid_branches[@]} -eq 0 ]; then
        log_success "所有分支命名符合规范"
    fi
}

# ============================================
# Git 提交频率检查
# ============================================

check_commit_frequency() {
    print_section "Git 提交频率分析"
    
    local since_date="${1:-7 days ago}"
    
    # 按作者统计提交
    local author_stats
    author_stats=$(git -C "$PROJECT_ROOT" log --since="$since_date" --pretty=format:"%an" 2>/dev/null | sort | uniq -c | sort -rn || true)
    
    if [ -z "$author_stats" ]; then
        log_warn "没有获取到提交数据"
        return
    fi
    
    log_info "最近7天提交频率统计:"
    echo "$author_stats" | while read -r count author; do
        echo "  - $author: $count 次提交"
    done || true
    
    # 检查批量提交
    log_info "检查批量提交 (>20个文件)..."
    git -C "$PROJECT_ROOT" log --since="$since_date" --pretty=format:"%H|%s" --shortstat 2>/dev/null | \
    awk '/^[a-f0-9]{40}\|/ { hash=$1; msg=$0 } /files? changed/ { 
        if ($1 > 20) {
            print "批量提交: " hash " " $1 " 个文件"
        }
    }' | while read -r line; do
        log_warn "$line"
    done || true
}

# ============================================
# 文档完整性检查
# ============================================

check_document_completeness() {
    print_section "文档完整性检查"
    
    local doc_paths=(
        "agents/*/IDENTITY.md"
        "workflows/*.md"
        "notion/*.md"
        "skills/*/README.md"
        "governance/*.md"
        "*.md"
    )
    
    local total_docs=0
    local recent_docs=0
    local stale_docs=0
    local now=$(date +%s)
    local ninety_days=$((90 * 86400))
    
    for pattern in "${doc_paths[@]}"; do
        for doc in $PROJECT_ROOT/$pattern; do
            [ -f "$doc" ] || continue
            ((total_docs++))
            
            local rel_path="${doc#$PROJECT_ROOT/}"
            local mtime=$(stat -c %Y "$doc" 2>/dev/null || stat -f %m "$doc" 2>/dev/null)
            local age=$((now - mtime))
            
            if [ "$age" -gt "$ninety_days" ]; then
                local days_old=$((age / 86400))
                log_warn "[$rel_path] 文档超过90天未更新 (${days_old}天)"
                ((stale_docs++))
            else
                ((recent_docs++))
            fi
        done
    done
    
    log_info "文档统计: 总计=$total_docs 近期更新=$recent_docs 过期=$stale_docs"
}

# ============================================
# 文档时间戳检查
# ============================================

check_document_timestamps() {
    print_section "文档时间戳检查"
    
    # 获取所有 Markdown 文档
    local docs
    docs=$(find "$PROJECT_ROOT" -name "*.md" -type f 2>/dev/null | grep -v "node_modules" | grep -v ".git" || true)
    
    local mismatched=0
    
    while IFS= read -r doc; do
        [ -f "$doc" ] || continue
        
        local rel_path="${doc#$PROJECT_ROOT/}"
        
        # 获取文件修改时间
        local file_mtime
        file_mtime=$(stat -c %Y "$doc" 2>/dev/null || stat -f %m "$doc" 2>/dev/null)
        
        # 获取 Git 最后提交时间
        local git_timestamp
        git_timestamp=$(git -C "$PROJECT_ROOT" log -1 --format=%at -- "$rel_path" 2>/dev/null || echo "")
        
        if [ -n "$git_timestamp" ] && [ -n "$file_mtime" ]; then
            local time_diff=$((file_mtime - git_timestamp))
            time_diff=${time_diff#-}  # 取绝对值
            
            if [ "$time_diff" -gt 60 ]; then
                log_warn "[$rel_path] 文件时间与 Git 提交时间不一致 (差异 ${time_diff}秒)"
                ((mismatched++))
            fi
        fi
    done <<< "$docs"
    
    if [ "$mismatched" -eq 0 ]; then
        log_success "所有文档时间戳与 Git 提交一致"
    fi
}

# ============================================
# Agent IDENTITY 文件检查
# ============================================

check_agent_identity_files() {
    print_section "Agent IDENTITY 文件检查"
    
    # 必需的角色列表
    local required_agents=(
        "zhangliang:张良(产品经理)"
        "xiaohe:萧何(架构师)"
        "hanxin:韩信(全栈研发)"
        "chenping:陈平(测试工程师)"
        "zhoubo:周勃(运维工程师)"
        "caocan:曹参(PMO)"
        "lishiyi:郦食其(外部助理)"
        "lujia:陆贾(知识库管理员)"
        "shusuntong:叔孙通(设计师)"
        "xiahouying:夏侯婴(私人助理)"
    )
    
    local missing=0
    local incomplete=0
    
    for agent_info in "${required_agents[@]}"; do
        local agent_id="${agent_info%%:*}"
        local agent_name="${agent_info##*:}"
        local identity_file="$PROJECT_ROOT/agents/$agent_id/IDENTITY.md"
        
        if [ ! -f "$identity_file" ]; then
            log_error "缺少 $agent_name 的 IDENTITY.md 文件: agents/$agent_id/IDENTITY.md"
            ((missing++))
            continue
        fi
        
        # 检查必需内容
        local content
        content=$(cat "$identity_file" 2>/dev/null || echo "")
        
        # 检查关键字段
        local required_keywords=("模型配置" "官方职位" "核心权责")
        for keyword in "${required_keywords[@]}"; do
            if ! echo "$content" | grep -q "$keyword"; then
                log_warn "[$agent_id/IDENTITY.md] 缺少关键内容: $keyword"
                ((incomplete++))
            fi
        done
        
        # 检查 Frontmatter
        if ! echo "$content" | head -5 | grep -q "^---"; then
            log_warn "[$agent_id/IDENTITY.md] 建议添加 YAML Frontmatter"
        fi
    done
    
    local total_agents=${#required_agents[@]}
    local found=$((total_agents - missing))
    
    log_info "Agent 文件统计: 必需=$total_agents 存在=$found 缺失=$missing 不完整=$incomplete"
    
    if [ "$missing" -eq 0 ] && [ "$incomplete" -eq 0 ]; then
        log_success "所有 Agent IDENTITY 文件完整"
    fi
}

# ============================================
# 工作流程文档检查
# ============================================

check_workflow_documents() {
    print_section "工作流程文档检查"
    
    local required_workflows=(
        "external_assistant_workflow.md:外部助理工作流程"
        "personal_assistant_workflow.md:私人助理工作流程"
        "internal_delivery_workflow.md:内部交付闭环流程"
    )
    
    local missing=0
    
    for workflow_info in "${required_workflows[@]}"; do
        local filename="${workflow_info%%:*}"
        local name="${workflow_info##*:}"
        local filepath="$PROJECT_ROOT/workflows/$filename"
        
        if [ ! -f "$filepath" ]; then
            log_error "缺少 $name: workflows/$filename"
            ((missing++))
        else
            # 检查文档内容完整性
            local content
            content=$(cat "$filepath" 2>/dev/null || echo "")
            
            if ! echo "$content" | grep -q "流程概述"; then
                log_warn "[workflows/$filename] 建议添加'流程概述'章节"
            fi
            
            if ! echo "$content" | grep -q "执行步骤"; then
                log_warn "[workflows/$filename] 建议添加'执行步骤'章节"
            fi
        fi
    done
    
    if [ "$missing" -eq 0 ]; then
        log_success "所有必需的工作流程文档存在"
    fi
}

# ============================================
# 环境检查日志验证（周勃每日18:00检查）
# ============================================

check_environment_logs() {
    print_section "环境检查日志验证"
    
    # 查找最近的环境检查日志
    local log_files
    log_files=$(find "$PROJECT_ROOT" -name "*environment*check*.log" -o -name "*env_check*.log" 2>/dev/null | head -5 || true)
    
    if [ -z "$log_files" ]; then
        log_warn "未找到环境检查日志文件"
        return
    fi
    
    local now=$(date +%s)
    local one_day=$((24 * 3600))
    
    while IFS= read -r logfile; do
        [ -f "$logfile" ] || continue
        
        local mtime
        mtime=$(stat -c %Y "$logfile" 2>/dev/null || stat -f %m "$logfile" 2>/dev/null)
        local age=$((now - mtime))
        
        if [ "$age" -lt "$one_day" ]; then
            log_success "环境检查日志已更新: $(basename "$logfile")"
        else
            local hours_old=$((age / 3600))
            log_warn "环境检查日志 ${hours_old}小时前更新，建议周勃执行每日检查"
        fi
    done <<< "$log_files"
}

# ============================================
# 报告生成
# ============================================

generate_report() {
    print_section "生成校验报告"
    
    local report_file="$REPORT_DIR/report_$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$report_file" << EOF
# 留痕校验报告

> **报告类型**: 日常检查  
> **检查时间**: $(date '+%Y-%m-%d %H:%M:%S')  
> **校验脚本**: traceability_check.sh v1.0.0  
> **执行路径**: $PROJECT_ROOT

---

## 📊 总体概览

| 指标 | 数值 |
|-----|------|
| 检查时间 | $(date '+%Y-%m-%d %H:%M:%S') |
| 错误数 | $ERRORS ❌ |
| 警告数 | $WARNINGS ⚠️ |
| 信息数 | $INFO ℹ️ |
| 合规状态 | $([ "$ERRORS" -eq 0 ] && echo "✅ 通过" || echo "❌ 未通过") |

---

## 📋 详细日志

\`\`\`
$(cat "$LOG_FILE")
\`\`\`

---

## 🔧 待办事项

$([ "$ERRORS" -gt 0 ] && echo "- [ ] 修复上述 $ERRORS 个错误" || echo "- ✅ 无待修复错误")
$([ "$WARNINGS" -gt 0 ] && echo "- [ ] 处理上述 $WARNINGS 个警告" || echo "- ✅ 无待处理警告")

---

*报告由 traceability_check.sh 自动生成*
EOF

    log_success "报告已生成: $report_file"
    echo ""
    echo -e "${GREEN}报告文件: $report_file${NC}"
}

# ============================================
# 主函数
# ============================================

show_usage() {
    cat << EOF
InfinityCompany 留痕校验脚本 v1.0.0

用法: $0 [选项] [命令]

命令:
    all              执行所有检查 (默认)
    git              仅执行 Git 相关检查
    docs             仅执行文档相关检查
    agents           仅执行 Agent IDENTITY 检查
    report           生成检查报告

选项:
    -h, --help       显示帮助信息
    -v, --verbose    显示详细输出
    --since DATE     指定 Git 检查起始日期 (默认: 7 days ago)

示例:
    $0                           # 执行所有检查
    $0 git                       # 仅检查 Git 提交
    $0 all --since "3 days ago"  # 检查最近3天的提交

EOF
}

main() {
    local command="all"
    local since_date="7 days ago"
    local verbose=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -v|--verbose)
                verbose=true
                shift
                ;;
            --since)
                since_date="$2"
                shift 2
                ;;
            all|git|docs|agents|report)
                command="$1"
                shift
                ;;
            *)
                echo "未知选项: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # 初始化
    init_report_dir
    
    print_header "InfinityCompany 留痕校验系统"
    log_info "项目路径: $PROJECT_ROOT"
    log_info "检查时间: $(date '+%Y-%m-%d %H:%M:%S')"
    log_info "执行命令: $command"
    
    # 执行检查
    case $command in
        all)
            check_git_commits "$since_date"
            check_git_branches
            check_commit_frequency "$since_date"
            check_document_completeness
            check_document_timestamps
            check_agent_identity_files
            check_workflow_documents
            check_environment_logs
            ;;
        git)
            check_git_commits "$since_date"
            check_git_branches
            check_commit_frequency "$since_date"
            ;;
        docs)
            check_document_completeness
            check_document_timestamps
            check_workflow_documents
            ;;
        agents)
            check_agent_identity_files
            ;;
        report)
            # 仅生成报告
            ;;
    esac
    
    # 生成报告
    generate_report
    
    # 输出总结
    print_header "校验完成"
    echo -e "错误数:   ${RED}$ERRORS${NC}"
    echo -e "警告数:   ${YELLOW}$WARNINGS${NC}"
    echo -e "信息数:   ${BLUE}$INFO${NC}"
    echo ""
    
    if [ "$ERRORS" -eq 0 ]; then
        echo -e "${GREEN}✅ 所有关键检查项通过${NC}"
        exit 0
    else
        echo -e "${RED}❌ 发现 $ERRORS 个错误，请查看报告并修复${NC}"
        exit 1
    fi
}

# 运行主函数
main "$@"
