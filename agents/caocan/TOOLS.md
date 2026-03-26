# 曹参 的工具集

## 必备技能 (Skills)

### 核心协作工具
- **`git` / `github`**: 用于在 InfinityCompany 仓库中提交和同步工作成果。
- **`notion`**: 用于读取需求、更新 Task 状态、记录复盘。
  - 迭代看板：跟踪 Sprint 内任务进度
  - Bug 看板：状态流转（新增→修复中→已修复）
  - 外部需求看板：管理外部输入的需求

### 记忆增强工具 (必需)
- **`openviking`**: OpenClaw Memory 增强版，承担日常记忆与检索增强。
  - 角色记忆：每日工作记录、决策上下文
  - 迭代记忆：历史迭代数据、团队速率
  - 检索增强：快速定位历史任务和文档

### PMO专业工具
- **`pmo_manager`**: 看板与任务管理技能
  - `create_story()`: 创建宏观需求 Story
  - `create_tasks()`: 创建具体执行任务（强制包含 deadline）
  - `update_task_status()`: 更新任务状态
  - `query_tasks()`: 按条件查询任务（支持未填 deadline 的不合规检查）
  - `get_board()`: 输出带超时警告的 Markdown 看板

### 辅助工具
- **`reminder` / `notification`**: 时间节点提醒（晨会、评审、复盘）
- **`data_analysis`**: Token 开销统计、周期时间分析、完成率计算

## 工具使用原则
1. **安全第一**：执行任何破坏性命令或修改关键配置前，必须确认风险。
2. **规范操作**：工具的输出必须符合项目的整体规范。
3. **记忆留痕**：所有工作上下文通过 OpenViking 持久化，确保跨会话连续性。
4. **看板同步**：Notion 看板状态与 Git 仓库提交保持同步更新。
