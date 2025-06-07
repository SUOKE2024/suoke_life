#!/usr/bin/env python3
"""
生命周期管理模块 - 提供智能体生命周期管理功能
"""

import asyncio
import contextlib
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class LifecycleState(Enum):
    """生命周期状态"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class AgentInfo:
    """智能体信息"""
    agent_id: str
    status: str
    last_heartbeat: float
    metrics: dict[str, Any] | None = None


class LifecycleManager:
    """生命周期管理器"""

    def __init__(self, heartbeat_interval: float = 30.0, health_check_timeout: float = 60.0):
        self.heartbeat_interval = heartbeat_interval
        self.health_check_timeout = health_check_timeout
        self.agents: dict[str, AgentInfo] = {}
        self.state = LifecycleState.STOPPED

        # 后台任务
        self._heartbeat_task: asyncio.Task | None = None
        self._health_check_task: asyncio.Task | None = None
        self._cleanup_task: asyncio.Task | None = None

    async def start(self):
        """启动生命周期管理器"""
        if self.state == LifecycleState.RUNNING:
            logger.warning("生命周期管理器已在运行")
            return

        try:
            self.state = LifecycleState.STARTING

            # 启动后台任务
            self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            self._health_check_task = asyncio.create_task(self._health_check_loop())
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

            self.state = LifecycleState.RUNNING
            logger.info("生命周期管理器已启动")

        except Exception as e:
            self.state = LifecycleState.ERROR
            logger.error(f"启动生命周期管理器失败: {e}")
            raise

    async def register_agent(self, agent_id: str, initial_status: str = "starting"):
        """注册智能体"""
        agent_info = AgentInfo(
            agent_id=agent_id,
            status=initial_status,
            last_heartbeat=time.time()
        )
        self.agents[agent_id] = agent_info
        logger.info(f"注册智能体: {agent_id}")

    async def unregister_agent(self, agent_id: str):
        """注销智能体"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"注销智能体: {agent_id}")

    def update_agent_heartbeat(self, agent_id: str, metrics: dict[str, Any] | None = None):
        """更新智能体心跳"""
        if agent_id in self.agents:
            agent_info = self.agents[agent_id]
            agent_info.last_heartbeat = time.time()
            if metrics:
                agent_info.metrics = metrics
            logger.debug(f"更新智能体心跳: {agent_id}")

    def update_agent_status(self, agent_id: str, status: str):
        """更新智能体状态"""
        if agent_id in self.agents:
            self.agents[agent_id].status = status
            logger.debug(f"更新智能体状态: {agent_id} -> {status}")

    def get_agent_status(self, agent_id: str) -> str | None:
        """获取智能体状态"""
        if agent_id in self.agents:
            return self.agents[agent_id].status
        return None

    def get_all_agents(self) -> dict[str, AgentInfo]:
        """获取所有智能体信息"""
        return self.agents.copy()

    async def _heartbeat_loop(self):
        """心跳循环"""
        while self.state == LifecycleState.RUNNING:
            try:
                # 检查所有智能体的心跳
                current_time = time.time()
                for agent_id, agent_info in self.agents.items():
                    time_since_heartbeat = current_time - agent_info.last_heartbeat

                    if time_since_heartbeat > self.heartbeat_interval * 2:
                        logger.warning(f"智能体心跳超时: {agent_id}")
                        agent_info.status = "timeout"

                await asyncio.sleep(self.heartbeat_interval)

            except Exception as e:
                logger.error(f"心跳循环异常: {e}")
                await asyncio.sleep(5)

    async def _health_check_loop(self):
        """健康检查循环"""
        while self.state == LifecycleState.RUNNING:
            try:
                # 执行健康检查
                for agent_id, agent_info in self.agents.items():
                    if agent_info.status == "timeout":
                        logger.info(f"智能体健康检查失败: {agent_id}")

                await asyncio.sleep(60)  # 每分钟检查一次

            except Exception as e:
                logger.error(f"健康检查循环异常: {e}")
                await asyncio.sleep(10)

    async def _cleanup_loop(self):
        """清理循环"""
        while self.state == LifecycleState.RUNNING:
            try:
                # 清理超时的智能体
                current_time = time.time()
                agents_to_remove = []

                for agent_id, agent_info in self.agents.items():
                    time_since_heartbeat = current_time - agent_info.last_heartbeat
                    if time_since_heartbeat > self.health_check_timeout:
                        agents_to_remove.append(agent_id)

                for agent_id in agents_to_remove:
                    logger.info(f"清理超时智能体: {agent_id}")
                    await self.unregister_agent(agent_id)

                await asyncio.sleep(120)  # 每2分钟清理一次

            except Exception as e:
                logger.error(f"清理循环异常: {e}")
                await asyncio.sleep(30)

    async def stop(self):
        """停止生命周期管理器"""
        try:
            self.state = LifecycleState.STOPPING

            # 取消所有后台任务
            tasks = [self._heartbeat_task, self._health_check_task, self._cleanup_task]
            for task in tasks:
                if task and not task.done():
                    task.cancel()
                    with contextlib.suppress(asyncio.CancelledError):
                        await task

            # 清理所有智能体
            for agent_id in list(self.agents.keys()):
                await self.unregister_agent(agent_id)

            self.state = LifecycleState.STOPPED
            logger.info("生命周期管理器已停止")

        except Exception as e:
            logger.error(f"清理生命周期管理器失败: {e}")
            self.state = LifecycleState.ERROR

    def get_manager_status(self) -> dict[str, Any]:
        """获取管理器状态"""
        current_time = time.time()

        return {
            "state": self.state.value,
            "agent_count": len(self.agents),
            "agents": {
                agent_id: {
                    "status": info.status,
                    "last_heartbeat": info.last_heartbeat,
                    "time_since_heartbeat": current_time - info.last_heartbeat,
                    "metrics": info.metrics,
                }
                for agent_id, info in self.agents.items()
            },
            "heartbeat_interval": self.heartbeat_interval,
            "health_check_timeout": self.health_check_timeout,
        }


# 全局生命周期管理器实例
_lifecycle_manager: LifecycleManager | None = None


def get_lifecycle_manager() -> LifecycleManager:
    """获取生命周期管理器实例"""
    global _lifecycle_manager
    if _lifecycle_manager is None:
        _lifecycle_manager = LifecycleManager()
    return _lifecycle_manager
