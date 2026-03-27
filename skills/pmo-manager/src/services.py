"""
核心业务逻辑服务
"""

from typing import List, Optional, Dict
from datetime import datetime, date, timedelta
from .models import (
    Story, Task, Retro, RetroItem, ActionItem, Iteration,
    TaskStatus, Priority, RetroType, RetroStatus, RetroTemplate
)
from .storage import Storage
from .validators import TaskValidator


class StoryService:
    """Story 服务 - 管理顶层需求"""
    
    def __init__(self, storage: Storage):
        self.storage = storage
    
    def create_story(self, title: str, creator_id: str, background: str = "",
                     objectives: List[str] = None, acceptance_criteria: List[str] = None,
                     priority: Priority = Priority.P1) -> Story:
        """创建 Story"""
        story = Story.create(title, creator_id, background, objectives, acceptance_criteria, priority)
        self.storage.save_story(story)
        return story
    
    def get_story(self, story_id: str) -> Optional[Story]:
        """获取 Story"""
        return self.storage.get_story(story_id)
    
    def list_stories(self, status: str = None) -> List[Story]:
        """列出 Story"""
        return self.storage.list_stories(status)


class TaskService:
    """Task 服务 - 管理任务生命周期"""
    
    def __init__(self, storage: Storage):
        self.storage = storage
        self.validator = TaskValidator(storage)
    
    def submit_task(self, title: str, assignee_id: str, story_id: str,
                    priority: Priority, deadline: datetime, description: str = "",
                    solution: str = "", start_time: datetime = None,
                    estimated_hours: float = 0.0) -> Dict:
        """
        提交 Task 审核
        
        Returns:
            {"success": bool, "task": Task, "errors": List[str]}
        """
        # 合规校验
        validation = self.validator.validate_task_submission(
            title, assignee_id, story_id, deadline, description
        )
        
        if not validation["valid"]:
            return {
                "success": False,
                "task": None,
                "errors": validation["errors"]
            }
        
        # 创建 Task
        task = Task.submit(title, assignee_id, story_id, priority, deadline,
                          description, solution, start_time, estimated_hours)
        
        self.storage.save_task(task)
        
        return {
            "success": True,
            "task": task,
            "message": f"Task '{task.task_id}' 已提交至 PMO 审核队列"
        }
    
    def review_task(self, task_id: str, decision: str, 
                    rejection_reason: str = None) -> Dict:
        """
        PMO 审核 Task
        
        Args:
            task_id: Task ID
            decision: "APPROVED" 或 "REJECTED"
            rejection_reason: 拒绝原因（REJECTED 时必填）
        
        Returns:
            {"success": bool, "task": Task, "message": str}
        """
        task = self.storage.get_task(task_id)
        if not task:
            return {"success": False, "task": None, "message": f"Task '{task_id}' 不存在"}
        
        if decision.upper() == "APPROVED":
            task.approve()
            # 批准后自动转为 TODO
            task.status = TaskStatus.TODO
            self.storage.save_task(task)
            return {"success": True, "task": task, "message": f"Task '{task_id}' 已批准"}
        
        elif decision.upper() == "REJECTED":
            if not rejection_reason:
                return {"success": False, "task": None, "message": "拒绝时必须提供原因"}
            task.reject(rejection_reason)
            self.storage.save_task(task)
            return {"success": True, "task": task, "message": f"Task '{task_id}' 已拒绝: {rejection_reason}"}
        
        else:
            return {"success": False, "task": None, "message": f"无效决策: {decision}"}
    
    def get_review_queue(self) -> List[Task]:
        """获取待审核队列"""
        return self.storage.get_review_queue()
    
    def update_task_status(self, task_id: str, new_status: str, 
                           output_summary: str = None, report_file: str = None,
                           blocker_reason: str = None) -> Dict:
        """
        更新 Task 状态
        
        Returns:
            {"success": bool, "task": Task, "message": str}
        """
        task = self.storage.get_task(task_id)
        if not task:
            return {"success": False, "task": None, "message": f"Task '{task_id}' 不存在"}
        
        # 状态流转校验
        validation = self.validator.validate_state_transition(task_id, new_status)
        if not validation["valid"]:
            return {"success": False, "task": None, "message": "; ".join(validation["errors"])}
        
        # 如果是 DONE，必须提供 report_file
        if new_status == "done":
            validation = self.validator.validate_task_completion(task_id, report_file)
            if not validation["valid"]:
                return {"success": False, "task": None, "message": "; ".join(validation["errors"])}
            task.complete(output_summary or "", report_file)
        
        elif new_status == "blocked":
            if not blocker_reason:
                return {"success": False, "task": None, "message": "BLOCKED 状态必须提供阻塞原因"}
            task.block(blocker_reason)
        
        elif new_status == "in_progress":
            task.start()
        
        else:
            # 其他状态直接更新
            from .models import TaskStatus
            task.status = TaskStatus(new_status)
            task.updated_at = datetime.now()
        
        self.storage.save_task(task)
        
        return {"success": True, "task": task, "message": f"Task '{task_id}' 状态已更新为 {new_status}"}
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取 Task"""
        return self.storage.get_task(task_id)
    
    def list_tasks(self, assignee_id: str = None, story_id: str = None,
                   status: str = None) -> List[Task]:
        """列出 Task"""
        return self.storage.list_tasks(assignee_id, story_id, status)
    
    def get_board(self) -> Dict:
        """
        生成看板数据
        
        Returns:
            按状态分组的 Task 列表
        """
        all_tasks = self.storage.list_tasks()
        
        board = {
            "draft": [],
            "pending_review": [],
            "rejected": [],
            "approved": [],
            "todo": [],
            "in_progress": [],
            "blocked": [],
            "done": [],
        }
        
        for task in all_tasks:
            status = task.status.value if hasattr(task.status, 'value') else str(task.status)
            if status in board:
                board[status].append(task)
        
        return board


class RetroService:
    """Retro 服务 - 管理复盘"""
    
    def __init__(self, storage: Storage):
        self.storage = storage
    
    def create_retro(self, title: str, retro_type: RetroType, facilitator_id: str,
                     template: RetroTemplate = RetroTemplate.MAD_SAD_GLAD,
                     participants: List[str] = None, sprint_id: str = None,
                     project_name: str = None, incident_id: str = None) -> Retro:
        """创建复盘"""
        retro = Retro.create(title, retro_type, facilitator_id, template, participants)
        retro.sprint_id = sprint_id
        retro.project_name = project_name
        retro.incident_id = incident_id
        
        self.storage.save_retro(retro)
        return retro
    
    def start_collecting(self, retro_id: str) -> Dict:
        """开始收集反馈"""
        retro = self.storage.get_retro(retro_id)
        if not retro:
            return {"success": False, "message": f"Retro '{retro_id}' 不存在"}
        
        retro.start_collecting()
        self.storage.save_retro(retro)
        
        # 根据模板返回类别
        template_categories = {
            RetroTemplate.MAD_SAD_GLAD: ["mad", "sad", "glad"],
            RetroTemplate.START_STOP_CONTINUE: ["start", "stop", "continue"],
            RetroTemplate.FOUR_LS: ["liked", "learned", "lacked", "longed_for"],
            RetroTemplate.CUSTOM: retro.custom_columns if retro.custom_columns else ["feedback"],
        }
        
        return {
            "success": True,
            "retro": retro,
            "categories": template_categories.get(retro.template, ["feedback"])
        }
    
    def add_item(self, retro_id: str, category: str, content: str, 
                 author_id: str) -> Dict:
        """添加复盘条目"""
        retro = self.storage.get_retro(retro_id)
        if not retro:
            return {"success": False, "message": f"Retro '{retro_id}' 不存在"}
        
        if retro.status not in [RetroStatus.COLLECTING, RetroStatus.DISCUSSING]:
            return {"success": False, "message": f"复盘当前状态 '{retro.status.value}' 不允许添加条目"}
        
        item = RetroItem.create(retro_id, category, content, author_id)
        self.storage.save_retro_item(item)
        
        return {"success": True, "item": item}
    
    def vote_item(self, item_id: str, voter_id: str) -> Dict:
        """为复盘条目投票"""
        item = self.storage.get_retro_item(item_id)
        if not item:
            return {"success": False, "message": f"Item '{item_id}' 不存在"}
        
        if voter_id in item.voters:
            return {"success": False, "message": "您已经投过票了"}
        
        item.vote(voter_id)
        self.storage.save_retro_item(item)
        
        return {"success": True, "item": item, "message": f"投票成功，当前票数: {item.votes}"}
    
    def discuss_item(self, item_id: str, notes: str) -> Dict:
        """记录讨论笔记"""
        item = self.storage.get_retro_item(item_id)
        if not item:
            return {"success": False, "message": f"Item '{item_id}' 不存在"}
        
        item.discussion_notes = notes
        self.storage.save_retro_item(item)
        
        return {"success": True, "item": item}
    
    def start_discussing(self, retro_id: str) -> Dict:
        """开始讨论阶段"""
        retro = self.storage.get_retro(retro_id)
        if not retro:
            return {"success": False, "message": f"Retro '{retro_id}' 不存在"}
        
        retro.start_discussing()
        self.storage.save_retro(retro)
        
        # 获取所有条目
        items = self.storage.list_retro_items(retro_id)
        
        return {
            "success": True,
            "retro": retro,
            "items": items,
            "total_votes": sum(item.votes for item in items)
        }
    
    def create_action_item(self, retro_id: str, title: str, assignee_id: str,
                           due_date: date, priority: Priority = Priority.P1,
                           description: str = "", related_item_ids: List[str] = None) -> Dict:
        """创建改进行动"""
        retro = self.storage.get_retro(retro_id)
        if not retro:
            return {"success": False, "message": f"Retro '{retro_id}' 不存在"}
        
        action = ActionItem.create(retro_id, title, assignee_id, due_date, priority, description)
        if related_item_ids:
            action.related_item_ids = related_item_ids
        
        self.storage.save_action_item(action)
        
        return {"success": True, "action_item": action}
    
    def complete_action_item(self, action_id: str, verification_method: str,
                             verified_by: str) -> Dict:
        """完成改进行动"""
        action = self.storage.get_action_item(action_id)
        if not action:
            return {"success": False, "message": f"Action Item '{action_id}' 不存在"}
        
        action.complete(verification_method, verified_by)
        self.storage.save_action_item(action)
        
        return {"success": True, "action_item": action}
    
    def complete_retro(self, retro_id: str, summary: str = "") -> Dict:
        """完成复盘"""
        retro = self.storage.get_retro(retro_id)
        if not retro:
            return {"success": False, "message": f"Retro '{retro_id}' 不存在"}
        
        retro.complete(summary)
        self.storage.save_retro(retro)
        
        # 获取完整数据用于生成报告
        items = self.storage.list_retro_items(retro_id)
        actions = self.storage.list_action_items(retro_id=retro_id)
        
        return {
            "success": True,
            "retro": retro,
            "items": items,
            "action_items": actions,
        }
    
    def generate_report(self, retro_id: str) -> Dict:
        """生成复盘报告"""
        retro = self.storage.get_retro(retro_id)
        if not retro:
            return {"success": False, "message": f"Retro '{retro_id}' 不存在"}
        
        items = self.storage.list_retro_items(retro_id)
        actions = self.storage.list_action_items(retro_id=retro_id)
        
        # 按类别统计
        categories = {}
        for item in items:
            cat = item.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(item)
        
        # 生成 Markdown 报告
        report = self._generate_markdown_report(retro, items, actions, categories)
        
        return {
            "success": True,
            "retro": retro,
            "report_markdown": report,
            "stats": {
                "total_items": len(items),
                "total_votes": sum(item.votes for item in items),
                "total_actions": len(actions),
                "categories": {cat: len(items) for cat, items in categories.items()}
            }
        }
    
    def _generate_markdown_report(self, retro: Retro, items: List[RetroItem],
                                   actions: List[ActionItem], categories: Dict) -> str:
        """生成 Markdown 格式报告"""
        lines = [
            f"# Retro 复盘报告: {retro.title}",
            "",
            "## 基本信息",
            f"- **复盘类型**: {retro.retro_type.value if hasattr(retro.retro_type, 'value') else retro.retro_type}",
            f"- **主持人**: {retro.facilitator_id}",
            f"- **参与人员**: {', '.join(retro.participants)}",
            f"- **复盘日期**: {retro.completed_at or '未完成'}",
            "",
            "## 统计数据",
            f"- **收集条目数**: {len(items)}",
            f"- **投票总数**: {sum(item.votes for item in items)}",
            f"- **改进行动数**: {len(actions)}",
            f"- **P0 改进项**: {sum(1 for a in actions if a.priority == Priority.P0)}",
            "",
            "## 反馈汇总",
            "",
        ]
        
        for cat_name, cat_items in categories.items():
            lines.append(f"### {cat_name.upper()} ({len(cat_items)} 条)")
            lines.append("")
            for i, item in enumerate(sorted(cat_items, key=lambda x: x.votes, reverse=True), 1):
                lines.append(f"{i}. **{item.content}** ({item.votes} 票)")
                lines.append(f"   - 作者: {item.author_id}")
                if item.discussion_notes:
                    lines.append(f"   - 讨论: {item.discussion_notes}")
                lines.append("")
        
        lines.extend([
            "## 改进行动计划",
            "",
            "| 优先级 | 行动项 | 负责人 | 截止日期 | 状态 |",
            "|--------|--------|--------|----------|------|",
        ])
        
        for action in sorted(actions, key=lambda x: x.priority.value if hasattr(x.priority, 'value') else x.priority):
            priority = action.priority.value if hasattr(action.priority, 'value') else action.priority
            due = action.due_date.isoformat() if hasattr(action.due_date, 'isoformat') else str(action.due_date)
            lines.append(f"| {priority} | {action.title} | {action.assignee_id} | {due} | {action.status} |")
        
        lines.extend([
            "",
            "## 复盘总结",
            retro.summary or "（暂无总结）",
            "",
            "---",
            f"报告生成时间: {datetime.now().isoformat()}",
            "PMO Manager Skill v1.0",
        ])
        
        return "\n".join(lines)
    
    def get_retro(self, retro_id: str) -> Optional[Retro]:
        """获取复盘"""
        return self.storage.get_retro(retro_id)
    
    def list_retros(self, retro_type: str = None, status: str = None, limit: int = 50) -> List[Retro]:
        """列出复盘"""
        return self.storage.list_retros(retro_type, status, limit)
    
    def list_action_items(self, retro_id: str = None, assignee_id: str = None,
                          status: str = None) -> List[ActionItem]:
        """列出改进行动"""
        return self.storage.list_action_items(retro_id, assignee_id, status)


class IterationService:
    """Iteration 服务 - 管理迭代"""
    
    def __init__(self, storage: Storage):
        self.storage = storage
    
    def create_iteration(self, name: str, goal: str, start_date: date, 
                         end_date: date) -> Iteration:
        """创建迭代"""
        iteration = Iteration.create(name, goal, start_date, end_date)
        self.storage.save_iteration(iteration)
        return iteration
    
    def get_iteration(self, iteration_id: str) -> Optional[Iteration]:
        """获取迭代"""
        return self.storage.get_iteration(iteration_id)
    
    def list_iterations(self, status: str = None) -> List[Iteration]:
        """列出迭代"""
        return self.storage.list_iterations(status)
    
    def get_stats(self, iteration_id: str) -> Dict:
        """获取迭代统计"""
        iteration = self.storage.get_iteration(iteration_id)
        if not iteration:
            return {"success": False, "message": f"Iteration '{iteration_id}' 不存在"}
        
        # 获取关联的 Tasks
        tasks = []
        for story_id in iteration.story_ids:
            tasks.extend(self.storage.list_tasks(story_id=story_id))
        
        total = len(tasks)
        done = sum(1 for t in tasks if str(t.status) in ['done', 'TaskStatus.DONE'])
        in_progress = sum(1 for t in tasks if str(t.status) in ['in_progress', 'TaskStatus.IN_PROGRESS'])
        todo = sum(1 for t in tasks if str(t.status) in ['todo', 'TaskStatus.TODO'])
        blocked = sum(1 for t in tasks if str(t.status) in ['blocked', 'TaskStatus.BLOCKED'])
        
        completion_rate = (done / total * 100) if total > 0 else 0
        
        return {
            "success": True,
            "iteration": iteration,
            "stats": {
                "total_tasks": total,
                "done": done,
                "in_progress": in_progress,
                "todo": todo,
                "blocked": blocked,
                "completion_rate": round(completion_rate, 2),
            }
        }
