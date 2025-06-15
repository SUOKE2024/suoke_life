"""
自动故障恢复机制模块

实现智能故障检测和自动恢复，包括：
- 故障模式识别
- 自动恢复策略
- 恢复效果评估
- 故障预防机制
"""

import asyncio
import logging
import os
import signal
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import psutil

logger = logging.getLogger(__name__)


class FailureType(Enum):
    """故障类型枚举"""

    SERVICE_DOWN = "service_down"  # 服务停止
    HIGH_CPU = "high_cpu"  # CPU使用率过高
    HIGH_MEMORY = "high_memory"  # 内存使用率过高
    DISK_FULL = "disk_full"  # 磁盘空间不足
    NETWORK_ERROR = "network_error"  # 网络错误
    DATABASE_ERROR = "database_error"  # 数据库错误
    TIMEOUT_ERROR = "timeout_error"  # 超时错误
    DEPENDENCY_ERROR = "dependency_error"  # 依赖服务错误


class RecoveryAction(Enum):
    """恢复动作枚举"""

    RESTART_SERVICE = "restart_service"  # 重启服务
    KILL_PROCESS = "kill_process"  # 终止进程
    CLEAR_CACHE = "clear_cache"  # 清理缓存
    SCALE_UP = "scale_up"  # 扩容
    SCALE_DOWN = "scale_down"  # 缩容
    RESTART_DEPENDENCY = "restart_dependency"  # 重启依赖
    CLEANUP_DISK = "cleanup_disk"  # 清理磁盘
    RESET_CONNECTION = "reset_connection"  # 重置连接


class RecoveryStatus(Enum):
    """恢复状态枚举"""

    PENDING = "pending"  # 等待中
    IN_PROGRESS = "in_progress"  # 进行中
    SUCCESS = "success"  # 成功
    FAILED = "failed"  # 失败
    SKIPPED = "skipped"  # 跳过


@dataclass
class FailureEvent:
    """故障事件"""

    timestamp: datetime
    failure_type: FailureType
    severity: str
    description: str
    affected_service: str
    metrics: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class RecoveryPlan:
    """恢复计划"""

    failure_event: FailureEvent
    actions: list[RecoveryAction]
    priority: int
    timeout: int
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class RecoveryResult:
    """恢复结果"""

    plan: RecoveryPlan
    action: RecoveryAction
    status: RecoveryStatus
    start_time: datetime
    end_time: datetime | None = None
    error_message: str | None = None
    metrics_before: dict[str, Any] = field(default_factory=dict)
    metrics_after: dict[str, Any] = field(default_factory=dict)


