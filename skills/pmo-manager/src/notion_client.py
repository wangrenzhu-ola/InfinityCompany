"""
Notion API 客户端

实现 Story/Task/Retro 与 Notion 数据库的同步。
"""

import os
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from .models import Story, Task, Retro, Priority, TaskStatus


class NotionClient:
    """Notion API 客户端"""
    
    def __init__(self, api_key: str = None, database_ids: Dict[str, str] = None):
        """
        初始化 Notion 客户端
        
        Args:
            api_key: Notion Integration API Key
            database_ids: 数据库 ID 映射
        """
        self.api_key = api_key or os.environ.get('NOTION_API_KEY')
        self.database_ids = database_ids or {
            'stories': os.environ.get('NOTION_STORY_DB_ID'),
            'tasks': os.environ.get('NOTION_TASK_DB_ID'),
            'retros': os.environ.get('NOTION_RETRO_DB_ID'),
        }
        
        # 尝试导入 notion-client
        try:
            from notion_client import Client
            self.client = Client(auth=self.api_key) if self.api_key else None
        except ImportError:
            self.client = None
    
    def is_available(self) -> bool:
        """检查 Notion 客户端是否可用"""
        return self.client is not None and self.api_key is not None
    
    def sync_story(self, story: Story) -> Dict[str, Any]:
        """
        同步 Story 到 Notion
        
        Args:
            story: Story 对象
            
        Returns:
            {"success": bool, "page_id": str, "message": str}
        """
        if not self.is_available():
            return {"success": False, "message": "Notion 客户端不可用"}
        
        db_id = self.database_ids.get('stories')
        if not db_id:
            return {"success": False, "message": "Story 数据库 ID 未配置"}
        
        try:
            # 检查是否已存在（通过 story_id）
            existing = self._find_page_by_story_id(db_id, story.story_id)
            
            properties = {
                "Name": {"title": [{"text": {"content": story.title}}]},
                "Story ID": {"rich_text": [{"text": {"content": story.story_id}}]},
                "Creator": {"select": {"name": story.creator_id}},
                "Priority": {"select": {"name": story.priority.value if hasattr(story.priority, 'value') else story.priority}},
                "Status": {"select": {"name": story.status}},
            }
            
            if story.background:
                properties["Background"] = {"rich_text": [{"text": {"content": story.background[:2000]}}]}
            
            if existing:
                # 更新已有页面
                self.client.pages.update(
                    page_id=existing['id'],
                    properties=properties
                )
                return {"success": True, "page_id": existing['id'], "message": "Story 已更新到 Notion"}
            else:
                # 创建新页面
                page = self.client.pages.create(
                    parent={"database_id": db_id},
                    properties=properties
                )
                return {"success": True, "page_id": page['id'], "message": "Story 已同步到 Notion"}
                
        except Exception as e:
            return {"success": False, "message": f"同步失败: {str(e)}"}
    
    def sync_task(self, task: Task, story_page_id: str = None) -> Dict[str, Any]:
        """
        同步 Task 到 Notion
        
        Args:
            task: Task 对象
            story_page_id: 关联的 Story 页面 ID
            
        Returns:
            {"success": bool, "page_id": str, "message": str}
        """
        if not self.is_available():
            return {"success": False, "message": "Notion 客户端不可用"}
        
        db_id = self.database_ids.get('tasks')
        if not db_id:
            return {"success": False, "message": "Task 数据库 ID 未配置"}
        
        try:
            existing = self._find_page_by_task_id(db_id, task.task_id)
            
            properties = {
                "Name": {"title": [{"text": {"content": task.title}}]},
                "Task ID": {"rich_text": [{"text": {"content": task.task_id}}]},
                "Story ID": {"rich_text": [{"text": {"content": task.story_id}}]},
                "Assignee": {"select": {"name": task.assignee_id}},
                "Priority": {"select": {"name": task.priority.value if hasattr(task.priority, 'value') else task.priority}},
                "Status": {"select": {"name": task.status.value if hasattr(task.status, 'value') else str(task.status)}},
            }
            
            if task.deadline:
                deadline_str = task.deadline
                if isinstance(task.deadline, datetime):
                    deadline_str = task.deadline.strftime('%Y-%m-%d')
                properties["Deadline"] = {"date": {"start": deadline_str}}
            
            if task.actual_hours:
                properties["Actual Hours"] = {"number": task.actual_hours}
            
            if task.estimated_hours:
                properties["Estimated Hours"] = {"number": task.estimated_hours}
            
            if existing:
                self.client.pages.update(
                    page_id=existing['id'],
                    properties=properties
                )
                return {"success": True, "page_id": existing['id'], "message": "Task 已更新到 Notion"}
            else:
                page = self.client.pages.create(
                    parent={"database_id": db_id},
                    properties=properties
                )
                return {"success": True, "page_id": page['id'], "message": "Task 已同步到 Notion"}
                
        except Exception as e:
            return {"success": False, "message": f"同步失败: {str(e)}"}
    
    def sync_retro(self, retro: Retro, items: List[Dict] = None) -> Dict[str, Any]:
        """
        同步 Retro 到 Notion
        
        Args:
            retro: Retro 对象
            items: 复盘条目列表
            
        Returns:
            {"success": bool, "page_id": str, "message": str}
        """
        if not self.is_available():
            return {"success": False, "message": "Notion 客户端不可用"}
        
        db_id = self.database_ids.get('retros')
        if not db_id:
            return {"success": False, "message": "Retro 数据库 ID 未配置"}
        
        try:
            existing = self._find_page_by_retro_id(db_id, retro.retro_id)
            
            properties = {
                "Name": {"title": [{"text": {"content": retro.title}}]},
                "Retro ID": {"rich_text": [{"text": {"content": retro.retro_id}}]},
                "Type": {"select": {"name": retro.retro_type.value if hasattr(retro.retro_type, 'value') else retro.retro_type}},
                "Facilitator": {"select": {"name": retro.facilitator_id}},
                "Status": {"select": {"name": retro.status.value if hasattr(retro.status, 'value') else retro.status}},
            }
            
            if items:
                content = f"## 反馈汇总\n\n"
                for item in items:
                    content += f"- **{item.get('category', '')}**: {item.get('content', '')}\n"
                properties["Content"] = {"rich_text": [{"text": {"content": content[:2000]}}]}
            
            if existing:
                self.client.pages.update(
                    page_id=existing['id'],
                    properties=properties
                )
                return {"success": True, "page_id": existing['id'], "message": "Retro 已更新到 Notion"}
            else:
                page = self.client.pages.create(
                    parent={"database_id": db_id},
                    properties=properties
                )
                return {"success": True, "page_id": page['id'], "message": "Retro 已同步到 Notion"}
                
        except Exception as e:
            return {"success": False, "message": f"同步失败: {str(e)}"}
    
    def _find_page_by_story_id(self, db_id: str, story_id: str) -> Optional[Dict]:
        """通过 Story ID 查找页面"""
        try:
            response = self.client.databases.query(
                database_id=db_id,
                filter={
                    "property": "Story ID",
                    "rich_text": {"equals": story_id}
                }
            )
            if response['results']:
                return response['results'][0]
            return None
        except:
            return None
    
    def _find_page_by_task_id(self, db_id: str, task_id: str) -> Optional[Dict]:
        """通过 Task ID 查找页面"""
        try:
            response = self.client.databases.query(
                database_id=db_id,
                filter={
                    "property": "Task ID",
                    "rich_text": {"equals": task_id}
                }
            )
            if response['results']:
                return response['results'][0]
            return None
        except:
            return None
    
    def _find_page_by_retro_id(self, db_id: str, retro_id: str) -> Optional[Dict]:
        """通过 Retro ID 查找页面"""
        try:
            response = self.client.databases.query(
                database_id=db_id,
                filter={
                    "property": "Retro ID",
                    "rich_text": {"equals": retro_id}
                }
            )
            if response['results']:
                return response['results'][0]
            return None
        except:
            return None
    
    def get_sync_status(self) -> Dict[str, Any]:
        """获取同步状态"""
        return {
            "notion_available": self.is_available(),
            "api_key_configured": self.api_key is not None,
            "databases_configured": {
                name: db_id is not None
                for name, db_id in self.database_ids.items()
            }
        }
