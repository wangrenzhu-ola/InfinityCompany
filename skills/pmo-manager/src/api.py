"""
Python API 层

提供 PMO Manager Skill 的 Python 编程接口
"""

from typing import List, Optional, Dict
from datetime import datetime, date
from .models import (
    Story, Task, Retro, RetroItem, ActionItem, Iteration,
    TaskStatus, Priority, RetroType, RetroStatus, RetroTemplate
)
from .services import StoryService, TaskService, RetroService, IterationService
from .storage import Storage


class PMOManagerAPI:
    """
    PMO Manager Skill 的 Python API
    
    使用示例:
        from pmo_manager import PMOManagerAPI
        
        pmo = PMOManagerAPI()
        
        # 创建 Story
        story = pmo.create_story("用户认证模块", "liubang")
        
        # 提交 Task
        result = pmo.submit_task(
            title="实现登录接口",
            assignee_id="hanxin",
            story_id=story.story_id,
            priority=Priority.P1,
            deadline=datetime(2026, 4, 1, 17, 0)
        )
    """
    
    def __init__(self, db_path: str = None):
        """
        初始化 API
        
        Args:
            db_path: 数据库文件路径
        """
        self.storage = Storage(db_path)
        self.story_service = StoryService(self.storage)
        self.task_service = TaskService(self.storage)
        self.retro_service = RetroService(self.storage)
        self.iteration_service = IterationService(self.storage)
    
    # ========== Story 接口 ==========
    
    def create_story(self, title: str, creator_id: str, background: str = "",
                     objectives: List[str] = None, acceptance_criteria: List[str] = None,
                     priority: Priority = Priority.P1) -> Story:
        """
        创建 Story（顶层需求）
        
        Args:
            title: 标题
            creator_id: 创建者 Agent ID
            background: 背景说明
            objectives: 目标列表
            acceptance_criteria: 验收标准
            priority: 优先级
            
        Returns:
            Story 对象
        """
        return self.story_service.create_story(title, creator_id, background,
                                               objectives, acceptance_criteria, priority)
    
    def get_story(self, story_id: str) -> Optional[Story]:
        """获取 Story"""
        return self.story_service.get_story(story_id)
    
    def list_stories(self, status: str = None) -> List[Story]:
        """列出 Story"""
        return self.story_service.list_stories(status)
    
    # ========== Task 接口 ==========
    
    def submit_task(self, title: str, assignee_id: str, story_id: str,
                    priority: Priority, deadline: datetime, description: str = "",
                    solution: str = "", start_time: datetime = None,
                    estimated_hours: float = 0.0) -> Dict:
        """
        提交 Task 审核
        
        Args:
            title: 任务标题
            assignee_id: 执行人 Agent ID
            story_id: 关联 Story ID
            priority: 优先级
            deadline: 截止时间
            description: 描述
            solution: 解决方案要点
            start_time: 开始时间
            estimated_hours: 预估工时
            
        Returns:
            {"success": bool, "task": Task, "message": str}
        """
        return self.task_service.submit_task(title, assignee_id, story_id, priority,
                                             deadline, description, solution, start_time,
                                             estimated_hours)
    
    def review_task(self, task_id: str, decision: str, 
                    rejection_reason: str = None) -> Dict:
        """
        审核 Task
        
        Args:
            task_id: Task ID
            decision: "APPROVED" 或 "REJECTED"
            rejection_reason: 拒绝原因
            
        Returns:
            {"success": bool, "task": Task, "message": str}
        """
        return self.task_service.review_task(task_id, decision, rejection_reason)
    
    def get_review_queue(self) -> List[Task]:
        """获取待审核队列"""
        return self.task_service.get_review_queue()
    
    def update_task_status(self, task_id: str, new_status: str, 
                           output_summary: str = None, report_file: str = None,
                           blocker_reason: str = None) -> Dict:
        """
        更新 Task 状态
        
        Args:
            task_id: Task ID
            new_status: 新状态
            output_summary: 完成摘要（DONE 时需要）
            report_file: 报告文件路径（DONE 时需要）
            blocker_reason: 阻塞原因（BLOCKED 时需要）
            
        Returns:
            {"success": bool, "task": Task, "message": str}
        """
        return self.task_service.update_task_status(task_id, new_status, output_summary,
                                                    report_file, blocker_reason)
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取 Task"""
        return self.task_service.get_task(task_id)
    
    def list_tasks(self, assignee_id: str = None, story_id: str = None,
                   status: str = None) -> List[Task]:
        """列出 Task"""
        return self.task_service.list_tasks(assignee_id, story_id, status)
    
    def get_board(self) -> Dict:
        """获取看板数据"""
        return self.task_service.get_board()
    
    # ========== Retro 接口 ==========
    
    def create_retro(self, title: str, retro_type: str, facilitator_id: str,
                     template: str = "mad_sad_glad", participants: List[str] = None,
                     sprint_id: str = None, project_name: str = None,
                     incident_id: str = None) -> Retro:
        """
        创建复盘
        
        Args:
            title: 标题
            retro_type: 类型 (sprint, project, incident, custom)
            facilitator_id: 主持人 Agent ID
            template: 模板 (mad_sad_glad, start_stop_continue, four_ls, custom)
            participants: 参与者列表
            sprint_id: 关联迭代ID
            project_name: 关联项目名称
            incident_id: 关联事故ID
            
        Returns:
            Retro 对象
        """
        type_enum = RetroType(retro_type) if isinstance(retro_type, str) else retro_type
        template_enum = RetroTemplate(template) if isinstance(template, str) else template
        
        return self.retro_service.create_retro(title, type_enum, facilitator_id,
                                               template_enum, participants, sprint_id,
                                               project_name, incident_id)
    
    def start_retro_collecting(self, retro_id: str) -> Dict:
        """开始复盘收集阶段"""
        return self.retro_service.start_collecting(retro_id)
    
    def add_retro_item(self, retro_id: str, category: str, content: str, 
                       author_id: str) -> Dict:
        """添加复盘条目"""
        return self.retro_service.add_item(retro_id, category, content, author_id)
    
    def vote_retro_item(self, item_id: str, voter_id: str) -> Dict:
        """为复盘条目投票"""
        return self.retro_service.vote_item(item_id, voter_id)
    
    def discuss_retro_item(self, item_id: str, notes: str) -> Dict:
        """记录讨论笔记"""
        return self.retro_service.discuss_item(item_id, notes)
    
    def start_retro_discussing(self, retro_id: str) -> Dict:
        """开始复盘讨论阶段"""
        return self.retro_service.start_discussing(retro_id)
    
    def create_action_item(self, retro_id: str, title: str, assignee_id: str,
                           due_date: date, priority: str = "P1",
                           description: str = "", related_item_ids: List[str] = None) -> Dict:
        """
        创建改进行动
        
        Args:
            retro_id: 复盘ID
            title: 标题
            assignee_id: 负责人
            due_date: 截止日期
            priority: 优先级 (P0/P1/P2)
            description: 描述
            related_item_ids: 关联复盘条目
        """
        priority_enum = Priority(priority) if isinstance(priority, str) else priority
        return self.retro_service.create_action_item(retro_id, title, assignee_id,
                                                     due_date, priority_enum, description,
                                                     related_item_ids)
    
    def complete_action_item(self, action_id: str, verification_method: str,
                             verified_by: str) -> Dict:
        """完成改进行动"""
        return self.retro_service.complete_action_item(action_id, verification_method, verified_by)
    
    def complete_retro(self, retro_id: str, summary: str = "") -> Dict:
        """完成复盘"""
        return self.retro_service.complete_retro(retro_id, summary)
    
    def generate_retro_report(self, retro_id: str) -> Dict:
        """生成复盘报告"""
        return self.retro_service.generate_report(retro_id)
    
    def get_retro(self, retro_id: str) -> Optional[Retro]:
        """获取复盘"""
        return self.retro_service.get_retro(retro_id)
    
    def list_retros(self, retro_type: str = None, status: str = None, limit: int = 50) -> List[Retro]:
        """列出复盘"""
        return self.retro_service.list_retros(retro_type, status, limit)
    
    def list_action_items(self, retro_id: str = None, assignee_id: str = None,
                          status: str = None) -> List[ActionItem]:
        """列出改进行动"""
        return self.retro_service.list_action_items(retro_id, assignee_id, status)
    
    # ========== Iteration 接口 ==========
    
    def create_iteration(self, name: str, goal: str, start_date: date, 
                         end_date: date) -> Iteration:
        """
        创建迭代
        
        Args:
            name: 迭代名称
            goal: 迭代目标
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            Iteration 对象
        """
        return self.iteration_service.create_iteration(name, goal, start_date, end_date)
    
    def get_iteration(self, iteration_id: str) -> Optional[Iteration]:
        """获取迭代"""
        return self.iteration_service.get_iteration(iteration_id)
    
    def list_iterations(self, status: str = None) -> List[Iteration]:
        """列出迭代"""
        return self.iteration_service.list_iterations(status)
    
    def get_iteration_stats(self, iteration_id: str) -> Dict:
        """获取迭代统计"""
        return self.iteration_service.get_stats(iteration_id)