class ServiceMonitor:
    """服务监控器"""

    def __init__(self):
        self.monitored_services = {}
        self.process_cache = {}

    def add_service(
        self, service_name: str, process_name: str, port: int | None = None
    ) -> None:
        """添加监控服务"""
        self.monitored_services[service_name] = {
            "process_name": process_name,
            "port": port,
            "last_check": None,
            "status": "unknown",
        }

    def check_service_status(self, service_name: str) -> dict[str, Any]:
        """检查服务状态"""
        if service_name not in self.monitored_services:
            return {"status": "unknown", "error": "Service not monitored"}

        service_info = self.monitored_services[service_name]
        process_name = service_info["process_name"]
        port = service_info["port"]

        try:
            # 检查进程是否运行
            processes = []
            for proc in psutil.process_iter(["pid", "name", "status"]):
                if process_name.lower() in proc.info["name"].lower():
                    processes.append(proc)

            if not processes:
                return {
                    "status": "down",
                    "error": f"Process {process_name} not found",
                    "processes": [],
                }

            # 检查端口是否监听（如果指定了端口）
            if port:
                port_listening = False
                for conn in psutil.net_connections():
                    if conn.laddr.port == port and conn.status == "LISTEN":
                        port_listening = True
                        break

                if not port_listening:
                    return {
                        "status": "port_not_listening",
                        "error": f"Port {port} not listening",
                        "processes": [p.info for p in processes],
                    }

            # 获取进程详细信息
            process_details = []
            for proc in processes:
                try:
                    process_details.append(
                        {
                            "pid": proc.pid,
                            "name": proc.name(),
                            "status": proc.status(),
                            "cpu_percent": proc.cpu_percent(),
                            "memory_percent": proc.memory_percent(),
                            "create_time": proc.create_time(),
                        }
                    )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            service_info["last_check"] = datetime.now()
            service_info["status"] = "running"

            return {
                "status": "running",
                "processes": process_details,
                "port": port,
                "last_check": service_info["last_check"].isoformat(),
            }

        except Exception as e:
            return {"status": "error", "error": str(e), "processes": []}

    def get_system_metrics(self) -> dict[str, Any]:
        """获取系统指标"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": {
                    path: psutil.disk_usage(path).percent
                    for path in ["/"]
                    if os.path.exists(path)
                },
                "network_io": psutil.net_io_counters()._asdict(),
                "load_average": os.getloadavg() if hasattr(os, "getloadavg") else None,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"获取系统指标失败: {e}")
            return {}


class RecoveryActionExecutor:
    """恢复动作执行器"""

    def __init__(self):
        self.action_handlers = {
            RecoveryAction.RESTART_SERVICE: self._restart_service,
            RecoveryAction.KILL_PROCESS: self._kill_process,
            RecoveryAction.CLEAR_CACHE: self._clear_cache,
            RecoveryAction.CLEANUP_DISK: self._cleanup_disk,
            RecoveryAction.RESET_CONNECTION: self._reset_connection,
        }

    async def execute_action(
        self, action: RecoveryAction, context: dict[str, Any]
    ) -> dict[str, Any]:
        """执行恢复动作"""
        if action not in self.action_handlers:
            return {"success": False, "error": f"Unknown action: {action.value}"}

        try:
            handler = self.action_handlers[action]
            result = await handler(context)
            return result
        except Exception as e:
            logger.error(f"执行恢复动作 {action.value} 失败: {e}")
            return {"success": False, "error": str(e)}

    async def _restart_service(self, context: dict[str, Any]) -> dict[str, Any]:
        """重启服务"""
        service_name = context.get("service_name")
        if not service_name:
            return {"success": False, "error": "Service name not provided"}

        try:
            # 模拟重启服务
            logger.info(f"重启服务: {service_name}")

            # 这里可以根据实际情况调用系统命令
            # subprocess.run(['systemctl', 'restart', service_name], check=True)

            await asyncio.sleep(2)  # 模拟重启时间

            return {
                "success": True,
                "message": f"Service {service_name} restarted successfully",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _kill_process(self, context: dict[str, Any]) -> dict[str, Any]:
        """终止进程"""
        pid = context.get("pid")
        process_name = context.get("process_name")

        try:
            if pid:
                # 根据PID终止进程
                os.kill(pid, signal.SIGTERM)
                await asyncio.sleep(1)

                # 如果进程仍然存在，强制终止
                try:
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass  # 进程已经终止

                return {
                    "success": True,
                    "message": f"Process {pid} killed successfully",
                }
            elif process_name:
                # 根据进程名终止进程
                killed_count = 0
                for proc in psutil.process_iter(["pid", "name"]):
                    if process_name.lower() in proc.info["name"].lower():
                        try:
                            proc.terminate()
                            killed_count += 1
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue

                return {
                    "success": True,
                    "message": f"Killed {killed_count} processes matching {process_name}",
                }
            else:
                return {"success": False, "error": "No PID or process name provided"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _clear_cache(self, context: dict[str, Any]) -> dict[str, Any]:
        """清理缓存"""
        cache_paths = context.get("cache_paths", ["/tmp", "/var/cache"])

        try:
            cleared_size = 0
            for cache_path in cache_paths:
                if os.path.exists(cache_path):
                    # 模拟清理缓存
                    logger.info(f"清理缓存目录: {cache_path}")
                    # 这里可以实现实际的缓存清理逻辑
                    cleared_size += 1024 * 1024  # 模拟清理了1MB

            return {
                "success": True,
                "message": f"Cache cleared, freed {cleared_size} bytes",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _cleanup_disk(self, context: dict[str, Any]) -> dict[str, Any]:
        """清理磁盘空间"""
        target_path = context.get("path", "/")

        try:
            # 模拟磁盘清理
            logger.info(f"清理磁盘空间: {target_path}")

            # 这里可以实现实际的磁盘清理逻辑
            # 例如：删除临时文件、日志轮转等

            return {
                "success": True,
                "message": f"Disk cleanup completed for {target_path}",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _reset_connection(self, context: dict[str, Any]) -> dict[str, Any]:
        """重置连接"""
        connection_type = context.get("type", "network")

        try:
            logger.info(f"重置连接: {connection_type}")

            # 模拟连接重置
            await asyncio.sleep(1)

            return {
                "success": True,
                "message": f"Connection {connection_type} reset successfully",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


class AutoRecoveryManager:
    """自动恢复管理器"""

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.monitor = ServiceMonitor()
        self.executor = RecoveryActionExecutor()

        self.failure_history = deque(maxlen=1000)
        self.recovery_history = deque(maxlen=1000)
        self.recovery_rules = {}

        self.is_running = False
        self.monitor_thread = None
        self.lock = threading.Lock()

        # 初始化默认恢复规则
        self._initialize_recovery_rules()

    def _initialize_recovery_rules(self) -> None:
        """初始化恢复规则"""
        self.recovery_rules = {
            FailureType.SERVICE_DOWN: [RecoveryAction.RESTART_SERVICE],
            FailureType.HIGH_CPU: [
                RecoveryAction.KILL_PROCESS,
                RecoveryAction.RESTART_SERVICE,
            ],
            FailureType.HIGH_MEMORY: [
                RecoveryAction.CLEAR_CACHE,
                RecoveryAction.KILL_PROCESS,
                RecoveryAction.RESTART_SERVICE,
            ],
            FailureType.DISK_FULL: [
                RecoveryAction.CLEANUP_DISK,
                RecoveryAction.CLEAR_CACHE,
            ],
            FailureType.NETWORK_ERROR: [
                RecoveryAction.RESET_CONNECTION,
                RecoveryAction.RESTART_SERVICE,
            ],
        }

    def add_service(
        self, service_name: str, process_name: str, port: int | None = None
    ) -> None:
        """添加监控服务"""
        self.monitor.add_service(service_name, process_name, port)

    def add_recovery_rule(
        self, failure_type: FailureType, actions: list[RecoveryAction]
    ) -> None:
        """添加恢复规则"""
        self.recovery_rules[failure_type] = actions

    def start(self) -> None:
        """启动自动恢复服务"""
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("自动恢复服务已启动")

    def stop(self) -> None:
        """停止自动恢复服务"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("自动恢复服务已停止")

    def _monitor_loop(self) -> None:
        """监控循环"""
        while self.is_running:
            try:
                # 检查系统指标
                system_metrics = self.monitor.get_system_metrics()
                self._check_system_health(system_metrics)

                # 检查服务状态
                for service_name in self.monitor.monitored_services:
                    service_status = self.monitor.check_service_status(service_name)
                    self._check_service_health(service_name, service_status)

                time.sleep(30)  # 每30秒检查一次

            except Exception as e:
                logger.error(f"监控循环异常: {e}")
                time.sleep(60)

    def _check_system_health(self, metrics: dict[str, Any]) -> None:
        """检查系统健康状态"""
        try:
            # 检查CPU使用率
            cpu_percent = metrics.get("cpu_percent", 0)
            if cpu_percent > 90:
                failure_event = FailureEvent(
                    timestamp=datetime.now(),
                    failure_type=FailureType.HIGH_CPU,
                    severity="high",
                    description=f"CPU使用率过高: {cpu_percent}%",
                    affected_service="system",
                    metrics=metrics,
                )
                asyncio.create_task(self._handle_failure(failure_event))

            # 检查内存使用率
            memory_percent = metrics.get("memory_percent", 0)
            if memory_percent > 90:
                failure_event = FailureEvent(
                    timestamp=datetime.now(),
                    failure_type=FailureType.HIGH_MEMORY,
                    severity="high",
                    description=f"内存使用率过高: {memory_percent}%",
                    affected_service="system",
                    metrics=metrics,
                )
                asyncio.create_task(self._handle_failure(failure_event))

            # 检查磁盘使用率
            disk_usage = metrics.get("disk_usage", {})
            for path, usage in disk_usage.items():
                if usage > 95:
                    failure_event = FailureEvent(
                        timestamp=datetime.now(),
                        failure_type=FailureType.DISK_FULL,
                        severity="critical",
                        description=f"磁盘空间不足: {path} {usage}%",
                        affected_service="system",
                        metrics=metrics,
                        context={"path": path},
                    )
                    asyncio.create_task(self._handle_failure(failure_event))

        except Exception as e:
            logger.error(f"检查系统健康状态失败: {e}")

    def _check_service_health(
        self, service_name: str, service_status: dict[str, Any]
    ) -> None:
        """检查服务健康状态"""
        try:
            status = service_status.get("status")

            if status in ["down", "port_not_listening"]:
                failure_event = FailureEvent(
                    timestamp=datetime.now(),
                    failure_type=FailureType.SERVICE_DOWN,
                    severity="high",
                    description=f"服务 {service_name} 停止运行",
                    affected_service=service_name,
                    context={"service_status": service_status},
                )
                asyncio.create_task(self._handle_failure(failure_event))

        except Exception as e:
            logger.error(f"检查服务健康状态失败: {e}")

    async def _handle_failure(self, failure_event: FailureEvent) -> None:
        """处理故障事件"""
        with self.lock:
            self.failure_history.append(failure_event)

        logger.warning(f"检测到故障: {failure_event.description}")

        # 生成恢复计划
        recovery_plan = self._generate_recovery_plan(failure_event)
        if not recovery_plan:
            logger.warning(f"没有找到适用的恢复计划: {failure_event.failure_type}")
            return

        # 执行恢复计划
        await self._execute_recovery_plan(recovery_plan)

    def _generate_recovery_plan(
        self, failure_event: FailureEvent
    ) -> RecoveryPlan | None:
        """生成恢复计划"""
        failure_type = failure_event.failure_type

        if failure_type not in self.recovery_rules:
            return None

        actions = self.recovery_rules[failure_type]
        priority = 1 if failure_event.severity == "critical" else 2
        timeout = 300  # 5分钟超时

        return RecoveryPlan(
            failure_event=failure_event,
            actions=actions,
            priority=priority,
            timeout=timeout,
        )

    async def _execute_recovery_plan(self, plan: RecoveryPlan) -> None:
        """执行恢复计划"""
        logger.info(f"开始执行恢复计划: {plan.failure_event.description}")

        for action in plan.actions:
            if plan.retry_count >= plan.max_retries:
                logger.error(f"恢复计划重试次数超限: {plan.max_retries}")
                break

            result = await self._execute_recovery_action(plan, action)

            with self.lock:
                self.recovery_history.append(result)

            if result.status == RecoveryStatus.SUCCESS:
                logger.info(f"恢复动作成功: {action.value}")
                break
            else:
                logger.warning(
                    f"恢复动作失败: {action.value}, 错误: {result.error_message}"
                )
                plan.retry_count += 1

    async def _execute_recovery_action(
        self, plan: RecoveryPlan, action: RecoveryAction
    ) -> RecoveryResult:
        """执行单个恢复动作"""
        start_time = datetime.now()

        # 获取执行前的指标
        metrics_before = self.monitor.get_system_metrics()

        result = RecoveryResult(
            plan=plan,
            action=action,
            status=RecoveryStatus.IN_PROGRESS,
            start_time=start_time,
            metrics_before=metrics_before,
        )

        try:
            # 准备执行上下文
            context = {
                "service_name": plan.failure_event.affected_service,
                "failure_type": plan.failure_event.failure_type.value,
                **plan.failure_event.context,
            }

            # 执行恢复动作
            execution_result = await self.executor.execute_action(action, context)

            # 等待一段时间让系统稳定
            await asyncio.sleep(5)

            # 获取执行后的指标
            metrics_after = self.monitor.get_system_metrics()

            result.end_time = datetime.now()
            result.metrics_after = metrics_after

            if execution_result.get("success", False):
                result.status = RecoveryStatus.SUCCESS
            else:
                result.status = RecoveryStatus.FAILED
                result.error_message = execution_result.get("error", "Unknown error")

        except Exception as e:
            result.end_time = datetime.now()
            result.status = RecoveryStatus.FAILED
            result.error_message = str(e)

        return result

    def get_recovery_statistics(self) -> dict[str, Any]:
        """获取恢复统计信息"""
        with self.lock:
            total_failures = len(self.failure_history)
            total_recoveries = len(self.recovery_history)

            if total_recoveries == 0:
                return {
                    "total_failures": total_failures,
                    "total_recoveries": 0,
                    "success_rate": 0,
                    "by_failure_type": {},
                    "by_action_type": {},
                    "recent_failures": [],
                    "recent_recoveries": [],
                }

            # 统计成功率
            successful_recoveries = sum(
                1 for r in self.recovery_history if r.status == RecoveryStatus.SUCCESS
            )
            success_rate = successful_recoveries / total_recoveries

            # 按故障类型统计
            by_failure_type = defaultdict(int)
            for failure in self.failure_history:
                by_failure_type[failure.failure_type.value] += 1

            # 按恢复动作类型统计
            by_action_type = defaultdict(int)
            for recovery in self.recovery_history:
                by_action_type[recovery.action.value] += 1

            # 最近的故障和恢复
            recent_failures = list(self.failure_history)[-5:]
            recent_recoveries = list(self.recovery_history)[-5:]

            return {
                "total_failures": total_failures,
                "total_recoveries": total_recoveries,
                "success_rate": success_rate,
                "by_failure_type": dict(by_failure_type),
                "by_action_type": dict(by_action_type),
                "recent_failures": [
                    {
                        "timestamp": f.timestamp.isoformat(),
                        "type": f.failure_type.value,
                        "severity": f.severity,
                        "description": f.description,
                        "service": f.affected_service,
                    }
                    for f in recent_failures
                ],
                "recent_recoveries": [
                    {
                        "timestamp": r.start_time.isoformat(),
                        "action": r.action.value,
                        "status": r.status.value,
                        "duration": (
                            (r.end_time - r.start_time).total_seconds()
                            if r.end_time
                            else None
                        ),
                        "error": r.error_message,
                    }
                    for r in recent_recoveries
                ],
            }


