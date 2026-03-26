# 留痕校验脚本大纲 (Traceability Check)

本文档定义了用于验证代码提交、文档更新、看板更新与复盘同步的协作留痕的校验策略。

## 校验目标
确保“无留痕不闭环”的规范得到严格执行：
1. **Git 留痕**: 所有产出物必须有对应的 commit 记录。
2. **Notion 留痕**: 所有 Task 状态变更必须在 Notion 中体现，且包含 token 开销和工时。
3. **一致性留痕**: Git 的 commit 必须与 Notion 的 Task ID 对应。

## 脚本大纲设计 (`validate_traceability.py`)

### 1. Git 提交校验模块
- **输入**: 时间范围 (如 `--since="yesterday 18:00"`)
- **逻辑**:
  - 获取指定时间内的所有 Git commits。
  - 正则匹配 commit message 是否包含合规的 Task ID (如 `[TASK-123]`)。
  - 统计各个角色的提交频次。

### 2. Notion 状态一致性模块
- **输入**: Notion API Key 和 Database IDs
- **逻辑**:
  - 查询当天标记为“已完成”的 Tasks。
  - 检查这些 Tasks 的必填字段：`actual_end`, `token_cost`, `reviewer` 是否为空。
  - 查询当天的 Bug 记录，验证处于“已修复”状态的 Bug 是否有关联的 PR 链接。

### 3. 复盘记录同步校验模块
- **输入**: 当天日期
- **逻辑**:
  - 检查 Notion 的“每日复盘记录”数据库是否存在当天的记录。
  - 验证记录内容是否涵盖了：当日产出、阻塞、风险、改进项。
  - 验证记录中的汇总数据（如 Token 总消耗）与 Task 明细之和是否匹配（容差 5%）。

## 运行方式与报警
该脚本应集成在每日 19:00 复盘会前自动运行。
输出格式为 Markdown 报告：
- ✅ `[Pass]` Git 提交均包含 Task ID
- ❌ `[Fail]` 发现 2 个已完成 Task 缺失 `token_cost` 记录 (链接1, 链接2)

发现 Fail 项时，通过 PMO(曹参) 通知对应责任人补齐。
