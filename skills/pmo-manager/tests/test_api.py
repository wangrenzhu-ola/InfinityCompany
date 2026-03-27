"""
PMO Manager API 测试
"""

import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from datetime import datetime, timedelta, date
from src.api import PMOManagerAPI
from src.models import Priority, TaskStatus, RetroType, RetroTemplate


class TestStoryService(unittest.TestCase):
    """测试 Story 服务"""
    
    def setUp(self):
        """测试前置"""
        # 使用临时数据库
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        self.api = PMOManagerAPI(self.db_path)
    
    def tearDown(self):
        """测试清理"""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_create_story(self):
        """测试创建 Story"""
        story = self.api.create_story(
            title="用户认证模块",
            creator_id="liubang",
            background="实现用户登录注册功能",
            objectives=["支持手机号登录", "支持邮箱登录"],
            priority=Priority.P0
        )
        
        self.assertIsNotNone(story)
        self.assertTrue(story.story_id.startswith("story-"))
        self.assertEqual(story.title, "用户认证模块")
        self.assertEqual(story.creator_id, "liubang")
    
    def test_get_story(self):
        """测试获取 Story"""
        story = self.api.create_story("测试 Story", "liubang")
        fetched = self.api.get_story(story.story_id)
        
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.story_id, story.story_id)
    
    def test_list_stories(self):
        """测试列出 Story"""
        self.api.create_story("Story 1", "liubang")
        self.api.create_story("Story 2", "zhangliang")
        
        stories = self.api.list_stories()
        self.assertEqual(len(stories), 2)


class TestTaskService(unittest.TestCase):
    """测试 Task 服务"""
    
    def setUp(self):
        """测试前置"""
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        self.api = PMOManagerAPI(self.db_path)
        
        # 创建测试 Story
        self.story = self.api.create_story("测试 Story", "liubang")
    
    def tearDown(self):
        """测试清理"""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_submit_task_success(self):
        """测试成功提交 Task"""
        result = self.api.submit_task(
            title="实现登录接口",
            assignee_id="hanxin",
            story_id=self.story.story_id,
            priority=Priority.P1,
            deadline=datetime.now() + timedelta(days=7),
            description="实现用户登录接口"
        )
        
        self.assertTrue(result["success"])
        self.assertIsNotNone(result["task"])
        self.assertEqual(result["task"].title, "实现登录接口")
    
    def test_submit_task_no_story(self):
        """测试提交 Task 无 Story"""
        result = self.api.submit_task(
            title="测试任务",
            assignee_id="hanxin",
            story_id="nonexistent-story",
            priority=Priority.P1,
            deadline=datetime.now() + timedelta(days=7)
        )
        
        self.assertFalse(result["success"])
        self.assertIn("errors", result)
    
    def test_submit_task_past_deadline(self):
        """测试提交 Task 截止时间在过去"""
        result = self.api.submit_task(
            title="测试任务",
            assignee_id="hanxin",
            story_id=self.story.story_id,
            priority=Priority.P1,
            deadline=datetime.now() - timedelta(days=1)
        )
        
        self.assertFalse(result["success"])
    
    def test_review_task_approve(self):
        """测试审核通过 Task"""
        submit_result = self.api.submit_task(
            title="测试任务",
            assignee_id="hanxin",
            story_id=self.story.story_id,
            priority=Priority.P1,
            deadline=datetime.now() + timedelta(days=7)
        )
        
        task_id = submit_result["task"].task_id
        result = self.api.review_task(task_id, "APPROVED")
        
        self.assertTrue(result["success"])
        self.assertIn("TODO", str(result["task"].status))
    
    def test_review_task_reject(self):
        """测试审核拒绝 Task"""
        submit_result = self.api.submit_task(
            title="测试任务",
            assignee_id="hanxin",
            story_id=self.story.story_id,
            priority=Priority.P1,
            deadline=datetime.now() + timedelta(days=7)
        )
        
        task_id = submit_result["task"].task_id
        result = self.api.review_task(task_id, "REJECTED", "需要修改")
        
        self.assertTrue(result["success"])
        self.assertIn("REJECTED", str(result["task"].status))
        self.assertEqual(result["task"].rejection_reason, "需要修改")
    
    def test_update_task_status(self):
        """测试更新 Task 状态"""
        # 先创建并批准 Task
        submit_result = self.api.submit_task(
            title="测试任务",
            assignee_id="hanxin",
            story_id=self.story.story_id,
            priority=Priority.P1,
            deadline=datetime.now() + timedelta(days=7)
        )
        task_id = submit_result["task"].task_id
        self.api.review_task(task_id, "APPROVED")
        
        # 更新为进行中
        result = self.api.update_task_status(task_id, "in_progress")
        self.assertTrue(result["success"])


class TestRetroService(unittest.TestCase):
    """测试 Retro 服务"""
    
    def setUp(self):
        """测试前置"""
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        self.api = PMOManagerAPI(self.db_path)
    
    def tearDown(self):
        """测试清理"""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_create_retro(self):
        """测试创建复盘"""
        retro = self.api.create_retro(
            title="Sprint 5 复盘",
            retro_type="sprint",
            facilitator_id="caocan",
            template="mad_sad_glad",
            participants=["liubang", "hanxin"]
        )
        
        self.assertIsNotNone(retro)
        self.assertTrue(retro.retro_id.startswith("retro-"))
        self.assertEqual(retro.title, "Sprint 5 复盘")
    
    def test_retro_workflow(self):
        """测试复盘完整流程"""
        # 创建复盘
        retro = self.api.create_retro(
            title="测试复盘",
            retro_type="sprint",
            facilitator_id="caocan",
            template="mad_sad_glad"
        )
        
        # 开始收集
        result = self.api.start_retro_collecting(retro.retro_id)
        self.assertTrue(result["success"])
        
        # 添加反馈
        result = self.api.add_retro_item(retro.retro_id, "glad", "协作很好", "hanxin")
        self.assertTrue(result["success"])
        item_id = result["item"].item_id
        
        # 投票
        result = self.api.vote_retro_item(item_id, "zhangliang")
        self.assertTrue(result["success"])
        self.assertEqual(result["item"].votes, 1)
        
        # 开始讨论
        result = self.api.start_retro_discussing(retro.retro_id)
        self.assertTrue(result["success"])
        
        # 创建改进行动
        result = self.api.create_action_item(
            retro.retro_id,
            "优化流程",
            "caocan",
            date.today() + timedelta(days=14),
            "P1"
        )
        self.assertTrue(result["success"])
        
        # 完成复盘
        result = self.api.complete_retro(retro.retro_id, "总结")
        self.assertTrue(result["success"])
    
    def test_generate_report(self):
        """测试生成复盘报告"""
        retro = self.api.create_retro(
            title="报告测试复盘",
            retro_type="sprint",
            facilitator_id="caocan"
        )
        
        # 添加一些反馈
        self.api.start_retro_collecting(retro.retro_id)
        self.api.add_retro_item(retro.retro_id, "glad", "协作很好", "hanxin")
        self.api.add_retro_item(retro.retro_id, "sad", "环境不稳定", "zhoubo")
        
        result = self.api.generate_retro_report(retro.retro_id)
        self.assertTrue(result["success"])
        self.assertIn("report_markdown", result)
        self.assertIn("协作很好", result["report_markdown"])


if __name__ == "__main__":
    unittest.main()
