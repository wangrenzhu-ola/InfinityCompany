# Task: Kimi Code CLI 开发规范迁移

**Task ID**: TASK-20260327-001  
**任务名称**: 迁移开发工具链至Kimi Code CLI  
**负责人**: 韩信 (hanxin)  
**优先级**: P1  
**截止日期**: 2026-03-30  
**关联需求**: 环境验收缺陷修复 (DEF-P1-001, DEF-P1-002)  

---

## 1. 任务背景

经OpenClaw环境验收测试发现：`company-directory`技能未正确部署，Agent间通信机制存在缺陷。为保障开发质量和效率，需将开发工具链从OpenClaw CLI迁移至Kimi Code CLI。

**验收报告**: `scripts/kimi_test_report_20260327.md`

---

## 2. 任务目标

1. 掌握Kimi Code CLI的使用方法
2. 学习并应用kimi-agent-swarm技能处理复杂任务
3. 更新个人TOOLS.md，纳入Kimi CLI相关技能
4. 完成试点任务验证新工具链的有效性

---

## 3. 具体任务清单

### 3.1 Skill学习阶段 (4小时)

| 子任务 | 描述 | 输出物 | 状态 |
|--------|------|--------|------|
| 3.1.1 | 阅读kimi-cli-help Skill | 学习笔记 | 待完成 |
| 3.1.2 | 阅读kimi-agent-swarm Skill | 学习笔记 | 待完成 |
| 3.1.3 | 实践Kimi Quick Mode | 实践记录 | 待完成 |
| 3.1.4 | 实践Agent Swarm模式 | 实践记录 | 待完成 |

**学习资源**:
- Kimi CLI Help: `~/.local/share/uv/tools/kimi-cli/lib/python*/site-packages/kimi_cli/skills/kimi-cli-help/SKILL.md`
- Agent Swarm: `/Users/wangrenzhu/work/MetaClaw/.trae/skills/kimi-agent-swarm/SKILL.md`

### 3.2 规范更新阶段 (2小时)

| 子任务 | 描述 | 输出物 | 状态 |
|--------|------|--------|------|
| 3.2.1 | 更新TOOLS.md添加Kimi CLI技能 | PR | 待完成 |
| 3.2.2 | 添加kimi-agent-swarm技能说明 | PR | 待完成 |
| 3.2.3 | 萧何技术评审 | 评审意见 | 待完成 |

**修改内容**:
```markdown
# 韩信 的工具集 (更新版)

## 必备技能 (Skills)

### 开发执行工具 (新增)
- **Kimi Code CLI**: 主要开发执行器，路径 `/Users/wangrenzhu/.local/bin/kimi`
  - Quick Mode: `kimi -m "任务描述"`
  - Interactive Mode: `kimi`
- **Kimi Agent Swarm**: 复杂任务并行处理，路径 `/.trae/skills/kimi-agent-swarm/`
  - 用于多角色并行、无强依赖的复杂开发任务
```

### 3.3 试点验证阶段 (4小时)

| 子任务 | 描述 | 输出物 | 状态 |
|--------|------|--------|------|
| 3.3.1 | 使用Kimi Quick Mode完成简单bug修复 | 代码+报告 | 待完成 |
| 3.3.2 | 使用Agent Swarm完成复杂功能开发 | 代码+报告 | 待完成 |
| 3.3.3 | 总结经验，更新最佳实践文档 | 文档 | 待完成 |

---

## 4. 验收标准

### 4.1 必须完成

- [ ] 能够独立使用 `kimi` 命令进行开发
- [ ] 能够正确使用Agent Swarm处理复杂任务
- [ ] TOOLS.md更新通过萧何技术评审
- [ ] 完成至少1个试点任务

### 4.2 交付物清单

| 交付物 | 路径 | 验收人 |
|--------|------|--------|
| 学习笔记 | `agents/hanxin/notes/kimi-cli-learning.md` | 韩信 |
| 更新后的TOOLS.md | `agents/hanxin/TOOLS.md` | 萧何 |
| 试点任务报告 | `agents/hanxin/reports/kimi-cli-pilot.md` | 曹参 |
| 最佳实践文档 | `agents/hanxin/notes/kimi-cli-best-practices.md` | 韩信 |

---

## 5. 技术规范

### 5.1 Kimi CLI 使用规范

```bash
# 环境检查
kimi --version  # 应显示v1.6.0+

# 简单任务 - Quick Mode
kimi -m "修复bug: company-directory部署问题"

# 复杂任务 - Agent Swarm模式
kimi --skill kimi-agent-swarm
# 然后输入: 使用Agent Swarm并行处理以下任务...
```

### 5.2 Agent Swarm 触发模板

```plaintext
使用Agent Swarm并行处理任务，严格按以下分工执行，所有子Agent同步并行：
1. 【架构师Agent】：分析需求，设计技术方案，输出架构文档
2. 【后端开发Agent】：实现API接口，输出Python代码
3. 【测试Agent】：编写单元测试，输出pytest测试代码
执行完成后，汇总所有结果，按项目结构整理输出。
```

---

## 6. 升级路径

```
阻塞超过2小时未解决 → 立即升级曹参(PMO)
技术方案争议 → 升级萧何(技术负责人)
工具链重大变更 → 需曹参+萧何联合审批
```

---

## 7. 参考文档

| 文档 | 路径 |
|------|------|
| 开发规范标准 | `specs/kimi-cli-development-standard.md` |
| Kimi CLI Help Skill | `~/.local/share/uv/tools/kimi-cli/lib/python*/site-packages/kimi_cli/skills/kimi-cli-help/SKILL.md` |
| Agent Swarm Skill | `/Users/wangrenzhu/work/MetaClaw/.trae/skills/kimi-agent-swarm/SKILL.md` |
| 环境验收报告 | `scripts/kimi_test_report_20260327.md` |

---

## 8. 任务状态跟踪

| 日期 | 状态 | 备注 |
|------|------|------|
| 2026-03-27 | 已创建 | 任务分配给韩信 |
| 2026-03-27 | SPEC已审批 | 测试负责人代审批，任务正式启动 |
| | | |

---

**Task结束**

*本Task由测试负责人于2026-03-27创建，需韩信确认接收后开始执行。*
