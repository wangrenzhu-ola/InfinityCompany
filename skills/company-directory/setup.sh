#!/bin/bash
# Company Directory Skill Setup Script
# 自动安装依赖并配置环境

set -e

echo "=================================="
echo "Company Directory Skill 安装脚本"
echo "=================================="

# 检查 Python 版本
python_version=$(python3 --version 2>&1 | sed 's/Python \([0-9]\+\.[0-9]\+\).*/\1/')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ 错误: 需要 Python 3.8 或更高版本，当前版本: $python_version"
    exit 1
fi

echo "✅ Python 版本检查通过: $python_version"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查是否存在虚拟环境
if [ -d "$SCRIPT_DIR/.venv" ]; then
    echo "📦 发现虚拟环境，激活中..."
    source "$SCRIPT_DIR/.venv/bin/activate"
else
    echo "📦 创建虚拟环境..."
    python3 -m venv "$SCRIPT_DIR/.venv"
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

# 升级 pip
echo "⬆️  升级 pip..."
pip install --upgrade pip -q

# 安装依赖
echo "📥 安装依赖包..."
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    pip install -r "$SCRIPT_DIR/requirements.txt" -q
    echo "✅ 依赖安装完成"
else
    echo "⚠️  未找到 requirements.txt，跳过依赖安装"
fi

# 验证安装
echo "🔍 验证安装..."
python3 -c "import yaml; print('✅ PyYAML 模块已正确安装')" 2>/dev/null || {
    echo "❌ PyYAML 安装失败"
    exit 1
}

echo ""
echo "=================================="
echo "✅ 安装完成！"
echo "=================================="
echo ""
echo "使用方法:"
echo "  1. 激活虚拟环境: source $SCRIPT_DIR/.venv/bin/activate"
echo "  2. 运行 CLI: python3 $SCRIPT_DIR/cli.py --help"
echo "  3. 运行测试: python3 $SCRIPT_DIR/tests/test_api.py"
echo ""
echo "或者使用快捷命令（自动激活虚拟环境）:"
echo "  bash $SCRIPT_DIR/setup.sh && python3 $SCRIPT_DIR/cli.py agent --list"
echo ""
