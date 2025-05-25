#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
应用服务初始化 - 整合所有服务模块
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path

# 导入配置
from config.config import config

# 导入核心服务
from internal.service.optimized_accessibility_service import OptimizedAccessibilityService

# 导入新增服务模块
from internal.service.edge_computing import EdgeComputingService
from internal.service.tcm_accessibility import TCMAccessibilityService
from internal.service.dialect_service import DialectService
from internal.service.background_collection import BackgroundCollectionService
from internal.service.crisis_alert import CrisisAlertService
from internal.integration.agent_coordination import AgentCoordinationService, EventBus
from internal.observability.monitoring import MonitoringService
from internal.security.privacy_service import PrivacyService
from internal.resilience.disaster_recovery import BackupScheduler

logger = logging.getLogger(__name__)


class AccessibilityApp:
    """应用程序类 - 整合所有服务模块"""

    def __init__(self, app_config=None):
        """
        初始化应用
        
        Args:
            app_config: 应用配置，默认使用全局配置
        """
        self.config = app_config or config
        logger.info("初始化无障碍服务应用")
        
        # 初始化监控服务（最先启动以便监控其他服务）
        self.monitoring_service = self._init_monitoring_service()
        
        # 初始化安全服务
        self.privacy_service = self._init_privacy_service()
        
        # 初始化事件总线
        self.event_bus = self._init_event_bus()
        
        # 初始化智能体协作服务
        self.agent_coordination = self._init_agent_coordination()
        
        # 初始化边缘计算服务
        self.edge_computing = self._init_edge_computing()
        
        # 初始化中医无障碍服务
        self.tcm_accessibility = self._init_tcm_accessibility()
        
        # 初始化方言支持服务
        self.dialect_service = self._init_dialect_service()
        
        # 初始化后台数据采集服务
        self.background_collection = self._init_background_collection()
        
        # 初始化危机报警服务
        self.crisis_alert = self._init_crisis_alert_service()
        
        # 初始化备份服务
        self.backup_scheduler = self._init_backup_scheduler()
        
        # 初始化核心无障碍服务
        self.accessibility_service = self._init_accessibility_service()
        
        logger.info("所有服务模块初始化完成")
        
    def _init_monitoring_service(self) -> MonitoringService:
        """初始化监控服务"""
        logger.info("初始化监控服务")
        service = MonitoringService(self.config)
        service.setup()
        return service
        
    def _init_privacy_service(self) -> PrivacyService:
        """初始化隐私服务"""
        logger.info("初始化隐私服务")
        return PrivacyService(self.config)
        
    def _init_event_bus(self) -> EventBus:
        """初始化事件总线"""
        logger.info("初始化事件总线")
        return EventBus(self.config)
        
    def _init_agent_coordination(self) -> AgentCoordinationService:
        """初始化智能体协作服务"""
        logger.info("初始化智能体协作服务")
        service = AgentCoordinationService(self.config, self.event_bus)
        service.register_capabilities()
        service.publish_capability_updates()
        return service
        
    def _init_edge_computing(self) -> EdgeComputingService:
        """初始化边缘计算服务"""
        logger.info("初始化边缘计算服务")
        return EdgeComputingService(self.config)
        
    def _init_tcm_accessibility(self) -> TCMAccessibilityService:
        """初始化中医无障碍服务"""
        logger.info("初始化中医无障碍服务")
        return TCMAccessibilityService(self.config)
        
    def _init_dialect_service(self) -> DialectService:
        """初始化方言支持服务"""
        logger.info("初始化方言支持服务")
        return DialectService(self.config)
    
    def _init_background_collection(self) -> BackgroundCollectionService:
        """初始化后台数据采集服务"""
        logger.info("初始化后台数据采集服务")
        service = BackgroundCollectionService(self.config)
        
        # 注入依赖服务
        service.privacy_service = self.privacy_service
        service.monitoring_service = self.monitoring_service
        
        # 设置加密
        service.setup_encryption()
        
        return service
    
    def _init_crisis_alert_service(self) -> CrisisAlertService:
        """初始化危机报警服务"""
        logger.info("初始化危机报警服务")
        service = CrisisAlertService(self.config)
        
        # 注入依赖服务
        service.monitoring_service = self.monitoring_service
        service.background_collection_service = self.background_collection
        service.agent_coordination = self.agent_coordination
        
        # 同时设置后台采集服务的危机报警引用
        self.background_collection.set_crisis_alert_service(service)
        
        return service
        
    def _init_backup_scheduler(self) -> BackupScheduler:
        """初始化备份调度器"""
        logger.info("初始化备份调度器")
        scheduler = BackupScheduler(self.config)
        
        if self.config.resilience.backup.enabled:
            logger.info("启动备份调度器")
            scheduler.start()
            
        return scheduler
        
    def _init_accessibility_service(self) -> OptimizedAccessibilityService:
        """
        初始化无障碍服务
        
        Returns:
            OptimizedAccessibilityService: 无障碍服务实例
        """
        try:
            logger.info("初始化无障碍服务")
            
            # 准备配置
            config_dict = {
                "features": self.config.get("features", {}),
                "models": self.config.get("models", {}),
                "performance": self.config.get("performance", {}),
                "cache": self.config.get("cache", {}),
                "security": self.config.get("security", {})
            }
            
            # 创建服务实例
            service = OptimizedAccessibilityService(config_dict)
            
            # 注入服务依赖
            service.edge_computing_service = self.edge_computing
            service.tcm_accessibility_service = self.tcm_accessibility
            service.dialect_service = self.dialect_service
            service.agent_coordination = self.agent_coordination
            service.privacy_service = self.privacy_service
            service.background_collection_service = self.background_collection
            service.crisis_alert_service = self.crisis_alert
            
            return service
        except Exception as e:
            logger.error(f"初始化无障碍服务失败: {str(e)}")
            return None
        
    def start(self):
        """启动应用服务"""
        logger.info("启动无障碍服务应用")
        
        # 启动后台数据采集服务
        try:
            if self.background_collection and hasattr(self.config, 'background_collection') and \
               hasattr(self.config.background_collection, 'enabled') and self.config.background_collection.enabled:
                logger.info("启动后台数据采集服务")
                self.background_collection.start()
        except AttributeError as e:
            logger.warning(f"未能启动后台数据采集服务: {str(e)}")
            
        # 启动危机报警服务
        try:
            if self.crisis_alert and hasattr(self.config, 'crisis_alert') and \
               hasattr(self.config.crisis_alert, 'enabled') and self.config.crisis_alert.enabled:
                logger.info("启动危机报警服务")
                self.crisis_alert.start()
        except AttributeError as e:
            logger.warning(f"未能启动危机报警服务: {str(e)}")
        
        # 记录应用启动指标
        if self.monitoring_service and hasattr(self.monitoring_service, 'metrics_client'):
            self.monitoring_service.metrics_client.counter("accessibility_app_start", 1)
        
    def stop(self):
        """停止应用服务"""
        logger.info("停止无障碍服务应用")
        
        # 停止危机报警服务
        if self.crisis_alert:
            logger.info("停止危机报警服务")
            self.crisis_alert.stop()
        
        # 停止后台数据采集服务
        if self.background_collection:
            logger.info("停止后台数据采集服务")
            self.background_collection.stop()
        
        # 停止备份调度器
        if self.backup_scheduler:
            logger.info("停止备份调度器")
            self.backup_scheduler.stop()
            
        # 记录应用停止指标
        if self.monitoring_service and hasattr(self.monitoring_service, 'metrics_client'):
            self.monitoring_service.metrics_client.counter("accessibility_app_stop", 1) 