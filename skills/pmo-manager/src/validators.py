"""
合规校验器
"""

import os
from typing import List, Dict, Optional
from datetime import datetime
from .storage import Storage


class TaskValidator:
    """Task 合规校验器"""
    
    def __init__(self, storage: Storage):
        self.storage = storage
    
    def validate_task_submission(self, title: str, assignee_id: str, story_id: str,
                                  deadline: datetime, description: str = "") -> Dict:
        """
        校验 Task 提交
        
        Returns:
            {"valid": bool, "errors": List[str]}
        """
        errors = []
        
        # 校验标题
        if not title or len(title) < 3:
            errors.append("任务标题至少需要 3 个字符")
        
        # 校验执行人
        if not assignee_id:
            errors.append("必须指定执行人")
        
        # 校验 Story 关联
        if not story_id:
            errors.append("必须关联一个 Story (story_id)")
        else:
            story = self.storage.get_story(story_id)
            if not story:
                errors.append(f"Story '{story_id}' 不存在")
        
        # 校验截止时间
        if not deadline:
            errors.append("必须设定截止时间 (deadline)")
        elif deadline < datetime.now():
            errors.append("截止时间必须在将来")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def validate_task_completion(self, task_id: str, report_file: str) -> Dict:
        """
        校验 Task 完成
        
        Returns:
            {"valid": bool, "errors": List[str]}
        """
        errors = []
        
        # 获取 Task
        task = self.storage.get_task(task_id)
        if not task:
            errors.append(f"Task '{task_id}' 不存在")
            return {"valid": False, "errors": errors}
        
        # 校验报告文件
        if not report_file:
            errors.append("DONE 状态必须提供 report_file（完成报告文件路径）")
        else:
            # 检查文件是否存在
            expanded_path = os.path.expanduser(report_file)
            if not os.path.exists(expanded_path):
                errors.append(f"报告文件不存在: {report_file}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def validate_state_transition(self, task_id: str, new_status: str) -> Dict:
        """
        校验状态流转
        
        Returns:
            {"valid": bool, "errors": List[str]}
        """
        errors = []
        
        # 获取 Task
        task = self.storage.get_task(task_id)
        if not task:
            errors.append(f"Task '{task_id}' 不存在")
            return {"valid": False, "errors": errors}
        
        current_status = task.status.value if hasattr(task.status, 'value') else str(task.status)
        
        # 定义合法的状态流转
        valid_transitions = {
            "draft": ["pending_review", "rejected"],
            "pending_review": ["approved", "rejected"],
            "rejected": ["draft", "pending_review"],
            "approved": ["todo"],
            "todo": ["in_progress", "blocked"],
            "in_progress": ["done", "blocked"],
            "blocked": ["in_progress", "todo"],
            "done": [],  # 完成状态不能再流转
        }
        
        allowed = valid_transitions.get(current_status, [])
        if new_status not in allowed:
            errors.append(f"非法状态流转: {current_status} -> {new_status}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
