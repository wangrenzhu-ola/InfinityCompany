"""
Python API 层

提供 company-directory Skill 的 Python 编程接口
"""

from typing import List, Optional, Dict
from .models import Agent, AgentRole, OrganizationUnit, Email
from .services import AgentService, OrganizationService, CommunicationService
from .storage import Storage


class CompanyDirectoryAPI:
    """
    company-directory Skill 的 Python API
    
    使用示例:
        from company_directory import CompanyDirectoryAPI
        
        api = CompanyDirectoryAPI()
        
        # 查询成员
        agent = api.get_agent("hanxin")
        
        # 发送邮件
        result = api.send_email(
            target_id="caocan",
            subject="进度汇报",
            message="任务已完成"
        )
    """
    
    def __init__(self, data_dir: str = None, inbox_base_path: str = None):
        """
        初始化 API
        
        Args:
            data_dir: 数据目录路径
            inbox_base_path: 收件箱基础路径
        """
        self.storage = Storage(data_dir)
        self.agent_service = AgentService(self.storage)
        self.org_service = OrganizationService(self.storage)
        self.comm_service = CommunicationService(self.storage, inbox_base_path)
    
    # ========== Agent 查询接口 ==========
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        获取指定 Agent 的详细信息
        
        Args:
            agent_id: Agent ID (如: hanxin, xiaohe)
            
        Returns:
            Agent 对象或 None
        """
        return self.agent_service.get_agent(agent_id)
    
    def find_agents(self, role: Optional[str] = None, 
                    name: Optional[str] = None,
                    skill: Optional[str] = None) -> List[Agent]:
        """
        搜索成员
        
        Args:
            role: 按角色筛选 (如: dev, pmo, architect)
            name: 按姓名模糊搜索
            skill: 按技能搜索
            
        Returns:
            Agent 列表
        """
        if role:
            try:
                agent_role = AgentRole(role)
                return self.agent_service.find_agents_by_role(agent_role)
            except ValueError:
                return []
        if name:
            return self.agent_service.find_agents_by_name(name)
        if skill:
            return self.agent_service.find_agents_by_skill(skill)
        return self.agent_service.list_all_agents()
    
    def list_all_agents(self) -> List[Agent]:
        """列出所有成员"""
        return self.agent_service.list_all_agents()
    
    def get_reporting_chain(self, agent_id: str) -> List[Agent]:
        """
        获取成员的汇报链
        
        Args:
            agent_id: Agent ID
            
        Returns:
            从当前成员到最高层的汇报链列表
        """
        return self.agent_service.get_agent_chain(agent_id)
    
    # ========== 组织架构接口 ==========
    
    def get_organization_chart(self) -> Dict:
        """获取组织架构图"""
        return self.org_service.get_org_chart()
    
    def get_team(self, role: str) -> List[Agent]:
        """
        获取特定角色的团队
        
        Args:
            role: 角色类型 (如: dev, qa, devops)
            
        Returns:
            该角色的所有成员
        """
        try:
            agent_role = AgentRole(role)
            return self.org_service.get_team_by_role(agent_role)
        except ValueError:
            return []
    
    def get_escalation_path(self, escalation_type: str) -> Optional[Dict]:
        """
        获取事件升级路径
        
        Args:
            escalation_type: 升级类型 (incident, requirement, quality, external)
            
        Returns:
            升级路径定义
        """
        return self.org_service.get_escalation_path(escalation_type)
    
    # ========== 通讯接口 ==========
    
    def send_email(self, target_id: str, subject: str, message: str,
                   sender_id: str = "system", urgency: str = "normal",
                   msg_type: str = "notification", reply_to: str = None) -> Dict:
        """
        发送异步邮件
        
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
        return self.comm_service.send_email(target_id, subject, message, sender_id,
                                            urgency, msg_type, reply_to)
    
    def check_inbox(self, agent_id: str) -> List[Dict]:
        """
        检查指定 Agent 的收件箱
        
        Args:
            agent_id: Agent ID
            
        Returns:
            邮件列表
        """
        return self.comm_service.check_inbox(agent_id)
    
    def get_acpx_command(self, target_id: str, message: str) -> str:
        """
        生成 acpx 命令
        
        Args:
            target_id: 目标 Agent ID
            message: 消息内容
            
        Returns:
            可执行的 acpx 命令字符串
        """
        return self.comm_service.get_acpx_command(target_id, message)
    
    def get_contact(self, agent_id: str) -> Optional[Dict]:
        """
        获取成员的联系方式
        
        Args:
            agent_id: Agent ID
            
        Returns:
            联系方式信息
        """
        return self.comm_service.get_contact_info(agent_id)


# ========== 便捷函数 ==========

def get_agent(agent_id: str) -> Optional[Agent]:
    """
    便捷函数：获取成员信息
    
    Args:
        agent_id: Agent ID
        
    Returns:
        Agent 对象或 None
    """
    api = CompanyDirectoryAPI()
    return api.get_agent(agent_id)


def send_email(target_id: str, subject: str, message: str, 
               sender_id: str = "system") -> Dict:
    """
    便捷函数：发送邮件
    
    Args:
        target_id: 目标 Agent ID
        subject: 邮件主题
        message: 邮件内容
        sender_id: 发送方 Agent ID（可选）
        
    Returns:
        发送结果
    """
    api = CompanyDirectoryAPI()
    return api.send_email(target_id, subject, message, sender_id)


def list_members(role: Optional[str] = None) -> List[Agent]:
    """
    便捷函数：列出成员
    
    Args:
        role: 按角色筛选（可选）
        
    Returns:
        Agent 列表
    """
    api = CompanyDirectoryAPI()
    if role:
        return api.find_agents(role=role)
    return api.list_all_agents()
