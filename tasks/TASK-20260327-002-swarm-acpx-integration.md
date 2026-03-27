# Task: kimi-agent-swarm 底层通信改造

**Task ID**: TASK-20260327-002  
**任务名称**: kimi-agent-swarm底层acpx/kimi集成  
**负责人**: 韩信 (hanxin)  
**优先级**: P2  
**截止日期**: 2026-04-03  
**前置任务**: TASK-20260327-001 (已完成)  
**状态**: 待启动

---

## 1. 任务背景

当前kimi-agent-swarm使用默认的子Agent调度机制。本任务将其底层通信改造为使用acpx/kimi机制，提升与InfinityCompany环境的集成度。

**前置条件**:
- ✅ company-directory技能已修复 (acpx-infinity可用)
- ✅ Kimi CLI已掌握
- ✅ Agent Swarm使用经验已积累

---

## 2. 任务目标

1. 分析当前kimi-agent-swarm的通信机制
2. 设计acpx/kimi集成方案
3. 实现底层通信改造
4. 验证改造后的Swarm效率

---

## 3. 具体任务清单

### 3.1 调研阶段 (2小时)

| 子任务 | 描述 | 输出物 | 状态 |
|--------|------|--------|------|
| 3.1.1 | 分析当前Swarm通信机制 | 调研报告 | 待完成 |
| 3.1.2 | 评估acpx/kimi集成可行性 | 技术方案 | 待完成 |

### 3.2 开发阶段 (6小时)

| 子任务 | 描述 | 输出物 | 状态 |
|--------|------|--------|------|
| 3.2.1 | 实现acpx-infinity集成 | 代码 | 待完成 |
| 3.2.2 | 改造子Agent调度逻辑 | 代码 | 待完成 |
| 3.2.3 | 添加错误处理和重试机制 | 代码 | 待完成 |

### 3.3 验证阶段 (4小时)

| 子任务 | 描述 | 输出物 | 状态 |
|--------|------|--------|------|
| 3.3.1 | 对比测试新旧Swarm效率 | 测试报告 | 待完成 |
| 3.3.2 | 验证跨Agent通信稳定性 | 测试报告 | 待完成 |
| 3.3.3 | 编写使用文档 | 文档 | 待完成 |

---

## 4. 技术方案

### 4.1 当前机制

```
主Agent → Task工具 → 子Agent
         (默认机制)
```

### 4.2 目标机制

```
主Agent → acpx-infinity → 子Agent (通过kimi)
         (InfinityCompany定制)
```

### 4.3 关键改造点

1. **子Agent启动**: 使用`kimi --agent-file`启动专用子Agent
2. **任务分发**: 使用`acpx-infinity <subagent> "任务"`分发任务
3. **结果收集**: 通过OpenViking记忆或文件系统收集结果
4. **错误处理**: 添加超时重试和失败降级机制

---

## 5. 验收标准

- [ ] Swarm底层成功集成acpx/kimi
- [ ] 子Agent通信成功率 > 95%
- [ ] 效率不低于原机制（或提供合理解释）
- [ ] 文档完整，团队可使用

---

## 6. 参考文档

| 文档 | 路径 |
|------|------|
| Agent Swarm Skill | `/.trae/skills/kimi-agent-swarm/SKILL.md` |
| company-directory | `skills/company-directory/SKILL.md` |
| acpx-infinity | `skills/company-directory/acpx-infinity` |
| 前置任务报告 | `agents/hanxin/reports/TASK-20260327-001-EXECUTION-REPORT.md` |

---

**Task待启动**

*由测试负责人在验收完成后创建，待韩信确认启动。*
