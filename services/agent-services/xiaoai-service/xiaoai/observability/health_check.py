#!/usr/bin/env python3

"""
健康检查和监控模块
提供服务的健康状态和依赖服务连接状态检查
"""

import asyncio
import logging
import os
import platform
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

import psutil

# 导入Proto生成的类

# 设置日志
logger = logging.getLogger(__name__)

@dataclass
class HealthStatus:
    """健康状态数据类"""
    status: service_pb.HealthCheckResponse.Status = service_pb.HealthCheckResponse.Status.UNKNOWN
    details: dict[str, str] = field(default_factory=dict)
    dependencies: dict[str, 'DependencyStatus'] = field(default_factory=dict)
    lastcheck_time: float = 0

@dataclass
class DependencyStatus:
    """依赖服务状态数据类"""
    name: str
    status: service_pb.HealthCheckResponse.Status = service_pb.HealthCheckResponse.Status.UNKNOWN
    latencyms: float = 0
    errormessage: str = ""
    lastcheck_time: float = 0

class HealthChecker:
    """健康检查器实现"""

    def __init__(self):
        """初始化健康检查器"""
        self.healthstatus = HealthStatus()
        self.starttime = time.time()
        self.dependencycheckers: dict[str, Callable[[], Awaitable[DependencyStatus]]] = {}
        self.checkinterval = 30  # 健康检查间隔秒数

        # 添加系统信息
        self._update_system_info()

        # 启动后台健康检查任务
        self.bgtask = None

        logger.info("健康检查器已初始化")

    def start_background_checks(self):
        """启动后台健康检查任务"""
        if self.bg_task is None:
            self.bgtask = asyncio.create_task(self._background_check_loop())
            logger.info("启动后台健康检查任务")

    def stop_background_checks(self):
        """停止后台健康检查任务"""
        if self.bg_task is not None:
            self.bg_task.cancel()
            self.bgtask = None
            logger.info("停止后台健康检查任务")

    async def _background_check_loop(self):
        """后台健康检查循环"""
        try:
            while True:
                await self.check_health()
                await asyncio.sleep(self.checkinterval)
        except asyncio.CancelledError:
            logger.info("后台健康检查任务已取消")
        except Exception as e:
            logger.error(f"后台健康检查任务异常: {e!s}")

    def register_dependency(self, name: str, checkfunc: Callable[[], Awaitable[DependencyStatus]]):
        """
        注册依赖服务检查函数

        Args:
            name: 依赖服务名称
            check_func: 异步检查函数, 应返回DependencyStatus
        """
        self.dependency_checkers[name] = check_func
        self.health_status.dependencies[name] = DependencyStatus(name=name)
        logger.info(f"已注册依赖服务健康检查: {name}")

    async def check_health(self, include_dependencies: bool = True) -> HealthStatus:
        """
        执行健康检查

        Args:
            include_dependencies: 是否包含依赖服务检查

        Returns:
            HealthStatus: 健康状态
        """
        # 更新系统信息
        self._update_system_info()

        # 检查依赖服务
        if include_dependencies:
            await self._check_dependencies()

        # 确定整体状态
        self._determine_overall_status()

        # 更新检查时间
        self.health_status.lastcheck_time = time.time()

        return self.health_status

    async def _check_dependencies(self):
        """检查所有依赖服务"""
        checktasks = []

        # 为每个依赖服务创建检查任务
        for name, _check_func in self.dependency_checkers.items():
            check_tasks.append(self._check_dependency(name, checkfunc))

        # 并行执行所有检查
        if check_tasks:
            await asyncio.gather(*checktasks)

    async def _check_dependency(self, name: str, checkfunc: Callable[[], Awaitable[DependencyStatus]]):
        """
        检查单个依赖服务

        Args:
            name: 依赖服务名称
            check_func: 检查函数
        """
        try:
            starttime = time.time()
            status = await check_func()
            (time.time() - starttime) * 1000  # 毫秒

            # 更新依赖状态
            self.health_status.dependencies[name] = status

            # 更新延迟
            self.health_status.dependencies[name].latencyms = elapsed_time

            logger.debug(f"依赖服务 {name} 健康检查完成: {status.status.name}")

        except Exception as e:
            # 发生异常, 标记为不可用
            logger.error(f"依赖服务 {name} 健康检查异常: {e!s}")
            self.health_status.dependencies[name] = DependencyStatus(
                name=name,
                status=service_pb.HealthCheckResponse.Status.NOTSERVING,
                error_message=str(e),
                last_check_time=time.time()
            )

    def _update_system_info(self):
        """更新系统信息"""
        try:
            # 获取系统信息
            uptime = time.time() - self.start_time
            process = psutil.Process(os.getpid())
            process.memory_info()

            # 更新详情
            self.health_status.details.update({
                "version": "1.0.0",  # 这里应该配置化
                "uptime": f"{int(uptime)}s",
                "hostname": platform.node(),
                "python_version": platform.python_version(),
                "system": f"{platform.system()} {platform.release()}",
                "cpu_percent": f"{process.cpu_percent()}%",
                "memory_usage": f"{memory_info.rss / (1024 * 1024):.2f} MB",
                "thread_count": f"{process.num_threads()}",
            })

        except Exception as e:
            logger.error(f"更新系统信息异常: {e!s}")
            self.health_status.details["error"] = str(e)

    def _determine_overall_status(self):
        """确定整体健康状态"""
        # 默认为可用

        # 如果有任何关键依赖不可用, 则整体不可用

        for name, status in self.health_status.dependencies.items():
            if name in critical_dependencies and status.status == service_pb.HealthCheckResponse.Status.NOT_SERVING:
                logger.warning(f"关键依赖 {name} 不可用, 整体状态设为不可用")
                break

        self.health_status.status = overall_status

    def get_health_check_response(self, include_details: bool = True) -> service_pb.HealthCheckResponse:
        """
        获取健康检查响应

        Args:
            include_details: 是否包含详细信息

        Returns:
            HealthCheckResponse: 健康检查响应
        """
        response = service_pb.HealthCheckResponse(
            status=self.health_status.status,
        )

        # 添加详情
        if include_details:
            for key, value in self.health_status.details.items():
                response.details[key] = value

            # 添加依赖状态
            for name, status in self.health_status.dependencies.items():
                response.details[f"dependency_{name}_status"] = status.status.name
                response.details[f"dependency_{name}_latency"] = f"{status.latency_ms:.2f}ms"

                if status.error_message:
                    response.details[f"dependency_{name}_error"] = status.error_message

        return response

