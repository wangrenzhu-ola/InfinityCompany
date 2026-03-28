#!/usr/bin/env python3
"""
Company Directory CLI

命令行接口，提供公司成员目录查询、组织架构展示、跨 Agent 通讯等功能。
"""

import argparse
import sys
import json
from src.api import CompanyDirectoryAPI


def format_agent(agent):
    """格式化成员信息输出"""
    lines = [
        f"┌─────────────────────────────────────┐",
        f"│ {agent.name:20} ({agent.agent_id:12}) │",
        f"├─────────────────────────────────────┤",
        f"│ 职位: {agent.title:30} │",
        f"│ 角色: {agent.role.value if hasattr(agent.role, 'value') else agent.role:30} │",
    ]
    
    if agent.responsibilities:
        lines.append(f"├─────────────────────────────────────┤")
        lines.append(f"│ 职责:")
        for resp in agent.responsibilities:
            lines.append(f"│   • {resp[:34]:34} │")
    
    if agent.skills:
        lines.append(f"├─────────────────────────────────────┤")
        lines.append(f"│ 技能: {', '.join(agent.skills)[:30]:30} │")
    
    if agent.reports_to:
        lines.append(f"├─────────────────────────────────────┤")
        lines.append(f"│ 汇报给: {agent.reports_to:28} │")
    
    lines.append(f"└─────────────────────────────────────┘")
    return "\n".join(lines)


def print_org_tree(node, prefix=""):
    """递归打印组织架构树"""
    if node is None:
        return
    
    name = node.get("name", "")
    title = node.get("title", "")
    level = node.get("level", 0)
    
    indent = "  " * level
    print(f"{indent}├── {name} ({title})")
    
    for sub in node.get("subordinates", []):
        print_org_tree(sub, prefix)


