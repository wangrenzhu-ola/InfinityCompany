"""
Swarm Master - Agent Swarm 主调度器

核心功能：
1. 协调 ACPXDispatcher 和 OpenVikingStore
2. 管理 Swarm 生命周期
3. 提供统一的任务分发接口
4. 支持降级到 kimi 原生 Task 工具
"""

import time
import uuid
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, field

from .dispatcher import ACPXDispatcher, AgentConfig, DispatchResult, DispatchMode
from .result_store import OpenVikingStore, ResultStatus


@dataclass
class SwarmConfig:
    """Swarm 配置"""
    master_agent_id: str = "hanxin"           # 主 Agent ID
    master_name: str = "韩信"                  # 主 Agent 名称
    parallel: bool = True                     # 是否并行执行
    timeout: int = 300                       # 默认超时
    max_retries: int = 3                     # 最大重试次数
    fallback_to_kimi: bool = True            # 是否允许降级到 kimi Task


@dataclass
class SubTask:
    """子任务"""
    task_id: str
    agent_id: str
    role: str
    description: str
    context: str = ""                         # 额外上下文


@dataclass
class SwarmResult:
    """Swarm 执行结果"""
    swarm_id: str
    success: bool
    results: Dict[str, DispatchResult]
    aggregated_output: str = ""
    total_duration_ms: int = 0
    errors: List[str] = field(default_factory=list)


class SwarmMaster:
    """
    Swarm 主调度器
    
    协调 ACPXDispatcher 和 OpenVikingStore，实现完整的 Agent Swarm 功能。
    支持并行/顺序执行、自动重试、结果聚合。
    """
    
    def __init__(
        self,
        agents: List[AgentConfig],
        config: Optional[SwarmConfig] = None
    ):
        """
        初始化 SwarmMaster
        
        Args:
            agents: 子 Agent 配置列表
            config: Swarm 配置
        """
        self.agents = {a.agent_id: a for a in agents}
        self.config = config or SwarmConfig()
        
        # 初始化调度器
        dispatch_mode = DispatchMode.PARALLEL if self.config.parallel else DispatchMode.SEQUENTIAL
        self.dispatcher = ACPXDispatcher(
            agents=agents,
            dispatch_mode=dispatch_mode,
            default_timeout=self.config.timeout
        )
        
        # 初始化存储
        self.store = OpenVikingStore()
        
        # 当前会话
        self.current_session = None
    
    def execute(
        self,
        master_task: str,
        tasks: List[SubTask],
        progress_callback: Optional[Callable[[str, Any], None]] = None
    ) -> SwarmResult:
        """
        执行 Swarm 任务
        
        Args:
            master_task: 主任务描述
            tasks: 子任务列表
            progress_callback: 进度回调
            
        Returns:
            SwarmResult: 执行结果
        """
        start_time = time.time()
        
        # 生成 swarm_id
        swarm_id = f"swarm-{uuid.uuid4().hex[:12]}"
        
        # 创建会话
        session = self.store.create_session(master_task)
        self.current_session = session
        
        # 构建任务字典
        task_dict = {}
        for task in tasks:
            if task.agent_id not in self.agents:
                continue
            
            agent_config = self.agents[task.agent_id]
            context = f"{task.description}"
            if task.context:
                context += f"\n\n【额外上下文】\n{task.context}"
            
            task_dict[task.agent_id] = context
        
        # 分发任务
        results = self.dispatcher.dispatch_all(task_dict, progress_callback)
        
        # 保存结果到 OpenViking
        for agent_id, result in results.items():
            agent_config = self.agents.get(agent_id)
            role = agent_config.role if agent_config else "unknown"
            
            status = ResultStatus.SUCCESS if result.success else ResultStatus.FAILED
            
            self.store.save_result(
                session_id=session.session_id,
                agent_id=agent_id,
                role=role,
                status=status,
                content=result.output,
                error=result.error,
                duration_ms=result.duration_ms
            )
        
        # 聚合结果
        aggregated = self.store.aggregate_results(session.session_id)
        
        # 标记完成
        has_errors = any(not r.success for r in results.values())
        self.store.complete_session(
            session.session_id, 
            status="completed" if not has_errors else "failed"
        )
        
        total_duration = int((time.time() - start_time) * 1000)
        errors = [r.error for r in results.values() if not r.success]
        
        return SwarmResult(
            swarm_id=swarm_id,
            success=not has_errors,
            results=results,
            aggregated_output=aggregated,
            total_duration_ms=total_duration,
            errors=errors
        )
    
    def execute_parallel(
        self,
        master_task: str,
        tasks: List[SubTask],
        progress_callback: Optional[Callable[[str, DispatchResult], Any]] = None
    ) -> SwarmResult:
        """并行执行（快捷方法）"""
        original_mode = self.config.parallel
        self.config.parallel = True
        
        dispatch_mode = self.dispatcher.dispatch_mode
        self.dispatcher.dispatch_mode = DispatchMode.PARALLEL
        
        result = self.execute(master_task, tasks, progress_callback)
        
        self.config.parallel = original_mode
        self.dispatcher.dispatch_mode = dispatch_mode
        
        return result
    
    def execute_sequential(
        self,
        master_task: str,
        tasks: List[SubTask],
        progress_callback: Optional[Callable[[str, DispatchResult], Any]] = None
    ) -> SwarmResult:
        """顺序执行（快捷方法）"""
        original_mode = self.config.parallel
        self.config.parallel = False
        
        dispatch_mode = self.dispatcher.dispatch_mode
        self.dispatcher.dispatch_mode = DispatchMode.SEQUENTIAL
        
        result = self.execute(master_task, tasks, progress_callback)
        
        self.config.parallel = original_mode
        self.dispatcher.dispatch_mode = dispatch_mode
        
        return result
    
    def get_session(self, session_id: str):
        """获取会话"""
        return self.store.get_session(session_id)
    
    def get_results(self, session_id: str) -> Dict[str, Any]:
        """获取所有子 Agent 结果"""
        return self.store.get_all_results(session_id)
    
    def aggregate(self, session_id: str) -> str:
        """聚合结果"""
        return self.store.aggregate_results(session_id)


# ========== 便捷函数 ==========

def create_swarm(
    agents: List[Dict[str, str]],
    parallel: bool = True,
    master_agent_id: str = "hanxin"
) -> SwarmMaster:
    """
    创建 Swarm 实例的便捷函数
    
    Args:
        agents: 子 Agent 配置列表 [{"agent_id": "xiaohe", "role": "架构师", "name": "萧何"}, ...]
        parallel: 是否并行执行
        master_agent_id: 主 Agent ID
        
    Returns:
        SwarmMaster 实例
    """
    agent_configs = [
        AgentConfig(
            agent_id=a["agent_id"],
            role=a["role"],
            name=a["name"]
        )
        for a in agents
    ]
    
    config = SwarmConfig(
        master_agent_id=master_agent_id,
        parallel=parallel
    )
    
    return SwarmMaster(agents=agent_configs, config=config)
