#!/usr/bin/env python3
"""
acpx-mock: acpx 插件的 Fallback 实现

当真实的 acpx 插件不可用时，使用 email 方式模拟实时通讯。
"""

import argparse
import sys
import os

# 添加 company-directory 路径
sys.path.insert(0, os.path.expanduser("~/.openclaw/workspace/skills/company-directory"))

try:
    from src.api import CompanyDirectoryAPI
except ImportError:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "company-directory"))
    from src.api import CompanyDirectoryAPI


def send_acpx_message(target_id: str, message: str, sender_id: str = None) -> dict:
    """
    发送 acpx 风格的消息
    
    Args:
        target_id: 目标 Agent ID
        message: 消息内容
        sender_id: 发送方 Agent ID（自动检测）
    
    Returns:
        发送结果
    """
    api = CompanyDirectoryAPI()
    
    # 自动检测发送方（从环境变量或当前上下文）
    if not sender_id:
        sender_id = os.environ.get('OPENCLAW_AGENT_ID', 'system')
    
    # 验证目标 Agent 存在
    target = api.get_agent(target_id)
    if not target:
        return {
            "success": False,
            "error": f"未知的 Agent ID: {target_id}",
            "valid_agents": [a.agent_id for a in api.list_all_agents()]
        }
    
    # 构建 acpx 风格的消息
    formatted_message = f"""
【acpx 实时消息】

发送者: {sender_id}
时间: 现在
消息ID: acpx-{target_id}-{hash(message) % 10000}

---

{message}

---

💬 这是一条模拟 acpx 的消息，通过 emergency_inbox 投递。
如需实时对话，建议使用 acpx 直接对话（如果已安装）。

快捷回复:
acpx-mock {sender_id} "你的回复"
"""
    
    # 发送邮件（使用 response_required 类型，因为这是实时通讯）
    result = api.send_email(
        target_id=target_id,
        subject=f"[acpx] 来自 {sender_id} 的消息",
        message=formatted_message,
        sender_id=sender_id,
        urgency="normal",
        msg_type="response_required"  # acpx 消息通常需要回复
    )
    
    if result["status"] == "success":
        return {
            "success": True,
            "message": f"消息已通过 acpx-mock 发送给 {target.name} ({target_id})",
            "email_id": result.get("email_id"),
            "file_path": result.get("file_path"),
            "note": "对方将在检查 inbox 时收到此消息"
        }
    else:
        return {
            "success": False,
            "error": result.get("message", "发送失败")
        }


def check_real_acpx() -> bool:
    """检查真实的 acpx 是否可用"""
    return os.system("which acpx > /dev/null 2>&1") == 0


def main():
    parser = argparse.ArgumentParser(
        prog='acpx-mock',
        description='acpx 插件的 Fallback 实现 - 通过 email 模拟实时通讯'
    )
    parser.add_argument('target_id', help='目标 Agent ID')
    parser.add_argument('message', help='消息内容')
    parser.add_argument('--from', '-f', dest='sender', help='发送方 Agent ID')
    parser.add_argument('--check', '-c', action='store_true', help='检查真实的 acpx 是否可用')
    
    args = parser.parse_args()
    
    # 检查模式
    if args.check:
        if check_real_acpx():
            print("✅ 真实的 acpx 插件已安装")
            print("   建议使用: acpx <agent_id> \"<message>\"")
        else:
            print("⚠️  真实的 acpx 插件未安装")
            print("   使用 acpx-mock 作为 fallback")
        return
    
    # 如果真实的 acpx 可用，提示用户使用真实的 acpx
    if check_real_acpx():
        print("⚠️  检测到真实的 acpx 插件已安装，建议使用:")
        print(f"   acpx {args.target_id} \"{args.message}\"")
        print("")
        response = input("是否仍要使用 acpx-mock? (y/N): ")
        if response.lower() != 'y':
            return
    
    # 发送消息
    result = send_acpx_message(args.target_id, args.message, args.sender)
    
    if result["success"]:
        print(f"\n✅ {result['message']}")
        print(f"   邮件ID: {result.get('email_id', 'N/A')}")
        if result.get('note'):
            print(f"   提示: {result['note']}")
        print()
    else:
        print(f"\n❌ 发送失败: {result.get('error', '未知错误')}")
        if 'valid_agents' in result:
            print("\n有效的 Agent ID:")
            for agent in result['valid_agents']:
                print(f"  - {agent}")
        sys.exit(1)


if __name__ == '__main__':
    main()
