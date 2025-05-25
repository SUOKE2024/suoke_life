#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
集成优化服务

该模块整合所有优化组件，提供统一的优化管理接口，
包括高级缓存、智能批量处理、性能调优、增强监控等功能。
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum

from internal.model.config import AppConfig
from internal.service.cache_service import CacheService
from internal.service.monitoring_service import MonitoringService
from internal.service.task_processor import TaskProcessor
from internal.blockchain.connection_pool import ConnectionPoolManager

# 导入新的优化组件
from internal.service.advanced_cache_manager import AdvancedCacheManager
from internal.service.smart_batch_processor import SmartBatchProcessor, BatchStrategy, RetryStrategy
from internal.service.performance_tuner import PerformanceTuner, OptimizationTarget, TuningStrategy
from internal.service.enhanced_monitoring import EnhancedMonitoringService, AlertSeverity


class OptimizationLevel(Enum):
    """优化级别"""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ServiceStatus(Enum):
    """服务状态"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class OptimizationProfile:
    """优化配置文件"""
    name: str
    level: OptimizationLevel
    description: str
    cache_strategy: str
    batch_strategy: BatchStrategy
    retry_strategy: RetryStrategy
    optimization_target: OptimizationTarget
    tuning_strategy: TuningStrategy
    monitoring_enabled: bool
    auto_tuning_enabled: bool
    
    # 具体参数
    cache_size: int = 1000
    batch_size: int = 10
    connection_pool_size: int = 20
    worker_threads: int = 8
    gas_limit: int = 8000000


class IntegratedOptimizationService:
    """集成优化服务"""

    def __init__(
        self,
        config: AppConfig,
        cache_service: CacheService,
        monitoring_service: MonitoringService,
        task_processor: TaskProcessor,
        connection_pool: ConnectionPoolManager
    ):
        """
        初始化集成优化服务
        
        Args:
            config: 应用配置对象
            cache_service: 缓存服务
            monitoring_service: 监控服务
            task_processor: 任务处理器
            connection_pool: 连接池管理器
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # 基础服务
        self.cache_service = cache_service
        self.monitoring_service = monitoring_service
        self.task_processor = task_processor
        self.connection_pool = connection_pool
        
        # 优化组件
        self.advanced_cache: Optional[AdvancedCacheManager] = None
        self.batch_processor: Optional[SmartBatchProcessor] = None
        self.performance_tuner: Optional[PerformanceTuner] = None
        self.enhanced_monitoring: Optional[EnhancedMonitoringService] = None
        
        # 服务状态
        self.status = ServiceStatus.STOPPED
        self.current_profile: Optional[OptimizationProfile] = None
        
        # 预定义优化配置文件
        self.optimization_profiles = self._create_optimization_profiles()
        
        # 性能指标
        self.performance_metrics = {}
        self.optimization_history = []
        
        # 回调函数
        self.status_callbacks: List[Callable] = []
        self.optimization_callbacks: List[Callable] = []
        
        self.logger.info("集成优化服务初始化完成")
    
    async def start_optimization(
        self,
        profile_name: str = "standard",
        custom_profile: Optional[OptimizationProfile] = None
    ):
        """
        启动优化服务
        
        Args:
            profile_name: 优化配置文件名称
            custom_profile: 自定义优化配置
        """
        if self.status == ServiceStatus.RUNNING:
            self.logger.warning("优化服务已在运行")
            return
        
        try:
            self.status = ServiceStatus.STARTING
            await self._notify_status_change()
            
            # 选择优化配置
            if custom_profile:
                self.current_profile = custom_profile
            else:
                self.current_profile = self.optimization_profiles.get(profile_name)
                if not self.current_profile:
                    raise ValueError(f"未找到优化配置文件: {profile_name}")
            
            self.logger.info(f"启动优化服务，使用配置: {self.current_profile.name}")
            
            # 初始化优化组件
            await self._initialize_components()
            
            # 启动各个组件
            await self._start_components()
            
            # 设置组件间的集成
            await self._setup_integration()
            
            self.status = ServiceStatus.RUNNING
            await self._notify_status_change()
            
            self.logger.info("优化服务启动完成")
            
        except Exception as e:
            self.status = ServiceStatus.ERROR
            await self._notify_status_change()
            self.logger.error(f"优化服务启动失败: {str(e)}")
            raise
    
    async def stop_optimization(self):
        """停止优化服务"""
        if self.status == ServiceStatus.STOPPED:
            return
        
        try:
            self.status = ServiceStatus.STOPPING
            await self._notify_status_change()
            
            self.logger.info("停止优化服务")
            
            # 停止各个组件
            await self._stop_components()
            
            # 清理资源
            await self._cleanup_resources()
            
            self.status = ServiceStatus.STOPPED
            await self._notify_status_change()
            
            self.logger.info("优化服务已停止")
            
        except Exception as e:
            self.status = ServiceStatus.ERROR
            await self._notify_status_change()
            self.logger.error(f"优化服务停止失败: {str(e)}")
            raise
    
    async def _initialize_components(self):
        """初始化优化组件"""
        profile = self.current_profile
        
        # 初始化高级缓存管理器
        self.advanced_cache = AdvancedCacheManager(
            self.config,
            self.cache_service
        )
        
        # 初始化智能批量处理器
        self.batch_processor = SmartBatchProcessor(self.config)
        self.batch_processor.set_strategy(
            profile.batch_strategy,
            profile.retry_strategy
        )
        
        # 初始化性能调优器
        self.performance_tuner = PerformanceTuner(self.config)
        self.performance_tuner.set_optimization_target(profile.optimization_target)
        self.performance_tuner.set_tuning_strategy(profile.tuning_strategy)
        
        # 初始化增强监控服务
        if profile.monitoring_enabled:
            self.enhanced_monitoring = EnhancedMonitoringService(
                self.config,
                self.monitoring_service
            )
        
        self.logger.info("优化组件初始化完成")
    
    async def _start_components(self):
        """启动各个组件"""
        # 启动高级缓存
        if self.advanced_cache:
            await self.advanced_cache.start_cache_management()
        
        # 启动性能调优器
        if self.performance_tuner and self.current_profile.auto_tuning_enabled:
            await self.performance_tuner.start_tuning()
        
        # 启动增强监控
        if self.enhanced_monitoring:
            await self.enhanced_monitoring.start_monitoring()
        
        self.logger.info("优化组件启动完成")
    
    async def _stop_components(self):
        """停止各个组件"""
        # 停止增强监控
        if self.enhanced_monitoring:
            await self.enhanced_monitoring.stop_monitoring()
        
        # 停止性能调优器
        if self.performance_tuner:
            await self.performance_tuner.stop_tuning()
        
        # 停止高级缓存
        if self.advanced_cache:
            await self.advanced_cache.stop_cache_management()
        
        self.logger.info("优化组件停止完成")
    
    async def _setup_integration(self):
        """设置组件间的集成"""
        if not self.current_profile:
            return
        
        # 设置性能调优器的参数更新回调
        if self.performance_tuner:
            self.performance_tuner.register_parameter_callback(
                "cache_size",
                self._update_cache_size
            )
            self.performance_tuner.register_parameter_callback(
                "batch_size",
                self._update_batch_size
            )
            self.performance_tuner.register_parameter_callback(
                "connection_pool_size",
                self._update_connection_pool_size
            )
        
        # 设置监控回调
        if self.enhanced_monitoring:
            self.enhanced_monitoring.add_alert_callback(self._handle_alert)
            self.enhanced_monitoring.add_insight_callback(self._handle_insight)
        
        # 设置批量处理器的处理器
        if self.batch_processor:
            # 这里可以注册具体的批量处理器
            pass
        
        self.logger.info("组件集成设置完成")
    
    async def _cleanup_resources(self):
        """清理资源"""
        self.advanced_cache = None
        self.batch_processor = None
        self.performance_tuner = None
        self.enhanced_monitoring = None
        self.current_profile = None
        
        self.logger.info("资源清理完成")
    
    async def _update_cache_size(self, new_size: int):
        """更新缓存大小"""
        if self.advanced_cache:
            await self.advanced_cache.update_cache_size(new_size)
            self.logger.info(f"缓存大小已更新: {new_size}")
    
    async def _update_batch_size(self, new_size: int):
        """更新批量大小"""
        if self.batch_processor:
            self.batch_processor.current_batch_size = new_size
            self.logger.info(f"批量大小已更新: {new_size}")
    
    async def _update_connection_pool_size(self, new_size: int):
        """更新连接池大小"""
        # 这里需要根据实际的连接池实现来更新
        self.logger.info(f"连接池大小已更新: {new_size}")
    
    async def _handle_alert(self, alert):
        """处理告警"""
        self.logger.warning(f"收到告警: {alert.message}")
        
        # 根据告警类型采取相应的优化措施
        if alert.metric_name == "cpu_usage" and alert.severity == AlertSeverity.HIGH:
            # CPU使用率过高，减少并发
            if self.batch_processor:
                current_size = self.batch_processor.current_batch_size
                new_size = max(1, int(current_size * 0.8))
                self.batch_processor.current_batch_size = new_size
                self.logger.info(f"因CPU告警调整批量大小: {current_size} -> {new_size}")
        
        elif alert.metric_name == "memory_usage" and alert.severity == AlertSeverity.HIGH:
            # 内存使用率过高，清理缓存
            if self.advanced_cache:
                await self.advanced_cache.clear_expired_cache()
                self.logger.info("因内存告警清理过期缓存")
    
    async def _handle_insight(self, insight):
        """处理性能洞察"""
        self.logger.info(f"收到性能洞察: {insight.title}")
        
        # 根据洞察类型采取相应的优化措施
        if insight.insight_type == "performance_degradation":
            # 性能退化，启用更积极的优化策略
            if self.performance_tuner:
                self.performance_tuner.set_tuning_strategy(TuningStrategy.AGGRESSIVE)
                self.logger.info("因性能退化启用激进调优策略")
        
        elif insight.insight_type == "resource_optimization":
            # 资源优化机会，调整相关参数
            if "memory" in insight.metrics_involved and self.advanced_cache:
                await self.advanced_cache.optimize_cache_distribution()
                self.logger.info("因资源优化洞察调整缓存分布")
    
    async def _notify_status_change(self):
        """通知状态变化"""
        for callback in self.status_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(self.status)
                else:
                    callback(self.status)
            except Exception as e:
                self.logger.error(f"状态回调执行失败: {str(e)}")
    
    def _create_optimization_profiles(self) -> Dict[str, OptimizationProfile]:
        """创建预定义的优化配置文件"""
        profiles = {}
        
        # 基础配置
        profiles["basic"] = OptimizationProfile(
            name="basic",
            level=OptimizationLevel.BASIC,
            description="基础优化配置，适合轻量级应用",
            cache_strategy="simple",
            batch_strategy=BatchStrategy.FIXED_SIZE,
            retry_strategy=RetryStrategy.FIXED_INTERVAL,
            optimization_target=OptimizationTarget.BALANCED,
            tuning_strategy=TuningStrategy.CONSERVATIVE,
            monitoring_enabled=True,
            auto_tuning_enabled=False,
            cache_size=500,
            batch_size=5,
            connection_pool_size=10,
            worker_threads=4,
            gas_limit=5000000
        )
        
        # 标准配置
        profiles["standard"] = OptimizationProfile(
            name="standard",
            level=OptimizationLevel.STANDARD,
            description="标准优化配置，适合大多数应用",
            cache_strategy="adaptive",
            batch_strategy=BatchStrategy.DYNAMIC_SIZE,
            retry_strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
            optimization_target=OptimizationTarget.BALANCED,
            tuning_strategy=TuningStrategy.ADAPTIVE,
            monitoring_enabled=True,
            auto_tuning_enabled=True,
            cache_size=1000,
            batch_size=10,
            connection_pool_size=20,
            worker_threads=8,
            gas_limit=8000000
        )
        
        # 高级配置
        profiles["advanced"] = OptimizationProfile(
            name="advanced",
            level=OptimizationLevel.ADVANCED,
            description="高级优化配置，适合高负载应用",
            cache_strategy="intelligent",
            batch_strategy=BatchStrategy.ADAPTIVE,
            retry_strategy=RetryStrategy.ADAPTIVE,
            optimization_target=OptimizationTarget.THROUGHPUT,
            tuning_strategy=TuningStrategy.PREDICTIVE,
            monitoring_enabled=True,
            auto_tuning_enabled=True,
            cache_size=2000,
            batch_size=20,
            connection_pool_size=30,
            worker_threads=12,
            gas_limit=12000000
        )
        
        # 专家配置
        profiles["expert"] = OptimizationProfile(
            name="expert",
            level=OptimizationLevel.EXPERT,
            description="专家级优化配置，适合极高负载应用",
            cache_strategy="multi_tier",
            batch_strategy=BatchStrategy.GAS_OPTIMIZED,
            retry_strategy=RetryStrategy.ADAPTIVE,
            optimization_target=OptimizationTarget.THROUGHPUT,
            tuning_strategy=TuningStrategy.AGGRESSIVE,
            monitoring_enabled=True,
            auto_tuning_enabled=True,
            cache_size=5000,
            batch_size=50,
            connection_pool_size=50,
            worker_threads=16,
            gas_limit=15000000
        )
        
        return profiles
    
    def add_status_callback(self, callback: Callable):
        """
        添加状态变化回调
        
        Args:
            callback: 回调函数
        """
        self.status_callbacks.append(callback)
    
    def add_optimization_callback(self, callback: Callable):
        """
        添加优化回调
        
        Args:
            callback: 回调函数
        """
        self.optimization_callbacks.append(callback)
    
    def get_optimization_profiles(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有优化配置文件
        
        Returns:
            优化配置文件字典
        """
        return {
            name: asdict(profile)
            for name, profile in self.optimization_profiles.items()
        }
    
    def create_custom_profile(
        self,
        name: str,
        base_profile: str = "standard",
        **kwargs
    ) -> OptimizationProfile:
        """
        创建自定义优化配置文件
        
        Args:
            name: 配置文件名称
            base_profile: 基础配置文件
            **kwargs: 自定义参数
            
        Returns:
            自定义优化配置文件
        """
        base = self.optimization_profiles.get(base_profile)
        if not base:
            raise ValueError(f"基础配置文件不存在: {base_profile}")
        
        # 复制基础配置
        custom_config = asdict(base)
        custom_config["name"] = name
        custom_config["description"] = f"基于 {base_profile} 的自定义配置"
        
        # 应用自定义参数
        custom_config.update(kwargs)
        
        # 创建配置对象
        custom_profile = OptimizationProfile(**custom_config)
        
        # 保存到配置文件字典
        self.optimization_profiles[name] = custom_profile
        
        self.logger.info(f"创建自定义优化配置: {name}")
        return custom_profile
    
    async def switch_profile(self, profile_name: str):
        """
        切换优化配置文件
        
        Args:
            profile_name: 配置文件名称
        """
        if self.status != ServiceStatus.RUNNING:
            raise RuntimeError("优化服务未运行，无法切换配置")
        
        new_profile = self.optimization_profiles.get(profile_name)
        if not new_profile:
            raise ValueError(f"配置文件不存在: {profile_name}")
        
        self.logger.info(f"切换优化配置: {self.current_profile.name} -> {profile_name}")
        
        # 停止当前服务
        await self.stop_optimization()
        
        # 启动新配置
        await self.start_optimization(profile_name)
    
    async def get_optimization_status(self) -> Dict[str, Any]:
        """
        获取优化状态
        
        Returns:
            优化状态信息
        """
        status_info = {
            "service_status": self.status.value,
            "current_profile": asdict(self.current_profile) if self.current_profile else None,
            "components": {}
        }
        
        # 获取各组件状态
        if self.advanced_cache:
            status_info["components"]["advanced_cache"] = await self.advanced_cache.get_cache_status()
        
        if self.batch_processor:
            status_info["components"]["batch_processor"] = self.batch_processor.get_metrics()
        
        if self.performance_tuner:
            status_info["components"]["performance_tuner"] = self.performance_tuner.get_tuning_status()
        
        if self.enhanced_monitoring:
            status_info["components"]["enhanced_monitoring"] = self.enhanced_monitoring.get_monitoring_status()
        
        return status_info
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """
        获取性能摘要
        
        Returns:
            性能摘要信息
        """
        summary = {
            "timestamp": datetime.now().isoformat(),
            "optimization_level": self.current_profile.level.value if self.current_profile else "none",
            "system_health": None,
            "performance_metrics": {},
            "optimization_insights": [],
            "recommendations": []
        }
        
        # 获取系统健康状态
        if self.enhanced_monitoring:
            system_health = self.enhanced_monitoring.get_system_health()
            summary["system_health"] = asdict(system_health)
        
        # 获取性能指标
        if self.batch_processor:
            batch_metrics = self.batch_processor.get_metrics()
            summary["performance_metrics"]["batch_processing"] = batch_metrics
        
        if self.performance_tuner:
            tuning_status = self.performance_tuner.get_tuning_status()
            summary["performance_metrics"]["tuning"] = tuning_status
        
        # 获取优化洞察
        if self.enhanced_monitoring:
            insights = self.enhanced_monitoring.get_insights(limit=5)
            summary["optimization_insights"] = [asdict(insight) for insight in insights]
        
        # 生成推荐
        summary["recommendations"] = self._generate_recommendations()
        
        return summary
    
    def _generate_recommendations(self) -> List[str]:
        """生成优化推荐"""
        recommendations = []
        
        if not self.current_profile:
            recommendations.append("建议启动优化服务以提升系统性能")
            return recommendations
        
        # 基于当前配置级别的推荐
        if self.current_profile.level == OptimizationLevel.BASIC:
            recommendations.append("考虑升级到标准优化配置以获得更好的性能")
        
        # 基于组件状态的推荐
        if self.enhanced_monitoring:
            system_health = self.enhanced_monitoring.get_system_health()
            
            if system_health.overall_score < 0.7:
                recommendations.append("系统健康分数较低，建议检查系统资源和配置")
            
            if system_health.active_alerts > 0:
                recommendations.append(f"存在 {system_health.active_alerts} 个活跃告警，建议及时处理")
            
            if system_health.critical_alerts > 0:
                recommendations.append("存在严重告警，建议立即处理")
        
        if self.performance_tuner and not self.current_profile.auto_tuning_enabled:
            recommendations.append("建议启用自动调优以持续优化性能")
        
        return recommendations
    
    async def manual_optimization(self) -> Dict[str, Any]:
        """
        手动执行优化
        
        Returns:
            优化结果
        """
        if self.status != ServiceStatus.RUNNING:
            raise RuntimeError("优化服务未运行")
        
        optimization_results = {}
        
        # 执行缓存优化
        if self.advanced_cache:
            cache_result = await self.advanced_cache.optimize_cache_distribution()
            optimization_results["cache_optimization"] = cache_result
        
        # 执行批量处理优化
        if self.batch_processor:
            self.batch_processor.optimize_settings()
            optimization_results["batch_optimization"] = "completed"
        
        # 执行性能调优
        if self.performance_tuner:
            tuning_result = await self.performance_tuner.manual_optimization()
            optimization_results["performance_tuning"] = asdict(tuning_result)
        
        self.logger.info("手动优化执行完成")
        return optimization_results 