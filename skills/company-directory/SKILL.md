# 汉初三杰虚拟公司 - 人员目录与通讯协议

本规范定义了**汉初三杰虚拟公司**内部全体人员的 `agent_id`、岗位职责，以及**唯一的、标准化的跨 Agent 通讯机制**。所有 Agent 必须严格遵守此规范，不得使用其他未授权的通讯方式。

---

## 🚨 跨Agent通讯核心双规机制

当前系统支持两种通讯方式：**`acpx` (实时双向沟通)** 和 **`emergency_inbox` (异步邮件投递)**。**原 `sessions_send` 机制已被完全废弃，禁止使用。**

### 1. 实时沟通：`acpx-infinity` CLI (敲门唤醒与同步对话)
当需要**即时反馈**、**紧急确认**或**多轮对话**时，必须使用 `acpx-infinity` CLI 工具。

`acpx-infinity` 当前支持增强能力：
- 发送后返回目标在线状态（`online/offline/busy/unknown`）
- 发送后返回送达状态（`delivered/read/failed`）
- 自动回执提示（消息自动附带 ACK 指令）
- 群发广播（`all` / `role:<role>` / `ids:id1,id2`）
- 消息持久化与历史追溯（jsonl 日志）
- 统一消息信封格式（包含 `id/from/to/runtime_to/requires_reply/attempt`）

**调用示例：**
```bash
# 唤醒并发送消息给曹参 (PMO)
acpx-infinity caocan "曹参，请提供最新的进度报告"

# 发送消息给张良 (PM)
acpx-infinity zhangliang "需求已更新，请查看"

# 发送消息给韩信 (Dev)
acpx-infinity hanxin "新任务已分配"

# 广播通知全员
acpx-infinity broadcast --targets all --message "19:00 复盘会准时开始"

# 广播失败目标重试（仅重试 failed）
acpx-infinity broadcast --targets all --message "通知全员" --retry-failed --retry-rounds 2

# 单发重试并在失败后降级到邮箱
acpx-infinity hanxin "紧急任务请处理" --retries 2 --fallback-email

# 查询目标在线状态
acpx-infinity status chenping

# 查询历史
acpx-infinity history --limit 20
```

**注意：** `acpx-infinity` 是 InfinityCompany 定制工具，支持虚拟公司 Agent ID。原生 `acpx` 仅支持系统预定义 agent，不支持我们的虚拟公司角色。当前已内置运行时映射：`caocan -> main`（用于兼容 OpenClaw 默认主代理命名）。所有实时消息必须通过 `acpx-infinity` 发送，禁止直接调用裸 `acpx`。
当前限制：`liubang` 为人类负责人，只在通讯录中保留用于组织关系，不支持 `acpx-infinity` 实时发送与探测。

### 2. 异步沟通：`emergency_inbox` (邮件箱投递)
当派发**非紧急的长期任务**、**大篇幅报告**，或者 `acpx` 暂时无法联系到目标时，使用异步邮箱投递。

**调用示例（使用内置 Python 脚本）：**
```bash
python3 ~/.openclaw/workspace/skills/company-directory/send_email.py \
  --agent-id zhoubo \
  --subject "系统巡检报告" \
  --message "这是本周的系统巡检报告详情..."
```

**⚠️ 唤醒必读规则 (第一优先级)：**
所有 Agent 在**每次被唤醒**（无论是被用户唤醒、被 cron 唤醒还是被 acpx 唤醒）时，**首要任务是检查自己的 `emergency_inbox`**：
- 路径：`~/.openclaw/workspace/emergency_inbox/{你的agent_id}/`
- 如果里面有文件，必须优先阅读并处理其中的任务/邮件，处理完成后删除或归档该文件。

---

## 🤝 沟通礼仪：双向确认机制 (Double-Confirmation)

为了确保信息传递的可靠性，所有通过 `acpx` 或邮件处理的任务，接收方必须进行明确的回复/确认：

1. **包含原始上下文**：回复时必须简述你收到并理解了什么指令。
2. **明确接收状态**：使用"收到，已执行/会继续处理"等明确字眼。

**示例：**
- **发件人 (刘邦)**: `acpx-infinity zhangliang "审核这个需求方案"`
- **收件人 (张良)**: 收到关于审核需求方案的指令。方案审核通过，风险在可控范围内。

---

## 👥 部门与人员清单 (Company Directory)

| 姓名 | 岗位 / 角色 | Agent ID | 核心职责 |
|------|------------|----------|----------|
| **刘邦** | Owner (主公，人类) | `liubang` | 战略制定，最终决策，全系统任务编排（不参与acpx实时通讯） |
| **张良** | PM (产品经理) | `zhangliang` | 需求分析，产品设计，对外交付对接 |
| **萧何** | Architect (架构师) | `xiaohe` | 系统架构设计，技术选型，代码审查 |
| **韩信** | Dev (全栈研发) | `hanxin` | 核心编码实现，技术攻坚，代码交付 |
| **曹参** | PMO负责人 | `caocan` | 建立顶层宏观需求(Story)，督促执行层认领并录入Task，合规审查，PMO看板维护 |
| **周勃** | DevOps (运维) | `zhoubo` | 系统部署，CI/CD，监控告警 |
| **陈平** | QA (测试) | `chenping` | 测试策略，质量保障，Bug跟踪 |
| **叔孙通** | Designer (设计师) | `shusuntong` | UI/UX设计，视觉规范，用户体验 |
| **陆贾** | KB (知识库) | `lujia` | 知识管理，文档归档，记忆检索 |
| **夏侯婴** | Personal Assistant (私人助理) | `xiahouying` | 个人事务管理，日程安排，效率工具 |
| **郦食其** | External Assistant (外部助理) | `lishiyi` | 外部对接，客户沟通，跨组织协作 |

---

## 📋 角色协作流程

### 标准需求流转流程

```
刘邦(战略) → 张良(产品方案) → 萧何(技术架构) → 韩信(开发实现)
                 ↓                    ↓                  ↓
               曹参(PMO监督)      周勃(环境准备)      陈平(测试验收)
                 ↓                    ↓                  ↓
               叔孙通(UI设计)     陆贾(文档沉淀)      夏侯婴/郦食其(交付)
```

### 紧急事件升级路径

1. **技术故障**: 韩信 → 萧何 → 周勃 → 刘邦
2. **需求变更**: 张良 → 曹参 → 刘邦
3. **质量问题**: 陈平 → 韩信 → 萧何 → 刘邦
4. **外部投诉**: 郦食其 → 张良 → 刘邦

---

*此规范为汉初三杰虚拟公司统一的底层通讯协议。任何旧有的 Slack 规则、sessions_send 脚本均已失效。*
