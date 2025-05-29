"""
健康聚合器
聚合多个服务的健康状态，提供统一的健康视图
"""

from dataclasses import dataclass, field
import logging
import time
from typing import Any

from .health_checker import HealthCheckResult, HealthStatus
from .health_monitor import AlertLevel, HealthAlert

logger = logging.getLogger(__name__)


@dataclass
class ServiceHealth:
    """服务健康状态"""

    service_name: str
    status: HealthStatus
    last_check: float
    checks: dict[str, HealthCheckResult] = field(default_factory=dict)
    alerts: list[HealthAlert] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "service_name": self.service_name,
            "status": self.status.value,
            "last_check": self.last_check,
            "checks": {name: check.to_dict() for name, check in self.checks.items()},
            "alerts": [alert.to_dict() for alert in self.alerts],
            "metadata": self.metadata,
        }


class HealthAggregator:
    """健康聚合器"""

    def __init__(self):
        self.services: dict[str, ServiceHealth] = {}
        self.config = {}
        self.aggregation_rules = {}
        self.dependencies: dict[str, set[str]] = {}  # 服务依赖关系
        self.service_weights: dict[str, float] = {}  # 服务权重

    async def initialize(self, config: dict[str, Any]):
        """初始化健康聚合器"""
        self.config = config

        # 聚合规则配置
        self.aggregation_rules = config.get(
            "aggregation_rules",
            {
                "critical_services": [],  # 关键服务列表
                "dependency_weight": 0.3,  # 依赖权重
                "alert_escalation": True,  # 告警升级
                "health_timeout": 300,  # 健康状态超时（秒）
            },
        )

        # 加载服务依赖关系
        dependencies_config = config.get("dependencies", {})
        for service, deps in dependencies_config.items():
            self.dependencies[service] = set(deps)

        # 加载服务权重
        self.service_weights = config.get("service_weights", {})

        logger.info("健康聚合器初始化完成")

    async def register_service(
        self, service_name: str, metadata: dict[str, Any] | None = None
    ):
        """注册服务"""
        if service_name not in self.services:
            self.services[service_name] = ServiceHealth(
                service_name=service_name,
                status=HealthStatus.UNKNOWN,
                last_check=time.time(),
                metadata=metadata or {},
            )
            logger.info(f"注册服务: {service_name}")

    async def unregister_service(self, service_name: str):
        """注销服务"""
        if service_name in self.services:
            del self.services[service_name]
            logger.info(f"注销服务: {service_name}")

    async def update_service_health(
        self, service_name: str, health_result: dict[str, Any]
    ):
        """更新服务健康状态"""
        if service_name not in self.services:
            await self.register_service(service_name)

        service = self.services[service_name]

        # 更新基本信息
        service.status = HealthStatus(health_result.get("status", "unknown"))
        service.last_check = health_result.get("timestamp", time.time())

        # 更新检查结果
        checks = health_result.get("checks", {})
        service.checks.clear()

        for check_name, check_data in checks.items():
            check_result = HealthCheckResult(
                name=check_name,
                status=HealthStatus(check_data.get("status", "unknown")),
                message=check_data.get("message", ""),
                details=check_data.get("details", {}),
                timestamp=check_data.get("timestamp", time.time()),
                duration_ms=check_data.get("duration_ms", 0),
            )
            service.checks[check_name] = check_result

        logger.debug(f"更新服务 {service_name} 健康状态: {service.status.value}")

    async def add_service_alert(self, service_name: str, alert: HealthAlert):
        """添加服务告警"""
        if service_name not in self.services:
            await self.register_service(service_name)

        service = self.services[service_name]
        service.alerts.append(alert)

        # 限制告警数量
        max_alerts = self.config.get("max_alerts_per_service", 50)
        if len(service.alerts) > max_alerts:
            service.alerts = service.alerts[-max_alerts:]

        logger.debug(f"添加服务 {service_name} 告警: {alert.message}")

    async def get_overall_health(self) -> dict[str, Any]:
        """获取整体健康状态"""
        if not self.services:
            return {
                "status": "unknown",
                "message": "没有注册的服务",
                "timestamp": time.time(),
            }

        # 计算整体状态
        overall_status = await self._calculate_overall_status()

        # 统计各状态的服务数量
        status_counts = {}
        for service in self.services.values():
            status = service.status.value
            status_counts[status] = status_counts.get(status, 0) + 1

        # 统计告警
        total_alerts = sum(len(service.alerts) for service in self.services.values())
        critical_alerts = sum(
            len([a for a in service.alerts if a.level == AlertLevel.CRITICAL])
            for service in self.services.values()
        )

        # 检查过期的健康状态
        current_time = time.time()
        timeout = self.aggregation_rules.get("health_timeout", 300)
        stale_services = [
            service.service_name
            for service in self.services.values()
            if current_time - service.last_check > timeout
        ]

        return {
            "status": overall_status.value,
            "timestamp": time.time(),
            "services": {
                "total": len(self.services),
                "by_status": status_counts,
                "stale": stale_services,
            },
            "alerts": {"total": total_alerts, "critical": critical_alerts},
            "dependencies": self._analyze_dependencies(),
        }

    async def _calculate_overall_status(self) -> HealthStatus:
        """计算整体健康状态"""
        if not self.services:
            return HealthStatus.UNKNOWN

        critical_services = set(self.aggregation_rules.get("critical_services", []))

        # 检查关键服务
        for service_name in critical_services:
            if service_name in self.services:
                service = self.services[service_name]
                if service.status == HealthStatus.UNHEALTHY:
                    return HealthStatus.UNHEALTHY

        # 统计各状态的服务
        status_counts = {}
        weighted_scores = {}
        total_weight = 0

        for service in self.services.values():
            status = service.status
            status_counts[status] = status_counts.get(status, 0) + 1

            # 计算加权得分
            weight = self.service_weights.get(service.service_name, 1.0)
            total_weight += weight

            if status == HealthStatus.HEALTHY:
                score = 1.0
            elif status == HealthStatus.DEGRADED:
                score = 0.5
            elif status == HealthStatus.UNHEALTHY:
                score = 0.0
            else:
                score = 0.25  # UNKNOWN

            weighted_scores[service.service_name] = score * weight

        # 计算整体得分
        if total_weight > 0:
            overall_score = sum(weighted_scores.values()) / total_weight
        else:
            overall_score = 0.0

        # 根据得分确定状态
        if overall_score >= 0.8:
            return HealthStatus.HEALTHY
        elif overall_score >= 0.5 or overall_score > 0:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.UNHEALTHY

    def _analyze_dependencies(self) -> dict[str, Any]:
        """分析服务依赖关系"""
        dependency_health = {}

        for service_name, dependencies in self.dependencies.items():
            if service_name not in self.services:
                continue

            service_status = self.services[service_name].status
            dependency_statuses = []

            for dep_name in dependencies:
                if dep_name in self.services:
                    dependency_statuses.append(self.services[dep_name].status)
                else:
                    dependency_statuses.append(HealthStatus.UNKNOWN)

            # 分析依赖影响
            unhealthy_deps = [
                s for s in dependency_statuses if s == HealthStatus.UNHEALTHY
            ]
            degraded_deps = [
                s for s in dependency_statuses if s == HealthStatus.DEGRADED
            ]

            dependency_health[service_name] = {
                "status": service_status.value,
                "dependencies": list(dependencies),
                "dependency_issues": {
                    "unhealthy": len(unhealthy_deps),
                    "degraded": len(degraded_deps),
                },
                "potentially_affected": len(unhealthy_deps) > 0
                or len(degraded_deps) > 0,
            }

        return dependency_health

    async def get_service_health(self, service_name: str) -> dict[str, Any] | None:
        """获取特定服务的健康状态"""
        if service_name not in self.services:
            return None

        service = self.services[service_name]

        # 分析依赖状态
        dependency_status = {}
        if service_name in self.dependencies:
            for dep_name in self.dependencies[service_name]:
                if dep_name in self.services:
                    dependency_status[dep_name] = self.services[dep_name].status.value
                else:
                    dependency_status[dep_name] = "unknown"

        return {
            **service.to_dict(),
            "dependencies": dependency_status,
            "weight": self.service_weights.get(service_name, 1.0),
            "is_critical": service_name
            in self.aggregation_rules.get("critical_services", []),
        }

    async def get_services_by_status(
        self, status: HealthStatus
    ) -> list[dict[str, Any]]:
        """获取指定状态的服务列表"""
        services = []

        for service in self.services.values():
            if service.status == status:
                services.append(service.to_dict())

        return services

    async def get_critical_issues(self) -> dict[str, Any]:
        """获取关键问题"""
        critical_services = set(self.aggregation_rules.get("critical_services", []))
        issues = {
            "critical_service_failures": [],
            "cascade_failures": [],
            "high_alert_services": [],
            "stale_services": [],
        }

        current_time = time.time()
        timeout = self.aggregation_rules.get("health_timeout", 300)

        for service in self.services.values():
            service_name = service.service_name

            # 关键服务故障
            if (
                service_name in critical_services
                and service.status == HealthStatus.UNHEALTHY
            ):
                issues["critical_service_failures"].append(
                    {
                        "service": service_name,
                        "status": service.status.value,
                        "last_check": service.last_check,
                    }
                )

            # 高告警服务
            critical_alerts = [
                a for a in service.alerts if a.level == AlertLevel.CRITICAL
            ]
            if len(critical_alerts) > 0:
                issues["high_alert_services"].append(
                    {
                        "service": service_name,
                        "critical_alerts": len(critical_alerts),
                        "total_alerts": len(service.alerts),
                    }
                )

            # 过期服务
            if current_time - service.last_check > timeout:
                issues["stale_services"].append(
                    {
                        "service": service_name,
                        "last_check": service.last_check,
                        "stale_duration": current_time - service.last_check,
                    }
                )

        # 分析级联故障
        for service_name, dependencies in self.dependencies.items():
            if service_name not in self.services:
                continue

            service = self.services[service_name]
            failed_deps = []

            for dep_name in dependencies:
                if dep_name in self.services:
                    dep_service = self.services[dep_name]
                    if dep_service.status == HealthStatus.UNHEALTHY:
                        failed_deps.append(dep_name)

            if failed_deps and service.status == HealthStatus.UNHEALTHY:
                issues["cascade_failures"].append(
                    {
                        "service": service_name,
                        "failed_dependencies": failed_deps,
                        "status": service.status.value,
                    }
                )

        return issues

    async def get_health_trends(self, time_window: int = 3600) -> dict[str, Any]:
        """获取健康趋势（需要历史数据支持）"""
        # 这里可以扩展为从时序数据库获取历史数据
        # 目前返回当前状态快照

        trends = {}
        for service_name, service in self.services.items():
            trends[service_name] = {
                "current_status": service.status.value,
                "last_check": service.last_check,
                "check_count": len(service.checks),
                "alert_count": len(service.alerts),
            }

        return {
            "time_window": time_window,
            "services": trends,
            "overall_trend": "stable",  # 可以基于历史数据计算
        }

    async def health_check(self) -> dict[str, Any]:
        """聚合器自身健康检查"""
        return {
            "status": "healthy",
            "registered_services": len(self.services),
            "dependencies_configured": len(self.dependencies),
            "service_weights_configured": len(self.service_weights),
        }

    async def shutdown(self):
        """关闭聚合器"""
        self.services.clear()
        self.dependencies.clear()
        self.service_weights.clear()
        logger.info("健康聚合器已关闭")
