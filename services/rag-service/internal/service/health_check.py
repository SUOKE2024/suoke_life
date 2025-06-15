#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
健康检查服务，用于检查服务依赖组件的状态
"""

import asyncio
import time
from typing import Dict, Optional, List, Tuple, Any
from enum import Enum
import logging
import json

import aiohttp
from redis.asyncio import Redis
import qdrant_client

from services.rag_service.internal.observability.telemetry import trace_method


class HealthStatus(Enum):
    """健康状态枚举"""
    UP = "up"  # 组件健康
    DOWN = "down"  # 组件不健康
    DEGRADED = "degraded"  # 组件部分功能可用
    UNKNOWN = "unknown"  # 组件状态未知


class ComponentType(Enum):
    """组件类型枚举"""
    DATABASE = "database"  # 数据库
    CACHE = "cache"  # 缓存
    API = "api"  # 外部API
    SERVICE = "service"  # 内部服务


class HealthCheckComponent:
    """健康检查组件基类"""
    
    def __init__(self, name: str, component_type: ComponentType):
        """
        初始化健康检查组件
        
        Args:
            name: 组件名称
            component_type: 组件类型
        """
        self.name = name
        self.type = component_type
        self.last_check_time = 0
        self.last_status = HealthStatus.UNKNOWN
        self.status_details = {}
    
    async def check(self) -> Tuple[HealthStatus, Dict[str, Any]]:
        """
        检查组件健康状态
        
        Returns:
            Tuple[HealthStatus, Dict]: 健康状态和详细信息
        """
        raise NotImplementedError("子类必须实现此方法")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典表示
        
        Returns:
            Dict: 组件健康状态字典
        """
        return {
            "name": self.name,
            "type": self.type.value,
            "status": self.last_status.value,
            "lastCheckTime": self.last_check_time,
            "details": self.status_details
        }


class VectorDBHealthCheck(HealthCheckComponent):
    """向量数据库健康检查组件"""
    
    def __init__(self, client: qdrant_client.QdrantClient, collection_name: str):
        """
        初始化向量数据库健康检查组件
        
        Args:
            client: Qdrant客户端
            collection_name: 集合名称
        """
        super().__init__("vector_database", ComponentType.DATABASE)
        self.client = client
        self.collection_name = collection_name
    
    @trace_method("vector_db_health_check")
    async def check(self) -> Tuple[HealthStatus, Dict[str, Any]]:
        """
        检查向量数据库健康状态
        
        Returns:
            Tuple[HealthStatus, Dict]: 健康状态和详细信息
        """
        self.last_check_time = time.time()
        details = {
            "collection": self.collection_name
        }
        
        try:
            # 检查连接状态
            collections = self.client.get_collections()
            
            # 检查集合是否存在
            collection_exists = False
            for collection in collections.collections:
                if collection.name == self.collection_name:
                    collection_exists = True
                    break
            
            if not collection_exists:
                self.last_status = HealthStatus.DEGRADED
                details["error"] = f"Collection {self.collection_name} not found"
                details["collections"] = [c.name for c in collections.collections]
            else:
                # 检查集合状态
                collection_info = self.client.get_collection(self.collection_name)
                details["vectors_count"] = collection_info.vectors_count
                details["status"] = "available"
                self.last_status = HealthStatus.UP
        except Exception as e:
            self.last_status = HealthStatus.DOWN
            details["error"] = str(e)
        
        self.status_details = details
        return self.last_status, details


