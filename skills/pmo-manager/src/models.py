"""
数据模型定义
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime, date
from enum import Enum
import uuid


class TaskStatus(Enum):
    """Task 状态枚举"""
    DRAFT = "draft"              # 草稿（待审核）
    PENDING_REVIEW = "pending_review"  # 待审核
    REJECTED = "rejected"        # 已拒绝
    APPROVED = "approved"        # 已批准（待执行）
    TODO = "todo"                # 待办
    IN_PROGRESS = "in_progress"  # 进行中
    BLOCKED = "blocked"          # 阻塞
    DONE = "done"                # 已完成


class Priority(Enum):
    """优先级枚举"""
    P0 = "P0"  # 最高
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"  # 最低


class RetroType(Enum):
    """复盘类型"""
    SPRINT = "sprint"      # 迭代复盘
    PROJECT = "project"    # 项目复盘
    INCIDENT = "incident"  # 事故复盘
    CUSTOM = "custom"      # 自定义复盘


class RetroStatus(Enum):
    """复盘状态"""
    PLANNING = "planning"      # 计划阶段
    COLLECTING = "collecting"  # 数据收集
    DISCUSSING = "discussing"  # 讨论分析
    COMPLETED = "completed"    # 已完成
    CANCELLED = "cancelled"    # 已取消


class RetroTemplate(Enum):
    """复盘模板"""
    MAD_SAD_GLAD = "mad_sad_glad"
    START_STOP_CONTINUE = "start_stop_continue"
    FOUR_LS = "four_ls"
    CUSTOM = "custom"


@dataclass
class Story:
    """
    Story（顶层需求）模型
    
    Story 代表一个业务需求或功能特性，由高层（刘邦/张良）创建，
    是 Task 的上层聚合。
    """
    story_id: str                      # Story ID
    title: str                         # 标题
    creator_id: str                    # 创建者 Agent ID
    background: str                    # 背景说明
    objectives: List[str]              # 目标列表
    acceptance_criteria: List[str]     # 验收标准
    priority: Priority = Priority.P1   # 优先级
    status: str = "active"             # 状态: active, completed, archived
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def create(cls, title: str, creator_id: str, background: str = "",
               objectives: List[str] = None, acceptance_criteria: List[str] = None,
               priority: Priority = Priority.P1) -> "Story":
        """工厂方法：创建新的 Story"""
        return cls(
            story_id=f"story-{uuid.uuid4().hex[:8]}",
            title=title,
            creator_id=creator_id,
            background=background,
            objectives=objectives or [],
            acceptance_criteria=acceptance_criteria or [],
            priority=priority,
        )
    
    def to_dict(self) -> Dict:
        return {
            "story_id": self.story_id,
            "title": self.title,
            "creator_id": self.creator_id,
            "background": self.background,
            "objectives": self.objectives,
            "acceptance_criteria": self.acceptance_criteria,
            "priority": self.priority.value if isinstance(self.priority, Priority) else self.priority,
            "status": self.status,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
        }


@dataclass
class Task:
    """
    Task（任务）模型
    
    Task 代表具体的执行工作，必须由执行者提交审核，PMO 批准后才能执行。
    """
    task_id: str                       # Task ID
    title: str                         # 标题
    assignee_id: str                   # 执行人 Agent ID
    story_id: str                      # 关联 Story ID
    priority: Priority                 # 优先级
    deadline: datetime                 # 截止时间
    status: TaskStatus                 # 状态
    description: str = ""              # 描述
    solution: str = ""                 # 解决方案要点
    start_time: Optional[datetime] = None  # 开始时间
    report_file: Optional[str] = None  # 完成报告文件路径
    output_summary: str = ""           # 完成摘要
    rejection_reason: Optional[str] = None  # 拒绝原因
    blocker_reason: Optional[str] = None    # 阻塞原因
    actual_hours: float = 0.0          # 实际工时
    estimated_hours: float = 0.0       # 预估工时
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def submit(cls, title: str, assignee_id: str, story_id: str,
               priority: Priority, deadline: datetime, description: str = "",
               solution: str = "", start_time: Optional[datetime] = None,
               estimated_hours: float = 0.0) -> "Task":
        """工厂方法：提交新的 Task 审核"""
        return cls(
            task_id=f"task-{uuid.uuid4().hex[:8]}",
            title=title,
            assignee_id=assignee_id,
            story_id=story_id,
            priority=priority,
            deadline=deadline,
            status=TaskStatus.DRAFT,
            description=description,
            solution=solution,
            start_time=start_time,
            estimated_hours=estimated_hours,
        )
    
    def approve(self) -> None:
        """批准 Task"""
        self.status = TaskStatus.APPROVED
        self.updated_at = datetime.now()
    
    def reject(self, reason: str) -> None:
        """拒绝 Task"""
        self.status = TaskStatus.REJECTED
        self.rejection_reason = reason
        self.updated_at = datetime.now()
    
    def start(self) -> None:
        """开始执行"""
        self.status = TaskStatus.IN_PROGRESS
        self.updated_at = datetime.now()
    
    def complete(self, output_summary: str, report_file: str, actual_hours: float = 0.0) -> None:
        """完成任务"""
        self.status = TaskStatus.DONE
        self.output_summary = output_summary
        self.report_file = report_file
        self.actual_hours = actual_hours
        self.updated_at = datetime.now()
    
    def block(self, reason: str) -> None:
        """阻塞任务"""
        self.status = TaskStatus.BLOCKED
        self.blocker_reason = reason
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "assignee_id": self.assignee_id,
            "story_id": self.story_id,
            "priority": self.priority.value if isinstance(self.priority, Priority) else self.priority,
            "deadline": self.deadline.isoformat() if isinstance(self.deadline, datetime) else self.deadline,
            "status": self.status.value if isinstance(self.status, TaskStatus) else self.status,
            "description": self.description,
            "solution": self.solution,
            "start_time": self.start_time.isoformat() if self.start_time and isinstance(self.start_time, datetime) else self.start_time,
            "report_file": self.report_file,
            "output_summary": self.output_summary,
            "rejection_reason": self.rejection_reason,
            "blocker_reason": self.blocker_reason,
            "actual_hours": self.actual_hours,
            "estimated_hours": self.estimated_hours,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
        }


@dataclass
class RetroItem:
    """复盘条目"""
    item_id: str                       # 条目ID
    retro_id: str                      # 所属复盘ID
    category: str                      # 类别: mad/sad/glad, start/stop/continue, etc.
    content: str                       # 内容
    author_id: str                     # 作者
    votes: int = 0                     # 投票数
    voters: List[str] = field(default_factory=list)  # 投票人
    discussion_notes: str = ""         # 讨论笔记
    action_item_id: Optional[str] = None  # 关联的改进行动ID
    created_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def create(cls, retro_id: str, category: str, content: str, author_id: str) -> "RetroItem":
        """创建复盘条目"""
        return cls(
            item_id=f"item-{uuid.uuid4().hex[:8]}",
            retro_id=retro_id,
            category=category,
            content=content,
            author_id=author_id,
        )
    
    def vote(self, voter_id: str) -> bool:
        """投票"""
        if voter_id not in self.voters:
            self.voters.append(voter_id)
            self.votes += 1
            return True
        return False
    
    def to_dict(self) -> Dict:
        return {
            "item_id": self.item_id,
            "retro_id": self.retro_id,
            "category": self.category,
            "content": self.content,
            "author_id": self.author_id,
            "votes": self.votes,
            "voters": self.voters,
            "discussion_notes": self.discussion_notes,
            "action_item_id": self.action_item_id,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
        }


@dataclass
class ActionItem:
    """改进行动项"""
    action_id: str                     # 行动ID
    retro_id: str                      # 所属复盘ID
    title: str                         # 标题
    description: str                   # 描述
    assignee_id: str                   # 负责人
    priority: Priority                 # 优先级
    status: str = "pending"            # 状态: pending, in_progress, done, cancelled
    due_date: Optional[date] = None    # 截止日期
    related_item_ids: List[str] = field(default_factory=list)  # 关联的复盘条目
    verification_method: str = ""      # 验证方法
    verified_by: Optional[str] = None  # 验证人
    completed_at: Optional[datetime] = None  # 完成时间
    created_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def create(cls, retro_id: str, title: str, assignee_id: str, 
               due_date: date, priority: Priority = Priority.P1,
               description: str = "") -> "ActionItem":
        """创建改进行动"""
        return cls(
            action_id=f"action-{uuid.uuid4().hex[:8]}",
            retro_id=retro_id,
            title=title,
            description=description,
            assignee_id=assignee_id,
            priority=priority,
            due_date=due_date,
        )
    
    def complete(self, verification_method: str, verified_by: str) -> None:
        """完成改进行动"""
        self.status = "done"
        self.verification_method = verification_method
        self.verified_by = verified_by
        self.completed_at = datetime.now()
    
    def to_dict(self) -> Dict:
        return {
            "action_id": self.action_id,
            "retro_id": self.retro_id,
            "title": self.title,
            "description": self.description,
            "assignee_id": self.assignee_id,
            "priority": self.priority.value if isinstance(self.priority, Priority) else self.priority,
            "status": self.status,
            "due_date": self.due_date.isoformat() if self.due_date and isinstance(self.due_date, date) else self.due_date,
            "related_item_ids": self.related_item_ids,
            "verification_method": self.verification_method,
            "verified_by": self.verified_by,
            "completed_at": self.completed_at.isoformat() if self.completed_at and isinstance(self.completed_at, datetime) else self.completed_at,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
        }


@dataclass
class Retro:
    """
    Retro（复盘）模型
    
    支持迭代复盘、项目复盘、事故复盘等多种类型。
    """
    retro_id: str                      # 复盘 ID
    title: str                         # 标题
    retro_type: RetroType              # 复盘类型
    status: RetroStatus                # 状态
    facilitator_id: str                # 主持人 Agent ID
    participants: List[str]            # 参与者 Agent ID 列表
    template: RetroTemplate            # 模板
    custom_columns: List[str]          # 自定义列（用于 custom 模板）
    summary: str = ""                  # 复盘总结
    sprint_id: Optional[str] = None    # 关联迭代ID
    project_name: Optional[str] = None # 关联项目名称
    incident_id: Optional[str] = None  # 关联事故ID
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    @classmethod
    def create(cls, title: str, retro_type: RetroType, facilitator_id: str,
               template: RetroTemplate = RetroTemplate.MAD_SAD_GLAD,
               participants: List[str] = None) -> "Retro":
        """工厂方法：创建复盘"""
        return cls(
            retro_id=f"retro-{uuid.uuid4().hex[:8]}",
            title=title,
            retro_type=retro_type,
            status=RetroStatus.PLANNING,
            facilitator_id=facilitator_id,
            participants=participants or [],
            template=template,
            custom_columns=[],
        )
    
    def start_collecting(self) -> None:
        """开始收集反馈"""
        self.status = RetroStatus.COLLECTING
        self.started_at = datetime.now()
    
    def start_discussing(self) -> None:
        """开始讨论"""
        self.status = RetroStatus.DISCUSSING
    
    def complete(self, summary: str = "") -> None:
        """完成复盘"""
        self.status = RetroStatus.COMPLETED
        self.summary = summary
        self.completed_at = datetime.now()
    
    def cancel(self) -> None:
        """取消复盘"""
        self.status = RetroStatus.CANCELLED
    
    def to_dict(self) -> Dict:
        return {
            "retro_id": self.retro_id,
            "title": self.title,
            "retro_type": self.retro_type.value if isinstance(self.retro_type, RetroType) else self.retro_type,
            "status": self.status.value if isinstance(self.status, RetroStatus) else self.status,
            "facilitator_id": self.facilitator_id,
            "participants": self.participants,
            "template": self.template.value if isinstance(self.template, RetroTemplate) else self.template,
            "custom_columns": self.custom_columns,
            "summary": self.summary,
            "sprint_id": self.sprint_id,
            "project_name": self.project_name,
            "incident_id": self.incident_id,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "started_at": self.started_at.isoformat() if self.started_at and isinstance(self.started_at, datetime) else self.started_at,
            "completed_at": self.completed_at.isoformat() if self.completed_at and isinstance(self.completed_at, datetime) else self.completed_at,
        }


@dataclass
class Iteration:
    """
    Iteration（迭代）模型
    
    用于追踪迭代周期内的任务完成情况。
    """
    iteration_id: str                  # 迭代 ID
    name: str                          # 迭代名称
    goal: str                          # 迭代目标
    start_date: date                   # 开始日期
    end_date: date                     # 结束日期
    status: str = "planning"           # 状态: planning, active, completed
    story_ids: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def create(cls, name: str, goal: str, start_date: date, end_date: date) -> "Iteration":
        """创建迭代"""
        return cls(
            iteration_id=f"iter-{uuid.uuid4().hex[:8]}",
            name=name,
            goal=goal,
            start_date=start_date,
            end_date=end_date,
        )
    
    def start(self) -> None:
        """开始迭代"""
        self.status = "active"
    
    def complete(self) -> None:
        """完成迭代"""
        self.status = "completed"
    
    def to_dict(self) -> Dict:
        return {
            "iteration_id": self.iteration_id,
            "name": self.name,
            "goal": self.goal,
            "start_date": self.start_date.isoformat() if isinstance(self.start_date, date) else self.start_date,
            "end_date": self.end_date.isoformat() if isinstance(self.end_date, date) else self.end_date,
            "status": self.status,
            "story_ids": self.story_ids,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
        }
