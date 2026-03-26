# InfinityCompany 协作规则

## 默认规则

- InfinityCompany 是虚拟团队默认的日常研发主仓库
- 日常编码改动、文档沉淀、看板结构调整、提示词优化和交付物默认都在本仓库留痕
- `main` 是随时可部署主分支
- 所有角色使用短生命周期分支提交改动后再合并回 `main`
- 禁止直接向 `main` 推送
- 分仓审批、授权和回链规则以 `governance/REPOSITORY_POLICY.md` 为准

## 分支命名

- `feature/<topic>`
- `fix/<topic>`
- `docs/<topic>`
- `ops/<topic>`

## 提交要求

- 每次提交只解决一个明确问题
- 代码变更需要同时补齐对应文档或配置
- 影响流程或知识结构的改动需要更新 `notion/`、`prompts/` 或 `workflows/` 中对应资产
- 提交或合并前需要补齐最小验证记录
- 发起合并时使用 `.github/PULL_REQUEST_TEMPLATE.md` 中的留痕检查项

## 分仓例外

只有满足以下条件之一，才允许单独新开 Git 仓库：

- 独立客户项目
- 安全隔离要求
- 独立交付周期

申请独立仓库时，必须先填写 `governance/NEW_REPO_REQUEST.md` 并获得老板批准。

## 回链要求

- 新项目独立分仓后，通用脚手架、组织规范、可复用提示词、流程模板和部署入口仍需回链到 InfinityCompany
- 独立仓库必须在 README 中写明其源自治理规则来自 InfinityCompany
- 新沉淀出的通用能力必须在合适时机同步回主仓库
