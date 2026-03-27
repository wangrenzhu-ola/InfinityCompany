# Agent Swarm 底层通信机制调研报告

**Task ID**: TASK-20260327-002  
**负责人**: 韩信 (hanxin)  
**日期**: 2026-03-27  
**状态**: Phase 1 完成

---

## 1. 调研目标

分析当前 kimi-agent-swarm 的通信机制，评估使用 acpx-infinity + kimi 集成的可行性。

---

## 2. 当前 Swarm 通信机制分析

### 2.1 架构概览

```
当前机制：
主Agent → Task工具 → 子Agent（默认机制）
```

kimi-agent-swarm Skill 定义的默认调度依赖于 **Kimi CLI 的 Task 工具**：
- `kimi_cli.tools.multiagent:Task` — 主Agent调度工具
- 子Agent需禁用 `Task`/`CreateSubagent` 防止嵌套

### 2.2 三种执行模式

| 模式 | 触发方式 | 通信机制 |
|------|----------|----------|
| **模式1：全自动开箱** | 主Agent接收指令后内部调度 | Task工具（内存级） |
| **模式2：预定义子Agent** | `kimi --agent-file ./swarm-master.yaml` | Task工具 + agent-file配置 |
| **模式3：动态创建** | 主Agent动态创建子Agent | CreateSubagent工具 |

### 2.3 当前机制局限

1. **与 InfinityCompany 环境隔离** — Task 工具是 kimi-cli 内部机制，无法直接与 OpenClaw 管理的 agent 通信
2. **无跨 Agent 能力** — 子Agent 无法访问 InfinityCompany 的 company-directory、Notion 等
3. **结果需手动收集** — 无统一的结果收集机制

---

## 3. acpx-infinity 工具分析

### 3.1 工作原理

```bash
# acpx-infinity 实现（简化）
acpx-infinity <agent_id> "<message>"
    ↓
openclaw agent --agent <agent_id> --message "<message>"
    ↓
通过 OpenClaw Gateway 路由到目标 Agent
```

**路径**：`/usr/local/bin/acpx-infinity`

### 3.2 验证测试

| 测试项 | 结果 |
|--------|------|
| 基本通信 | ✅ 成功 |
| 消息传递 | ✅ 成功 |
| 回复接收 | ✅ 收到回复 "收到" |

### 3.3 优势

1. **直接与 InfinityCompany Agent 通信** — 打通 kimi-cli 与 OpenClaw 生态
2. **支持 company-directory** — 可访问组织架构和 agent 信息
3. **结果易收集** — 直接返回响应内容
4. **已集成 OpenViking** — 记忆和上下文自动管理

---

## 4. 集成可行性评估

### 4.1 改造目标

```
目标机制：
主Agent → acpx-infinity → 子Agent（通过kimi/OpenClaw）
```

### 4.2 关键改造点

| 改造点 | 当前实现 | 目标实现 | 难度 |
|--------|----------|----------|------|
| 子Agent启动 | kimi 内部 Task 工具 | acpx-infinity + kimi | 中 |
| 任务分发 | Task 调用 | acpx-infinity 消息 | 低 |
| 结果收集 | 内存返回 | 响应捕获/文件 | 低 |
| 上下文传递 | 自动上下文继承 | 显式传递完整上下文 | 中 |

### 4.3 可行性结论

**✅ 可行** — 理由：
1. acpx-infinity 已验证可用
2. kimi 支持 `-m` 参数传递消息
3. OpenClaw agent 机制成熟稳定

---

## 5. 推荐集成方案

### 5.1 架构设计

```
主Agent（Kimi会话）
    ↓ acpx-infinity
┌─────────────────────────────────────┐
│  子Agent 1 (openclaw: xiaohe)       │ ← 架构师角色
│  子Agent 2 (openclaw: hanxin)       │ ← 开发者角色
│  子Agent 3 (openclaw: chenping)      │ ← 测试角色
└─────────────────────────────────────┘
    ↓ 结果收集
主Agent 汇总 → 最终输出
```

### 5.2 配置文件 swarm-master.yaml

```yaml
# swarm-master.yaml (InfinityCompany 定制版)
version: "1.0"

master:
  name: "hanxin"
  model: "kimi"

agents:
  - id: "architect"
    name: "萧何"
    agent_id: "xiaohe"          # InfinityCompany agent ID
    role: "架构师"
    capabilities:
      - "架构设计"
      - "技术方案评审"
    
  - id: "developer"
    name: "韩信"
    agent_id: "hanxin"
    role: "开发者"
    capabilities:
      - "代码实现"
      - "技术攻关"
    
  - id: "tester"
    name: "陈平"
    agent_id: "chenping"
    role: "测试工程师"
    capabilities:
      - "测试策略"
      - "质量保障"

dispatcher:
  # 使用 acpx-infinity 替代默认 Task 工具
  command: "acpx-infinity"
  format: "message"
  parallel: true
  timeout: 300
```

### 5.3 调度伪代码

```python
def dispatch_task(agent_config, task_content):
    """使用 acpx-infinity 分发任务"""
    agent_id = agent_config["agent_id"]
    
    # 构建完整上下文消息
    message = f"""
    角色: {agent_config['role']}
    任务: {task_content}
    
    输出规范:
    1. 直接输出结果，不要解释
    2. 使用标准格式
    3. 完成后输出 [DONE]
    """
    
    # 调用 acpx-infinity
    result = subprocess.run(
        ["acpx-infinity", agent_id, message],
        capture_output=True,
        text=True,
        timeout=300
    )
    
    return result.stdout
```

---

## 6. 风险与应对

| 风险 | 等级 | 应对措施 |
|------|------|----------|
| 子Agent 响应慢 | 中 | 设置 timeout，自动重试 |
| 上下文丢失 | 中 | 显式传递完整上下文 |
| Token 消耗高 | 低 | 精简 prompt，控制子Agent数量 |
| 并行度不足 | 低 | 强制并行执行，禁止顺序 |

---

## 7. 下一步行动

| 阶段 | 任务 | 预计工时 |
|------|------|----------|
| Phase 2 | 实现 acpx-infinity 集成代码 | 4h |
| Phase 2 | 创建 swarm-master.yaml 配置 | 1h |
| Phase 2 | 编写调度器脚本 | 1h |
| Phase 3 | 对比测试 | 2h |
| Phase 3 | 文档编写 | 2h |

---

**调研结论**：集成可行，建议进入 Phase 2 开发阶段。

**待确认**：
1. 是否需要支持 kimi 原生 Task 工具作为备选？
2. 子Agent 结果存储在文件系统还是 OpenViking？
