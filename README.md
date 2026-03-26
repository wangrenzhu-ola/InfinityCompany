# InfinityCompany

私人 AI 公司主仓库。

## 目标

InfinityCompany 是虚拟团队默认的日常研发主仓库。

- 团队的代码改动、文档沉淀、流程优化、提示词演进和交付产物默认都在这里迭代
- 通过脚本把本仓库附着到任意 OpenClaw 环境，尽量恢复一致的组织能力
- 只有老板明确授权的新项目，才允许拆分到独立 Git 仓库

## 当前目录骨架

```text
InfinityCompany/
├── .github/
├── governance/
├── agents/
├── configs/
├── notion/
├── overlay/
├── prompts/
├── scripts/
├── skills/
├── snapshots/
└── workflows/
```

## 第一阶段交付

- 固化 Clawpanel 本地部署参数
- 建立仓库骨架与统一入口
- 提供 attach、deploy、rollback、validate 脚本
- 固化主仓库协作规则

## 一键入口

```bash
./Init-InfinityCompany.command
./Open-InfinityCompany.command
```

- `Init-InfinityCompany.command` 用于首次初始化本地干净环境，会自动生成 `configs/openclaw-target.local.env`、校验配置、部署 overlay、检测并拉起 Gateway 与 ClawPanel
- `Open-InfinityCompany.command` 用于日常启动，会检测 Gateway、启动或重建 ClawPanel，并弹出 token 与访问链接
- 两个入口都会读取 `~/.openclaw/openclaw.json` 中的 token，并把 token 复制到剪贴板
- 如果需要指定其他配置文件，可以在命令后追加 env 路径

## 本地配置

- 默认优先读取 `configs/openclaw-target.local.env`
- 若该文件不存在，会从 `configs/openclaw-target.example.env` 自动生成
- `CLAWPANEL_URL` 默认是 `http://127.0.0.1:1420/`

## OpenClaw 附着方式

```bash
./scripts/validate-overlay.sh ./configs/openclaw-target.example.env
./scripts/attach-openclaw.sh ./configs/openclaw-target.example.env
./scripts/deploy-overlay.sh ./configs/openclaw-target.example.env
```

## 说明

- `governance/` 放仓库治理规则、分仓审批模板和授权约束
- `overlay/` 放可附着到 OpenClaw 环境的运行时资产
- `skills/`、`agents/`、`workflows/`、`prompts/` 放团队能力本体
- `notion/` 放知识库结构定义与模板
- `snapshots/` 放部署与回滚快照
- `configs/` 放部署目标配置
- `scripts/init-local-environment.sh` 是一键初始化入口
- `scripts/run-local-workbench.sh` 是日常启动入口

## 仓库治理入口

- 协作规范见 `CONTRIBUTING.md`
- 仓库治理与分仓审批见 `governance/REPOSITORY_POLICY.md`
- 新项目独立仓库申请模板见 `governance/NEW_REPO_REQUEST.md`
