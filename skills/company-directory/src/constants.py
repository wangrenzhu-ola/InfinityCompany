"""
常量定义
"""

from .models import AgentRole

# InfinityCompany 全体成员定义
AGENT_DEFINITIONS = [
    {
        "agent_id": "liubang",
        "name": "刘邦",
        "role": "owner",
        "title": "Owner/CEO",
        "responsibilities": ["战略制定", "最终决策", "全系统任务编排"],
        "reports_to": None,
        "skills": ["战略规划", "决策", "团队管理"],
        "aliases": ["主公", "老刘"],
    },
    {
        "agent_id": "zhangliang",
        "name": "张良",
        "role": "pm",
        "title": "产品经理 (PM)",
        "responsibilities": ["需求分析", "产品设计", "对外交付对接"],
        "reports_to": "liubang",
        "skills": ["需求分析", "产品设计", "用户研究"],
        "aliases": ["子房"],
    },
    {
        "agent_id": "xiaohe",
        "name": "萧何",
        "role": "architect",
        "title": "架构师/技术负责人",
        "responsibilities": ["系统架构设计", "技术选型", "代码审查"],
        "reports_to": "liubang",
        "skills": ["系统架构", "技术选型", "代码审查", "性能优化"],
        "aliases": ["相国"],
    },
    {
        "agent_id": "hanxin",
        "name": "韩信",
        "role": "dev",
        "title": "全栈研发工程师",
        "responsibilities": ["核心编码实现", "技术攻坚", "代码交付"],
        "reports_to": "xiaohe",
        "skills": ["全栈开发", "技术攻坚", "问题解决"],
        "aliases": ["兵仙"],
    },
    {
        "agent_id": "caocan",
        "name": "曹参",
        "role": "pmo",
        "title": "PMO/Scrum Master",
        "responsibilities": ["建立顶层宏观需求(Story)", "督促执行层认领并录入Task", "合规审查", "PMO看板维护"],
        "reports_to": "liubang",
        "skills": ["项目管理", "流程优化", "敏捷实践", "数据分析"],
        "aliases": ["萧规曹随"],
    },
    {
        "agent_id": "zhoubo",
        "name": "周勃",
        "role": "devops",
        "title": "DevOps工程师",
        "responsibilities": ["系统部署", "CI/CD", "监控告警"],
        "reports_to": "xiaohe",
        "skills": ["DevOps", "CI/CD", "容器化", "监控"],
        "aliases": ["绛侯"],
    },
    {
        "agent_id": "chenping",
        "name": "陈平",
        "role": "qa",
        "title": "QA/测试工程师",
        "responsibilities": ["测试策略", "质量保障", "Bug跟踪"],
        "reports_to": "xiaohe",
        "skills": ["测试", "质量保障", "自动化测试"],
        "aliases": ["陈丞相"],
    },
    {
        "agent_id": "shusuntong",
        "name": "叔孙通",
        "role": "designer",
        "title": "UI/UX设计师",
        "responsibilities": ["UI/UX设计", "视觉规范", "用户体验"],
        "reports_to": "zhangliang",
        "skills": ["UI设计", "UX设计", "视觉设计"],
        "aliases": ["叔孙"],
    },
    {
        "agent_id": "lujia",
        "name": "陆贾",
        "role": "kb",
        "title": "知识库管理员",
        "responsibilities": ["知识管理", "文档归档", "记忆检索"],
        "reports_to": "liubang",
        "skills": ["知识管理", "文档编写", "信息检索"],
        "aliases": ["陆大夫"],
    },
    {
        "agent_id": "xiahouying",
        "name": "夏侯婴",
        "role": "pa",
        "title": "个人助理",
        "responsibilities": ["个人事务管理", "日程安排", "效率工具"],
        "reports_to": "liubang",
        "skills": ["时间管理", "效率工具", "日程安排"],
        "aliases": ["滕公"],
    },
    {
        "agent_id": "lishiyi",
        "name": "郦食其",
        "role": "ea",
        "title": "外部助理",
        "responsibilities": ["外部对接", "客户沟通", "跨组织协作"],
        "reports_to": "zhangliang",
        "skills": ["商务沟通", "客户对接", "跨组织协作"],
        "aliases": ["郦生"],
    },
]

# 升级路径定义
ESCALATION_PATHS = {
    "incident": {
        "name": "技术故障升级路径",
        "path": [
            {"level": 1, "agent_id": "hanxin", "role": "一线处理"},
            {"level": 2, "agent_id": "xiaohe", "role": "技术决策"},
            {"level": 3, "agent_id": "zhoubo", "role": "运维介入"},
            {"level": 4, "agent_id": "liubang", "role": "最终决策"},
        ]
    },
    "requirement": {
        "name": "需求变更升级路径",
        "path": [
            {"level": 1, "agent_id": "zhangliang", "role": "需求评估"},
            {"level": 2, "agent_id": "caocan", "role": "影响分析"},
            {"level": 3, "agent_id": "liubang", "role": "最终决策"},
        ]
    },
    "quality": {
        "name": "质量问题升级路径",
        "path": [
            {"level": 1, "agent_id": "chenping", "role": "问题确认"},
            {"level": 2, "agent_id": "hanxin", "role": "修复处理"},
            {"level": 3, "agent_id": "xiaohe", "role": "技术评估"},
            {"level": 4, "agent_id": "liubang", "role": "最终决策"},
        ]
    },
    "external": {
        "name": "外部投诉升级路径",
        "path": [
            {"level": 1, "agent_id": "lishiyi", "role": "初步处理"},
            {"level": 2, "agent_id": "zhangliang", "role": "产品评估"},
            {"level": 3, "agent_id": "liubang", "role": "最终决策"},
        ]
    },
}

# 默认配置
DEFAULT_CONFIG = {
    "inbox_base_path": "~/.openclaw/workspace/emergency_inbox",
    "data_file": "agents.yaml",
}