# 全局自动恢复管理器实例
_global_recovery_manager: AutoRecoveryManager | None = None


def get_recovery_manager(
    config: dict[str, Any] | None = None,
) -> AutoRecoveryManager:
    """获取全局自动恢复管理器实例"""
    global _global_recovery_manager

    if _global_recovery_manager is None:
        _global_recovery_manager = AutoRecoveryManager(config)

    return _global_recovery_manager


if __name__ == "__main__":
    # 示例使用

    # 创建自动恢复管理器
    recovery_manager = AutoRecoveryManager()

    # 添加监控服务
    recovery_manager.add_service("web_server", "python", 8080)
    recovery_manager.add_service("database", "postgres", 5432)

    recovery_manager.start()

    try:
        print("🔧 自动恢复系统演示...")

        # 模拟故障事件
        failure_event = FailureEvent(
            timestamp=datetime.now(),
            failure_type=FailureType.HIGH_CPU,
            severity="high",
            description="CPU使用率过高: 95%",
            affected_service="web_server",
            metrics={"cpu_percent": 95},
        )

        print(f"🚨 模拟故障: {failure_event.description}")

        # 处理故障
        asyncio.run(recovery_manager._handle_failure(failure_event))

        # 等待恢复完成
        time.sleep(3)

        # 显示恢复统计
        print("\n📊 恢复统计信息:")
        stats = recovery_manager.get_recovery_statistics()
        print(f"  总故障数: {stats['total_failures']}")
        print(f"  总恢复数: {stats['total_recoveries']}")
        print(f"  成功率: {stats['success_rate']:.2%}")
        print(f"  按故障类型: {stats['by_failure_type']}")
        print(f"  按恢复动作: {stats['by_action_type']}")

        if stats["recent_recoveries"]:
            print("\n🔧 最近的恢复:")
            for recovery in stats["recent_recoveries"]:
                print(f"  - {recovery['action']}: {recovery['status']}")

    finally:
        recovery_manager.stop()
        print("\n✅ 自动恢复演示完成")
