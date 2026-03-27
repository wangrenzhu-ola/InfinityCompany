#!/usr/bin/env python3
"""
InfinityCompany 定时任务调度器

执行每日定时任务，如健康提醒、早会、复盘等。
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path


SCHEDULE_CONFIG = {
    "08:30": {
        "name": "health_reminder",
        "description": "健康提醒、饮水提醒、早餐建议",
        "agent": "xiahouying",  # 私人助理
        "action": "health_check"
    },
    "09:00": {
        "name": "external_sync",
        "description": "汇总夜间外部消息并登记到 Notion",
        "agent": "lishiyi",  # 外部助理
        "action": "sync_external_requests"
    },
    "09:15": {
        "name": "intent_recognition",
        "description": "读取外部需求看板与老板待办，做意图识别和分发建议",
        "agent": "xiahouying",  # 私人助理
        "action": "analyze_pending_tasks"
    },
    "09:30": {
        "name": "daily_standup",
        "description": "组织早会，建立当日迭代目标、阻塞项和负责人",
        "agent": "caocan",  # PMO
        "action": "start_daily_iteration"
    },
    "10:00": {
        "name": "product_sync",
        "description": "校准当日需求优先级、验收口径与待验收清单",
        "agent": "zhangliang",  # 产品经理
        "action": "sync_product_backlog"
    },
    "11:00": {
        "name": "knowledge_sync",
        "description": "维护迭代看板、外部需求看板、Bug 看板，并校验 Notion 与 OpenViking 同步",
        "agent": "lujia",  # 知识库管理员
        "action": "sync_knowledge_bases"
    },
    "14:00": {
        "name": "dev_checkin",
        "description": "研发推进检查、联调状态同步、Bug 单更新",
        "agent": "caocan",  # PMO
        "action": "check_dev_progress"
    },
    "17:30": {
        "name": "product_acceptance",
        "description": "执行功能点验收，失败则打回并新增或重开 Bug 单",
        "agent": "zhangliang",  # 产品经理
        "action": "acceptance_review"
    },
    "18:00": {
        "name": "deployment_check",
        "description": "检查当日附着环境、发布准备与回滚条件",
        "agent": "zhoubo",  # 运维
        "action": "check_deployment_readiness"
    },
    "19:00": {
        "name": "daily_retrospective",
        "description": "组织晚间复盘会，记录产出、阻塞、风险和次日建议",
        "agent": "caocan",  # PMO
        "action": "run_retrospective"
    },
    "21:00": {
        "name": "external_wrapup",
        "description": "更新晚间外部沟通结果并同步外部需求看板",
        "agent": "lishiyi",  # 外部助理
        "action": "wrapup_external_comms"
    }
}


class Scheduler:
    """定时任务调度器"""
    
    def __init__(self, log_dir: str = None):
        self.log_dir = log_dir or os.path.expanduser("~/.openclaw/logs/scheduler")
        os.makedirs(self.log_dir, exist_ok=True)
        self.pid_file = os.path.expanduser("~/.openclaw/scheduler.pid")
    
    def list_tasks(self) -> None:
        """列出所有定时任务"""
        print("=== InfinityCompany 每日定时任务 ===\n")
        print(f"{'时间':<10} {'任务名称':<25} {'执行角色':<15} {'描述'}")
        print("-" * 80)
        
        for time_str, task in sorted(SCHEDULE_CONFIG.items()):
            print(f"{time_str:<10} {task['name']:<25} {task['agent']:<15} {task['description'][:30]}...")
        
        print(f"\n共 {len(SCHEDULE_CONFIG)} 个定时任务")
    
    def run_task(self, task_name: str) -> bool:
        """
        手动执行指定任务
        
        Args:
            task_name: 任务名称
            
        Returns:
            是否成功
        """
        # 查找任务
        task = None
        for time_str, t in SCHEDULE_CONFIG.items():
            if t['name'] == task_name:
                task = t
                task['scheduled_time'] = time_str
                break
        
        if not task:
            print(f"❌ 任务 '{task_name}' 不存在")
            return False
        
        print(f"=== 执行任务: {task_name} ===")
        print(f"时间: {task.get('scheduled_time', '手动')}")
        print(f"角色: {task['agent']}")
        print(f"描述: {task['description']}")
        print()
        
        # 记录执行日志
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task_name": task_name,
            "agent": task['agent'],
            "action": task['action'],
            "status": "running"
        }
        
        # 这里模拟任务执行
        # 实际实现中，这里会通过 acpx 或其他方式触发 Agent 执行任务
        print(f"🤖 通知 Agent '{task['agent']}' 执行动作 '{task['action']}'")
        print("   (实际执行需要通过 acpx 或邮件触发)")
        
        # 发送邮件通知（模拟）
        self._notify_agent(task['agent'], task['action'], task['description'])
        
        log_entry['status'] = 'completed'
        self._write_log(log_entry)
        
        print(f"\n✅ 任务 '{task_name}' 已触发")
        return True
    
    def _notify_agent(self, agent_id: str, action: str, description: str) -> None:
        """通知 Agent 执行任务"""
        # 使用 company-directory 的 email 功能发送通知
        try:
            sys.path.insert(0, os.path.expanduser("~/.openclaw/workspace/skills/company-directory"))
            from src.api import CompanyDirectoryAPI
            
            api = CompanyDirectoryAPI()
            result = api.send_email(
                target_id=agent_id,
                subject=f"[定时任务] {action}",
                message=f"""
这是一个定时任务通知。

任务: {action}
描述: {description}
时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

