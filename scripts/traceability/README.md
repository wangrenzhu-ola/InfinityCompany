# InfinityCompany 留痕校验工具

> 自动化校验 InfinityCompany 项目的协作活动留痕情况

## 功能特性

- ✅ **Git 提交校验** - 提交信息规范、频率分析、改动量统计
- ✅ **文档更新校验** - 时间戳检查、模板合规、版本关联
- ✅ **Notion 看板校验** - 必填字段、状态流转、SLA 合规
- ✅ **复盘同步校验** - Task/Bug 关联、改进项跟进、周期合规
- 📝 **多格式报告** - Markdown + JSON 双格式输出

## 快速开始

### 1. 安装依赖

```bash
cd scripts/traceability
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# Notion API 配置
export NOTION_API_KEY="your_notion_api_key"
export NOTION_STORY_DB_ID="your_story_db_id"
export NOTION_TASK_DB_ID="your_task_db_id"
export NOTION_BUG_DB_ID="your_bug_db_id"
export NOTION_ITERATION_DB_ID="your_iteration_db_id"
export NOTION_RETROSPECTIVE_DB_ID="your_retrospective_db_id"
export NOTION_EXTERNAL_REQ_DB_ID="your_external_req_db_id"

# 可选：Slack 通知
export SLACK_WEBHOOK_URL="your_slack_webhook"
```

### 3. 运行检查

```bash
# 运行所有检查
python main.py --check all

# 仅检查 Git 提交
python main.py --check git --since "7 days ago"

# 生成周报
python main.py --check all --report weekly --output ./reports

# 错误时退出（用于 CI）
python main.py --check all --fail-on-error
```

## 目录结构

```
traceability/
├── README.md                 # 本文件
├── requirements.txt          # Python 依赖
├── config.yaml              # 校验配置
├── main.py                  # 主入口脚本
├── core/                    # 核心校验模块
│   ├── __init__.py
│   ├── git_checker.py       # Git 提交校验
│   ├── document_checker.py  # 文档更新校验
│   ├── notion_checker.py    # Notion 看板校验
│   └── retro_checker.py     # 复盘同步校验
├── utils/                   # 工具模块
│   ├── __init__.py
│   ├── notion_client.py     # Notion API 客户端
│   ├── git_helper.py        # Git 操作辅助
│   └── logger.py            # 日志工具
└── reports/                 # 报告输出目录（自动生成）
```

## 使用场景

### 场景1: 开发时本地检查

```bash
# 在 Git Hook 中集成
# .git/hooks/commit-msg

python scripts/traceability/main.py --check git --since "1 day ago"
```

### 场景2: 每日自动检查

```bash
# 添加到 crontab
# 每天 18:30 执行

30 18 * * * cd /path/to/InfinityCompany && \
  python scripts/traceability/main.py --check all --report daily >> logs/traceability.log 2>&1
```

### 场景3: CI/CD 集成

```yaml
# .github/workflows/traceability.yml

- name: Run traceability checks
  run: |
    python scripts/traceability/main.py \
      --check all \
      --fail-on-error \
      --output reports/
```

## 配置说明

编辑 `config.yaml` 自定义校验规则：

```yaml
# Git 提交规范配置
git:
  valid_types:
    - feat
    - fix
    - docs
    # ...

# 文档检查配置
documents:
  stale_days_threshold: 90  # 文档过期天数

# Notion SLA 配置
notion:
  sla:
    external_req:
      待评估: 24  # 小时
      已采纳: 4
```

## 报告输出

检查完成后，报告会保存到 `reports/` 目录：

```
reports/
├── traceability_daily_20260327_183000.md    # Markdown 格式
├── traceability_daily_20260327_183000.json  # JSON 格式
├── traceability_weekly_20260327_190000.md
└── ...
```

## 开发指南

### 添加新的检查项

1. 在 `core/` 下创建新的 checker 类
2. 继承 `BaseChecker` 接口
3. 在 `main.py` 中注册新的检查

```python
# core/custom_checker.py

class CustomChecker:
    def run_all_checks(self):
        errors = []
        warnings = []
        # 实现检查逻辑
        return CheckResult(errors, warnings)
```

### 运行测试

```bash
# 安装开发依赖
pip install pytest black flake8

# 运行测试
pytest tests/

# 代码格式化
black core/ utils/ main.py
```

## 常见问题

### Q: Notion API 调用失败？

A: 检查环境变量是否正确设置：
```bash
echo $NOTION_API_KEY
echo $NOTION_STORY_DB_ID
```

### Q: 如何跳过某些检查？

A: 使用 `--check` 参数指定：
```bash
# 跳过 Notion 检查
python main.py --check git --check document
```

### Q: 报告格式如何自定义？

A: 修改 `TraceabilityReport.to_markdown()` 方法，或直接使用 JSON 输出进行自定义处理。

## 维护者

- **陆贾(知识库管理员)** - 文档校验、脚本维护
- **周勃(运维工程师)** - Git 校验、自动化部署
- **曹参(PMO)** - Notion 校验、流程监督

## 参考文档

- [InfinityCompany 留痕校验策略](../traceability_check.md)
- [Phase 4 知识与看板体系落地报告](../../../PHASE4_KNOWLEDGE_BOARD_IMPLEMENTATION_REPORT.md)
- [Phase 5 协作流程与技能接入落地报告](../../../PHASE5_COLLABORATION_WORKFLOW_IMPLEMENTATION_REPORT.md)

---

**版本**: v1.0.0  
**最后更新**: 2026-03-27
