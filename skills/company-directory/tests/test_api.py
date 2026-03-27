"""
Company Directory API 测试
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from src.api import CompanyDirectoryAPI
from src.models import AgentRole


class TestCompanyDirectoryAPI(unittest.TestCase):
    """测试 CompanyDirectoryAPI"""
    
    def setUp(self):
        """测试前置"""
        self.api = CompanyDirectoryAPI()
    
    def test_get_agent(self):
        """测试获取成员"""
        agent = self.api.get_agent("hanxin")
        self.assertIsNotNone(agent)
        self.assertEqual(agent.agent_id, "hanxin")
        self.assertEqual(agent.name, "韩信")
    
    def test_get_nonexistent_agent(self):
        """测试获取不存在的成员"""
        agent = self.api.get_agent("nonexistent")
        self.assertIsNone(agent)
    
    def test_list_all_agents(self):
        """测试列出所有成员"""
        agents = self.api.list_all_agents()
        self.assertEqual(len(agents), 11)  # 共有11个成员
        
        agent_ids = [a.agent_id for a in agents]
        self.assertIn("liubang", agent_ids)
        self.assertIn("zhangliang", agent_ids)
        self.assertIn("hanxin", agent_ids)
    
    def test_find_agents_by_role(self):
        """测试按角色搜索"""
        devs = self.api.find_agents(role="dev")
        self.assertEqual(len(devs), 1)
        self.assertEqual(devs[0].agent_id, "hanxin")
        
        pmos = self.api.find_agents(role="pmo")
        self.assertEqual(len(pmos), 1)
        self.assertEqual(pmos[0].agent_id, "caocan")
    
    def test_find_agents_by_skill(self):
        """测试按技能搜索"""
        architects = self.api.find_agents(skill="架构")
        self.assertTrue(len(architects) >= 1)
    
    def test_get_reporting_chain(self):
        """测试获取汇报链"""
        chain = self.api.get_reporting_chain("hanxin")
        self.assertTrue(len(chain) >= 1)
        self.assertEqual(chain[0].agent_id, "hanxin")
    
    def test_get_organization_chart(self):
        """测试获取组织架构"""
        chart = self.api.get_organization_chart()
        self.assertIn("organization", chart)
        self.assertIn("roots", chart)
    
    def test_get_escalation_path(self):
        """测试获取升级路径"""
        path = self.api.get_escalation_path("incident")
        self.assertIsNotNone(path)
        self.assertIn("path", path)
        self.assertTrue(len(path["path"]) >= 1)
    
    def test_get_contact(self):
        """测试获取联系方式"""
        contact = self.api.get_contact("caocan")
        self.assertIsNotNone(contact)
        self.assertEqual(contact["agent_id"], "caocan")
        self.assertIn("acpx_command", contact)
        self.assertIn("inbox_path", contact)


class TestCommunicationService(unittest.TestCase):
    """测试通讯服务"""
    
    def setUp(self):
        """测试前置"""
        self.api = CompanyDirectoryAPI()
    
    def test_send_email_invalid_agent(self):
        """测试发送邮件到无效成员"""
        result = self.api.send_email(
            target_id="invalid_agent",
            subject="测试",
            message="测试消息"
        )
        self.assertEqual(result["status"], "error")
        self.assertIn("valid_agents", result)
    
    def test_get_acpx_command(self):
        """测试生成 acpx 命令"""
        cmd = self.api.get_acpx_command("caocan", "测试消息")
        self.assertIn("acpx", cmd)
        self.assertIn("caocan", cmd)
        self.assertIn("测试消息", cmd)


if __name__ == "__main__":
    unittest.main()
