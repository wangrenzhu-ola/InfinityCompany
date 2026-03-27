# InfinityCompany Skills

汉初三杰虚拟公司的技能目录。

## 已集成技能

| 技能 | 路径 | 说明 |
|------|------|------|
| company-directory | `skills/company-directory/` | 公司人员目录与通讯协议 |
| pmo-manager | `skills/pmo-manager/` | PMO 看板与任务管理 |
| openviking | `skills/openviking/` | OpenViking 工具链 |

## 技能说明

### company-directory（公司目录）

定义了汉初三杰虚拟公司的：
- 全体人员 `agent_id` 与岗位职责
- 标准化跨 Agent 通讯机制（`acpx` + `emergency_inbox`）
- 双向确认沟通礼仪
- 角色协作流程与紧急事件升级路径

**核心角色映射：**
- `liubang` - 刘邦 (Owner)
- `zhangliang` - 张良 (PM)
- `xiaohe` - 萧何 (Architect)
- `hanxin` - 韩信 (Dev)
- `caocan` - 曹参 (PMO)
- `zhoubo` - 周勃 (DevOps)
- `chenping` - 陈平 (QA)
- `shusuntong` - 叔孙通 (Designer)
- `lujia` - 陆贾 (KB)
- `xiahouying` - 夏侯婴 (Personal Assistant)
- `lishiyi` - 郦食其 (External Assistant)

### pmo-manager（PMO管理）

数据库支撑的 PMO 看板工具，提供：
- Task 提交与审核流程
- Story 创建与管理
- 任务状态看板
- 合规检查（Deadline、Story关联、DONE报告）

### openviking（OpenViking）

OpenViking 工具链集成。

---

*技能目录由韩信(Dev)和萧何(Architect)共同维护*
