#!/usr/bin/env python3
"""
智能体管理服务
Agent Manager Service
"""

import asyncio
import logging
import time
from datetime import UTC, datetime
from typing import Any

import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential

from ..model.agent import (
    AgentConfig,
    AgentHealthCheck,
    AgentInfo,
    AgentMetrics,
    AgentRequest,
    AgentResponse,
    AgentStatus,
)

logger = logging.getLogger(__name__)


class AgentManager:
    """智能体管理器"""

    def __init__(self, config: dict[str, Any]) -> None:
        """
        初始化智能体管理器

        Args:
            config: 配置字典
        """
        self.config = config
        self.agents: dict[str, AgentInfo] = {}
        self.agent_configs: dict[str, AgentConfig] = {}
        self.agent_metrics: dict[str, AgentMetrics] = {}
        self.session: aiohttp.ClientSession | None = None
        self._health_check_tasks: dict[str, asyncio.Task[None]] = {}

        # 初始化智能体配置
        self._load_agent_configs()

        # 动态注册相关
        self._registration_callbacks: list[callable] = []
        self._deregistration_callbacks: list[callable] = []

        logger.info("智能体管理器初始化完成")

    def _load_agent_configs(self) -> None:
        """加载智能体配置"""
        agents_config = self.config.get("agents", {})

        for agent_id, agent_config in agents_config.items():
            config = AgentConfig(
                name=agent_config.get("name", agent_id),
                url=agent_config["url"],
                timeout=agent_config.get("timeout", 30),
                retry_count=agent_config.get("retry_count", 3),
                health_check_interval=agent_config.get("health_check_interval", 60),
                capabilities=agent_config.get("capabilities", []),
            )
            self.agent_configs[agent_id] = config

            # 初始化智能体信息
            agent_info = AgentInfo(
                id=agent_id,
                name=config.name,
                description="",
                version="1.0.0",
                url=config.url,
                status=AgentStatus.OFFLINE,
                last_heartbeat=None,
            )
            self.agents[agent_id] = agent_info

            # 初始化指标
            self.agent_metrics[agent_id] = AgentMetrics(
                agent_id=agent_id,
                request_count=0,
                success_count=0,
                error_count=0,
                avg_response_time=0.0,
                last_request_time=None,
                uptime=0.0,
            )

            logger.info(f"已加载智能体配置: {agent_id}")

    async def start(self) -> None:
        """启动智能体管理器"""
        # 创建 HTTP 会话
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))

        # 启动健康检查任务
        for agent_id in self.agents:
            await self._start_health_check(agent_id)

        logger.info("智能体管理器已启动")

    async def stop(self) -> None:
        """停止智能体管理器"""
        # 停止健康检查任务
        for task in self._health_check_tasks.values():
            task.cancel()

        # 等待任务完成
        if self._health_check_tasks:
            await asyncio.gather(
                *self._health_check_tasks.values(), return_exceptions=True
            )

        # 关闭 HTTP 会话
        if self.session:
            await self.session.close()
            self.session = None

        logger.info("智能体管理器已停止")

    async def _start_health_check(self, agent_id: str) -> None:
        """启动智能体健康检查"""
        config = self.agent_configs[agent_id]

        async def health_check_loop() -> None:
            while True:
                try:
                    await self._perform_health_check(agent_id)
                    await asyncio.sleep(config.health_check_interval)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"智能体 {agent_id} 健康检查异常: {e}")
                    await asyncio.sleep(10)  # 异常时短暂等待

        task = asyncio.create_task(health_check_loop())
        self._health_check_tasks[agent_id] = task

    async def _perform_health_check(self, agent_id: str) -> AgentHealthCheck:
        """执行健康检查"""
        agent = self.agents[agent_id]
        config = self.agent_configs[agent_id]

        start_time = time.time()

        try:
            if not self.session:
                raise Exception("HTTP 会话未初始化")

            # 发送健康检查请求
            async with self.session.get(
                f"{config.url}/health", timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response_time = (time.time() - start_time) * 1000

                if response.status == 200:
                    # 更新智能体状态
                    agent.status = AgentStatus.ONLINE
                    agent.last_heartbeat = datetime.now(UTC).isoformat()

                    health_check = AgentHealthCheck(
                        agent_id=agent_id,
                        status=AgentStatus.ONLINE,
                        response_time=response_time,
                        timestamp=datetime.now(UTC).isoformat(),
                        error_message=None,
                    )
                else:
                    agent.status = AgentStatus.ERROR
                    health_check = AgentHealthCheck(
                        agent_id=agent_id,
                        status=AgentStatus.ERROR,
                        response_time=response_time,
                        error_message=f"HTTP {response.status}",
                        timestamp=datetime.now(UTC).isoformat(),
                    )

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            agent.status = AgentStatus.OFFLINE

            health_check = AgentHealthCheck(
                agent_id=agent_id,
                status=AgentStatus.OFFLINE,
                response_time=response_time,
                error_message=str(e),
                timestamp=datetime.now(UTC).isoformat(),
            )

        return health_check

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def send_request(self, request: AgentRequest) -> AgentResponse:
        """
        发送请求到智能体

        Args:
            request: 智能体请求

        Returns:
            智能体响应
        """
        agent_id = request.agent_id
        agent = self.agents.get(agent_id)
        config = self.agent_configs.get(agent_id)

        if not agent or not config:
            return AgentResponse(
                success=False,
                error=f"智能体 {agent_id} 不存在",
                agent_id=agent_id,
                request_id=request.request_id,
                timestamp=datetime.now(UTC).isoformat(),
                execution_time=0.0,
            )

        if agent.status != AgentStatus.ONLINE:
            return AgentResponse(
                success=False,
                error=f"智能体 {agent_id} 不在线",
                agent_id=agent_id,
                request_id=request.request_id,
                timestamp=datetime.now(UTC).isoformat(),
                execution_time=0.0,
            )

        start_time = time.time()

        try:
            if not self.session:
                raise Exception("HTTP 会话未初始化")

            # 构建请求数据
            request_data = {
                "action": request.action,
                "parameters": request.parameters,
                "user_id": request.user_id,
                "request_id": request.request_id,
            }

            # 发送请求
            timeout = request.timeout or config.timeout
            async with self.session.post(
                f"{config.url}/api/v1/execute",
                json=request_data,
                timeout=aiohttp.ClientTimeout(total=timeout),
            ) as response:
                execution_time = time.time() - start_time

                if response.status == 200:
                    response_data = await response.json()

                    # 更新指标
                    self._update_metrics(agent_id, True, execution_time)

                    return AgentResponse(
                        success=True,
                        data=response_data,
                        error=None,
                        agent_id=agent_id,
                        request_id=request.request_id,
                        timestamp=datetime.now(UTC).isoformat(),
                        execution_time=execution_time,
                    )
                else:
                    error_text = await response.text()
                    self._update_metrics(agent_id, False, execution_time)

                    return AgentResponse(
                        success=False,
                        error=f"HTTP {response.status}: {error_text}",
                        agent_id=agent_id,
                        request_id=request.request_id,
                        timestamp=datetime.now(UTC).isoformat(),
                        execution_time=execution_time,
                    )

        except Exception as e:
            execution_time = time.time() - start_time
            self._update_metrics(agent_id, False, execution_time)

            return AgentResponse(
                success=False,
                error=str(e),
                agent_id=agent_id,
                request_id=request.request_id,
                timestamp=datetime.now(UTC).isoformat(),
                execution_time=execution_time,
            )

    def _update_metrics(
        self, agent_id: str, success: bool, execution_time: float
    ) -> None:
        """更新智能体指标"""
        metrics = self.agent_metrics[agent_id]

        metrics.request_count += 1
        if success:
            metrics.success_count += 1
        else:
            metrics.error_count += 1

        # 更新平均响应时间
        total_time = (
            metrics.avg_response_time * (metrics.request_count - 1) + execution_time
        )
        metrics.avg_response_time = total_time / metrics.request_count

        metrics.last_request_time = datetime.now(UTC).isoformat()

    def get_agent_info(self, agent_id: str) -> AgentInfo | None:
        """获取智能体信息"""
        return self.agents.get(agent_id)

    def get_all_agents(self) -> list[AgentInfo]:
        """获取所有智能体信息"""
        return list(self.agents.values())

    def get_agent_metrics(self, agent_id: str) -> AgentMetrics | None:
        """获取智能体指标"""
        return self.agent_metrics.get(agent_id)

    def get_all_metrics(self) -> list[AgentMetrics]:
        """获取所有智能体指标"""
        return list(self.agent_metrics.values())

    def get_network_status(self) -> dict[str, Any]:
        """获取网络状态"""
        online_count = sum(
            1 for agent in self.agents.values() if agent.status == AgentStatus.ONLINE
        )
        total_count = len(self.agents)

        return {
            "total_agents": total_count,
            "online_agents": online_count,
            "offline_agents": total_count - online_count,
            "network_health": online_count / total_count if total_count > 0 else 0.0,
            "agents": [
                {
                    "id": agent.id,
                    "name": agent.name,
                    "status": agent.status.value,
                    "last_heartbeat": agent.last_heartbeat,
                }
                for agent in self.agents.values()
            ],
        }

    async def register_agent(self, agent: AgentInfo) -> bool:
        """
        动态注册智能体

        Args:
            agent: 智能体信息

        Returns:
            是否注册成功
        """
        try:
            # 验证智能体信息
            if not agent.id or not agent.url:
                logger.error(f"智能体信息不完整: {agent.id}")
                return False

            # 检查是否已存在
            if agent.id in self.agents:
                logger.warning(f"智能体已存在，将更新信息: {agent.id}")

            # 测试连接
            if not await self._test_agent_connection(agent):
                logger.error(f"无法连接到智能体: {agent.id} ({agent.url})")
                return False

            # 注册智能体
            self.agents[agent.id] = agent
            
            # 初始化指标
            self.agent_metrics[agent.id] = AgentMetrics(
                agent_id=agent.id,
                request_count=0,
                success_count=0,
                error_count=0,
                avg_response_time=0.0,
                last_request_time=None,
                uptime=0.0,
            )

            # 触发注册回调
            for callback in self._registration_callbacks:
                try:
                    await callback(agent)
                except Exception as e:
                    logger.error(f"注册回调执行失败: {e}")

            logger.info(f"智能体注册成功: {agent.id}")
            return True

        except Exception as e:
            logger.error(f"智能体注册失败: {agent.id}, 错误: {e}")
            return False

    async def deregister_agent(self, agent_id: str) -> bool:
        """
        注销智能体

        Args:
            agent_id: 智能体ID

        Returns:
            是否注销成功
        """
        try:
            if agent_id not in self.agents:
                logger.warning(f"智能体不存在: {agent_id}")
                return False

            agent = self.agents[agent_id]

            # 触发注销回调
            for callback in self._deregistration_callbacks:
                try:
                    await callback(agent)
                except Exception as e:
                    logger.error(f"注销回调执行失败: {e}")

            # 移除智能体
            del self.agents[agent_id]
            
            # 清理指标
            if agent_id in self.agent_metrics:
                del self.agent_metrics[agent_id]

            logger.info(f"智能体注销成功: {agent_id}")
            return True

        except Exception as e:
            logger.error(f"智能体注销失败: {agent_id}, 错误: {e}")
            return False

    def add_registration_callback(self, callback: callable) -> None:
        """
        添加智能体注册回调

        Args:
            callback: 回调函数，接收 Agent 参数
        """
        self._registration_callbacks.append(callback)

    def add_deregistration_callback(self, callback: callable) -> None:
        """
        添加智能体注销回调

        Args:
            callback: 回调函数，接收 Agent 参数
        """
        self._deregistration_callbacks.append(callback)

    async def _test_agent_connection(self, agent: AgentInfo) -> bool:
        """
        测试智能体连接

        Args:
            agent: 智能体信息

        Returns:
            是否连接成功
        """
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                # 尝试健康检查端点
                health_url = f"{agent.url.rstrip('/')}/health"
                async with session.get(health_url) as response:
                    if response.status == 200:
                        return True
                    
                # 如果健康检查失败，尝试根路径
                async with session.get(agent.url) as response:
                    return response.status < 500

        except Exception as e:
            logger.debug(f"智能体连接测试失败: {agent.id}, 错误: {e}")
            return False
