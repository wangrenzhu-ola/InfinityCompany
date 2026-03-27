# PMO Manager Skill

InfinityCompany PMO 看板管理 Skill，支持 Story/Task 管理、迭代跟踪、复盘管理等功能。

## 功能特性

- 📋 **Story 管理**: 创建、查询、更新顶层需求
- 📝 **Task 管理**: 完整的任务生命周期管理，含审核流程
- 🔍 **合规校验**: 自动检查 deadline、story 关联、报告文件
- 📊 **看板视图**: 按状态分组展示任务
- 🔄 **Retro 复盘**: 支持迭代复盘、项目复盘、事故复盘
- 📈 **迭代管理**: Sprint 创建与跟踪

## 安装

```bash
# 进入 skill 目录
cd InfinityCompany/skills/pmo-manager

# 安装依赖（如需额外依赖）
pip install pyyaml
```

数据将存储在 SQLite 数据库 `~/.openclaw/workspace/pmo.db`。

## 使用方式

### CLI 使用

#### Story 管理

```bash
# 创建 Story
python cli.py story create "用户认证模块" --creator liubang --priority P0

# 获取 Story
python cli.py story get story-xxx

# 列出 Story
python cli.py story list
```

#### Task 管理

```bash
# 提交 Task 审核
python cli.py task submit \
  --title "实现登录接口" \
  --assignee hanxin \
  --story story-xxx \
  --priority P1 \
  --deadline "2026-04-01 17:00" \
  --estimated-hours 8

# 审核 Task（PMO 使用）
python cli.py task review task-xxx APPROVED
python cli.py task review task-xxx REJECTED --reason "需要补充测试用例"

# 更新 Task 状态
python cli.py task status task-xxx in_progress
python cli.py task status task-xxx done --report-file ~/reports/login.md
python cli.py task status task-xxx blocked --blocker-reason "依赖 API 文档"

# 查看待审核队列
python cli.py task queue

# 查看看板
python cli.py board
```

#### Retro 复盘

```bash
# 创建复盘
python cli.py retro create "Sprint 5 复盘" \
  --type sprint \
  --facilitator caocan \
  --template mad_sad_glad \
  --participants "liubang,zhangliang,xiaohe,hanxin"

# 开始收集阶段
python cli.py retro start retro-xxx

# 添加反馈条目
python cli.py retro item-add retro-xxx glad "团队协作很好" --author hanxin
python cli.py retro item-add retro-xxx sad "测试环境不稳定" --author zhoubo

# 投票
python cli.py retro item-vote item-xxx --voter hanxin

# 开始讨论阶段
python cli.py retro discuss retro-xxx

# 创建改进行动
python cli.py retro action-add retro-xxx "优化测试环境" \
  --assignee zhoubo \
  --due "2026-04-15" \
  --priority P0

# 完成复盘
python cli.py retro complete retro-xxx --summary "本次迭代整体顺利..."

# 生成复盘报告
python cli.py retro report retro-xxx

# 列出复盘
python cli.py retro list

# 列出改进行动
python cli.py retro actions --retro-id retro-xxx
```

### Python API 使用

```python
from src.api import PMOManagerAPI
from src.models import Priority
from datetime import datetime, timedelta

# 初始化 API
pmo = PMOManagerAPI()

# 创建 Story
story = pmo.create_story(
    title="用户认证模块",
    creator_id="liubang",
    priority=Priority.P0
)

# 提交 Task
result = pmo.submit_task(
    title="实现登录接口",
    assignee_id="hanxin",
    story_id=story.story_id,
    priority=Priority.P1,
    deadline=datetime.now() + timedelta(days=7)
)

if result['success']:
    task = result['task']
    print(f"Task 创建成功: {task.task_id}")

# 审核 Task
pmo.review_task(task.task_id, "APPROVED")

# 更新状态
pmo.update_task_status(task.task_id, "done", 
                       output_summary="已完成",
                       report_file="~/reports/login.md")

# 创建复盘
retro = pmo.create_retro(
    title="Sprint 5 复盘",
    retro_type="sprint",
    facilitator_id="caocan",
    template="mad_sad_glad"
)

# 添加反馈
pmo.add_retro_item(retro.retro_id, "glad", "团队协作很好", "hanxin")

# 生成报告
report = pmo.generate_retro_report(retro.retro_id)
print(report['report_markdown'])
```

## 数据模型

### Task 状态流转

```
DRAFT → PENDING_REVIEW → APPROVED → TODO → IN_PROGRESS → DONE
  ↓         ↓
REJECTED ←──┘
              
BLOCKED ←──── IN_PROGRESS
```

### Retro 复盘流程

```
PLANNING → COLLECTING → DISCUSSING → COMPLETED
```

### Retro 模板

- **mad_sad_glad**: Mad(愤怒) / Sad(沮丧) / Glad(高兴)
- **start_stop_continue**: Start(开始) / Stop(停止) / Continue(继续)
- **four_ls**: Liked(喜欢) / Learned(学到) / Lacked(缺失) / Longed For(渴望)

## 合规规则

1. **Deadline 强制**: 所有 Task 必须有 Deadline，且必须在未来时间
2. **Story 关联强制**: 所有 Task 必须关联到已存在的 Story
3. **DONE 报告强制**: Task 标记为 DONE 时必须提供 report_file
4. **审核流程强制**: 新建 Task 必须走审核流程

## 复盘报告示例

复盘报告将生成 Markdown 格式：

```markdown
# Retro 复盘报告: Sprint 5 复盘

## 基本信息
- **复盘类型**: sprint
- **主持人**: caocan
- **参与人员**: liubang, zhangliang, xiaohe, hanxin
- **复盘日期**: 2026-03-30T15:00:00

## 统计数据
- **收集条目数**: 12
- **投票总数**: 25
- **改进行动数**: 5

## 反馈汇总
### GLAD (4 条)
1. **团队协作很好** (5 票)
   - 作者: hanxin

### SAD (3 条)
1. **测试环境不稳定** (4 票)
   - 作者: zhoubo

## 改进行动计划
| 优先级 | 行动项 | 负责人 | 截止日期 | 状态 |
|--------|--------|--------|----------|------|
| P0 | 优化测试环境 | zhoubo | 2026-04-15 | pending |

## 复盘总结
本次迭代整体顺利...
```
