# PMO Manager Skill

数据库支撑的 PMO 看板工具，为刘邦（CEO）和团队提供固定格式状态看板。

## 核心原则

> **所有 Task 必须先审核，再执行。未经 PMO 批准的 Task 不得进入执行状态。**

### 合规铁则
1. **Deadline 强制**：所有 Task 必须有 Deadline，且必须在未来时间
2. **Story 关联强制**：所有 Task 必须关联到已存在的 Story
3. **DONE 报告强制**：Task 标记为 DONE 时必须提供 `report_file`（Markdown 路径）
4. **审核流程强制**：新建 Task 必须走 `submit_task_for_review` → PMO 审核 → APPROVED/REJECTED

---

## Actions

### 1. submit_task_for_review（新建 Task 标准入口）

所有执行者创建 Task **必须**使用此 action，PMO 审核通过后才进入 TODO 状态。

```json
{
  "action": "submit_task_for_review",
  "task_id": "可选，不填则自动生成 UUID",
  "title": "任务标题（≥3字符）",
  "assignee": "执行人 agent_id",
  "story_id": "关联的 Story ID",
  "priority": "P0/P1/P2/P3",
  "deadline": "2026-03-23T17:00:00（ISO 8601，必须在未来）",
  "description": "任务描述（可选）",
  "solution": "解决方案要点（可选）",
  "start_time": "2026-03-23T09:00:00+08:00（可选）"
}
```

**合规校验失败返回示例：**
```json
{
  "status": "error",
  "message": "合规校验失败:",
  "errors": ["必须设定截止时间 (deadline)", "必须关联一个 Story (story_id)"]
}
```

**提交成功返回示例：**
```json
{
  "status": "success",
  "message": "Task xxx 已提交至 PMO 审核队列，请等待审批。",
  "task_id": "xxx",
  "review_required": true
}
```

---

### 2. review_task（PMO 审核 Task）

PMO（曹参）收到提交后进行合规审核，作出最终决定。

```json
{
  "action": "review_task",
  "task_id": "task-uuid",
  "decision": "APPROVED",
  "rejection_reason": "（REJECTED 时必填）"
}
```

- **APPROVED**：Task 进入 TODO 状态，正式激活
- **REJECTED**：Task 进入 REJECTED 状态，附带拒绝原因，执行者修改后可重新提交

---

### 3. get_review_queue（查看待审核队列）

```json
{
  "action": "get_review_queue"
}
```

返回所有 DRAFT/REJECTED 状态的 Task，供 PMO 批量审核。

---

### 4. create_story（创建顶层需求）

```json
{
  "action": "create_story",
  "title": "Market Operations - 市场运营闭环",
  "creator": "刘邦",
  "background": "确保每日交易全流程合规高效运转",
  "objectives": "1. 盘前指令校验\n2. 盘中交易执行\n3. 盘后清算"
}
```

---

### 5. query_tasks（查询 Task）

```json
{
  "action": "query_tasks",
  "assignee": "hanxin",
  "status": ["TODO", "IN_PROGRESS"],
  "date_range": "today",
  "missing_deadline": false
}
```

---

### 6. update_task_status（更新 Task 状态）

> **PMO 合规规则**：DONE 状态必须附带 `report_file`（Markdown 绝对路径），否则 PMO 自动将其置为 BLOCKED。

```json
{
  "action": "update_task_status",
  "task_id": "uuid",
  "status": "DONE",
  "output_summary": "七重风控体系完整编码完成",
  "report_file": "~/.openclaw/workspace-hanxin/reports/风控报告.md"
}
```

---

### 7. sync_from_orchestrator（同步 Orchestrator 状态）

由心跳驱动，每分钟自动调用，将执行层状态同步至 PMO 看板。

---

### 8. get_board（生成看板）

```json
{
  "action": "get_board"
}
```

---

## 完整工作流

```
CEO/造物主  →  create_story（建立顶层需求）
     ↓
执行者  →  submit_task_for_review（提交 Task 草稿）
     ↓
PMO(曹参)  →  review_task → APPROVED/REJECTED
     ↓（APPROVED）
Task 进入 TODO 状态 → 执行者执行
     ↓
执行者  →  update_task_status → DONE（附 report_file）
     ↓
PMO 验证 report_file 存在 → 关闭 Task
```

---

## 状态流转图

```
DRAFT → [PMO审核] → APPROVED → TODO → IN_PROGRESS → DONE
                ↘ REJECTED → [修改后重新提交] → DRAFT
```

---

## 角色映射表

| 角色 | agent_id | 职责 |
|------|----------|------|
| 刘邦 | liubang | Owner/CEO |
| 张良 | zhangliang | PM/项目经理 |
| 萧何 | xiaohe | Architect/架构师 |
| 韩信 | hanxin | Dev/开发 |
| 曹参 | caocan | PMO/项目管理办公室 |
| 周勃 | zhoubo | DevOps/运维 |
| 陈平 | chenping | QA/质量保证 |
| 叔孙通 | shusuntong | Designer/设计师 |
| 陆贾 | lujia | KB/知识库 |
| 夏侯婴 | xiahouying | Personal Assistant/个人助理 |
| 郦食其 | lishiyi | External Assistant/外部助理 |

---

## 常见错误处理

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| 合规校验失败 | deadline 为空或在过去 | 提供未来时间的 deadline |
| Story 不存在 | story_id 错误 | 先通过 CEO 创建 Story |
| DONE 无报告 | 未提供 report_file | 补充 Markdown 汇报文件路径 |
| REJECTED 状态 | PMO 审核未通过 | 查看 blocker_reason，修改后重新 submit |

---

## 公司背景

**汉初三杰虚拟研发公司** - 以刘邦为核心的高效虚拟研发团队，继承汉初三杰（张良、萧何、韩信）的智慧与协作精神，致力于通过严谨的 PMO 流程管理，确保所有项目高质量交付。
