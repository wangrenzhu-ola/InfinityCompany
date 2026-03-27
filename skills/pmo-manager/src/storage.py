"""
数据存储层 - SQLite 实现
"""

import os
import sqlite3
import json
from typing import List, Optional, Dict
from datetime import datetime, date
from .models import (
    Story, Task, Retro, RetroItem, ActionItem, Iteration,
    TaskStatus, Priority, RetroType, RetroStatus, RetroTemplate
)


class Storage:
    """SQLite 存储管理器"""
    
    def __init__(self, db_path: str = None):
        """
        初始化存储
        
        Args:
            db_path: 数据库文件路径，默认 ~/.openclaw/workspace/pmo.db
        """
        if db_path is None:
            home = os.path.expanduser("~")
            db_path = os.path.join(home, ".openclaw", "workspace", "pmo.db")
        
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()
    
    def _get_conn(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self):
        """初始化数据库表结构"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Story 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stories (
                story_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                creator_id TEXT NOT NULL,
                background TEXT,
                objectives TEXT,  -- JSON array
                acceptance_criteria TEXT,  -- JSON array
                priority TEXT,
                status TEXT DEFAULT 'active',
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Task 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                assignee_id TEXT NOT NULL,
                story_id TEXT NOT NULL,
                priority TEXT,
                deadline TEXT,
                status TEXT DEFAULT 'draft',
                description TEXT,
                solution TEXT,
                start_time TEXT,
                report_file TEXT,
                output_summary TEXT,
                rejection_reason TEXT,
                blocker_reason TEXT,
                actual_hours REAL DEFAULT 0,
                estimated_hours REAL DEFAULT 0,
                created_at TEXT,
                updated_at TEXT,
                FOREIGN KEY (story_id) REFERENCES stories(story_id)
            )
        ''')
        
        # Retro 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS retros (
                retro_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                retro_type TEXT,
                status TEXT DEFAULT 'planning',
                facilitator_id TEXT,
                participants TEXT,  -- JSON array
                template TEXT,
                custom_columns TEXT,  -- JSON array
                summary TEXT,
                sprint_id TEXT,
                project_name TEXT,
                incident_id TEXT,
                created_at TEXT,
                started_at TEXT,
                completed_at TEXT
            )
        ''')
        
        # RetroItem 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS retro_items (
                item_id TEXT PRIMARY KEY,
                retro_id TEXT NOT NULL,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                author_id TEXT,
                votes INTEGER DEFAULT 0,
                voters TEXT,  -- JSON array
                discussion_notes TEXT,
                action_item_id TEXT,
                created_at TEXT,
                FOREIGN KEY (retro_id) REFERENCES retros(retro_id)
            )
        ''')
        
        # ActionItem 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS action_items (
                action_id TEXT PRIMARY KEY,
                retro_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                assignee_id TEXT,
                priority TEXT,
                status TEXT DEFAULT 'pending',
                due_date TEXT,
                related_item_ids TEXT,  -- JSON array
                verification_method TEXT,
                verified_by TEXT,
                completed_at TEXT,
                created_at TEXT,
                FOREIGN KEY (retro_id) REFERENCES retros(retro_id)
            )
        ''')
        
        # Iteration 表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS iterations (
                iteration_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                goal TEXT,
                start_date TEXT,
                end_date TEXT,
                status TEXT DEFAULT 'planning',
                story_ids TEXT,  -- JSON array
                created_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    # ===== Story 操作 =====
    
    def save_story(self, story: Story) -> None:
        """保存 Story"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO stories 
            (story_id, title, creator_id, background, objectives, acceptance_criteria,
             priority, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            story.story_id, story.title, story.creator_id, story.background,
            json.dumps(story.objectives, ensure_ascii=False),
            json.dumps(story.acceptance_criteria, ensure_ascii=False),
            story.priority.value if isinstance(story.priority, Priority) else story.priority,
            story.status,
            story.created_at.isoformat() if isinstance(story.created_at, datetime) else story.created_at,
            story.updated_at.isoformat() if isinstance(story.updated_at, datetime) else story.updated_at,
        ))
        
        conn.commit()
        conn.close()
    
    def get_story(self, story_id: str) -> Optional[Story]:
        """获取 Story"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM stories WHERE story_id = ?', (story_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_story(row)
        return None
    
    def list_stories(self, status: str = None) -> List[Story]:
        """列出 Story"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        if status:
            cursor.execute('SELECT * FROM stories WHERE status = ? ORDER BY created_at DESC', (status,))
        else:
            cursor.execute('SELECT * FROM stories ORDER BY created_at DESC')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_story(row) for row in rows]
    
    def _row_to_story(self, row) -> Story:
        """将数据库行转换为 Story 对象"""
        return Story(
            story_id=row['story_id'],
            title=row['title'],
            creator_id=row['creator_id'],
            background=row['background'] or '',
            objectives=json.loads(row['objectives']) if row['objectives'] else [],
            acceptance_criteria=json.loads(row['acceptance_criteria']) if row['acceptance_criteria'] else [],
            priority=Priority(row['priority']) if row['priority'] else Priority.P1,
            status=row['status'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
        )
    
    # ===== Task 操作 =====
    
    def save_task(self, task: Task) -> None:
        """保存 Task"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO tasks 
            (task_id, title, assignee_id, story_id, priority, deadline, status,
             description, solution, start_time, report_file, output_summary,
             rejection_reason, blocker_reason, actual_hours, estimated_hours,
             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task.task_id, task.title, task.assignee_id, task.story_id,
            task.priority.value if isinstance(task.priority, Priority) else task.priority,
            task.deadline.isoformat() if isinstance(task.deadline, datetime) else task.deadline,
            task.status.value if isinstance(task.status, TaskStatus) else task.status,
            task.description, task.solution,
            task.start_time.isoformat() if task.start_time and isinstance(task.start_time, datetime) else task.start_time,
            task.report_file, task.output_summary, task.rejection_reason, task.blocker_reason,
            task.actual_hours, task.estimated_hours,
            task.created_at.isoformat() if isinstance(task.created_at, datetime) else task.created_at,
            task.updated_at.isoformat() if isinstance(task.updated_at, datetime) else task.updated_at,
        ))
        
        conn.commit()
        conn.close()
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """获取 Task"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM tasks WHERE task_id = ?', (task_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_task(row)
        return None
    
    def list_tasks(self, assignee_id: str = None, story_id: str = None,
                   status: str = None, priority: str = None) -> List[Task]:
        """列出 Task"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM tasks WHERE 1=1'
        params = []
        
        if assignee_id:
            query += ' AND assignee_id = ?'
            params.append(assignee_id)
        if story_id:
            query += ' AND story_id = ?'
            params.append(story_id)
        if status:
            query += ' AND status = ?'
            params.append(status)
        if priority:
            query += ' AND priority = ?'
            params.append(priority)
        
        query += ' ORDER BY created_at DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_task(row) for row in rows]
    
    def get_review_queue(self) -> List[Task]:
        """获取待审核队列"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM tasks 
            WHERE status IN ('draft', 'rejected') 
            ORDER BY created_at ASC
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_task(row) for row in rows]
    
    def _row_to_task(self, row) -> Task:
        """将数据库行转换为 Task 对象"""
        return Task(
            task_id=row['task_id'],
            title=row['title'],
            assignee_id=row['assignee_id'],
            story_id=row['story_id'],
            priority=Priority(row['priority']) if row['priority'] else Priority.P1,
            deadline=row['deadline'],
            status=TaskStatus(row['status']) if row['status'] else TaskStatus.DRAFT,
            description=row['description'] or '',
            solution=row['solution'] or '',
            start_time=row['start_time'],
            report_file=row['report_file'],
            output_summary=row['output_summary'] or '',
            rejection_reason=row['rejection_reason'],
            blocker_reason=row['blocker_reason'],
            actual_hours=row['actual_hours'] or 0.0,
            estimated_hours=row['estimated_hours'] or 0.0,
            created_at=row['created_at'],
            updated_at=row['updated_at'],
        )
    
    # ===== Retro 操作 =====
    
    def save_retro(self, retro: Retro) -> None:
        """保存 Retro"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO retros 
            (retro_id, title, retro_type, status, facilitator_id, participants,
             template, custom_columns, summary, sprint_id, project_name, incident_id,
             created_at, started_at, completed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            retro.retro_id, retro.title,
            retro.retro_type.value if isinstance(retro.retro_type, RetroType) else retro.retro_type,
            retro.status.value if isinstance(retro.status, RetroStatus) else retro.status,
            retro.facilitator_id,
            json.dumps(retro.participants, ensure_ascii=False),
            retro.template.value if isinstance(retro.template, RetroTemplate) else retro.template,
            json.dumps(retro.custom_columns, ensure_ascii=False) if retro.custom_columns else '[]',
            retro.summary,
            retro.sprint_id, retro.project_name, retro.incident_id,
            retro.created_at.isoformat() if isinstance(retro.created_at, datetime) else retro.created_at,
            retro.started_at.isoformat() if retro.started_at and isinstance(retro.started_at, datetime) else retro.started_at,
            retro.completed_at.isoformat() if retro.completed_at and isinstance(retro.completed_at, datetime) else retro.completed_at,
        ))
        
        conn.commit()
        conn.close()
    
    def get_retro(self, retro_id: str) -> Optional[Retro]:
        """获取 Retro"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM retros WHERE retro_id = ?', (retro_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_retro(row)
        return None
    
    def list_retros(self, retro_type: str = None, status: str = None, limit: int = 50) -> List[Retro]:
        """列出 Retro"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM retros WHERE 1=1'
        params = []
        
        if retro_type:
            query += ' AND retro_type = ?'
            params.append(retro_type)
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_retro(row) for row in rows]
    
    def _row_to_retro(self, row) -> Retro:
        """将数据库行转换为 Retro 对象"""
        retro = Retro(
            retro_id=row['retro_id'],
            title=row['title'],
            retro_type=RetroType(row['retro_type']) if row['retro_type'] else RetroType.CUSTOM,
            status=RetroStatus(row['status']) if row['status'] else RetroStatus.PLANNING,
            facilitator_id=row['facilitator_id'],
            participants=json.loads(row['participants']) if row['participants'] else [],
            template=RetroTemplate(row['template']) if row['template'] else RetroTemplate.MAD_SAD_GLAD,
            custom_columns=json.loads(row['custom_columns']) if row['custom_columns'] else [],
            summary=row['summary'] or '',
            sprint_id=row['sprint_id'],
            project_name=row['project_name'],
            incident_id=row['incident_id'],
            created_at=row['created_at'],
            started_at=row['started_at'],
            completed_at=row['completed_at'],
        )
        return retro
    
    # ===== RetroItem 操作 =====
    
    def save_retro_item(self, item: RetroItem) -> None:
        """保存 RetroItem"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO retro_items 
            (item_id, retro_id, category, content, author_id, votes, voters,
             discussion_notes, action_item_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item.item_id, item.retro_id, item.category, item.content, item.author_id,
            item.votes,
            json.dumps(item.voters, ensure_ascii=False),
            item.discussion_notes, item.action_item_id,
            item.created_at.isoformat() if isinstance(item.created_at, datetime) else item.created_at,
        ))
        
        conn.commit()
        conn.close()
    
    def get_retro_item(self, item_id: str) -> Optional[RetroItem]:
        """获取 RetroItem"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM retro_items WHERE item_id = ?', (item_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_retro_item(row)
        return None
    
    def list_retro_items(self, retro_id: str) -> List[RetroItem]:
        """列出 RetroItem"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM retro_items WHERE retro_id = ? ORDER BY votes DESC', (retro_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_retro_item(row) for row in rows]
    
    def _row_to_retro_item(self, row) -> RetroItem:
        """将数据库行转换为 RetroItem 对象"""
        return RetroItem(
            item_id=row['item_id'],
            retro_id=row['retro_id'],
            category=row['category'],
            content=row['content'],
            author_id=row['author_id'],
            votes=row['votes'] or 0,
            voters=json.loads(row['voters']) if row['voters'] else [],
            discussion_notes=row['discussion_notes'] or '',
            action_item_id=row['action_item_id'],
            created_at=row['created_at'],
        )
    
    # ===== ActionItem 操作 =====
    
    def save_action_item(self, action: ActionItem) -> None:
        """保存 ActionItem"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO action_items 
            (action_id, retro_id, title, description, assignee_id, priority, status,
             due_date, related_item_ids, verification_method, verified_by, completed_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            action.action_id, action.retro_id, action.title, action.description,
            action.assignee_id,
            action.priority.value if isinstance(action.priority, Priority) else action.priority,
            action.status,
            action.due_date.isoformat() if action.due_date and isinstance(action.due_date, date) else action.due_date,
            json.dumps(action.related_item_ids, ensure_ascii=False),
            action.verification_method, action.verified_by,
            action.completed_at.isoformat() if action.completed_at and isinstance(action.completed_at, datetime) else action.completed_at,
            action.created_at.isoformat() if isinstance(action.created_at, datetime) else action.created_at,
        ))
        
        conn.commit()
        conn.close()
    
    def get_action_item(self, action_id: str) -> Optional[ActionItem]:
        """获取 ActionItem"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM action_items WHERE action_id = ?', (action_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_action_item(row)
        return None
    
    def list_action_items(self, retro_id: str = None, assignee_id: str = None,
                          status: str = None) -> List[ActionItem]:
        """列出 ActionItem"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM action_items WHERE 1=1'
        params = []
        
        if retro_id:
            query += ' AND retro_id = ?'
            params.append(retro_id)
        if assignee_id:
            query += ' AND assignee_id = ?'
            params.append(assignee_id)
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        query += ' ORDER BY created_at DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_action_item(row) for row in rows]
    
    def _row_to_action_item(self, row) -> ActionItem:
        """将数据库行转换为 ActionItem 对象"""
        return ActionItem(
            action_id=row['action_id'],
            retro_id=row['retro_id'],
            title=row['title'],
            description=row['description'] or '',
            assignee_id=row['assignee_id'],
            priority=Priority(row['priority']) if row['priority'] else Priority.P1,
            status=row['status'],
            due_date=row['due_date'],
            related_item_ids=json.loads(row['related_item_ids']) if row['related_item_ids'] else [],
            verification_method=row['verification_method'] or '',
            verified_by=row['verified_by'],
            completed_at=row['completed_at'],
            created_at=row['created_at'],
        )
    
    # ===== Iteration 操作 =====
    
    def save_iteration(self, iteration: Iteration) -> None:
        """保存 Iteration"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO iterations 
            (iteration_id, name, goal, start_date, end_date, status, story_ids, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            iteration.iteration_id, iteration.name, iteration.goal,
            iteration.start_date.isoformat() if isinstance(iteration.start_date, date) else iteration.start_date,
            iteration.end_date.isoformat() if isinstance(iteration.end_date, date) else iteration.end_date,
            iteration.status,
            json.dumps(iteration.story_ids, ensure_ascii=False),
            iteration.created_at.isoformat() if isinstance(iteration.created_at, datetime) else iteration.created_at,
        ))
        
        conn.commit()
        conn.close()
    
    def get_iteration(self, iteration_id: str) -> Optional[Iteration]:
        """获取 Iteration"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM iterations WHERE iteration_id = ?', (iteration_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_iteration(row)
        return None
    
    def list_iterations(self, status: str = None) -> List[Iteration]:
        """列出 Iteration"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        if status:
            cursor.execute('SELECT * FROM iterations WHERE status = ? ORDER BY created_at DESC', (status,))
        else:
            cursor.execute('SELECT * FROM iterations ORDER BY created_at DESC')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_iteration(row) for row in rows]
    
    def _row_to_iteration(self, row) -> Iteration:
        """将数据库行转换为 Iteration 对象"""
        return Iteration(
            iteration_id=row['iteration_id'],
            name=row['name'],
            goal=row['goal'] or '',
            start_date=row['start_date'],
            end_date=row['end_date'],
            status=row['status'],
            story_ids=json.loads(row['story_ids']) if row['story_ids'] else [],
            created_at=row['created_at'],
        )
