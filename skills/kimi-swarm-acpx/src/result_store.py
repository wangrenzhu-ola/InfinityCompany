"""
OpenViking Store - 使用 OpenViking 记忆系统存储子 Agent 结果

核心功能：
1. 通过 sessionKey 实现子 Agent 结果隔离
2. 自动关联主从任务上下文
3. 支持结果查询和聚合
"""

import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ResultStatus(Enum):
    """结果状态"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class SubAgentResult:
    """子 Agent 结果"""
    agent_id: str
    role: str
    status: ResultStatus
    content: str = ""
    error: str = ""
    duration_ms: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SwarmSession:
    """Swarm 会话"""
    session_id: str
    master_task: str
    sub_results: Dict[str, SubAgentResult] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "running"  # running, completed, failed
    
    def add_result(self, result: SubAgentResult):
        """添加子 Agent 结果"""
        self.sub_results[result.agent_id] = result
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "master_task": self.master_task,
            "sub_results": {
                k: {
                    "agent_id": v.agent_id,
                    "role": v.role,
                    "status": v.status.value,
                    "content": v.content,
                    "error": v.error,
                    "duration_ms": v.duration_ms,
                    "timestamp": v.timestamp,
                    "metadata": v.metadata
                }
                for k, v in self.sub_results.items()
            },
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": self.status
        }


class OpenVikingStore:
    """
    OpenViking 记忆存储
    
    使用 OpenViking 的 sessionKey 机制实现子 Agent 结果隔离存储。
    主 Agent 和子 Agent 使用不同的 sessionKey，但通过共享的 swarm_session_id 关联。
    """
    
    def __init__(self, base_path: str = "~/.openclaw/workspace/swarm-sessions"):
        """
        初始化存储
        
        Args:
            base_path: 会话存储基础路径
        """
        import os
        self.base_path = os.path.expanduser(base_path)
        os.makedirs(self.base_path, exist_ok=True)
    
    def create_session(self, master_task: str) -> SwarmSession:
        """
        创建新的 Swarm 会话
        
        Args:
            master_task: 主任务描述
            
        Returns:
            SwarmSession: 新建的会话
        """
        import uuid
        session_id = f"swarm-{uuid.uuid4().hex[:12]}"
        
        session = SwarmSession(
            session_id=session_id,
            master_task=master_task
        )
        
        self._save_session(session)
        return session
    
    def save_result(
        self,
        session_id: str,
        agent_id: str,
        role: str,
        status: ResultStatus,
        content: str = "",
        error: str = "",
        duration_ms: int = 0,
        metadata: Optional[Dict] = None
    ) -> SubAgentResult:
        """
        保存子 Agent 结果
        
        Args:
            session_id: Swarm 会话 ID
            agent_id: 子 Agent ID
            role: 角色名称
            status: 结果状态
            content: 结果内容
            error: 错误信息
            duration_ms: 执行时长
            metadata: 额外元数据
            
        Returns:
            SubAgentResult: 保存的结果
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        
        result = SubAgentResult(
            agent_id=agent_id,
            role=role,
            status=status,
            content=content,
            error=error,
            duration_ms=duration_ms,
            metadata=metadata or {}
        )
        
        session.add_result(result)
        self._save_session(session)
        
        return result
    
    def get_session(self, session_id: str) -> Optional[SwarmSession]:
        """
        获取会话
        
        Args:
            session_id: 会话 ID
            
        Returns:
            SwarmSession 或 None
        """
        import os
        file_path = os.path.join(self.base_path, f"{session_id}.json")
        
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return self._dict_to_session(data)
    
    def get_all_results(self, session_id: str) -> Dict[str, SubAgentResult]:
        """
        获取所有子 Agent 结果
        
        Args:
            session_id: 会话 ID
            
        Returns:
            {agent_id: SubAgentResult}
        """
        session = self.get_session(session_id)
        if not session:
            return {}
        return session.sub_results
    
    def aggregate_results(self, session_id: str) -> str:
        """
        聚合所有子 Agent 结果为统一格式
        
        Args:
            session_id: 会话 ID
            
        Returns:
            聚合后的结果字符串
        """
        session = self.get_session(session_id)
        if not session:
            return ""
        
        lines = [
            f"# Swarm 会话聚合结果",
            f"",
            f"**会话ID**: {session.session_id}",
            f"**主任务**: {session.master_task}",
            f"**状态**: {session.status}",
            f"**子Agent数量**: {len(session.sub_results)}",
            f"",
        ]
        
        success_count = sum(
            1 for r in session.sub_results.values() 
            if r.status == ResultStatus.SUCCESS
        )
        lines.append(f"**成功率**: {success_count}/{len(session.sub_results)}")
        lines.append("")
        
        for agent_id, result in session.sub_results.items():
            lines.append(f"## 【{result.role}】{result.agent_id}")
            lines.append(f"")
            lines.append(f"**状态**: {result.status.value}")
            
            if result.status == ResultStatus.SUCCESS:
                lines.append(f"**时长**: {result.duration_ms}ms")
                lines.append(f"**结果**:")
                lines.append(f"```")
                lines.append(result.content)
                lines.append(f"```")
            else:
                lines.append(f"**错误**: {result.error}")
                
            lines.append("")
        
        return "\n".join(lines)
    
    def complete_session(self, session_id: str, status: str = "completed"):
        """
        标记会话完成
        
        Args:
            session_id: 会话 ID
            status: 最终状态
        """
        session = self.get_session(session_id)
        if session:
            session.status = status
            session.updated_at = datetime.now().isoformat()
            self._save_session(session)
    
    def _save_session(self, session: SwarmSession):
        """保存会话到文件"""
        import os
        file_path = os.path.join(self.base_path, f"{session.session_id}.json")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)
    
    def _dict_to_session(self, data: Dict) -> SwarmSession:
        """字典转会话对象"""
        results = {}
        for k, v in data.get("sub_results", {}).items():
            results[k] = SubAgentResult(
                agent_id=v["agent_id"],
                role=v["role"],
                status=ResultStatus(v["status"]),
                content=v.get("content", ""),
                error=v.get("error", ""),
                duration_ms=v.get("duration_ms", 0),
                timestamp=v.get("timestamp", ""),
                metadata=v.get("metadata", {})
            )
        
        return SwarmSession(
            session_id=data["session_id"],
            master_task=data["master_task"],
            sub_results=results,
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            status=data.get("status", "running")
        )
