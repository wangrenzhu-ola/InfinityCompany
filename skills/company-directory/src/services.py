"""
核心业务逻辑服务
"""

import os
import uuid
from typing import List, Optional, Dict
from datetime import datetime
from .models import Agent, AgentRole, OrganizationUnit, Email
from .storage import Storage
from .constants import ESCALATION_PATHS


class AgentService:
    """成员服务 - 处理成员查询相关操作"""
    
    def __init__(self, storage: Storage):
        self.storage = storage
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """根据ID获取成员信息"""
        return self.storage.get_agent(agent_id)
    
    def find_agents_by_role(self, role: AgentRole) -> List[Agent]:
        """根据角色查找成员"""
        return self.storage.find_agents_by_role(role)
    
    def find_agents_by_name(self, name: str) -> List[Agent]:
        """根据姓名模糊搜索成员"""
        return self.storage.find_agents_by_name(name)
    
    def find_agents_by_skill(self, skill: str) -> List[Agent]:
        """根据技能搜索成员"""
        return self.storage.find_agents_by_skill(skill)
    
    def list_all_agents(self) -> List[Agent]:
        """列出所有成员"""
        return self.storage.list_all_agents()
    
    def get_agent_chain(self, agent_id: str) -> List[Agent]:
        """获取成员的汇报链"""
        return self.storage.get_reporting_chain(agent_id)


class OrganizationService:
    """组织服务 - 处理组织架构相关操作"""
    
    def __init__(self, storage: Storage):
        self.storage = storage
    
    def get_org_chart(self) -> Dict:
        """获取完整组织架构图"""
        return self.storage.get_org_chart()
    
    def get_team_by_role(self, role: AgentRole) -> List[Agent]:
        """根据角色获取团队"""
        return self.storage.find_agents_by_role(role)
    
    def get_escalation_path(self, escalation_type: str) -> Optional[Dict]:
        """
        获取事件升级路径
        
        Args:
            escalation_type: 升级类型 (incident, requirement, quality, external)
            
        Returns:
            升级路径定义或 None
        """
        path_def = ESCALATION_PATHS.get(escalation_type)
        if not path_def:
            return None
        
        # 丰富路径信息
        enriched_path = []
        for step in path_def["path"]:
            agent = self.storage.get_agent(step["agent_id"])
            enriched_path.append({
                "level": step["level"],
                "agent_id": step["agent_id"],
                "agent_name": agent.name if agent else step["agent_id"],
                "title": agent.title if agent else "",
                "role": step["role"],
            })
        
        return {
            "type": escalation_type,
            "name": path_def["name"],
            "path": enriched_path,
        }


class CommunicationService:
    """通讯服务 - 处理跨Agent通讯"""
    
    def __init__(self, storage: Storage, inbox_base_path: str = None):
        self.storage = storage
        self.inbox_base_path = inbox_base_path or "~/.openclaw/workspace/emergency_inbox"
    
    def send_email(self, target_id: str, subject: str, message: str, 
                   sender_id: str = "system", urgency: str = "normal",
                   msg_type: str = "notification", reply_to: str = None) -> Dict:
        """
        发送异步邮件到指定 Agent 的 emergency_inbox
        
        Args:
            target_id: 目标 Agent ID
            subject: 邮件主题
            message: 邮件内容
            sender_id: 发送方 Agent ID（可选）
            urgency: 紧急程度 - urgent(紧急), normal(普通), low(低优先级)
            msg_type: 消息类型 - notification(只需知悉), response_required(需要回复), action_required(需要行动)
            reply_to: 回复引用的消息ID（可选）
        
        Returns:
            {"status": "success"/"error", "message": str, "email_id": str}
        """
        # 验证目标Agent存在
        target = self.storage.get_agent(target_id)
        if not target:
            return {
                "status": "error",
                "message": f"未知的 Agent ID: {target_id}",
                "valid_agents": [a.agent_id for a in self.storage.list_all_agents()]
            }
        
        # 获取发送方信息
        sender = self.storage.get_agent(sender_id)
        sender_name = sender.name if sender else (sender_id if sender_id != "system" else "系统")
        
        # 创建邮件对象
        email = Email(
            email_id=str(uuid.uuid4()),
            sender_id=sender_id,
            sender_name=sender_name,
            target_id=target_id,
            subject=subject,
            message=message,
            timestamp=datetime.now(),
            urgency=urgency,
            msg_type=msg_type,
            reply_to=reply_to
        )
        
        # 写入文件
        inbox_path = os.path.expanduser(f"{self.inbox_base_path}/{target_id}")
        os.makedirs(inbox_path, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"email_{urgency}_{timestamp}_{email.email_id[:8]}.md"
        filepath = os.path.join(inbox_path, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(email.to_file_content())
            
            urgency_desc = {"urgent": "紧急", "normal": "普通", "low": "低优先级"}.get(urgency, urgency)
            type_desc = {"notification": "通知", "response_required": "需回复", "action_required": "需行动"}.get(msg_type, msg_type)
            
            return {
                "status": "success",
                "message": f"[{urgency_desc}/{type_desc}] 邮件已投递至 {target.name} ({target_id})",
                "email_id": email.email_id,
                "file_path": filepath,
                "target_name": target.name,
                "urgency": urgency,
                "msg_type": msg_type,
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"邮件投递失败: {str(e)}"
            }
    
    def check_inbox(self, agent_id: str) -> List[Dict]:
        """
        检查指定 Agent 的收件箱
        
        Args:
            agent_id: Agent ID
            
        Returns:
            邮件列表
        """
        inbox_path = os.path.expanduser(f"{self.inbox_base_path}/{agent_id}")
        if not os.path.exists(inbox_path):
            return []
        
        import glob
        emails = []
        for filepath in glob.glob(f"{inbox_path}/email_*.md"):
            emails.append({
                "file_path": filepath,
                "filename": os.path.basename(filepath)
            })
        
        return sorted(emails, key=lambda x: x["filename"], reverse=True)
    
    def get_acpx_command(self, target_id: str, message: str) -> str:
        """
        生成 acpx 命令
        
        Args:
            target_id: 目标 Agent ID
            message: 消息内容
            
        Returns:
            可执行的 acpx 命令字符串
        """
        # 转义消息中的特殊字符
        escaped_message = message.replace('"', '\\"')
        return f"acpx {target_id} \"{escaped_message}\""
    
    def get_contact_info(self, agent_id: str) -> Optional[Dict]:
        """
        获取成员的联系方式
        
        Args:
            agent_id: Agent ID
            
        Returns:
            联系方式信息
        """
        agent = self.storage.get_agent(agent_id)
        if not agent:
            return None
        
        return {
            "agent_id": agent.agent_id,
            "name": agent.name,
            "title": agent.title,
            "acpx_command": f"acpx {agent.agent_id} \"你的消息\"",
            "inbox_path": f"~/.openclaw/workspace/emergency_inbox/{agent.agent_id}",
            "email": agent.email or f"{agent.agent_id}@infinity.company",
        }