请按照日常流程执行此任务。
""",
                sender_id="system",
                urgency="normal",
                msg_type="action_required"
            )
            
            if result['status'] == 'success':
                print(f"   ✅ 已发送通知给 {agent_id}")
            else:
                print(f"   ⚠️  通知发送失败: {result.get('message')}")
                
        except Exception as e:
            print(f"   ⚠️  通知发送异常: {e}")
    
    def _write_log(self, entry: Dict) -> None:
        """写入执行日志"""
        log_file = os.path.join(self.log_dir, f"{datetime.now().strftime('%Y%m%d')}.jsonl")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def show_logs(self, date: str = None, limit: int = 20) -> None:
        """
        显示执行日志
        
        Args:
            date: 日期 (YYYYMMDD)，默认为今天
            limit: 显示条数
        """
        if date is None:
            date = datetime.now().strftime('%Y%m%d')
        
        log_file = os.path.join(self.log_dir, f"{date}.jsonl")
        
        if not os.path.exists(log_file):
            print(f"📭 没有找到 {date} 的日志")
            return
        
        print(f"=== 执行日志 ({date}) ===\n")
        
        entries = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
        
        # 显示最近的记录
        for entry in entries[-limit:]:
            time_str = entry['timestamp'][11:19]  # 提取时间部分
            status_emoji = "✅" if entry['status'] == 'completed' else "❌" if entry['status'] == 'failed' else "⏳"
            print(f"{time_str} {status_emoji} {entry['task_name']} ({entry['agent']})")
        
        print(f"\n显示 {min(len(entries), limit)}/{len(entries)} 条记录")
    
    def generate_cron(self) -> str:
        """生成 cron 表达式"""
        cron_lines = ["# InfinityCompany 定时任务"]
        
        for time_str, task in sorted(SCHEDULE_CONFIG.items()):
            hour, minute = time_str.split(':')
            cron_line = f"{minute} {hour} * * * cd {os.path.expanduser('~/.openclaw/workspace/skills/scheduler')} && python3 scheduler.py run {task['name']} >> ~/.openclaw/logs/scheduler/cron.log 2>&1"
            cron_lines.append(f"# {task['description']}")
            cron_lines.append(cron_line)
        
        return '\n'.join(cron_lines)
    
    def install_cron(self) -> None:
        """安装 cron 任务"""
        import tempfile
        
        # 获取现有 crontab
        try:
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            existing = result.stdout if result.returncode == 0 else ""
        except:
            existing = ""
        
        # 生成新的 crontab（移除旧的 InfinityCompany 任务）
        lines = existing.split('\n')
        new_lines = []
        skip = False
        for line in lines:
            if '# InfinityCompany 定时任务' in line:
                skip = True
                continue
            if skip and line.startswith('#'):
                skip = False
            if not skip:
                new_lines.append(line)
        
        # 添加新任务
        new_crontab = '\n'.join(new_lines) + '\n' + self.generate_cron()
        
        # 写入临时文件并安装
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cron', delete=False) as f:
            f.write(new_crontab)
            temp_file = f.name
        
        try:
            subprocess.run(['crontab', temp_file], check=True)
            print("✅ 定时任务已安装到 cron")
            print("\n任务列表:")
            self.list_tasks()
        finally:
            os.unlink(temp_file)
    
    def uninstall_cron(self) -> None:
        """卸载 cron 任务"""
        try:
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            existing = result.stdout if result.returncode == 0 else ""
        except:
            existing = ""
        
        # 移除 InfinityCompany 任务
        lines = existing.split('\n')
        new_lines = []
        skip = False
        for line in lines:
            if '# InfinityCompany 定时任务' in line:
                skip = True
                continue
            if skip and line.startswith('#'):
                skip = False
                continue
            if skip:
                continue
            new_lines.append(line)
        
        new_crontab = '\n'.join(new_lines)
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cron', delete=False) as f:
            f.write(new_crontab)
            temp_file = f.name
        
        try:
            subprocess.run(['crontab', temp_file], check=True)
            print("✅ 定时任务已从 cron 移除")
        finally:
            os.unlink(temp_file)


def main():
    parser = argparse.ArgumentParser(
        prog='scheduler',
        description='InfinityCompany 定时任务调度器'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # list 命令
    list_parser = subparsers.add_parser('list', help='列出所有定时任务')
    
    # run 命令
    run_parser = subparsers.add_parser('run', help='手动执行指定任务')
    run_parser.add_argument('task_name', help='任务名称')
    
    # logs 命令
    logs_parser = subparsers.add_parser('logs', help='查看执行日志')
    logs_parser.add_argument('--date', '-d', help='日期 (YYYYMMDD)')
    logs_parser.add_argument('--limit', '-l', type=int, default=20, help='显示条数')
    
    # install 命令
    install_parser = subparsers.add_parser('install', help='安装 cron 任务')
    
    # uninstall 命令
    uninstall_parser = subparsers.add_parser('uninstall', help='卸载 cron 任务')
    
    # cron 命令（显示 cron 表达式）
    cron_parser = subparsers.add_parser('cron', help='显示 cron 表达式')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    scheduler = Scheduler()
    
    if args.command == 'list':
        scheduler.list_tasks()
    elif args.command == 'run':
        success = scheduler.run_task(args.task_name)
        sys.exit(0 if success else 1)
    elif args.command == 'logs':
        scheduler.show_logs(args.date, args.limit)
    elif args.command == 'install':
        scheduler.install_cron()
    elif args.command == 'uninstall':
        scheduler.uninstall_cron()
    elif args.command == 'cron':
        print(scheduler.generate_cron())


if __name__ == '__main__':
    main()
