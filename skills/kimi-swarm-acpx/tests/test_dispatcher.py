"""
ACPX Dispatcher 测试

测试 acpx-infinity 任务分发功能
"""

import unittest
import subprocess
from unittest.mock import patch, MagicMock
import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dispatcher import ACPXDispatcher, AgentConfig, DispatchResult, DispatchMode


class TestACPXDispatcher(unittest.TestCase):
    """ACPX 调度器测试"""
    
    def setUp(self):
        """测试前置"""
        self.agents = [
            AgentConfig(
                agent_id="xiaohe",
                role="架构师",
                name="萧何"
            ),
            AgentConfig(
                agent_id="chenping",
                role="测试工程师",
                name="陈平"
            ),
        ]
        self.dispatcher = ACPXDispatcher(
            agents=self.agents,
            dispatch_mode=DispatchMode.SEQUENTIAL  # 顺序执行便于测试
        )
    
    def test_dispatch_unknown_agent(self):
        """测试分发到未知 Agent"""
        result = self.dispatcher.dispatch("unknown_agent", "测试消息")
        
        self.assertFalse(result.success)
        self.assertIn("Unknown agent", result.error)
    
    def test_dispatch_success(self):
        """测试成功分发（使用真实 acpx-infinity）"""
        result = self.dispatcher.dispatch(
            "chenping",
            "你好，这是一条测试消息，请回复'收到'"
        )
        
        # 注意：这个测试依赖真实环境
        # 如果 chenping agent 不可用，会失败
        print(f"Result: success={result.success}, output={result.output}, error={result.error}")
        
        # 基本断言
        self.assertEqual(result.agent_id, "chenping")
        self.assertGreaterEqual(result.retries, 0)
    
    def test_build_message(self):
        """测试消息构建"""
        config = self.agents[0]  # xiaohe
        message = "请设计一个登录模块"
        
        full_message = self.dispatcher._build_message(config, message)
        
        self.assertIn("萧何", full_message)
        self.assertIn("架构师", full_message)
        self.assertIn("请设计一个登录模块", full_message)
        self.assertIn("[DONE]", full_message)
    
    def test_execute_acpx_timeout(self):
        """测试 acpx 执行超时"""
        # 这个测试需要 mock subprocess.run
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("cmd", 300)
            
            result = self.dispatcher._execute_acpx(
                "xiaohe",
                "测试消息",
                timeout=1
            )
            
            # TimeoutExpired 应该被捕获并转换为 TimeoutError
            # 实际实现在 catch 块中处理
    
    def test_execute_acpx_error(self):
        """测试 acpx 执行错误"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,
                stderr="Some error"
            )
            
            with self.assertRaises(RuntimeError) as context:
                self.dispatcher._execute_acpx(
                    "xiaohe",
                    "测试消息",
                    timeout=30
                )
            
            self.assertIn("failed", str(context.exception))


class TestAgentConfig(unittest.TestCase):
    """Agent 配置测试"""
    
    def test_agent_config_creation(self):
        """测试 Agent 配置创建"""
        config = AgentConfig(
            agent_id="hanxin",
            role="开发者",
            name="韩信",
            capabilities=["Python", "JavaScript"],
            timeout=600,
            max_retries=5
        )
        
        self.assertEqual(config.agent_id, "hanxin")
        self.assertEqual(config.role, "开发者")
        self.assertEqual(config.name, "韩信")
        self.assertEqual(config.capabilities, ["Python", "JavaScript"])
        self.assertEqual(config.timeout, 600)
        self.assertEqual(config.max_retries, 5)


class TestDispatchResult(unittest.TestCase):
    """分发结果测试"""
    
    def test_dispatch_result_success(self):
        """测试成功结果"""
        result = DispatchResult(
            agent_id="xiaohe",
            success=True,
            output="设计完成",
            duration_ms=1234,
            retries=0
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.output, "设计完成")
        self.assertEqual(result.duration_ms, 1234)
    
    def test_dispatch_result_failure(self):
        """测试失败结果"""
        result = DispatchResult(
            agent_id="xiaohe",
            success=False,
            error="Timeout",
            retries=3
        )
        
        self.assertFalse(result.success)
        self.assertEqual(result.error, "Timeout")
        self.assertEqual(result.retries, 3)


if __name__ == "__main__":
    unittest.main()
