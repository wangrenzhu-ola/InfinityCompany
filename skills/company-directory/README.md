# Company Directory Skill

InfinityCompany 公司成员目录与通讯管理 Skill。

## 功能特性

- 👥 **成员查询**: 查询公司所有成员信息、职责、技能
- 🏢 **组织架构**: 展示团队层级结构和汇报关系
- 📨 **通讯管理**: 支持 acpx 实时通讯和 emergency\_inbox 异步邮件
- 🚨 **升级路径**: 查询技术故障、需求变更等事件的升级路径
- 🔍 **技能搜索**: 按技能标签搜索成员

## 安装

```bash
# 进入 skill 目录
cd InfinityCompany/skills/company-directory

# 安装依赖（如需额外依赖）
pip install pyyaml
```

## 使用方式

### CLI 使用

```bash
# 列出所有成员
python cli.py agent --list

# 查看特定成员
python cli.py agent hanxin

# 按角色筛选
python cli.py agent --role dev

# 按技能搜索
python cli.py agent --skill "架构"

# 查看组织架构
python cli.py org --chart

# 获取联系方式
python cli.py contact caocan

# 发送邮件
python cli.py email -t caocan -s "进度汇报" -m "任务已完成"

# 生成 acpx 命令
python cli.py acpx hanxin "请检查这个问题"

# 查看汇报链
python cli.py chain hanxin

# 查询升级路径
python cli.py escalation incident
```

### Python API 使用

```python
from src.api import CompanyDirectoryAPI

# 初始化 API
api = CompanyDirectoryAPI()

# 获取成员信息
agent = api.get_agent("hanxin")
print(agent.name, agent.title)

# 列出所有成员
members = api.list_all_agents()

# 按角色筛选
devs = api.find_agents(role="dev")

# 发送邮件
result = api.send_email(
    target_id="caocan",
    subject="进度汇报",
    message="任务已完成"
)

# 获取组织架构
org_chart = api.get_organization_chart()

# 查询升级路径
escalation = api.get_escalation_path("incident")
```

## 成员列表

| Agent ID   | 姓名  | 角色        | 职责         |
| ---------- | --- | --------- | ---------- |
| liubang    | 刘邦  | Owner     | 战略制定，最终决策  |
| zhangliang | 张良  | PM        | 需求分析，产品设计  |
| xiaohe     | 萧何  | Architect | 系统架构，技术选型  |
| hanxin     | 韩信  | Dev       | 核心编码，技术攻坚  |
| caocan     | 曹参  | PMO       | PMO管理，合规审查 |
| zhoubo     | 周勃  | DevOps    | 系统部署，CI/CD |
| chenping   | 陈平  | QA        | 测试策略，质量保障  |
| shusuntong | 叔孙通 | Designer  | UI/UX设计    |
| lujia      | 陆贾  | KB        | 知识管理，文档归档  |
| xiahouying | 夏侯婴 | PA        | 个人事务管理     |
| lishiyi    | 郦食其 | EA        | 外部对接，客户沟通  |

## 通讯协议

### 实时通讯 (acpx)

```bash
acpx <agent_id> "消息内容"
```

### 异步邮件 (emergency\_inbox)

邮件将投递到 `~/.openclaw/workspace/emergency_inbox/<agent_id>/` 目录下。

#### 紧急程度 (Urgency)

- 🔴 **urgent** - 紧急，需要立即处理
- 🟡 **normal** - 普通，按优先级处理（默认）
- 🟢 **low** - 低优先级，有空处理

#### 消息类型 (Message Type)

- 📢 **notification** - 通知，只需知悉，无需回复（默认）
- 💬 **response_required** - 需要回复
- ⚡ **action_required** - 需要采取行动

#### 使用示例

```bash
# 普通通知（无需回复）
python cli.py email -t hanxin -s "任务已分配" -m "请查看新任务" --type notification

# 需要回复的消息
python cli.py email -t caocan -s "进度确认" -m "请确认当前进度" --type response_required

# 紧急消息
python cli.py email -t zhoubo -s "P0故障" -m "生产环境故障" --urgent urgent --type action_required

# 低优先级消息
python cli.py email -t lujia -s "文档整理" -m "有空时整理一下文档" --urgent low
```

#### 避免死循环的最佳实践

1. **默认使用 notification 类型**：大部分消息只需知悉，无需回复
2. **谨慎使用 response_required**：只在真正需要对方回复时使用
3. **在回复中改变消息类型**：回复时改用 notification，避免循环
4. **使用 acpx 进行简短确认**：需要快速回复时使用 acpx 而非邮件

## 配置文件

数据文件位于 `data/` 目录：

- `agents.yaml` - 成员基础信息
- `organization.yaml` - 组织架构
- `protocols.yaml` - 通讯协议配置

