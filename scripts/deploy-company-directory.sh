#!/bin/bash
# 部署company-directory技能到所有Agent

set -e

SOURCE_DIR="/Users/wangrenzhu/work/MetaClaw/InfinityCompany/skills/company-directory"
AGENTS_BASE="/Users/wangrenzhu/work/MetaClaw/InfinityCompany/agents"
AGENTS=("caocan" "zhangliang" "xiaohe" "hanxin" "chenping" "zhoubo" "shusuntong" "lujia" "xiahouying" "lishiyi")

echo "=== 开始部署company-directory技能 ==="
echo "源目录: $SOURCE_DIR"
echo "目标Agents: ${AGENTS[@]}"
echo ""

for agent in "${AGENTS[@]}"; do
    TARGET_DIR="$AGENTS_BASE/$agent/.openclaw/workspace/skills/company-directory"
    
    echo "[$agent] 部署中..."
    
    # 创建目标目录
    mkdir -p "$TARGET_DIR"
    
    # 复制技能文件
    cp -r "$SOURCE_DIR/"* "$TARGET_DIR/"
    
    # 验证部署
    if [ -f "$TARGET_DIR/SKILL.md" ]; then
        echo "  ✅ $agent 部署成功"
    else
        echo "  ❌ $agent 部署失败"
    fi
done

echo ""
echo "=== 部署完成 ==="

# 同时部署到全局技能目录
GLOBAL_SKILL="$HOME/.openclaw/workspace/skills/company-directory"
echo ""
echo "部署到全局技能目录: $GLOBAL_SKILL"
mkdir -p "$GLOBAL_SKILL"
cp -r "$SOURCE_DIR/"* "$GLOBAL_SKILL/"
echo "✅ 全局技能目录部署完成"
