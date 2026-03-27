#!/usr/bin/env python3
"""
PMO Manager CLI

命令行接口，提供 PMO 看板管理、任务跟踪、复盘管理等功能。
"""

import argparse
import sys
import json
from datetime import datetime, date, timedelta
from src.api import PMOManagerAPI
from src.models import Priority, TaskStatus


def format_task(task):
    """格式化任务输出"""
    status_emoji = {
        "draft": "📝",
        "pending_review": "⏳",
        "rejected": "❌",
        "approved": "✅",
        "todo": "📋",
        "in_progress": "🔄",
        "blocked": "🚫",
        "done": "✓",
    }
    
    status = task.status.value if hasattr(task.status, 'value') else str(task.status)
    priority = task.priority.value if hasattr(task.priority, 'value') else str(task.priority)
    
    emoji = status_emoji.get(status, "•")
    
    lines = [
        f"{emoji} [{priority}] {task.title}",
        f"   ID: {task.task_id}",
        f"   执行人: {task.assignee_id}",
        f"   关联Story: {task.story_id}",
        f"   状态: {status}",
        f"   截止: {task.deadline}",
    ]
    
    if task.rejection_reason:
        lines.append(f"   拒绝原因: {task.rejection_reason}")
    if task.blocker_reason:
        lines.append(f"   阻塞原因: {task.blocker_reason}")
    
    return "\n".join(lines)


def format_retro(retro):
    """格式化复盘输出"""
    status_emoji = {
        "planning": "📋",
        "collecting": "📥",
        "discussing": "💬",
        "completed": "✅",
        "cancelled": "❌",
    }
    
    status = retro.status.value if hasattr(retro.status, 'value') else str(retro.status)
    retro_type = retro.retro_type.value if hasattr(retro.retro_type, 'value') else str(retro.retro_type)
    emoji = status_emoji.get(status, "•")
    
    return f"{emoji} [{retro.retro_id}] {retro.title} ({retro_type}) - {status}"


def parse_date(date_str):
    """解析日期字符串"""
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise argparse.ArgumentTypeError(f"无效的日期格式: {date_str}")


