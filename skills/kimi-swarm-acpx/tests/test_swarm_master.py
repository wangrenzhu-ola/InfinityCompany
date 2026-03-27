"""
Swarm Master 测试

测试主调度器功能
"""

import unittest
import tempfile
import shutil
import os
import sys

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from swarm_master import (
    SwarmMaster, 
    SwarmConfig, 
    SubTask, 
    create_swarm
)
from dispatcher import AgentConfig, DispatchMode
from result_store import OpenVikingStore


class TestSwarmMaster(unittest.TestCase):
    """SwarmMaster 测试"""
    
    def setUp(self):
        """测试前置"""
        self.temp_dir = tempfile.mkdtemp()
        
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
        
        config = SwarmConfig(
            master_agent_id="hanxin",
            parallel=False,  # 顺序执行便于测试
            timeout=60
        )
        
        # 使用临时存储
        self.store_path = os.path.join(self.temp_dir, "swarm-sessions")
        self.master = SwarmMaster(agents=self.agents, config=config)
        self.master.store = OpenVikingStore(base_path=self.store_path)
    
    def tearDown(self):
        """清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_swarm(self):
        """测试创建 Swarm"""
        self.assertEqual(len(self.master.agents), 2)
        self.assertIn("xiaohe", self.master.agents)
        self.assertIn("chenping", self.master.agents)
    
    def test_execute_single_task(self):
        """测试单个任务执行"""
        tasks = [
            SubTask(
                task_id="task-1",
                agent_id="chenping",
                role="测试工程师",
                description="请回复'收到'"
            )
        ]
        
        result = self.master.execute(
            master_task="测试任务",
            tasks=tasks
        )
        
        self.assertEqual(result.swarm_id.startswith("swarm-"), True)
        self.assertGreater(result.total_duration_ms, 0)
        # 注意：真实执行可能成功或失败，取决于 agent 可用性
    
    def test_execute_parallel_tasks(self):
        """测试并行任务执行"""
        self.master.config.parallel = True
        self.master.dispatcher.dispatch_mode = DispatchMode.PARALLEL
        
        tasks = [
            SubTask(
                task_id="task-1",
                agent_id="xiaohe",
                role="架构师",
                description="请回复'收到'"
            ),
            SubTask(
                task_id="task-2",
                agent_id="chenping",
                role="测试工程师",
                description="请回复'收到'"
            ),
        ]
        
        result = self.master.execute_parallel(
            master_task="并行测试",
            tasks=tasks
        )
        
        self.assertEqual(result.swarm_id.startswith("swarm-"), True)
        # 验证两个 agent 都被调用
        self.assertEqual(len(result.results), 2)
    
    def test_subtask_filtering(self):
        """测试子任务过滤（忽略未知 agent）"""
        tasks = [
            SubTask(
                task_id="task-1",
                agent_id="unknown_agent",  # 不存在的 agent
                role="未知",
                description="这条任务应该被忽略"
            ),
            SubTask(
                task_id="task-2",
                agent_id="chenping",
                role="测试工程师",
                description="这条任务应该执行"
            ),
        ]
        
        result = self.master.execute(
            master_task="过滤测试",
            tasks=tasks
        )
        
        # 只有 chenping 会被执行
        self.assertEqual(len(result.results), 1)
        self.assertIn("chenping", result.results)


class TestCreateSwarm(unittest.TestCase):
    """create_swarm 便捷函数测试"""
    
    def test_create_swarm_with_dicts(self):
        """测试使用字典创建 Swarm"""
        agents = [
            {"agent_id": "xiaohe", "role": "架构师", "name": "萧何"},
            {"agent_id": "hanxin", "role": "开发者", "name": "韩信"},
        ]
        
        swarm = create_swarm(agents=agents, parallel=True)
        
        self.assertEqual(len(swarm.agents), 2)
        self.assertTrue(swarm.config.parallel)
    
    def test_create_swarm_sequential(self):
        """测试创建顺序执行的 Swarm"""
        agents = [
            {"agent_id": "xiaohe", "role": "架构师", "name": "萧何"},
        ]
        
        swarm = create_swarm(agents=agents, parallel=False)
        
        self.assertFalse(swarm.config.parallel)


class TestSubTask(unittest.TestCase):
    """SubTask 测试"""
    
    def test_subtask_creation(self):
        """测试子任务创建"""
        task = SubTask(
            task_id="task-1",
            agent_id="xiaohe",
            role="架构师",
            description="设计登录模块",
            context="需要支持OAuth"
        )
        
        self.assertEqual(task.task_id, "task-1")
        self.assertEqual(task.agent_id, "xiaohe")
        self.assertEqual(task.description, "设计登录模块")
        self.assertEqual(task.context, "需要支持OAuth")


if __name__ == "__main__":
    unittest.main()
