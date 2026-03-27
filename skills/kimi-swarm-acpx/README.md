# Kimi Swarm ACPX - InfinityCompany 定制版

使用 `acpx-infinity` 实现与 InfinityCompany OpenClaw Agent 集成的 Agent Swarm 调度器。

## 功能特性

- 🔗 **acpx-infinity 集成** — 通过 `acpx-infinity` 向子 Agent 分发任务
- 🧠 **OpenViking 存储** — 使用 OpenViking 记忆系统存储子 Agent 结果
- 🔄 **并行/顺序执行** — 支持并行和顺序两种分发模式
- ⏱️ **超时重试** — 内置超时和自动重试机制
- 📉 **降级方案** — 支持降级到 kimi 原生 Task 工具

## 安装

```bash
# 确保 acpx-infinity 可用
which acpx-infinity

# 如果不可用，从 skills/company-directory 复制
cp skills/company-directory/acpx-infinity /usr/local/bin/
chmod +x /usr/local/bin/acpx-infinity
```

## 快速开始

### 基本用法

```python
from swarm_master import create_swarm, SubTask

# 定义子 Agent
agents = [
    {"agent_id": "xiaohe", "role": "架构师", "name": "萧何"},
    {"agent_id": "chenping", "role": "测试工程师", "name": "陈平"},
]

# 创建 Swarm
swarm = create_swarm(agents=agents, parallel=True)

# 定义子任务
tasks = [
    SubTask(
        task_id="task-1",
        agent_id="xiaohe",
        role="架构师",
        description="设计一个用户认证模块的架构"
    ),
    SubTask(
        task_id="task-2",
        agent_id="chenping",
        role="测试工程师",
        description="为用户认证模块编写测试用例"
    ),
]

# 执行
result = swarm.execute(
    master_task="实现用户认证功能",
    tasks=tasks
)

# 输出结果
print(result.aggregated_output)
```

### 并行执行

```python
result = swarm.execute_parallel(
    master_task="重构数据库模块",
    tasks=tasks
)
```

### 顺序执行

```python
result = swarm.execute_sequential(
    master_task="迭代开发任务",
    tasks=tasks
)
```

## 架构

```
kimi-swarm-acpx/
├── src/
│   ├── __init__.py
│   ├── dispatcher.py      # ACPX 任务分发器
│   ├── result_store.py   # OpenViking 结果存储
│   └── swarm_master.py   # 主调度器
└── tests/
    ├── test_dispatcher.py
    ├── test_result_store.py
    └── test_swarm_master.py
```

## 核心组件

### ACPXDispatcher

负责通过 `acpx-infinity` 向子 Agent 分发任务。

```python
from dispatcher import ACPXDispatcher, AgentConfig, DispatchMode

dispatcher = ACPXDispatcher(
    agents=[
        AgentConfig(agent_id="xiaohe", role="架构师", name="萧何"),
    ],
    dispatch_mode=DispatchMode.PARALLEL,
    default_timeout=300
)

result = dispatcher.dispatch("xiaohe", "设计登录模块")
```

### OpenVikingStore

使用 OpenViking sessionKey 机制存储子 Agent 结果。

```python
from result_store import OpenVikingStore, ResultStatus

store = OpenVikingStore()

# 创建会话
session = store.create_session("主任务描述")

# 保存结果
store.save_result(
    session_id=session.session_id,
    agent_id="xiaohe",
    role="架构师",
    status=ResultStatus.SUCCESS,
    content="架构设计完成"
)

# 聚合结果
aggregated = store.aggregate_results(session.session_id)
```

### SwarmMaster

协调 dispatcher 和 store，提供统一接口。

```python
from swarm_master import SwarmMaster, SwarmConfig, SubTask

config = SwarmConfig(
    master_agent_id="hanxin",
    parallel=True,
    timeout=300,
    max_retries=3
)

master = SwarmMaster(agents=agent_configs, config=config)
result = master.execute(master_task="任务", tasks=subtasks)
```

## 错误处理

```python
result = swarm.execute(master_task="任务", tasks=tasks)

if not result.success:
    print("执行失败:")
    for error in result.errors:
        print(f"  - {error}")
else:
    print(f"成功率: {len(result.results) - len(result.errors)}/{len(result.results)}")
```

## 降级机制

当 `acpx-infinity` 不可用时，可降级到 kimi 原生 Task 工具：

```python
config = SwarmConfig(
    fallback_to_kimi=True,  # 启用降级
    timeout=300
)
```

## 测试

```bash
cd skills/kimi-swarm-acpx
python -m pytest tests/ -v
```

## License

InfinityCompany Internal
