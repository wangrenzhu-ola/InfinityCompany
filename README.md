# InfinityCompany

InfinityCompany 是虚拟团队默认的日常研发主仓库，用于统一沉淀多角色协作流程、OpenClaw 运行时附着能力和可复用技能体系。

## 项目现状

当前仓库已完成从基础骨架到协同交付闭环的阶段演进：

- Phase 1：仓库骨架、基础脚本和治理规则落地
- Phase 4：知识板与 Notion 结构化配置完成
- Phase 5：跨角色协作与交付流程固化完成
- Phase 6：测试、验收与回归链路打通
- 验收状态：已形成最终验收通过报告（详见根目录验收文档）

## 快速开始

```bash
./Init-InfinityCompany.command
./Open-InfinityCompany.command
```

- `Init-InfinityCompany.command`：首次初始化，自动准备 `configs/openclaw-target.local.env`、执行配置校验、部署 overlay、检查并拉起服务
- `Open-InfinityCompany.command`：日常启动，执行健康检查并启动工作台
- 默认配置文件：`configs/openclaw-target.local.env`
- 若本地配置不存在，会从 `configs/openclaw-target.example.env` 自动生成

## 核心能力

- OpenClaw 附着与发布：`validate -> attach -> deploy -> rollback` 全链路脚本化
- 团队运行框架：多角色 agent 身份与协作模板已标准化
- 业务技能体系：`company-directory`、`pmo-manager`、`kimi-swarm-acpx` 等能力可独立运行
- 测试与回归：`scripts/run_tests.sh` 提供阶段 6 核心验证用例集
- 知识沉淀：`notion/` 与 `workflows/` 内置流程与模板

## 常用命令

```bash
./scripts/validate-overlay.sh ./configs/openclaw-target.local.env
./scripts/attach-openclaw.sh ./configs/openclaw-target.local.env
./scripts/deploy-overlay.sh ./configs/openclaw-target.local.env
./scripts/rollback-overlay.sh ./configs/openclaw-target.local.env
./scripts/run_tests.sh
./scripts/sync-openclaw-skills.sh --skill company-directory
./scripts/sync-openclaw-skills.sh --check --skill company-directory
```

## 目录说明（当前）

```text
InfinityCompany/
├── .github/
├── agents/
├── configs/
├── governance/
├── notion/
├── overlay/
├── prompts/
├── scripts/
├── skills/
├── snapshots/
├── specs/
├── tasks/
└── workflows/
```

- `.github/`：PR 模板与协作入口
- `agents/`：角色定义与个体工作区
- `configs/`：目标环境配置
- `governance/`：治理规则与流程基线
- `notion/`：知识结构与配置模板
- `overlay/`：可附着到运行时的资产
- `prompts/`：提示词与协作提示
- `scripts/`：初始化、部署、验证、回滚脚本
- `skills/`：团队技能实现与说明
- `snapshots/`：快照与回滚数据
- `specs/`：规范与方案文档
- `tasks/`：任务单与执行记录
- `workflows/`：业务流程与协作流

## 治理与协作入口

- 协作规范：`CONTRIBUTING.md`
- 仓库治理策略：`governance/REPOSITORY_POLICY.md`
- 新仓审批模板：`governance/NEW_REPO_REQUEST.md`
- 日常节奏基线：`governance/DAILY_ROUTINE.md`

## 关键参考文档

- `ADMIN_GUIDE.md`：运维与管理员操作说明
- `ACCEPTANCE_REPORT_FINAL_20260327.md`：最终验收结论
- `PHASE4_KNOWLEDGE_BOARD_IMPLEMENTATION_REPORT.md`：Phase 4 实施报告
- `PHASE5_COLLABORATION_WORKFLOW_IMPLEMENTATION_REPORT.md`：Phase 5 实施报告
- `scripts/phase6_report.md`：Phase 6 实施与测试报告
