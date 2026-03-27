#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOP_FILE="${ROOT_DIR}/governance/CROSS_ROLE_KNOWLEDGE_PUBLISH_SOP.md"
TEMPLATE_FILE="${ROOT_DIR}/notion/cross_role_publish_template.md"
CONFIG_FILE="${HOME}/.openclaw/openclaw.json"

pass=0
fail=0

check_contains() {
  local file="$1"
  local pattern="$2"
  local label="$3"
  if grep -Fq -- "$pattern" "$file"; then
    echo "PASS: ${label}"
    pass=$((pass + 1))
  else
    echo "FAIL: ${label}"
    fail=$((fail + 1))
  fi
}

check_file() {
  local file="$1"
  local label="$2"
  if [[ -f "$file" ]]; then
    echo "PASS: ${label}"
    pass=$((pass + 1))
  else
    echo "FAIL: ${label}"
    fail=$((fail + 1))
  fi
}

check_file "$SOP_FILE" "SOP 文件存在"
check_file "$TEMPLATE_FILE" "发布模板存在"

check_contains "$SOP_FILE" "跨角色共享必须先入 Notion" "SOP 定义先入 Notion"
check_contains "$SOP_FILE" "共享发布只能由知识库管理员执行" "SOP 定义管理员发布"
check_contains "$SOP_FILE" "运行时记忆默认隔离" "SOP 定义运行时隔离"

check_contains "$TEMPLATE_FILE" "- 来源角色：" "模板包含来源角色"
check_contains "$TEMPLATE_FILE" "- 适用角色：" "模板包含适用角色"
check_contains "$TEMPLATE_FILE" "- 发布者（知识库管理员）：" "模板包含发布者"
check_contains "$TEMPLATE_FILE" "- 发布状态：草稿/已发布/已回滚" "模板包含发布状态"
check_contains "$TEMPLATE_FILE" "- [ ] 不含秘钥与令牌" "模板包含安全检查"

if [[ -f "$CONFIG_FILE" ]]; then
  if grep -Fq '"targetUri": "viking://agent/memories"' "$CONFIG_FILE"; then
    echo "PASS: OpenViking 为 agent 隔离作用域"
    pass=$((pass + 1))
  else
    echo "FAIL: OpenViking 不是 agent 隔离作用域"
    fail=$((fail + 1))
  fi
else
  echo "FAIL: 缺少 OpenClaw 配置文件"
  fail=$((fail + 1))
fi

echo "SUMMARY: pass=${pass} fail=${fail}"
if [[ "$fail" -gt 0 ]]; then
  exit 1
fi
