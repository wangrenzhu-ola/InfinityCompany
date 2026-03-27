"""
数据模型定义
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class AgentRole(Enum):
    """角色类型枚举"""
    OWNER = "owner"           # 刘邦
    PM = "pm"                 # 张良
    ARCHITECT = "architect"   # 萧何
    DEV = "dev"               # 韩信
    PMO = "pmo"               # 曹参
    DEVOPS = "devops"         # 周勃
    QA = "qa"                 # 陈平
    DESIGNER = "designer"     # 叔孙通
    KB = "kb"                 # 陆贾
    PA = "pa"                 # 夏侯婴
    EA = "ea"                 # 郦食其


class CommunicationType(Enum):
    """通讯类型"""
    ACPX = "acpx"                    # 实时沟通
    EMERGENCY_INBOX = "emergency_inbox"  # 异步邮件


@dataclass
class Agent:
    """Agent（公司成员）数据模型"""
    agent_id: str                      # 唯一标识
    name: str                          # 姓名
    role: AgentRole                    # 角色
    title: str                         # 岗位名称
    responsibilities: List[str]        # 核心职责
    reports_to: Optional[str] = None   # 汇报对象
    skills: List[str] = field(default_factory=list)  # 技能标签
    email: Optional[str] = None        # 联系邮箱
    aliases: List[str] = field(default_factory=list)  # 别名
    
    def to_dict(self) -> Dict:
        """序列化为字典"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role.value if isinstance(self.role, AgentRole) else self.role,
            "title": self.title,
            "responsibilities": self.responsibilities,
            "reports_to": self.reports_to,
            "skills": self.skills,
            "email": self.email,
            "aliases": self.aliases,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Agent":
        """从字典反序列化"""
        role_value = data.get("role", "dev")
        role = AgentRole(role_value) if isinstance(role_value, str) else role_value
        
        return cls(
            agent_id=data["agent_id"],
            name=data["name"],
            role=role,
            title=data.get("title", ""),
            responsibilities=data.get("responsibilities", []),
            reports_to=data.get("reports_to"),
            skills=data.get("skills", []),
            email=data.get("email"),
            aliases=data.get("aliases", []),
        )


@dataclass
class OrganizationUnit:
    """组织架构单元"""
    unit_id: str                       # 单元ID
    name: str                          # 单元名称
    leader_id: str                     # 负责人ID
    member_ids: List[str]              # 成员ID列表
    parent_id: Optional[str] = None    # 父单元ID
    description: Optional[str] = None  # 描述


@dataclass
class Email:
    """邮件消息模型"""
    email_id: str                      # 邮件ID
    sender_id: str                     # 发送方
    sender_name: str                   # 发送方姓名
    target_id: str                     # 接收方
    subject: str                       # 主题
    message: str                       # 内容
    timestamp: datetime                # 时间戳
    urgency: str = "normal"            # 紧急程度: urgent, normal, low
    msg_type: str = "notification"     # 消息类型: notification(只需知悉), response_required(需要回复), action_required(需要行动)
    reply_to: Optional[str] = None     # 回复地址/引用ID
    
    def to_file_content(self) -> str:
        """生成邮件文件内容"""
        urgency_label = {
            "urgent": "🔴 紧急",
            "normal": "🟡 普通", 
            "low": "🟢 低优先级"
        }.get(self.urgency, "🟡 普通")
        
        msg_type_label = {
            "notification": "📢 通知（无需回复）",
            "response_required": "💬 需要回复",
            "action_required": "⚡ 需要行动"
        }.get(self.msg_type, "📢 通知")
        
        return f"""---
type: emergency_email
email_id: {self.email_id}
sender: {self.sender_id}
sender_name: {self.sender_name}
target: {self.target_id}
subject: {self.subject}
timestamp: {self.timestamp.isoformat()}
urgency: {self.urgency}
msg_type: {self.msg_type}
reply_to: {self.reply_to or 'null'}
---

# {urgency_label} | {self.subject}

**发送方**: {self.sender_name} ({self.sender_id})  
**时间**: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}  
**类型**: {msg_type_label}  
**消息ID**: {self.email_id}

---

{self.message}

---

## 回复指引

{"⚠️ **此消息需要您的回复**" if self.msg_type == "response_required" else "💡 **此消息只需知悉，无需回复**" if self.msg_type == "notification" else "⚡ **此消息需要您采取行动**"}

{"🔴 **紧急消息，请尽快处理**" if self.urgency == "urgent" else ""}

### 快捷回复命令
```bash
# 回复发件人
acpx {self.sender_id} "已收到，[您的回复内容]"

# 发送邮件回复
python3 ~/.openclaw/workspace/skills/company-directory/cli.py email \
  --to {self.sender_id} \
  --subject "Re: {self.subject}" \
  --message "[您的回复内容]" \
  --from {self.target_id}
```

---
*此邮件由 company-directory 邮件系统自动生成 | InfinityCompany*
"""
