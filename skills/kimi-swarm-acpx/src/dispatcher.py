"""
ACPX Dispatcher - 使用 acpx-infinity 进行跨 Agent 任务分发

核心功能：
1. 通过 acpx-infinity 向子 Agent 分发任务
2. 支持并行分发和顺序分发
3. 内置超时和重试机制
4. 支持降级到 kimi 原生 Task 工具
"""

import subprocess
import time
import json
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class DispatchMode(Enum):
    """分发模式"""
    PARALLEL = "parallel"      # 并行分发
    SEQUENTIAL = "sequential"   # 顺序分发


class FallbackMode(Enum):
    """降级模式"""
    ACPX = "acpx"             # acpx-infinity（默认）
    KIMI_TASK = "kimi_task"   # kimi 原生 Task 工具


@dataclass
class DispatchResult:
    """分发结果"""
    agent_id: str
    success: bool
    output: str = ""
    error: str = ""
    duration_ms: int = 0
    retries: int = 0


@dataclass
class AgentConfig:
    """子 Agent 配置"""
    agent_id: str           # InfinityCompany agent ID (如: xiaohe, hanxin)
    role: str               # 角色名称
    name: str               # 显示名称
    capabilities: List[str] = field(default_factory=list)
    timeout: int = 300      # 超时时间（秒）
    max_retries: int = 3    # 最大重试次数


class ACPXDispatcher:
    """
    ACPX 调度器
    
    使用 acpx-infinity 向 InfinityCompany 的子 Agent 分发任务。
    支持并行/顺序分发、自动重试、结果收集。
    """
    
    def __init__(
        self,
        agents: List[AgentConfig],
        dispatch_mode: DispatchMode = DispatchMode.PARALLEL,
        fallback_mode: FallbackMode = FallbackMode.KIMI_TASK,
        default_timeout: int = 300
    ):
        """
        初始化调度器
        
        Args:
            agents: 子 Agent 配置列表
            dispatch_mode: 分发模式
            fallback_mode: 降级模式
            default_timeout: 默认超时时间
        """
        self.agents = {a.agent_id: a for a in agents}
        self.dispatch_mode = dispatch_mode
        self.fallback_mode = fallback_mode
        self.default_timeout = default_timeout
        
    def dispatch(
        self,
        agent_id: str,
        message: str,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None
    ) -> DispatchResult:
        """
        向指定 Agent 分发任务
        
        Args:
            agent_id: 目标 Agent ID
            message: 任务消息
            timeout: 超时时间（秒）
            max_retries: 最大重试次数
            
        Returns:
            DispatchResult: 分发结果
        """
        if agent_id not in self.agents:
            return DispatchResult(
                agent_id=agent_id,
                success=False,
                error=f"Unknown agent: {agent_id}"
            )
        
        config = self.agents[agent_id]
        timeout = timeout or config.timeout
        max_retries = max_retries or config.max_retries
        
        # 构建完整上下文消息
        full_message = self._build_message(config, message)
        
        # 尝试执行，带重试
        last_error = ""
        for attempt in range(max_retries):
            start_time = time.time()
            
            try:
                output = self._execute_acpx(agent_id, full_message, timeout)
                duration_ms = int((time.time() - start_time) * 1000)
                
                return DispatchResult(
                    agent_id=agent_id,
                    success=True,
                    output=output,
                    duration_ms=duration_ms,
                    retries=attempt
                )
                
            except Exception as e:
                last_error = str(e)
                duration_ms = int((time.time() - start_time) * 1000)
                
                # 如果还有重试次数，等待后重试
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    time.sleep(wait_time)
                    
        # 所有重试都失败
        return DispatchResult(
            agent_id=agent_id,
            success=False,
            error=last_error,
            retries=max_retries
        )
    
    def dispatch_all(
        self,
        tasks: Dict[str, str],
        progress_callback: Optional[Callable[[str, DispatchResult], None]] = None
    ) -> Dict[str, DispatchResult]:
        """
        向所有 Agent 分发任务
        
        Args:
            tasks: {agent_id: message} 任务字典
            progress_callback: 进度回调函数
            
        Returns:
            {agent_id: DispatchResult} 结果字典
        """
        if self.dispatch_mode == DispatchMode.PARALLEL:
            return self._dispatch_parallel(tasks, progress_callback)
        else:
            return self._dispatch_sequential(tasks, progress_callback)
    
    def _dispatch_parallel(
        self,
        tasks: Dict[str, str],
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, DispatchResult]:
        """并行分发"""
        import concurrent.futures
        
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(tasks)) as executor:
            future_to_agent = {
                executor.submit(self.dispatch, agent_id, message): agent_id
                for agent_id, message in tasks.items()
            }
            
            for future in concurrent.futures.as_completed(future_to_agent):
                agent_id = future_to_agent[future]
                try:
                    result = future.result()
                    results[agent_id] = result
                    
                    if progress_callback:
                        progress_callback(agent_id, result)
                        
                except Exception as e:
                    results[agent_id] = DispatchResult(
                        agent_id=agent_id,
                        success=False,
                        error=str(e)
                    )
                    
        return results
    
    def _dispatch_sequential(
        self,
        tasks: Dict[str, str],
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, DispatchResult]:
        """顺序分发"""
        results = {}
        
        for agent_id, message in tasks.items():
            result = self.dispatch(agent_id, message)
            results[agent_id] = result
            
            if progress_callback:
                progress_callback(agent_id, result)
                
        return results
    
    def _build_message(self, config: AgentConfig, message: str) -> str:
        """构建完整的上下文消息"""
        return f"""【角色】{config.name} ({config.role})
【任务】{message}

【输出规范】
1. 直接输出结果，不要解释你在做什么
2. 完成后输出 [DONE]
3. 如果遇到问题，输出 [ERROR] 并描述错误
"""
    
    def _execute_acpx(
        self,
        agent_id: str,
        message: str,
        timeout: int
    ) -> str:
        """执行 acpx-infinity 命令"""
        try:
            result = subprocess.run(
                ["acpx-infinity", agent_id, message],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode != 0:
                # 检查是否是超时
                if "timeout" in result.stderr.lower():
                    raise TimeoutError(f"Agent {agent_id} timeout after {timeout}s")
                raise RuntimeError(f"acpx-infinity failed: {result.stderr}")
            
            return result.stdout.strip()
            
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Agent {agent_id} timeout after {timeout}s")
    
    def _execute_kimi_task(
        self,
        agent_id: str,
        message: str,
        timeout: int
    ) -> str:
        """降级执行：使用 kimi 原生 Task 工具（占位实现）"""
        # TODO: 实现 kimi 原生 Task 调用
        # 这是一个占位符，当 acpx 不可用时降级使用
        raise NotImplementedError("kimi Task fallback not implemented yet")
