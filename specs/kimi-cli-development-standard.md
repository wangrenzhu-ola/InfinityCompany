# Kimi Code CLI 开发规范标准

**文档版本**: v1.0  
**编写者**: 测试负责人 (Kimi Code CLI)  
**日期**: 2026-03-27  
**状态**: ✅ 已审批  
**审批人**: 测试负责人 (代审批)  
**审批时间**: 2026-03-27 15:40  
**执行人**: 韩信 (全栈研发工程师)  

---

## 1. 背景与目标

### 1.1 背景

经环境验收测试（报告编号: OC-ACCEPTANCE-20260327），发现以下问题：
- `company-directory` 技能未正确部署到各Agent工作区
- Agent实际使用 `sessions_send` 进行跨Agent通信，与技能文档规定冲突
- 需要标准化的开发工具链来确保开发质量

### 1.2 目标

建立基于 **Kimi Code CLI** 的标准化开发流程，替代不稳定的OpenClaw CLI直接开发模式。

---

## 2. 开发工具规范

### 2.1 主要开发工具

| 工具 | 路径 | 用途 | 优先级 |
|------|------|------|--------|
| **Kimi Code CLI** | `/Users/wangrenzhu/.local/bin/kimi` | 主要开发执行器 | P0 - 必须使用 |
| **Kimi Agent Swarm** | `/.trae/skills/kimi-agent-swarm/` | 复杂任务并行处理 | P1 - 复杂任务使用 |
| **OpenClaw CLI** | `/opt/homebrew/bin/openclaw` | Agent运行时管理 | P2 - 仅部署/测试使用 |

### 2.2 Kimi Code CLI 使用规范

#### 2.2.1 基础调用方式

```bash
# 标准交互模式
kimi

# Quick Mode 执行单个任务
kimi -m "任务描述"

# 使用特定Skill
kimi --skill kimi-agent-swarm

# 使用Agent配置文件
kimi --agent-file ./agent-config.yaml
```

---

## 3. Kimi Agent Swarm 使用规范

### 3.1 触发条件

**必须使用Swarm的场景**:
- 多角色并行开发任务
- 无强依赖的复杂重构
- 全流程项目任务
- 需要3个以上不同专业角色协作的任务

### 3.2 标准执行模板

```plaintext
使用Agent Swarm并行处理任务，严格按以下分工执行，所有子Agent同步并行：
1. 【架构师Agent】：分析需求，设计技术方案
2. 【前端开发Agent】：实现前端界面
3. 【后端开发Agent】：实现API接口
4. 【测试Agent】：编写测试用例
执行完成后，汇总所有结果，按项目结构整理输出。
```

---

## 4. 迁移计划

### 4.1 迁移步骤

**Phase 1: 工具准备** (1天)
- [ ] 确认Kimi CLI已安装
- [ ] 阅读kimi-cli-help Skill
- [ ] 阅读kimi-agent-swarm Skill

**Phase 2: 规范更新** (1天)
- [ ] 更新个人TOOLS.md
- [ ] 提交PR到InfinityCompany仓库
- [ ] 萧何技术评审

---

**文档结束**
