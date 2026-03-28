"""
数据存储层
"""

from typing import List, Optional, Dict
from .models import Agent, AgentRole
from .constants import AGENT_DEFINITIONS


class Storage:
    """数据存储管理器"""
    
    def __init__(self, data_dir: str = None):
        """
        初始化存储
        
        Args:
            data_dir: 数据目录路径，默认为 None（使用内置数据）
        """
        self.data_dir = data_dir
        self._agents: Dict[str, Agent] = {}
        self._load_agents()
    
    def _load_agents(self):
        """加载 Agent 数据"""
        # 从常量定义加载
        for agent_data in AGENT_DEFINITIONS:
            agent = Agent.from_dict(agent_data)
            self._agents[agent.agent_id] = agent
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        根据ID获取成员信息
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent 对象或 None
        """
        return self._agents.get(agent_id)
    
    def find_agents_by_role(self, role: AgentRole) -> List[Agent]:
        """
        根据角色查找成员
        
        Args:
            role: 角色类型
            
        Returns:
            Agent 列表
        """
        return [a for a in self._agents.values() if a.role == role]
    
    def find_agents_by_name(self, name: str) -> List[Agent]:
        """
        根据姓名模糊搜索成员
        
        Args:
            name: 姓名关键词
            
        Returns:
            Agent 列表
        """
        name_lower = name.lower()
        results = []
        
        for agent in self._agents.values():
            # 匹配姓名
            if name_lower in agent.name.lower():
                results.append(agent)
                continue
            
            # 匹配别名
            for alias in agent.aliases:
                if name_lower in alias.lower():
                    results.append(agent)
                    break
        
        return results
    
    def find_agents_by_skill(self, skill: str) -> List[Agent]:
        """
        根据技能搜索成员
        
        Args:
            skill: 技能关键词
            
        Returns:
            Agent 列表
        """
        skill_lower = skill.lower()
        results = []
        
        for agent in self._agents.values():
            for agent_skill in agent.skills:
                if skill_lower in agent_skill.lower():
                    results.append(agent)
                    break
        
        return results
    
    def list_all_agents(self) -> List[Agent]:
        """列出所有成员"""
        return list(self._agents.values())
    
    def get_org_chart(self) -> Dict:
        """
        获取组织架构图
        
        Returns:
            组织架构树形结构
        """
        # 找到根节点（没有汇报对象的）
        roots = [a for a in self._agents.values() if a.reports_to is None]
        
        def build_tree(agent_id: str, level: int = 0) -> Dict:
            """递归构建树形结构"""
            agent = self._agents.get(agent_id)
            if not agent:
                return None
            
            # 查找直接下属
            subordinates = [
                a for a in self._agents.values() 
                if a.reports_to == agent_id
            ]
            
            return {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "title": agent.title,
                "level": level,
                "subordinates": [
                    build_tree(s.agent_id, level + 1) 
                    for s in subordinates
                ]
            }
        
        return {
            "organization": "InfinityCompany",
            "roots": [build_tree(r.agent_id) for r in roots]
        }
    
    def get_reporting_chain(self, agent_id: str) -> List[Agent]:
        """
        获取成员的汇报链
        
        Args:
            agent_id: Agent ID
            
        Returns:
            从当前成员到最高层的汇报链列表
        """
        chain = []
        current = self.get_agent(agent_id)
        
        while current:
            chain.append(current)
            if current.reports_to:
                current = self.get_agent(current.reports_to)
            else:
                break
        
        return chain
