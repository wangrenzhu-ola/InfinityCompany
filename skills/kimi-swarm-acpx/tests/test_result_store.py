"""
OpenViking Store 测试

测试 OpenViking 记忆系统集成
"""

import unittest
import tempfile
import shutil
import os
import sys

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from result_store import (
    OpenVikingStore, 
    SubAgentResult, 
    SwarmSession, 
    ResultStatus
)


class TestOpenVikingStore(unittest.TestCase):
    """OpenViking 存储测试"""
    
    def setUp(self):
        """测试前置 - 使用临时目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.store = OpenVikingStore(base_path=self.temp_dir)
    
    def tearDown(self):
        """清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_session(self):
        """测试创建会话"""
        session = self.store.create_session("测试任务")
        
        self.assertIsNotNone(session.session_id)
        self.assertTrue(session.session_id.startswith("swarm-"))
        self.assertEqual(session.master_task, "测试任务")
        self.assertEqual(session.status, "running")
        self.assertEqual(len(session.sub_results), 0)
    
    def test_save_and_get_result(self):
        """测试保存和获取结果"""
        # 创建会话
        session = self.store.create_session("测试任务")
        
        # 保存结果
        result = self.store.save_result(
            session_id=session.session_id,
            agent_id="xiaohe",
            role="架构师",
            status=ResultStatus.SUCCESS,
            content="架构设计完成",
            duration_ms=1234
        )
        
        self.assertEqual(result.agent_id, "xiaohe")
        self.assertEqual(result.status, ResultStatus.SUCCESS)
        self.assertEqual(result.content, "架构设计完成")
        
        # 获取会话验证
        saved_session = self.store.get_session(session.session_id)
        self.assertEqual(len(saved_session.sub_results), 1)
        self.assertIn("xiaohe", saved_session.sub_results)
    
    def test_save_multiple_results(self):
        """测试保存多个结果"""
        session = self.store.create_session("复杂任务")
        
        # 保存多个子 Agent 结果
        agents = [
            ("xiaohe", "架构师", "架构设计完成"),
            ("hanxin", "开发者", "代码实现完成"),
            ("chenping", "测试工程师", "测试用例编写完成"),
        ]
        
        for agent_id, role, content in agents:
            self.store.save_result(
                session_id=session.session_id,
                agent_id=agent_id,
                role=role,
                status=ResultStatus.SUCCESS,
                content=content,
                duration_ms=1000
            )
        
        # 验证
        saved_session = self.store.get_session(session.session_id)
        self.assertEqual(len(saved_session.sub_results), 3)
    
    def test_save_failed_result(self):
        """测试保存失败结果"""
        session = self.store.create_session("测试任务")
        
        result = self.store.save_result(
            session_id=session.session_id,
            agent_id="xiaohe",
            role="架构师",
            status=ResultStatus.FAILED,
            error="网络超时"
        )
        
        self.assertEqual(result.status, ResultStatus.FAILED)
        self.assertEqual(result.error, "网络超时")
    
    def test_get_session_not_found(self):
        """测试获取不存在的会话"""
        result = self.store.get_session("non-existent")
        self.assertIsNone(result)
    
    def test_aggregate_results(self):
        """测试结果聚合"""
        session = self.store.create_session("聚合测试")
        
        # 添加成功结果
        self.store.save_result(
            session_id=session.session_id,
            agent_id="xiaohe",
            role="架构师",
            status=ResultStatus.SUCCESS,
            content="架构设计完成",
            duration_ms=1000
        )
        
        # 添加失败结果
        self.store.save_result(
            session_id=session.session_id,
            agent_id="hanxin",
            role="开发者",
            status=ResultStatus.FAILED,
            error="代码编译失败"
        )
        
        # 聚合
        aggregated = self.store.aggregate_results(session.session_id)
        
        self.assertIn("聚合测试", aggregated)
        self.assertIn("成功率", aggregated)
        self.assertIn("1/2", aggregated)  # 1/2 成功
        self.assertIn("架构师", aggregated)
        self.assertIn("开发者", aggregated)
    
    def test_complete_session(self):
        """测试完成会话"""
        session = self.store.create_session("测试任务")
        
        # 添加一些结果
        self.store.save_result(
            session_id=session.session_id,
            agent_id="xiaohe",
            role="架构师",
            status=ResultStatus.SUCCESS,
            content="完成"
        )
        
        # 完成会话
        self.store.complete_session(session.session_id, status="completed")
        
        # 验证
        saved_session = self.store.get_session(session.session_id)
        self.assertEqual(saved_session.status, "completed")


class TestSwarmSession(unittest.TestCase):
    """Swarm 会话测试"""
    
    def test_session_creation(self):
        """测试会话创建"""
        session = SwarmSession(
            session_id="swarm-123",
            master_task="测试任务"
        )
        
        self.assertEqual(session.session_id, "swarm-123")
        self.assertEqual(session.master_task, "测试任务")
        self.assertEqual(session.status, "running")
        self.assertEqual(len(session.sub_results), 0)
    
    def test_add_result(self):
        """测试添加结果"""
        session = SwarmSession(
            session_id="swarm-123",
            master_task="测试任务"
        )
        
        result = SubAgentResult(
            agent_id="xiaohe",
            role="架构师",
            status=ResultStatus.SUCCESS,
            content="完成"
        )
        
        session.add_result(result)
        
        self.assertEqual(len(session.sub_results), 1)
        self.assertIn("xiaohe", session.sub_results)
    
    def test_session_to_dict(self):
        """测试转换为字典"""
        session = SwarmSession(
            session_id="swarm-123",
            master_task="测试任务"
        )
        
        data = session.to_dict()
        
        self.assertEqual(data["session_id"], "swarm-123")
        self.assertEqual(data["master_task"], "测试任务")
        self.assertEqual(data["status"], "running")


if __name__ == "__main__":
    unittest.main()
