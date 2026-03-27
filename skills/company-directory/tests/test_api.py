"""
Company Directory API 测试
"""

import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import patch
from src.api import CompanyDirectoryAPI


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
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        self.api.comm_service.acpx_store_path = self.temp_file.name

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)
    
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

    @patch("src.services.CommunicationService._execute_openclaw_agent")
    def test_send_acpx_message_with_receipt(self, mock_exec):
        mock_exec.side_effect = [
            {"status": "success", "response": "ONLINE_ACK"},
            {"status": "success", "response": "ACK 11111111-1111-1111-1111-111111111111"},
        ]
        with patch("src.services.uuid.uuid4", return_value="11111111-1111-1111-1111-111111111111"):
            result = self.api.send_acpx_message(
                target_id="hanxin",
                message="测试回执",
                sender_id="caocan",
                auto_ack=True
            )
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["delivery_status"], "read")

    @patch("src.services.CommunicationService._execute_openclaw_agent")
    def test_broadcast_and_history(self, mock_exec):
        mock_exec.side_effect = [
            {"status": "success", "response": "ONLINE_ACK"},
            {"status": "success", "response": "ACK ok"},
            {"status": "success", "response": "ONLINE_ACK"},
            {"status": "error", "error": "timeout"},
        ]
        result = self.api.send_broadcast(
            selector="ids:hanxin,caocan",
            message="全员通知",
            sender_id="system",
            auto_ack=False
        )
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["total"], 2)
        history = self.api.query_message_history(limit=10)
        self.assertEqual(len(history), 2)

    @patch("src.services.CommunicationService._execute_openclaw_agent")
    def test_presence_status_busy(self, mock_exec):
        mock_exec.return_value = {"status": "error", "error": "session file locked (timeout 10000ms)"}
        result = self.api.check_presence("chenping")
        self.assertEqual(result["status"], "busy")

    @patch("src.services.CommunicationService._execute_openclaw_agent")
    def test_send_acpx_message_retry_success(self, mock_exec):
        mock_exec.side_effect = [
            {"status": "success", "response": "ONLINE_ACK"},
            {"status": "error", "error": "timeout"},
            {"status": "success", "response": "收到"},
        ]
        result = self.api.send_acpx_message(
            target_id="hanxin",
            message="重试消息",
            retries=1,
            auto_ack=False
        )
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["delivery_status"], "delivered")
        self.assertEqual(result["attempts"], 2)

    @patch("src.services.CommunicationService._execute_openclaw_agent")
    @patch("src.services.CommunicationService.send_email")
    def test_send_acpx_message_fallback_email(self, mock_send_email, mock_exec):
        mock_exec.side_effect = [
            {"status": "success", "response": "ONLINE_ACK"},
            {"status": "error", "error": "timeout"},
            {"status": "error", "error": "timeout"},
        ]
        mock_send_email.return_value = {
            "status": "success",
            "file_path": "/tmp/fallback.md"
        }
        result = self.api.send_acpx_message(
            target_id="hanxin",
            message="降级消息",
            retries=1,
            fallback_to_email=True,
            auto_ack=False
        )
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["delivery_status"], "fallback_email")
        self.assertTrue(result["fallback_email_result"]["status"] == "success")

    @patch("src.services.CommunicationService._execute_openclaw_agent")
    def test_broadcast_retry_failed_targets(self, mock_exec):
        mock_exec.side_effect = [
            {"status": "success", "response": "ONLINE_ACK"},
            {"status": "success", "response": "收到"},
            {"status": "success", "response": "ONLINE_ACK"},
            {"status": "error", "error": "timeout"},
            {"status": "success", "response": "ONLINE_ACK"},
            {"status": "success", "response": "收到"},
        ]
        result = self.api.send_broadcast(
            selector="ids:hanxin,caocan",
            message="广播重试",
            auto_ack=False,
            retry_failed_targets=True,
            retry_rounds=1
        )
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["total"], 2)
        self.assertEqual(result["failed"], 0)


if __name__ == "__main__":
    unittest.main()
