#!/usr/bin/env python3
"""
汉初三杰虚拟公司 - 异步邮件投递工具
用于向指定 Agent 的 emergency_inbox 发送异步消息
"""

import argparse
import os
import sys
from datetime import datetime

# Agent 目录映射（汉初三杰虚拟公司）
AGENT_DIRECTORY = {
    "liubang": "liubang",           # 刘邦 (Owner)
    "zhangliang": "zhangliang",     # 张良 (产品经理)
    "xiaohe": "xiaohe",             # 萧何 (架构师)
    "hanxin": "hanxin",             # 韩信 (全栈研发)
    "caocan": "caocan",             # 曹参 (PMO)
    "zhoubo": "zhoubo",             # 周勃 (运维)
    "chenping": "chenping",         # 陈平 (测试)
    "shusuntong": "shusuntong",     # 叔孙通 (设计师)
    "lujia": "lujia",               # 陆贾 (知识库)
    "xiahouying": "xiahouying",     # 夏侯婴 (私人助理)
    "lishiyi": "lishiyi",           # 郦食其 (外部助理)
}


def get_inbox_path(agent_id: str) -> str:
    """获取指定 Agent 的 emergency_inbox 路径"""
    home_dir = os.path.expanduser("~")
    return os.path.join(
        home_dir, ".openclaw", 
        "workspace", "emergency_inbox", 
        agent_id
    )


def send_email(agent_id: str, subject: str, message: str, sender: str = None) -> dict:
    """
    发送异步邮件到指定 Agent 的 emergency_inbox
    
    Args:
        agent_id: 目标 Agent ID
        subject: 邮件主题
        message: 邮件内容
        sender: 发件人 Agent ID（可选）
    
    Returns:
        dict: 发送结果
    """
    # 验证 Agent ID
    if agent_id not in AGENT_DIRECTORY:
        return {
            "status": "error",
            "message": f"未知的 Agent ID: {agent_id}",
            "valid_agents": list(AGENT_DIRECTORY.keys())
        }
    
    # 获取收件箱路径
    inbox_path = get_inbox_path(agent_id)
    
    # 确保目录存在
    os.makedirs(inbox_path, exist_ok=True)
    
    # 生成邮件文件名（带时间戳）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    email_filename = f"email_{timestamp}_{os.urandom(4).hex()}.md"
    email_path = os.path.join(inbox_path, email_filename)
    
    # 构建邮件内容
    sender_info = f"来自: {sender}\n" if sender else ""
    email_content = f"""---
type: emergency_email
sender: {sender or 'system'}
target: {agent_id}
subject: {subject}
timestamp: {datetime.now().isoformat()}
---

# {subject}

{sender_info}
{message}

---
*此邮件由 company-directory 邮件系统自动生成*
"""
    
    # 写入文件
    try:
        with open(email_path, 'w', encoding='utf-8') as f:
            f.write(email_content)
        
        return {
            "status": "success",
            "message": f"邮件已投递至 {agent_id} 的 emergency_inbox",
            "email_file": email_path,
            "timestamp": timestamp
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"邮件投递失败: {str(e)}"
        }


def main():
    parser = argparse.ArgumentParser(
        description='汉初三杰虚拟公司 - 异步邮件投递工具'
    )
    parser.add_argument(
        '--agent-id', '-a',
        required=True,
        help='目标 Agent ID (如: hanxin, caocan, liubang)'
    )
    parser.add_argument(
        '--subject', '-s',
        required=True,
        help='邮件主题'
    )
    parser.add_argument(
        '--message', '-m',
        required=True,
        help='邮件内容'
    )
    parser.add_argument(
        '--from', '-f',
        dest='sender',
        help='发件人 Agent ID（可选）'
    )
    
    args = parser.parse_args()
    
    result = send_email(
        agent_id=args.agent_id,
        subject=args.subject,
        message=args.message,
        sender=args.sender
    )
    
    # 输出结果
    if result["status"] == "success":
        print(f"✅ {result['message']}")
        print(f"   文件: {result['email_file']}")
    else:
        print(f"❌ {result['message']}")
        if "valid_agents" in result:
            print(f"\n有效的 Agent ID 列表:")
            for agent in result["valid_agents"]:
                print(f"  - {agent}")
        sys.exit(1)


if __name__ == "__main__":
    main()