class RedisHealthCheck(HealthCheckComponent):
    """Redis健康检查组件"""
    
    def __init__(self, redis_client: Redis):
        """
        初始化Redis健康检查组件
        
        Args:
            redis_client: Redis客户端
        """
        super().__init__("redis_cache", ComponentType.CACHE)
        self.redis_client = redis_client
    
    @trace_method("redis_health_check")
    async def check(self) -> Tuple[HealthStatus, Dict[str, Any]]:
        """
        检查Redis健康状态
        
        Returns:
            Tuple[HealthStatus, Dict]: 健康状态和详细信息
        """
        self.last_check_time = time.time()
        details = {}
        
        try:
            # 检查连接状态
            ping_result = await self.redis_client.ping()
            
            if ping_result:
                # 获取更多信息
                info = await self.redis_client.info()
                details["version"] = info.get("redis_version", "unknown")
                details["memory_used"] = info.get("used_memory_human", "unknown")
                details["clients_connected"] = info.get("connected_clients", "unknown")
                self.last_status = HealthStatus.UP
            else:
                self.last_status = HealthStatus.DOWN
                details["error"] = "Redis ping failed"
        except Exception as e:
            self.last_status = HealthStatus.DOWN
            details["error"] = str(e)
        
        self.status_details = details
        return self.last_status, details


class OpenAIHealthCheck(HealthCheckComponent):
    """OpenAI API健康检查组件"""
    
    def __init__(self, api_key: str, timeout: int = 5):
        """
        初始化OpenAI API健康检查组件
        
        Args:
            api_key: OpenAI API密钥
            timeout: 请求超时时间，单位秒
        """
        super().__init__("openai_api", ComponentType.API)
        self.api_key = api_key
        self.timeout = timeout
    
    @trace_method("openai_health_check")
    async def check(self) -> Tuple[HealthStatus, Dict[str, Any]]:
        """
        检查OpenAI API健康状态
        
        Returns:
            Tuple[HealthStatus, Dict]: 健康状态和详细信息
        """
        self.last_check_time = time.time()
        details = {}
        
        url = "https://api.openai.com/v1/models"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=self.timeout) as response:
                    if response.status == 200:
                        # 提取可用模型信息
                        data = await response.json()
                        available_models = [model["id"] for model in data["data"] if "gpt-4" in model["id"] or "gpt-3.5" in model["id"]]
                        details["available_models"] = available_models
                        details["total_models"] = len(data["data"])
                        self.last_status = HealthStatus.UP
                    else:
                        error_data = await response.text()
                        self.last_status = HealthStatus.DOWN
                        details["error"] = f"API返回错误: {response.status} - {error_data}"
        except asyncio.TimeoutError:
            self.last_status = HealthStatus.DOWN
            details["error"] = f"请求超时 (>{self.timeout}s)"
        except Exception as e:
            self.last_status = HealthStatus.DOWN
            details["error"] = str(e)
        
        self.status_details = details
        return self.last_status, details


class HealthCheckService:
    """健康检查服务"""
    
    def __init__(self):
        """初始化健康检查服务"""
        self.components: List[HealthCheckComponent] = []
        self.logger = logging.getLogger(__name__)
    
    def add_component(self, component: HealthCheckComponent) -> None:
        """
        添加健康检查组件
        
        Args:
            component: 健康检查组件
        """
        self.components.append(component)
    
    @trace_method("health_check")
    async def check_health(self) -> Dict[str, Any]:
        """
        检查所有组件健康状态
        
        Returns:
            Dict: 健康状态报告
        """
        overall_status = HealthStatus.UP
        components_status = []
        
        for component in self.components:
            try:
                status, _ = await component.check()
                components_status.append(component.to_dict())
                
                # 更新整体状态
                if status == HealthStatus.DOWN:
                    overall_status = HealthStatus.DOWN
                elif status == HealthStatus.DEGRADED and overall_status != HealthStatus.DOWN:
                    overall_status = HealthStatus.DEGRADED
            except Exception as e:
                self.logger.error(f"检查组件 {component.name} 健康状态时出错: {str(e)}")
                component.last_status = HealthStatus.UNKNOWN
                component.status_details = {"error": str(e)}
                components_status.append(component.to_dict())
        
        # 构建健康状态报告
        health_report = {
            "status": overall_status.value,
            "timestamp": time.time(),
            "components": components_status
        }
        
        return health_report 