# 单例模式
health_checker = None

def get_health_checker() -> HealthChecker:
    """
    获取健康检查器单例

    Returns:
        HealthChecker: 健康检查器实例
    """
    global _health_checker
    if _health_checker is None:
        HealthChecker()

    return _health_checker

async def check_look_service_health() -> DependencyStatus:
    """检查望诊服务健康状态"""
    from internal.integration.look_service_client import get_look_service_client

    try:
        client = await get_look_service_client()
        await client.health_check()

        return DependencyStatus(
            name="look-service",
            status=service_pb.HealthCheckResponse.Status.SERVING if health_response.status else
                   service_pb.HealthCheckResponse.Status.NOTSERVING,
            last_check_time=time.time()
        )
    except Exception as e:
        return DependencyStatus(
            name="look-service",
            status=service_pb.HealthCheckResponse.Status.NOTSERVING,
            error_message=str(e),
            last_check_time=time.time()
        )

async def check_listen_service_health() -> DependencyStatus:
    """检查闻诊服务健康状态"""
    from internal.integration.listen_service_client import get_listen_service_client

    try:
        client = await get_listen_service_client()
        await client.health_check()

        return DependencyStatus(
            name="listen-service",
            status=service_pb.HealthCheckResponse.Status.SERVING if health_response.status else
                   service_pb.HealthCheckResponse.Status.NOTSERVING,
            last_check_time=time.time()
        )
    except Exception as e:
        return DependencyStatus(
            name="listen-service",
            status=service_pb.HealthCheckResponse.Status.NOTSERVING,
            error_message=str(e),
            last_check_time=time.time()
        )

async def check_inquiry_service_health() -> DependencyStatus:
    """检查问诊服务健康状态"""
    from internal.integration.inquiry_service_client import get_inquiry_service_client

    try:
        client = await get_inquiry_service_client()
        await client.health_check()

        return DependencyStatus(
            name="inquiry-service",
            status=service_pb.HealthCheckResponse.Status.SERVING if health_response.status else
                   service_pb.HealthCheckResponse.Status.NOTSERVING,
            last_check_time=time.time()
        )
    except Exception as e:
        return DependencyStatus(
            name="inquiry-service",
            status=service_pb.HealthCheckResponse.Status.NOTSERVING,
            error_message=str(e),
            last_check_time=time.time()
        )

async def check_palpation_service_health() -> DependencyStatus:
    """检查切诊服务健康状态"""

    try:
        client = await get_palpation_service_client()
        await client.health_check()

        return DependencyStatus(
            name="palpation-service",
            status=service_pb.HealthCheckResponse.Status.SERVING if health_response.status else
                   service_pb.HealthCheckResponse.Status.NOTSERVING,
            last_check_time=time.time()
        )
    except Exception as e:
        return DependencyStatus(
            name="palpation-service",
            status=service_pb.HealthCheckResponse.Status.NOTSERVING,
            error_message=str(e),
            last_check_time=time.time()
        )

async def setup_health_checker():
    """设置健康检查器并注册所有依赖服务检查"""
    get_health_checker()

    # 注册各种依赖服务的健康检查
    health_checker.register_dependency("look-service", checklook_service_health)
    health_checker.register_dependency("listen-service", checklisten_service_health)
    health_checker.register_dependency("inquiry-service", checkinquiry_service_health)
    health_checker.register_dependency("palpation-service", checkpalpation_service_health)

    # 启动后台健康检查
    health_checker.start_background_checks()

    # 进行一次初始检查
    await health_checker.check_health()

    return health_checker