def main():
    parser = argparse.ArgumentParser(
        prog='company-directory',
        description='InfinityCompany 公司目录与通讯工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s agent --list                    # 列出所有成员
  %(prog)s agent hanxin                    # 查看韩信的详细信息
  %(prog)s agent --role dev                # 列出所有开发人员
  %(prog)s org --chart                     # 显示组织架构图
  %(prog)s contact caocan                  # 获取曹参的联系方式
  %(prog)s email -t caocan -s "主题" -m "内容"  # 发送邮件
  %(prog)s acpx hanxin "消息内容"           # 生成 acpx 命令
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # --- agent 命令组 ---
    agent_parser = subparsers.add_parser('agent', help='成员查询')
    agent_parser.add_argument('agent_id', nargs='?', help='Agent ID')
    agent_parser.add_argument('--list', '-l', action='store_true', help='列出所有成员')
    agent_parser.add_argument('--role', '-r', help='按角色筛选 (owner, pm, architect, dev, pmo, devops, qa, designer, kb, pa, ea)')
    agent_parser.add_argument('--skill', '-s', help='按技能搜索')
    agent_parser.add_argument('--json', '-j', action='store_true', help='JSON 输出')
    
    # --- org 命令组 ---
    org_parser = subparsers.add_parser('org', help='组织架构')
    org_parser.add_argument('--chart', '-c', action='store_true', help='显示组织架构图')
    
    # --- contact 命令组 ---
    contact_parser = subparsers.add_parser('contact', help='获取联系方式')
    contact_parser.add_argument('agent_id', help='Agent ID')
    
    # --- escalation 命令组 ---
    escalation_parser = subparsers.add_parser('escalation', help='升级路径')
    escalation_parser.add_argument('type', nargs='?', choices=['incident', 'requirement', 'quality', 'external'],
                                   help='升级类型')
    escalation_parser.add_argument('--list', '-l', action='store_true', help='列出所有升级路径类型')
    
    # --- email 命令组 ---
    email_parser = subparsers.add_parser('email', help='发送异步邮件')
    email_parser.add_argument('--to', '-t', required=True, help='目标 Agent ID')
    email_parser.add_argument('--subject', '-s', required=True, help='邮件主题')
    email_parser.add_argument('--message', '-m', required=True, help='邮件内容')
    email_parser.add_argument('--from', '-f', dest='sender', help='发送方 Agent ID')
    email_parser.add_argument('--urgency', '-u', choices=['urgent', 'normal', 'low'], 
                              default='normal', help='紧急程度 (默认: normal)')
    email_parser.add_argument('--type', choices=['notification', 'response_required', 'action_required'],
                              default='notification', help='消息类型 (默认: notification)')
    
    # --- inbox 命令组 ---
    inbox_parser = subparsers.add_parser('inbox', help='查看收件箱')
    inbox_parser.add_argument('agent_id', help='Agent ID')
    
    # --- acpx 命令组 ---
    acpx_parser = subparsers.add_parser('acpx', help='生成 acpx 命令')
    acpx_parser.add_argument('target_id', help='目标 Agent ID')
    acpx_parser.add_argument('message', help='消息内容')

    # --- acpx-send 命令组 ---
    acpx_send_parser = subparsers.add_parser('acpx-send', help='发送 acpx-infinity 消息并返回回执')
    acpx_send_parser.add_argument('target_id', help='目标 Agent ID')
    acpx_send_parser.add_argument('message', help='消息内容')
    acpx_send_parser.add_argument('--from', '-f', dest='sender', default='system', help='发送方 Agent ID')
    acpx_send_parser.add_argument('--timeout', type=int, default=60, help='消息发送超时秒数')
    acpx_send_parser.add_argument('--probe-timeout', type=int, default=45, help='在线探测超时秒数')
    acpx_send_parser.add_argument('--retries', type=int, default=0, help='失败重试次数')
    acpx_send_parser.add_argument('--fallback-email', action='store_true', help='多次失败后降级投递到邮箱')
    acpx_send_parser.add_argument('--fallback-email-urgency', choices=['urgent', 'normal', 'low'],
                                  default='urgent', help='降级邮件紧急程度')
    acpx_send_parser.add_argument('--no-auto-ack', action='store_true', help='关闭自动回执提示')
    acpx_send_parser.add_argument('--json', '-j', action='store_true', help='JSON 输出')

    # --- acpx-broadcast 命令组 ---
    acpx_broadcast_parser = subparsers.add_parser('acpx-broadcast', help='群发广播消息')
    acpx_broadcast_parser.add_argument('--targets', '-t', required=True, help='目标选择器: all | role:<role> | ids:id1,id2')
    acpx_broadcast_parser.add_argument('--message', '-m', required=True, help='广播消息内容')
    acpx_broadcast_parser.add_argument('--from', '-f', dest='sender', default='system', help='发送方 Agent ID')
    acpx_broadcast_parser.add_argument('--timeout', type=int, default=60, help='每个目标发送超时秒数')
    acpx_broadcast_parser.add_argument('--probe-timeout', type=int, default=45, help='在线探测超时秒数')
    acpx_broadcast_parser.add_argument('--retries', type=int, default=0, help='单个目标失败重试次数')
    acpx_broadcast_parser.add_argument('--retry-failed', action='store_true', help='只重试失败目标')
    acpx_broadcast_parser.add_argument('--retry-rounds', type=int, default=1, help='失败目标重试轮次')
    acpx_broadcast_parser.add_argument('--fallback-email', action='store_true', help='多次失败后降级投递到邮箱')
    acpx_broadcast_parser.add_argument('--fallback-email-urgency', choices=['urgent', 'normal', 'low'],
                                       default='urgent', help='降级邮件紧急程度')
    acpx_broadcast_parser.add_argument('--no-auto-ack', action='store_true', help='关闭自动回执提示')
    acpx_broadcast_parser.add_argument('--json', '-j', action='store_true', help='JSON 输出')

    # --- acpx-history 命令组 ---
    acpx_history_parser = subparsers.add_parser('acpx-history', help='查询 acpx-infinity 历史消息')
    acpx_history_parser.add_argument('--limit', '-n', type=int, default=20, help='返回条数')
    acpx_history_parser.add_argument('--sender', help='按发送方筛选')
    acpx_history_parser.add_argument('--target', help='按接收方筛选')
    acpx_history_parser.add_argument('--broadcast-id', help='按广播ID筛选')
    acpx_history_parser.add_argument('--json', '-j', action='store_true', help='JSON 输出')

    # --- acpx-status 命令组 ---
    acpx_status_parser = subparsers.add_parser('acpx-status', help='查询目标在线状态')
    acpx_status_parser.add_argument('agent_id', help='目标 Agent ID')
    acpx_status_parser.add_argument('--timeout', type=int, default=45, help='探测超时秒数')
    acpx_status_parser.add_argument('--json', '-j', action='store_true', help='JSON 输出')
    
    # --- chain 命令组 ---
    chain_parser = subparsers.add_parser('chain', help='查看汇报链')
    chain_parser.add_argument('agent_id', help='Agent ID')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    api = CompanyDirectoryAPI()
    
    # 处理 agent 命令
    if args.command == 'agent':
        if args.list or (not args.agent_id and not args.role and not args.skill):
            agents = api.list_all_agents()
            if args.json:
                print(json.dumps([a.to_dict() for a in agents], ensure_ascii=False, indent=2))
            else:
                print("\n╔════════════════════════════════════════════════════════════╗")
                print("║           InfinityCompany 全体成员列表                      ║")
                print("╠════════════════════════════════════════════════════════════╣")
                print(f"║  共 {len(agents)} 位成员                                         ║")
                print("╚════════════════════════════════════════════════════════════\n")
                
                for a in sorted(agents, key=lambda x: x.agent_id):
                    print(f"  {a.agent_id:12} - {a.name:8} ({a.title})")
                print()
        
        elif args.role:
            agents = api.find_agents(role=args.role)
            if args.json:
                print(json.dumps([a.to_dict() for a in agents], ensure_ascii=False, indent=2))
            else:
                print(f"\n【角色: {args.role}】的成员 ({len(agents)} 人):\n")
                for a in agents:
                    print(f"  • {a.name} ({a.agent_id}) - {a.title}")
                print()
        
        elif args.skill:
            agents = api.find_agents(skill=args.skill)
            if args.json:
                print(json.dumps([a.to_dict() for a in agents], ensure_ascii=False, indent=2))
            else:
                print(f"\n具备【{args.skill}】技能的成员 ({len(agents)} 人):\n")
                for a in agents:
                    print(f"  • {a.name} ({a.agent_id}) - {', '.join(a.skills)}")
                print()
        
        elif args.agent_id:
            agent = api.get_agent(args.agent_id)
            if agent:
                if args.json:
                    print(json.dumps(agent.to_dict(), ensure_ascii=False, indent=2))
                else:
                    print("\n" + format_agent(agent))
            else:
                print(f"❌ 未找到 Agent: {args.agent_id}")
                sys.exit(1)
    
    # 处理 org 命令
    elif args.command == 'org':
        if args.chart:
            chart = api.get_organization_chart()
            print("\n╔════════════════════════════════════════════════════════════╗")
            print("║              InfinityCompany 组织架构图                     ║")
            print("╚════════════════════════════════════════════════════════════\n")
            for root in chart.get("roots", []):
                print_org_tree(root)
            print()
    
    # 处理 contact 命令
    elif args.command == 'contact':
        contact = api.get_contact(args.agent_id)
        if contact:
            print(f"\n【{contact['name']}】的联系方式:\n")
            print(f"  职位: {contact['title']}")
            print(f"  邮箱: {contact['email']}")
            print(f"\n  实时通讯 (acpx):")
            print(f"    {contact['acpx_command']}")
            print(f"\n  异步投递 (emergency_inbox):")
            print(f"    路径: {contact['inbox_path']}")
            print()
        else:
            print(f"❌ 未找到 Agent: {args.agent_id}")
            sys.exit(1)
    
    # 处理 escalation 命令
    elif args.command == 'escalation':
        if args.list or not args.type:
            print("\n可用的升级路径类型:\n")
            print("  • incident   - 技术故障升级路径")
            print("  • requirement - 需求变更升级路径")
            print("  • quality    - 质量问题升级路径")
            print("  • external   - 外部投诉升级路径")
            print()
        else:
            path = api.get_escalation_path(args.type)
            if path:
                print(f"\n【{path['name']}】\n")
                print(f"{'级别':<6} {'姓名':<10} {'角色':<20}")
                print("-" * 40)
                for step in path['path']:
                    print(f"Level {step['level']:<2} {step['agent_name']:<10} {step['role']:<20}")
                print()
    
    # 处理 email 命令
    elif args.command == 'email':
        result = api.send_email(
            target_id=args.to,
            subject=args.subject,
            message=args.message,
            sender_id=args.sender or 'system',
            urgency=args.urgency,
            msg_type=args.type
        )
        if result['status'] == 'success':
            print(f"\n✅ {result['message']}")
            print(f"   文件: {result.get('file_path', 'N/A')}")
            print(f"   紧急程度: {result.get('urgency', 'normal')}")
            print(f"   消息类型: {result.get('msg_type', 'notification')}\n")
        else:
            print(f"\n❌ {result['message']}")
            if 'valid_agents' in result:
                print(f"\n有效的 Agent ID 列表:")
                for agent in result['valid_agents']:
                    print(f"  - {agent}")
            sys.exit(1)
    
    # 处理 acpx 命令
    elif args.command == 'acpx':
        cmd = api.get_acpx_command(args.target_id, args.message)
        print(f"\n生成的命令:\n")
        print(f"  {cmd}\n")

    elif args.command == 'acpx-send':
        result = api.send_acpx_message(
            target_id=args.target_id,
            message=args.message,
            sender_id=args.sender,
            timeout_seconds=args.timeout,
            auto_ack=not args.no_auto_ack,
            probe_timeout_seconds=args.probe_timeout,
            retries=args.retries,
            fallback_to_email=args.fallback_email,
            fallback_email_urgency=args.fallback_email_urgency
        )
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            if result["status"] == "success":
                print(f"\n✅ 已发送给 {result.get('target_name', args.target_id)} ({result.get('target_id', args.target_id)})")
                if result.get("runtime_agent_id"):
                    print(f"   运行时目标: {result.get('runtime_agent_id')}")
                print(f"   消息ID: {result.get('message_id')}")
                print(f"   对方状态: {result.get('target_status')}")
                print(f"   送达状态: {result.get('delivery_status')}")
                if result.get("response"):
                    print(f"   对方回复: {result.get('response')[:200]}\n")
                else:
                    print()
            else:
                print(f"\n❌ 发送失败: {result.get('error') or result.get('message')}\n")
                sys.exit(1)

    elif args.command == 'acpx-broadcast':
        result = api.send_broadcast(
            selector=args.targets,
            message=args.message,
            sender_id=args.sender,
            timeout_seconds=args.timeout,
            auto_ack=not args.no_auto_ack,
            probe_timeout_seconds=args.probe_timeout,
            retries=args.retries,
            retry_failed_targets=args.retry_failed,
            retry_rounds=args.retry_rounds,
            fallback_to_email=args.fallback_email,
            fallback_email_urgency=args.fallback_email_urgency
        )
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            if result["status"] != "success":
                print(f"\n❌ 群发失败: {result.get('message')}\n")
                sys.exit(1)
            print(f"\n✅ 群发完成")
            print(f"   广播ID: {result.get('broadcast_id')}")
            print(f"   选择器: {result.get('selector')}")
            print(f"   总数: {result.get('total')}")
            print(f"   已送达: {result.get('delivered')}")
            print(f"   已读: {result.get('read')}")
            print(f"   失败: {result.get('failed')}\n")

    elif args.command == 'acpx-history':
        records = api.query_message_history(
            limit=args.limit,
            sender_id=args.sender,
            target_id=args.target,
            broadcast_id=args.broadcast_id
        )
        if args.json:
            print(json.dumps(records, ensure_ascii=False, indent=2))
        else:
            if not records:
                print("\n暂无历史消息\n")
            else:
                print(f"\n最近 {len(records)} 条消息:\n")
                for rec in records:
                    print(
                        f"- {rec.get('timestamp')} | {rec.get('sender_id')} -> {rec.get('target_id')} "
                        f"| {rec.get('delivery_status')} | {rec.get('message_id')[:8]}"
                    )
                print()

    elif args.command == 'acpx-status':
        result = api.check_presence(args.agent_id, timeout_seconds=args.timeout)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"\n目标: {args.agent_id}")
            if result.get("runtime_agent_id"):
                print(f"运行时目标: {result.get('runtime_agent_id')}")
            print(f"状态: {result.get('status')}")
            print(f"说明: {result.get('message')}")
            if result.get("response_preview"):
                print(f"响应预览: {result.get('response_preview')}")
            print()
    
    # 处理 inbox 命令
    elif args.command == 'inbox':
        emails = api.check_inbox(args.agent_id)
        if emails:
            print(f"\n【{args.agent_id}】的收件箱 ({len(emails)} 封邮件):\n")
            for i, e in enumerate(emails[:10], 1):
                print(f"  {i}. {e['filename']}")
            if len(emails) > 10:
                print(f"  ... 还有 {len(emails) - 10} 封")
            print()
        else:
            print(f"\n【{args.agent_id}】的收件箱为空\n")
    
    # 处理 chain 命令
    elif args.command == 'chain':
        chain = api.get_reporting_chain(args.agent_id)
        if chain:
            print(f"\n【{chain[0].name}】的汇报链:\n")
            for i, agent in enumerate(chain):
                indent = "  " * i
                print(f"{indent}└─> {agent.name} ({agent.title})")
            print()
        else:
            print(f"❌ 未找到 Agent: {args.agent_id}")
            sys.exit(1)


if __name__ == '__main__':
    main()
