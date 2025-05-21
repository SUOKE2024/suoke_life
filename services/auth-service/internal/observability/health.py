#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
健康检查模块

按照索克生活APP微服务可观测性指南实现标准的健康检查功能。
提供三种标准健康检查端点：
1. 存活检查 (Liveness)
2. 就绪检查 (Readiness)
3. 全面健康检查
"""
import logging
import time
import psutil
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

class ComponentHealth(BaseModel):
    """组件健康状态模型"""
    status: str  # "UP" | "DOWN" | "DEGRADED"
    name: str
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class HealthStatus(BaseModel):
    """整体健康状态模型"""
    status: str  # "UP" | "DOWN" | "DEGRADED"
    version: str
    timestamp: int
    components: List[ComponentHealth]

class HealthCheck:
    """健康检查服务"""
    
    def __init__(self, app=None):
        """
        初始化健康检查服务
        
        Args:
            app: FastAPI应用实例，用于访问应用状态
        """
        self.app = app
        self.version = "1.0.0"  # 从应用配置中获取
        self.logger = logging.getLogger(__name__)
    
    async def check_database(self) -> ComponentHealth:
        """
        检查数据库连接状态
        
        Returns:
            ComponentHealth: 数据库组件健康状态
        """
        try:
            if not self.app or not hasattr(self.app.state, "db_pool"):
                return ComponentHealth(
                    name="database",
                    status="DOWN",
                    error="数据库连接未初始化"
                )
            
            # 执行简单查询验证连接
            async with self.app.state.db_pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1")
                if result != 1:
                    raise Exception("数据库查询结果异常")
                
                # 获取数据库版本信息
                db_version = await conn.fetchval("SELECT version()")
                
                return ComponentHealth(
                    name="database",
                    status="UP",
                    details={
                        "type": "postgresql",
                        "version": db_version
                    }
                )
        except Exception as e:
            self.logger.error(f"数据库健康检查失败: {str(e)}")
            return ComponentHealth(
                name="database",
                status="DOWN",
                error=str(e)
            )
    
    async def check_redis(self) -> ComponentHealth:
        """
        检查Redis连接状态
        
        Returns:
            ComponentHealth: Redis组件健康状态
        """
        try:
            if not self.app or not hasattr(self.app.state, "redis_pool"):
                return ComponentHealth(
                    name="redis",
                    status="DOWN",
                    error="Redis连接未初始化"
                )
            
            # 执行PING命令验证连接
            redis = self.app.state.redis_pool
            result = await redis.ping()
            if not result:
                raise Exception("Redis PING命令失败")
            
            # 获取Redis信息
            info = await redis.info()
            redis_version = info.get("redis_version", "未知")
            
            return ComponentHealth(
                name="redis",
                status="UP",
                details={
                    "version": redis_version,
                    "clients_connected": info.get("connected_clients", 0),
                    "used_memory_human": info.get("used_memory_human", "未知")
                }
            )
        except Exception as e:
            self.logger.error(f"Redis健康检查失败: {str(e)}")
            return ComponentHealth(
                name="redis",
                status="DOWN",
                error=str(e)
            )
    
    async def check_system_resources(self) -> ComponentHealth:
        """
        检查系统资源使用情况
        
        Returns:
            ComponentHealth: 系统资源组件健康状态
        """
        try:
            # 获取CPU、内存和磁盘使用率
            cpu_usage = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            status = "UP"
            details = {
                "cpu_usage": f"{cpu_usage}%",
                "memory_used": f"{memory.percent}%",
                "disk_used": f"{disk.percent}%"
            }
            
            # 如果资源使用率超过阈值，标记为降级状态
            if memory.percent > 90:
                status = "DEGRADED"
                details["warnings"] = ["内存使用率超过90%"]
            elif disk.percent > 90:
                status = "DEGRADED"
                details["warnings"] = ["磁盘使用率超过90%"]
            elif cpu_usage > 85:
                status = "DEGRADED"
                details["warnings"] = ["CPU使用率超过85%"]
            
            return ComponentHealth(
                name="system_resources",
                status=status,
                details=details
            )
        except Exception as e:
            self.logger.error(f"系统资源检查失败: {str(e)}")
            return ComponentHealth(
                name="system_resources",
                status="DOWN",
                error=str(e)
            )
    
    async def check_jwt_service(self) -> ComponentHealth:
        """
        检查JWT服务状态
        
        Returns:
            ComponentHealth: JWT服务组件健康状态
        """
        try:
            if not self.app or not hasattr(self.app.state, "jwt_service"):
                return ComponentHealth(
                    name="jwt_service",
                    status="DOWN",
                    error="JWT服务未初始化"
                )
            
            # 检查JWT服务是否正常
            jwt_service = self.app.state.jwt_service
            test_token = jwt_service.generate_test_token()
            
            if not test_token:
                raise Exception("JWT测试令牌生成失败")
            
            return ComponentHealth(
                name="jwt_service",
                status="UP",
                details={
                    "algorithm": jwt_service.algorithm
                }
            )
        except Exception as e:
            self.logger.error(f"JWT服务健康检查失败: {str(e)}")
            return ComponentHealth(
                name="jwt_service",
                status="DOWN",
                error=str(e)
            )
    
    async def liveness_check(self) -> Dict[str, str]:
        """
        存活检查 - 检查服务是否在运行
        
        存活探针失败将导致Kubernetes重启容器，因此该检查应该非常轻量，
        只有在服务完全不可恢复的情况下才返回失败。
        
        Returns:
            Dict[str, str]: 存活检查结果
        """
        # 简单检查，只要服务能响应就认为是存活的
        return {"status": "UP"}
    
    async def readiness_check(self) -> Dict[str, Any]:
        """
        就绪检查 - 检查服务是否准备好处理请求
        
        就绪探针失败将导致Kubernetes停止向服务发送流量，
        因此该检查应该验证所有关键依赖是否正常。
        
        Returns:
            Dict[str, Any]: 就绪检查结果
        """
        # 检查关键依赖：数据库和Redis
        db_health = await self.check_database()
        redis_health = await self.check_redis()
        
        status = "UP"
        result = {
            "database": db_health.status,
            "redis": redis_health.status
        }
        
        # 如果任何一个关键依赖不可用，则服务不就绪
        if db_health.status == "DOWN" or redis_health.status == "DOWN":
            status = "DOWN"
        
        result["status"] = status
        return result
    
    async def full_health_check(self) -> HealthStatus:
        """
        全面健康检查 - 检查所有组件的健康状态
        
        Returns:
            HealthStatus: 全面健康状态信息
        """
        # 并行检查所有组件
        db_health, redis_health, system_health, jwt_health = await asyncio.gather(
            self.check_database(),
            self.check_redis(),
            self.check_system_resources(),
            self.check_jwt_service()
        )
        
        components = [db_health, redis_health, system_health, jwt_health]
        
        # 确定整体状态
        overall_status = "UP"
        for component in components:
            if component.status == "DOWN":
                overall_status = "DOWN"
                break
            elif component.status == "DEGRADED" and overall_status != "DOWN":
                overall_status = "DEGRADED"
        
        return HealthStatus(
            status=overall_status,
            version=self.version,
            timestamp=int(time.time()),
            components=components
        )