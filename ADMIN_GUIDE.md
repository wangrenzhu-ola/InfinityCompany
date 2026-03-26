# InfinityCompany 管理员指南 (Admin Guide)

欢迎来到 InfinityCompany 虚拟研发公司。本文档面向系统管理员（通常是刘邦/Owner 或周勃/运维），提供日常运行、演示和验收的操作指引。

## 1. 系统架构速览
InfinityCompany 采用 **"代码即公司" (Company-as-Code)** 架构：
- **OpenClaw**: 作为底层运行时基座。
- **InfinityCompany 仓库**: 作为公司灵魂，包含所有角色设定、工作流、知识和脚本。
- **Notion**: 作为看板和项目管理中心。
- **OpenViking**: 作为长期记忆和知识检索增强系统。

## 2. 演示路径 (Demo Path)

如果您需要向其他人展示公司的运转机制，请按以下路径演示：

### Step 1: 外部需求输入
向 `lishiyi` (外部助理) 发送一段模糊的需求消息。展示她如何将需求登记到 Notion 的“外部需求看板”中，而不是直接去写代码。

### Step 2: 私人助理意图识别
触发 `xiahouying` (私人助理) 读取外部需求看板。展示她如何分析需求、打标签，并生成一份“待老板审核清单”。

### Step 3: 内部流转
老板批准需求后，展示 `caocan` (PMO) 如何将需求转化为具体的 Story 和 Task。接着展示 `xiaohe` (架构师) 进行技术拆解，`hanxin` (研发) 编写代码，以及 `chenping` (测试) 验证并更新 Bug 看板的全过程。

### Step 4: 知识沉淀
展示每天 19:00 复盘后，`lujia` (知识库管理员) 如何将当天的决策同步到 OpenViking 和 Notion 归档中。

## 3. 日常运维操作

### 3.1 环境更新与部署
当 InfinityCompany 仓库有配置更新时，执行：
```bash
./scripts/deploy-overlay.sh .env
```

### 3.2 运行环境校验
检查环境健康度（建议每天 18:00 执行）：
```bash
./scripts/validate-overlay.sh .env
```

### 3.3 留痕合规检查
检查团队成员是否合规填写了 Token 开销和时间：
```bash
python3 ./scripts/validate_traceability.py --date today
```

## 4. 验收清单 (Checklist)

对于每一次新的基座升级或公司重构，请核对以下清单：
- [ ] 10 个核心角色的配置（IDENTITY/TOOLS/AGENTS）成功加载。
- [ ] 角色对应的模型分配（GPT5.4 / GPT5.3-Codex / MiniMax）正确无误。
- [ ] Notion 5大看板（外部需求、需求、迭代、Bug、复盘）连通性正常。
- [ ] OpenViking 记忆检索服务运行正常。
- [ ] `deploy` 和 `rollback` 脚本测试通过。
