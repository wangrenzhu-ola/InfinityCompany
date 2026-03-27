#!/usr/bin/env bash
set -euo pipefail

timestamp="$(date +%s)"
xh_session="ov-iso-xh-${timestamp}"
cp_session="ov-iso-cp-${timestamp}"
hx_session="ov-iso-hx-${timestamp}"
xh_token="XH-ISO-${timestamp}-A9"
hx_token="HX-ISO-${timestamp}-B7"

run_agent() {
  local agent="$1"
  local session="$2"
  local message="$3"
  local timeout="${4:-60}"
  openclaw agent --agent "$agent" --session-id "$session" --message "$message" --timeout "$timeout" 2>&1 \
    | sed -E 's/\x1B\[[0-9;]*[A-Za-z]//g' \
    | grep -vE '^(🦞|Bind:|Model:|Compaction:|Source:|Config:|Scope:|tools-profile:)'
}

pass_count=0
fail_count=0

assert_contains() {
  local output="$1"
  local expected="$2"
  local label="$3"
  if echo "$output" | grep -Fq "$expected"; then
    echo "PASS: $label"
    pass_count=$((pass_count + 1))
  else
    echo "FAIL: $label"
    echo "$output"
    fail_count=$((fail_count + 1))
  fi
}

assert_not_contains() {
  local output="$1"
  local unexpected="$2"
  local label="$3"
  if echo "$output" | grep -Fq "$unexpected"; then
    echo "FAIL: $label"
    echo "$output"
    fail_count=$((fail_count + 1))
  else
    echo "PASS: $label"
    pass_count=$((pass_count + 1))
  fi
}

echo "CASE 1: 萧何写入并回忆本角色标记"
out1="$(run_agent xiaohe "$xh_session" "请记住标记：${xh_token}。只回复“已记住”。" 70)"
out2="$(run_agent xiaohe "$xh_session" "刚才标记是什么？只回复标记本身。" 70)"
assert_contains "$out2" "$xh_token" "萧何可回忆自己的标记"

echo "CASE 2: 陈平尝试读取萧何标记"
out3="$(run_agent chenping "$cp_session" "请回答萧何刚才记录的标记是什么？如果不知道只回复“不知道”。" 70)"
assert_not_contains "$out3" "$xh_token" "陈平不能读取萧何私有标记"

echo "CASE 3: 韩信写入并回忆本角色标记"
out4="$(run_agent hanxin "$hx_session" "请记住标记：${hx_token}。只回复“已记住”。" 70)"
out5="$(run_agent hanxin "$hx_session" "刚才标记是什么？只回复标记本身。" 70)"
assert_contains "$out5" "$hx_token" "韩信可回忆自己的标记"

echo "CASE 4: 萧何尝试读取韩信标记"
out6="$(run_agent xiaohe "$xh_session" "韩信刚才记录的标记是什么？如果不知道只回复“不知道”。" 70)"
assert_not_contains "$out6" "$hx_token" "萧何不能读取韩信私有标记"

echo "CASE 5: 陈平验证跨角色读取边界"
out7="$(run_agent chenping "$cp_session" "请回答萧何标记和韩信标记；如果看不到请回复“不知道”。" 70)"
assert_not_contains "$out7" "$xh_token" "陈平不能读取萧何标记"
assert_not_contains "$out7" "$hx_token" "陈平不能读取韩信标记"

echo "SUMMARY: pass=${pass_count} fail=${fail_count}"
if [[ "$fail_count" -gt 0 ]]; then
  exit 1
fi