def main():
    parser = argparse.ArgumentParser(
        prog='pmo-manager',
        description='InfinityCompany PMO 管理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s story create "用户认证" --creator liubang    # 创建 Story
  %(prog)s task submit --title "实现登录" --assignee hanxin --story story-xxx --priority P1 --deadline "2026-04-01 17:00"
  %(prog)s task review task-xxx APPROVED               # 审核 Task
  %(prog)s task status task-xxx done --report-file ~/report.md
  %(prog)s board                                       # 查看看板
  %(prog)s retro create "Sprint 5复盘" --type sprint --facilitator caocan
  %(prog)s retro item-add retro-xxx glad "团队协作很好" --author hanxin
  %(prog)s retro report retro-xxx                      # 生成复盘报告
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # ===== Story 命令组 =====
    story_parser = subparsers.add_parser('story', help='Story 管理')
    story_subparsers = story_parser.add_subparsers(dest='story_action')
    
    story_create = story_subparsers.add_parser('create', help='创建 Story')
    story_create.add_argument('title', help='Story 标题')
    story_create.add_argument('--creator', '-c', required=True, help='创建者 Agent ID')
    story_create.add_argument('--background', '-b', help='背景说明')
    story_create.add_argument('--priority', '-p', choices=['P0', 'P1', 'P2'], default='P1')
    
    story_get = story_subparsers.add_parser('get', help='获取 Story')
    story_get.add_argument('story_id', help='Story ID')
    
    story_list = story_subparsers.add_parser('list', help='列出 Story')
    story_list.add_argument('--status', choices=['active', 'completed', 'archived'])
    
    # ===== Task 命令组 =====
    task_parser = subparsers.add_parser('task', help='Task 管理')
    task_subparsers = task_parser.add_subparsers(dest='task_action')
    
    task_submit = task_subparsers.add_parser('submit', help='提交 Task 审核')
    task_submit.add_argument('--title', '-t', required=True, help='任务标题')
    task_submit.add_argument('--assignee', '-a', required=True, help='执行人 Agent ID')
    task_submit.add_argument('--story', '-s', required=True, help='关联 Story ID')
    task_submit.add_argument('--priority', '-p', choices=['P0', 'P1', 'P2', 'P3'], default='P1')
    task_submit.add_argument('--deadline', '-d', required=True, type=parse_date, help='截止时间 (ISO 8601)')
    task_submit.add_argument('--description', '-D', help='任务描述')
    task_submit.add_argument('--estimated-hours', '-e', type=float, default=0, help='预估工时')
    
    task_review = task_subparsers.add_parser('review', help='审核 Task')
    task_review.add_argument('task_id', help='Task ID')
    task_review.add_argument('decision', choices=['APPROVED', 'REJECTED'], help='审核决策')
    task_review.add_argument('--reason', '-r', help='拒绝原因（REJECTED 时必填）')
    
    task_status = task_subparsers.add_parser('status', help='更新 Task 状态')
    task_status.add_argument('task_id', help='Task ID')
    task_status.add_argument('new_status', 
                             choices=['draft', 'pending_review', 'rejected', 'approved',
                                     'todo', 'in_progress', 'blocked', 'done'],
                             help='新状态')
    task_status.add_argument('--summary', help='完成摘要')
    task_status.add_argument('--report-file', help='报告文件路径（DONE 时必填）')
    task_status.add_argument('--blocker-reason', help='阻塞原因（BLOCKED 时必填）')
    
    task_get = task_subparsers.add_parser('get', help='获取 Task')
    task_get.add_argument('task_id', help='Task ID')
    
    task_list = task_subparsers.add_parser('list', help='列出 Task')
    task_list.add_argument('--assignee', '-a', help='按执行人筛选')
    task_list.add_argument('--story', '-s', help='按 Story 筛选')
    task_list.add_argument('--status', choices=['draft', 'pending_review', 'rejected', 
                                                 'approved', 'todo', 'in_progress', 
                                                 'blocked', 'done'])
    
    task_queue = task_subparsers.add_parser('queue', help='查看待审核队列')
    
    # ===== Board 命令组 =====
    board_parser = subparsers.add_parser('board', help='查看看板')
    
    # ===== Retro 命令组 =====
    retro_parser = subparsers.add_parser('retro', help='复盘管理')
    retro_subparsers = retro_parser.add_subparsers(dest='retro_action')
    
    retro_create = retro_subparsers.add_parser('create', help='创建复盘')
    retro_create.add_argument('title', help='复盘标题')
    retro_create.add_argument('--type', '-t', required=True, 
                              choices=['sprint', 'project', 'incident', 'custom'],
                              help='复盘类型')
    retro_create.add_argument('--facilitator', '-f', required=True, help='主持人 Agent ID')
    retro_create.add_argument('--template', choices=['mad_sad_glad', 'start_stop_continue', 
                                                      'four_ls', 'custom'],
                              default='mad_sad_glad', help='复盘模板')
    retro_create.add_argument('--participants', help='参与者，逗号分隔')
    retro_create.add_argument('--sprint-id', help='关联迭代ID')
    
    retro_start = retro_subparsers.add_parser('start', help='开始复盘收集阶段')
    retro_start.add_argument('retro_id', help='复盘ID')
    
    retro_item_add = retro_subparsers.add_parser('item-add', help='添加复盘条目')
    retro_item_add.add_argument('retro_id', help='复盘ID')
    retro_item_add.add_argument('category', help='类别 (如: mad, sad, glad)')
    retro_item_add.add_argument('content', help='内容')
    retro_item_add.add_argument('--author', '-a', required=True, help='作者 Agent ID')
    
    retro_item_vote = retro_subparsers.add_parser('item-vote', help='投票')
    retro_item_vote.add_argument('item_id', help='条目ID')
    retro_item_vote.add_argument('--voter', '-v', required=True, help='投票人 Agent ID')
    
    retro_discuss = retro_subparsers.add_parser('discuss', help='开始讨论阶段')
    retro_discuss.add_argument('retro_id', help='复盘ID')
    
    retro_action_add = retro_subparsers.add_parser('action-add', help='添加改进行动')
    retro_action_add.add_argument('retro_id', help='复盘ID')
    retro_action_add.add_argument('title', help='行动标题')
    retro_action_add.add_argument('--assignee', '-a', required=True, help='负责人')
    retro_action_add.add_argument('--due', '-d', required=True, type=parse_date, help='截止日期')
    retro_action_add.add_argument('--priority', '-p', choices=['P0', 'P1', 'P2'], default='P1')
    retro_action_add.add_argument('--description', '-D', help='描述')
    
    retro_complete = retro_subparsers.add_parser('complete', help='完成复盘')
    retro_complete.add_argument('retro_id', help='复盘ID')
    retro_complete.add_argument('--summary', '-s', help='复盘总结')
    
    retro_report = retro_subparsers.add_parser('report', help='生成复盘报告')
    retro_report.add_argument('retro_id', help='复盘ID')
    
    retro_get = retro_subparsers.add_parser('get', help='获取复盘')
    retro_get.add_argument('retro_id', help='复盘ID')
    
    retro_list = retro_subparsers.add_parser('list', help='列出复盘')
    retro_list.add_argument('--type', choices=['sprint', 'project', 'incident', 'custom'])
    retro_list.add_argument('--status', choices=['planning', 'collecting', 'discussing', 
                                                  'completed', 'cancelled'])
    
    retro_actions = retro_subparsers.add_parser('actions', help='列出改进行动')
    retro_actions.add_argument('--retro-id', help='复盘ID')
    retro_actions.add_argument('--assignee', help='负责人')
    retro_actions.add_argument('--status', choices=['pending', 'in_progress', 'done', 'cancelled'])
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    pmo = PMOManagerAPI()
    
    # ===== 处理 Story 命令 =====
    if args.command == 'story':
        if args.story_action == 'create':
            story = pmo.create_story(
                title=args.title,
                creator_id=args.creator,
                background=args.background or "",
                priority=Priority(args.priority)
            )
            print(f"\n✅ Story 创建成功!")
            print(f"   ID: {story.story_id}")
            print(f"   标题: {story.title}")
            print(f"   创建者: {story.creator_id}\n")
        
        elif args.story_action == 'get':
            story = pmo.get_story(args.story_id)
            if story:
                print(f"\n📋 Story: {story.title}")
                print(f"   ID: {story.story_id}")
                print(f"   创建者: {story.creator_id}")
                print(f"   优先级: {story.priority.value if hasattr(story.priority, 'value') else story.priority}")
                print(f"   状态: {story.status}")
                if story.background:
                    print(f"   背景: {story.background}")
                if story.objectives:
                    print(f"   目标: {', '.join(story.objectives)}")
                print()
            else:
                print(f"❌ Story '{args.story_id}' 不存在")
                sys.exit(1)
        
        elif args.story_action == 'list':
            stories = pmo.list_stories(status=args.status)
            print(f"\n📋 Story 列表 ({len(stories)} 个):\n")
            for s in stories:
                p = s.priority.value if hasattr(s.priority, 'value') else s.priority
                print(f"  [{p}] {s.title} ({s.story_id}) - {s.status}")
            print()
    
    # ===== 处理 Task 命令 =====
    elif args.command == 'task':
        if args.task_action == 'submit':
            result = pmo.submit_task(
                title=args.title,
                assignee_id=args.assignee,
                story_id=args.story,
                priority=Priority(args.priority),
                deadline=args.deadline,
                description=args.description or "",
                estimated_hours=args.estimated_hours
            )
            
            if result['success']:
                print(f"\n✅ {result['message']}")
                print(f"   Task ID: {result['task'].task_id}\n")
            else:
                print(f"\n❌ 提交失败:")
                for error in result['errors']:
                    print(f"   - {error}")
                print()
                sys.exit(1)
        
        elif args.task_action == 'review':
            result = pmo.review_task(args.task_id, args.decision, args.reason)
            if result['success']:
                print(f"\n✅ {result['message']}\n")
            else:
                print(f"\n❌ {result['message']}\n")
                sys.exit(1)
        
        elif args.task_action == 'status':
            result = pmo.update_task_status(
                args.task_id, args.new_status,
                output_summary=args.summary,
                report_file=args.report_file,
                blocker_reason=args.blocker_reason
            )
            if result['success']:
                print(f"\n✅ {result['message']}\n")
            else:
                print(f"\n❌ {result['message']}\n")
                sys.exit(1)
        
        elif args.task_action == 'get':
            task = pmo.get_task(args.task_id)
            if task:
                print("\n" + format_task(task) + "\n")
            else:
                print(f"❌ Task '{args.task_id}' 不存在")
                sys.exit(1)
        
        elif args.task_action == 'list':
            tasks = pmo.list_tasks(
                assignee_id=args.assignee,
                story_id=args.story,
                status=args.status
            )
            print(f"\n📝 Task 列表 ({len(tasks)} 个):\n")
            for t in tasks:
                print(format_task(t))
                print()
        
        elif args.task_action == 'queue':
            tasks = pmo.get_review_queue()
            print(f"\n⏳ 待审核队列 ({len(tasks)} 个):\n")
            for t in tasks:
                print(format_task(t))
                print()
    
    # ===== 处理 Board 命令 =====
    elif args.command == 'board':
        board = pmo.get_board()
        print("\n" + "=" * 60)
        print("           📊 PMO 看板")
        print("=" * 60 + "\n")
        
        status_names = {
            "draft": "📝 草稿",
            "pending_review": "⏳ 待审核",
            "rejected": "❌ 已拒绝",
            "approved": "✅ 已批准",
            "todo": "📋 待办",
            "in_progress": "🔄 进行中",
            "blocked": "🚫 阻塞",
            "done": "✓ 已完成",
        }
        
        for status, tasks in board.items():
            if tasks:
                print(f"{status_names.get(status, status)} ({len(tasks)}):")
                for t in tasks:
                    p = t.priority.value if hasattr(t.priority, 'value') else str(t.priority)
                    print(f"  • [{p}] {t.title} ({t.assignee_id})")
                print()
    
    # ===== 处理 Retro 命令 =====
    elif args.command == 'retro':
        if args.retro_action == 'create':
            participants = args.participants.split(',') if args.participants else []
            retro = pmo.create_retro(
                title=args.title,
                retro_type=args.type,
                facilitator_id=args.facilitator,
                template=args.template,
                participants=participants,
                sprint_id=args.sprint_id
            )
            print(f"\n✅ 复盘创建成功!")
            print(f"   ID: {retro.retro_id}")
            print(f"   标题: {retro.title}")
            print(f"   模板: {retro.template.value if hasattr(retro.template, 'value') else retro.template}\n")
        
        elif args.retro_action == 'start':
            result = pmo.start_retro_collecting(args.retro_id)
            if result['success']:
                print(f"\n✅ 复盘已进入收集阶段")
                print(f"   可用类别: {', '.join(result['categories'])}\n")
            else:
                print(f"\n❌ {result['message']}\n")
                sys.exit(1)
        
        elif args.retro_action == 'item-add':
            result = pmo.add_retro_item(args.retro_id, args.category, args.content, args.author)
            if result['success']:
                print(f"\n✅ 反馈已添加")
                print(f"   Item ID: {result['item'].item_id}\n")
            else:
                print(f"\n❌ {result['message']}\n")
                sys.exit(1)
        
        elif args.retro_action == 'item-vote':
            result = pmo.vote_retro_item(args.item_id, args.voter)
            if result['success']:
                print(f"\n✅ {result['message']}\n")
            else:
                print(f"\n❌ {result['message']}\n")
                sys.exit(1)
        
        elif args.retro_action == 'discuss':
            result = pmo.start_retro_discussing(args.retro_id)
            if result['success']:
                print(f"\n💬 复盘已进入讨论阶段")
                print(f"   共 {len(result['items'])} 条反馈，总计 {result['total_votes']} 票\n")
            else:
                print(f"\n❌ {result['message']}\n")
                sys.exit(1)
        
        elif args.retro_action == 'action-add':
            result = pmo.create_action_item(
                args.retro_id, args.title, args.assignee,
                args.due.date() if hasattr(args.due, 'date') else args.due,
                args.priority, args.description or ""
            )
            if result['success']:
                print(f"\n✅ 改进行动已创建")
                print(f"   Action ID: {result['action_item'].action_id}\n")
            else:
                print(f"\n❌ {result['message']}\n")
                sys.exit(1)
        
        elif args.retro_action == 'complete':
            result = pmo.complete_retro(args.retro_id, args.summary or "")
            if result['success']:
                print(f"\n✅ 复盘已完成")
                print(f"   共 {len(result['items'])} 条反馈")
                print(f"   共 {len(result['action_items'])} 个改进行动\n")
            else:
                print(f"\n❌ {result['message']}\n")
                sys.exit(1)
        
        elif args.retro_action == 'report':
            result = pmo.generate_retro_report(args.retro_id)
            if result['success']:
                print("\n" + "=" * 60)
                print(result['report_markdown'])
                print("=" * 60 + "\n")
            else:
                print(f"\n❌ {result['message']}\n")
                sys.exit(1)
        
        elif args.retro_action == 'get':
            retro = pmo.get_retro(args.retro_id)
            if retro:
                print(f"\n{format_retro(retro)}")
                print(f"   主持人: {retro.facilitator_id}")
                print(f"   参与者: {', '.join(retro.participants)}")
                print()
            else:
                print(f"❌ Retro '{args.retro_id}' 不存在")
                sys.exit(1)
        
        elif args.retro_action == 'list':
            retros = pmo.list_retros(retro_type=args.type, status=args.status)
            print(f"\n📊 复盘列表 ({len(retros)} 个):\n")
            for r in retros:
                print(format_retro(r))
            print()
        
        elif args.retro_action == 'actions':
            actions = pmo.list_action_items(
                retro_id=args.retro_id,
                assignee_id=args.assignee,
                status=args.status
            )
            print(f"\n🎯 改进行动列表 ({len(actions)} 个):\n")
            for a in actions:
                p = a.priority.value if hasattr(a.priority, 'value') else a.priority
                due = a.due_date.isoformat() if hasattr(a.due_date, 'isoformat') else str(a.due_date)
                print(f"  [{p}] {a.title}")
                print(f"     负责人: {a.assignee_id} | 截止: {due} | 状态: {a.status}")
            print()


if __name__ == '__main__':
    main()
