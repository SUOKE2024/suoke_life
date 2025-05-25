#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能模型管理器 - 支持模型版本控制、热更新、A/B测试等功能
"""

import asyncio
import time
import json
import hashlib
import os
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import pickle
import threading
from loguru import logger

from ..observability.metrics import MetricsCollector
from ..observability.tracing import trace_operation, SpanKind
from .ab_testing import ABTestingFramework, Experiment


class ModelType(str, Enum):
    """模型类型"""
    EMBEDDING = "embedding"                 # 嵌入模型
    GENERATION = "generation"               # 生成模型
    RETRIEVAL = "retrieval"                 # 检索模型
    CLASSIFICATION = "classification"       # 分类模型
    RANKING = "ranking"                     # 排序模型
    TCM_SYNDROME = "tcm_syndrome"          # 中医辨证模型
    TCM_HERB = "tcm_herb"                  # 中药推荐模型
    MULTIMODAL = "multimodal"              # 多模态模型


class ModelStatus(str, Enum):
    """模型状态"""
    LOADING = "loading"                     # 加载中
    READY = "ready"                         # 就绪
    UPDATING = "updating"                   # 更新中
    ERROR = "error"                         # 错误
    DEPRECATED = "deprecated"               # 已弃用
    ARCHIVED = "archived"                   # 已归档


class DeploymentStrategy(str, Enum):
    """部署策略"""
    BLUE_GREEN = "blue_green"               # 蓝绿部署
    CANARY = "canary"                       # 金丝雀部署
    ROLLING = "rolling"                     # 滚动部署
    IMMEDIATE = "immediate"                 # 立即部署
    SCHEDULED = "scheduled"                 # 定时部署


@dataclass
class ModelMetadata:
    """模型元数据"""
    name: str
    version: str
    type: ModelType
    description: str = ""
    author: str = ""
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    size_bytes: int = 0
    checksum: str = ""
    tags: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "version": self.version,
            "type": self.type.value,
            "description": self.description,
            "author": self.author,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "size_bytes": self.size_bytes,
            "checksum": self.checksum,
            "tags": self.tags,
            "config": self.config,
            "performance_metrics": self.performance_metrics,
            "dependencies": self.dependencies
        }


@dataclass
class ModelInstance:
    """模型实例"""
    metadata: ModelMetadata
    model_object: Any
    status: ModelStatus = ModelStatus.LOADING
    load_time: float = 0.0
    memory_usage: int = 0
    last_used: float = field(default_factory=time.time)
    usage_count: int = 0
    error_count: int = 0
    
    def update_usage(self):
        """更新使用统计"""
        self.last_used = time.time()
        self.usage_count += 1
    
    def record_error(self):
        """记录错误"""
        self.error_count += 1


@dataclass
class DeploymentPlan:
    """部署计划"""
    model_name: str
    old_version: Optional[str]
    new_version: str
    strategy: DeploymentStrategy
    traffic_split: Dict[str, float] = field(default_factory=dict)  # 版本 -> 流量比例
    rollback_threshold: float = 0.1  # 错误率阈值
    max_duration: int = 3600  # 最大部署时间（秒）
    health_check_interval: int = 30  # 健康检查间隔（秒）
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "model_name": self.model_name,
            "old_version": self.old_version,
            "new_version": self.new_version,
            "strategy": self.strategy.value,
            "traffic_split": self.traffic_split,
            "rollback_threshold": self.rollback_threshold,
            "max_duration": self.max_duration,
            "health_check_interval": self.health_check_interval
        }


class ModelLoader:
    """模型加载器"""
    
    def __init__(self):
        self.loaders: Dict[ModelType, Callable] = {}
    
    def register_loader(self, model_type: ModelType, loader_func: Callable):
        """注册模型加载器"""
        self.loaders[model_type] = loader_func
        logger.info(f"注册模型加载器: {model_type.value}")
    
    async def load_model(self, metadata: ModelMetadata, model_path: str) -> Any:
        """加载模型"""
        if metadata.type not in self.loaders:
            raise ValueError(f"不支持的模型类型: {metadata.type}")
        
        loader_func = self.loaders[metadata.type]
        
        # 在线程池中加载模型（避免阻塞）
        loop = asyncio.get_event_loop()
        model_object = await loop.run_in_executor(
            None, loader_func, model_path, metadata.config
        )
        
        return model_object


class ModelRegistry:
    """模型注册表"""
    
    def __init__(self, registry_path: str = "models/registry.json"):
        self.registry_path = Path(registry_path)
        self.models: Dict[str, Dict[str, ModelMetadata]] = {}  # name -> version -> metadata
        self._lock = threading.RLock()
        self._load_registry()
    
    def _load_registry(self):
        """加载注册表"""
        if self.registry_path.exists():
            try:
                with open(self.registry_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for name, versions in data.items():
                    self.models[name] = {}
                    for version, metadata_dict in versions.items():
                        metadata = ModelMetadata(**metadata_dict)
                        metadata.type = ModelType(metadata_dict['type'])
                        self.models[name][version] = metadata
                
                logger.info(f"加载模型注册表: {len(self.models)} 个模型")
                
            except Exception as e:
                logger.error(f"加载模型注册表失败: {e}")
                self.models = {}
    
    def _save_registry(self):
        """保存注册表"""
        try:
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {}
            for name, versions in self.models.items():
                data[name] = {}
                for version, metadata in versions.items():
                    data[name][version] = metadata.to_dict()
            
            with open(self.registry_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"保存模型注册表失败: {e}")
    
    def register_model(self, metadata: ModelMetadata) -> bool:
        """注册模型"""
        with self._lock:
            if metadata.name not in self.models:
                self.models[metadata.name] = {}
            
            self.models[metadata.name][metadata.version] = metadata
            self._save_registry()
            
            logger.info(f"注册模型: {metadata.name}:{metadata.version}")
            return True
    
    def get_model_metadata(self, name: str, version: Optional[str] = None) -> Optional[ModelMetadata]:
        """获取模型元数据"""
        with self._lock:
            if name not in self.models:
                return None
            
            if version is None:
                # 返回最新版本
                versions = list(self.models[name].keys())
                if not versions:
                    return None
                version = max(versions)  # 假设版本号可以直接比较
            
            return self.models[name].get(version)
    
    def list_models(self, model_type: Optional[ModelType] = None) -> List[ModelMetadata]:
        """列出模型"""
        with self._lock:
            result = []
            for name, versions in self.models.items():
                for version, metadata in versions.items():
                    if model_type is None or metadata.type == model_type:
                        result.append(metadata)
            return result
    
    def get_model_versions(self, name: str) -> List[str]:
        """获取模型版本列表"""
        with self._lock:
            if name not in self.models:
                return []
            return list(self.models[name].keys())
    
    def delete_model(self, name: str, version: Optional[str] = None) -> bool:
        """删除模型"""
        with self._lock:
            if name not in self.models:
                return False
            
            if version is None:
                # 删除所有版本
                del self.models[name]
            else:
                if version in self.models[name]:
                    del self.models[name][version]
                    if not self.models[name]:
                        del self.models[name]
                else:
                    return False
            
            self._save_registry()
            logger.info(f"删除模型: {name}:{version or 'all'}")
            return True


class ModelManager:
    """模型管理器"""
    
    def __init__(
        self,
        model_storage_path: str = "models",
        metrics_collector: Optional[MetricsCollector] = None,
        ab_testing: Optional[ABTestingFramework] = None
    ):
        self.model_storage_path = Path(model_storage_path)
        self.metrics_collector = metrics_collector
        self.ab_testing = ab_testing
        
        # 组件
        self.registry = ModelRegistry(self.model_storage_path / "registry.json")
        self.loader = ModelLoader()
        
        # 运行时状态
        self.loaded_models: Dict[str, Dict[str, ModelInstance]] = {}  # name -> version -> instance
        self.active_deployments: Dict[str, DeploymentPlan] = {}  # model_name -> plan
        self.traffic_routing: Dict[str, Dict[str, float]] = {}  # model_name -> version -> weight
        
        # 锁
        self._lock = asyncio.Lock()
        
        # 后台任务
        self._health_check_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # 配置
        self.max_loaded_models = 10  # 最大加载模型数
        self.model_ttl = 3600  # 模型TTL（秒）
        self.health_check_interval = 60  # 健康检查间隔（秒）
    
    async def start(self):
        """启动模型管理器"""
        # 启动后台任务
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("模型管理器已启动")
    
    async def stop(self):
        """停止模型管理器"""
        # 停止后台任务
        if self._health_check_task:
            self._health_check_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        # 卸载所有模型
        await self.unload_all_models()
        
        logger.info("模型管理器已停止")
    
    def register_loader(self, model_type: ModelType, loader_func: Callable):
        """注册模型加载器"""
        self.loader.register_loader(model_type, loader_func)
    
    async def register_model(
        self,
        name: str,
        version: str,
        model_type: ModelType,
        model_path: str,
        description: str = "",
        config: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """注册模型"""
        try:
            # 计算文件校验和
            model_file_path = self.model_storage_path / model_path
            if not model_file_path.exists():
                logger.error(f"模型文件不存在: {model_file_path}")
                return False
            
            checksum = await self._calculate_checksum(model_file_path)
            size_bytes = model_file_path.stat().st_size
            
            # 创建元数据
            metadata = ModelMetadata(
                name=name,
                version=version,
                type=model_type,
                description=description,
                size_bytes=size_bytes,
                checksum=checksum,
                config=config or {},
                tags=tags or []
            )
            
            # 注册到注册表
            success = self.registry.register_model(metadata)
            
            if success and self.metrics_collector:
                await self.metrics_collector.increment_counter(
                    "models_registered",
                    {"name": name, "type": model_type.value}
                )
            
            return success
            
        except Exception as e:
            logger.error(f"注册模型失败: {e}")
            return False
    
    @trace_operation("model.load", SpanKind.INTERNAL)
    async def load_model(self, name: str, version: Optional[str] = None) -> bool:
        """加载模型"""
        async with self._lock:
            try:
                # 获取模型元数据
                metadata = self.registry.get_model_metadata(name, version)
                if not metadata:
                    logger.error(f"模型不存在: {name}:{version}")
                    return False
                
                # 检查是否已加载
                if (name in self.loaded_models and 
                    metadata.version in self.loaded_models[name]):
                    logger.info(f"模型已加载: {name}:{metadata.version}")
                    return True
                
                # 检查加载数量限制
                total_loaded = sum(len(versions) for versions in self.loaded_models.values())
                if total_loaded >= self.max_loaded_models:
                    await self._evict_least_used_model()
                
                # 构建模型路径
                model_path = self.model_storage_path / f"{name}/{metadata.version}"
                
                # 创建模型实例
                instance = ModelInstance(
                    metadata=metadata,
                    model_object=None,
                    status=ModelStatus.LOADING
                )
                
                # 添加到加载列表
                if name not in self.loaded_models:
                    self.loaded_models[name] = {}
                self.loaded_models[name][metadata.version] = instance
                
                # 加载模型
                start_time = time.time()
                model_object = await self.loader.load_model(metadata, str(model_path))
                load_time = time.time() - start_time
                
                # 更新实例
                instance.model_object = model_object
                instance.status = ModelStatus.READY
                instance.load_time = load_time
                
                # 记录指标
                if self.metrics_collector:
                    await self.metrics_collector.increment_counter(
                        "models_loaded",
                        {"name": name, "version": metadata.version, "type": metadata.type.value}
                    )
                    await self.metrics_collector.record_histogram(
                        "model_load_duration",
                        load_time,
                        {"name": name, "type": metadata.type.value}
                    )
                
                logger.info(f"模型加载成功: {name}:{metadata.version} ({load_time:.2f}s)")
                return True
                
            except Exception as e:
                logger.error(f"加载模型失败: {e}")
                
                # 更新状态
                if (name in self.loaded_models and 
                    metadata.version in self.loaded_models[name]):
                    self.loaded_models[name][metadata.version].status = ModelStatus.ERROR
                
                return False
    
    async def unload_model(self, name: str, version: Optional[str] = None) -> bool:
        """卸载模型"""
        async with self._lock:
            try:
                if name not in self.loaded_models:
                    return False
                
                if version is None:
                    # 卸载所有版本
                    for ver in list(self.loaded_models[name].keys()):
                        await self._unload_model_version(name, ver)
                    del self.loaded_models[name]
                else:
                    if version not in self.loaded_models[name]:
                        return False
                    await self._unload_model_version(name, version)
                    del self.loaded_models[name][version]
                    
                    if not self.loaded_models[name]:
                        del self.loaded_models[name]
                
                logger.info(f"模型卸载成功: {name}:{version or 'all'}")
                return True
                
            except Exception as e:
                logger.error(f"卸载模型失败: {e}")
                return False
    
    async def _unload_model_version(self, name: str, version: str):
        """卸载特定版本的模型"""
        instance = self.loaded_models[name][version]
        
        # 清理模型对象
        if hasattr(instance.model_object, 'cleanup'):
            try:
                await instance.model_object.cleanup()
            except:
                pass
        
        instance.model_object = None
        instance.status = ModelStatus.ARCHIVED
        
        # 记录指标
        if self.metrics_collector:
            await self.metrics_collector.increment_counter(
                "models_unloaded",
                {"name": name, "version": version}
            )
    
    async def unload_all_models(self):
        """卸载所有模型"""
        async with self._lock:
            for name in list(self.loaded_models.keys()):
                await self.unload_model(name)
    
    async def get_model(self, name: str, version: Optional[str] = None) -> Optional[Any]:
        """获取模型对象"""
        async with self._lock:
            if name not in self.loaded_models:
                # 尝试自动加载
                if await self.load_model(name, version):
                    pass  # 继续获取
                else:
                    return None
            
            # 确定版本
            if version is None:
                # 使用流量路由确定版本
                if name in self.traffic_routing:
                    version = self._select_version_by_traffic(name)
                else:
                    # 使用最新版本
                    versions = list(self.loaded_models[name].keys())
                    if not versions:
                        return None
                    version = max(versions)
            
            if version not in self.loaded_models[name]:
                return None
            
            instance = self.loaded_models[name][version]
            if instance.status != ModelStatus.READY:
                return None
            
            # 更新使用统计
            instance.update_usage()
            
            # 记录指标
            if self.metrics_collector:
                await self.metrics_collector.increment_counter(
                    "model_requests",
                    {"name": name, "version": version}
                )
            
            return instance.model_object
    
    def _select_version_by_traffic(self, name: str) -> str:
        """根据流量权重选择版本"""
        import random
        
        weights = self.traffic_routing[name]
        versions = list(weights.keys())
        probabilities = list(weights.values())
        
        return random.choices(versions, weights=probabilities)[0]
    
    async def deploy_model(self, plan: DeploymentPlan) -> bool:
        """部署模型"""
        try:
            # 检查新版本是否存在
            new_metadata = self.registry.get_model_metadata(plan.model_name, plan.new_version)
            if not new_metadata:
                logger.error(f"新版本不存在: {plan.model_name}:{plan.new_version}")
                return False
            
            # 记录部署计划
            self.active_deployments[plan.model_name] = plan
            
            # 根据策略执行部署
            if plan.strategy == DeploymentStrategy.BLUE_GREEN:
                success = await self._deploy_blue_green(plan)
            elif plan.strategy == DeploymentStrategy.CANARY:
                success = await self._deploy_canary(plan)
            elif plan.strategy == DeploymentStrategy.ROLLING:
                success = await self._deploy_rolling(plan)
            elif plan.strategy == DeploymentStrategy.IMMEDIATE:
                success = await self._deploy_immediate(plan)
            else:
                logger.error(f"不支持的部署策略: {plan.strategy}")
                success = False
            
            # 清理部署记录
            if plan.model_name in self.active_deployments:
                del self.active_deployments[plan.model_name]
            
            # 记录指标
            if self.metrics_collector:
                await self.metrics_collector.increment_counter(
                    "model_deployments",
                    {
                        "name": plan.model_name,
                        "strategy": plan.strategy.value,
                        "success": str(success)
                    }
                )
            
            return success
            
        except Exception as e:
            logger.error(f"部署模型失败: {e}")
            return False
    
    async def _deploy_blue_green(self, plan: DeploymentPlan) -> bool:
        """蓝绿部署"""
        # 加载新版本（绿色环境）
        if not await self.load_model(plan.model_name, plan.new_version):
            return False
        
        # 切换流量到新版本
        self.traffic_routing[plan.model_name] = {plan.new_version: 1.0}
        
        # 等待一段时间观察
        await asyncio.sleep(30)
        
        # 检查健康状态
        if await self._check_model_health(plan.model_name, plan.new_version):
            # 卸载旧版本
            if plan.old_version:
                await self.unload_model(plan.model_name, plan.old_version)
            logger.info(f"蓝绿部署成功: {plan.model_name}:{plan.new_version}")
            return True
        else:
            # 回滚
            await self._rollback_deployment(plan)
            return False
    
    async def _deploy_canary(self, plan: DeploymentPlan) -> bool:
        """金丝雀部署"""
        # 加载新版本
        if not await self.load_model(plan.model_name, plan.new_version):
            return False
        
        # 逐步增加新版本流量
        traffic_steps = [0.05, 0.1, 0.25, 0.5, 1.0]  # 5%, 10%, 25%, 50%, 100%
        
        for target_traffic in traffic_steps:
            # 更新流量分配
            if plan.old_version:
                self.traffic_routing[plan.model_name] = {
                    plan.old_version: 1.0 - target_traffic,
                    plan.new_version: target_traffic
                }
            else:
                self.traffic_routing[plan.model_name] = {plan.new_version: 1.0}
            
            # 等待观察
            await asyncio.sleep(60)
            
            # 检查健康状态
            if not await self._check_model_health(plan.model_name, plan.new_version):
                await self._rollback_deployment(plan)
                return False
            
            logger.info(f"金丝雀部署进度: {plan.model_name} -> {target_traffic*100:.0f}%")
        
        # 卸载旧版本
        if plan.old_version:
            await self.unload_model(plan.model_name, plan.old_version)
        
        logger.info(f"金丝雀部署成功: {plan.model_name}:{plan.new_version}")
        return True
    
    async def _deploy_rolling(self, plan: DeploymentPlan) -> bool:
        """滚动部署"""
        # 简化实现：类似于金丝雀部署
        return await self._deploy_canary(plan)
    
    async def _deploy_immediate(self, plan: DeploymentPlan) -> bool:
        """立即部署"""
        # 加载新版本
        if not await self.load_model(plan.model_name, plan.new_version):
            return False
        
        # 立即切换流量
        self.traffic_routing[plan.model_name] = {plan.new_version: 1.0}
        
        # 卸载旧版本
        if plan.old_version:
            await self.unload_model(plan.model_name, plan.old_version)
        
        logger.info(f"立即部署成功: {plan.model_name}:{plan.new_version}")
        return True
    
    async def _check_model_health(self, name: str, version: str) -> bool:
        """检查模型健康状态"""
        if name not in self.loaded_models or version not in self.loaded_models[name]:
            return False
        
        instance = self.loaded_models[name][version]
        
        # 检查状态
        if instance.status != ModelStatus.READY:
            return False
        
        # 检查错误率
        if instance.usage_count > 0:
            error_rate = instance.error_count / instance.usage_count
            if error_rate > 0.1:  # 10%错误率阈值
                return False
        
        # 可以添加更多健康检查逻辑
        return True
    
    async def _rollback_deployment(self, plan: DeploymentPlan):
        """回滚部署"""
        logger.warning(f"回滚部署: {plan.model_name}")
        
        if plan.old_version:
            # 恢复旧版本流量
            self.traffic_routing[plan.model_name] = {plan.old_version: 1.0}
            # 卸载新版本
            await self.unload_model(plan.model_name, plan.new_version)
        else:
            # 没有旧版本，卸载新版本
            await self.unload_model(plan.model_name, plan.new_version)
            if plan.model_name in self.traffic_routing:
                del self.traffic_routing[plan.model_name]
    
    async def _evict_least_used_model(self):
        """驱逐最少使用的模型"""
        min_usage = float('inf')
        target_name = None
        target_version = None
        
        for name, versions in self.loaded_models.items():
            for version, instance in versions.items():
                if instance.usage_count < min_usage:
                    min_usage = instance.usage_count
                    target_name = name
                    target_version = version
        
        if target_name and target_version:
            await self.unload_model(target_name, target_version)
            logger.info(f"驱逐最少使用模型: {target_name}:{target_version}")
    
    async def _health_check_loop(self):
        """健康检查循环"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                
                # 检查所有加载的模型
                for name, versions in self.loaded_models.items():
                    for version, instance in versions.items():
                        if instance.status == ModelStatus.READY:
                            healthy = await self._check_model_health(name, version)
                            if not healthy:
                                logger.warning(f"模型健康检查失败: {name}:{version}")
                                instance.status = ModelStatus.ERROR
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"健康检查错误: {e}")
    
    async def _cleanup_loop(self):
        """清理循环"""
        while True:
            try:
                await asyncio.sleep(300)  # 5分钟清理一次
                
                current_time = time.time()
                to_unload = []
                
                # 查找过期模型
                for name, versions in self.loaded_models.items():
                    for version, instance in versions.items():
                        if (current_time - instance.last_used > self.model_ttl and
                            instance.usage_count == 0):
                            to_unload.append((name, version))
                
                # 卸载过期模型
                for name, version in to_unload:
                    await self.unload_model(name, version)
                    logger.info(f"清理过期模型: {name}:{version}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"清理任务错误: {e}")
    
    async def _calculate_checksum(self, file_path: Path) -> str:
        """计算文件校验和"""
        hash_md5 = hashlib.md5()
        
        def _read_file():
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _read_file)
    
    async def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_loaded = sum(len(versions) for versions in self.loaded_models.values())
        total_registered = len(self.registry.list_models())
        
        model_stats = {}
        for name, versions in self.loaded_models.items():
            model_stats[name] = {}
            for version, instance in versions.items():
                model_stats[name][version] = {
                    "status": instance.status.value,
                    "usage_count": instance.usage_count,
                    "error_count": instance.error_count,
                    "load_time": instance.load_time,
                    "last_used": instance.last_used
                }
        
        return {
            "total_registered": total_registered,
            "total_loaded": total_loaded,
            "max_loaded_models": self.max_loaded_models,
            "active_deployments": len(self.active_deployments),
            "traffic_routing": self.traffic_routing,
            "models": model_stats
        }


# 全局模型管理器实例
_model_manager: Optional[ModelManager] = None


def initialize_model_manager(
    model_storage_path: str = "models",
    metrics_collector: Optional[MetricsCollector] = None,
    ab_testing: Optional[ABTestingFramework] = None
) -> ModelManager:
    """初始化模型管理器"""
    global _model_manager
    _model_manager = ModelManager(model_storage_path, metrics_collector, ab_testing)
    return _model_manager


def get_model_manager() -> Optional[ModelManager]:
    """获取模型管理器实例"""
    return _model_manager 