#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
健康检查控制器
"""

import time
import psutil
import socket
import platform
from fastapi import APIRouter, Response, status, Depends
from pkg.utils.config import Config
from pkg.utils.logger import get_logger
from internal.repository.health_check import HealthCheckRepository

router = APIRouter(tags=["健康检查"])
logger = get_logger(__name__)
config = Config()


class SystemInfo:
    """系统信息收集器"""
    
    @staticmethod
    def get_cpu_usage():
        """获取CPU使用率"""
        return psutil.cpu_percent(interval=0.1)
    
    @staticmethod
    def get_memory_usage():
        """获取内存使用情况"""
        memory = psutil.virtual_memory()
        return {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent,
            "used": memory.used,
            "free": memory.free
        }
    
    @staticmethod
    def get_disk_usage():
        """获取磁盘使用情况"""
        disk = psutil.disk_usage('/')
        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        }
    
    @staticmethod
    def get_hostname():
        """获取主机名"""
        return socket.gethostname()
    
    @staticmethod
    def get_platform_info():
        """获取平台信息"""
        return {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "python_version": platform.python_version()
        }


@router.get("/health", summary="健康检查")
async def health_check():
    """
    健康检查端点
    
    返回:
        dict: 健康状态信息
    """
    start_time = time.time()
    
    # 进行必要的健康检查
    # 例如，检查数据库连接、缓存服务等
    db_status = "UP"
    cache_status = "UP"
    
    # 检查数据库连接
    health_repo = HealthCheckRepository()
    db_check = await health_repo.check_database_connection()
    if not db_check["status"]:
        db_status = "DOWN"
    
    # 检查缓存服务状态
    cache_check = await health_repo.check_cache_connection()
    if not cache_check["status"]:
        cache_status = "DOWN"
    
    # 判断整体健康状态
    status_code = status.HTTP_200_OK
    overall_status = "UP"
    
    if db_status == "DOWN" or cache_status == "DOWN":
        overall_status = "DEGRADED"
        if db_status == "DOWN" and cache_status == "DOWN":
            overall_status = "DOWN"
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    # 计算响应时间
    response_time = time.time() - start_time
    
    # 构建健康检查响应
    health_data = {
        "status": overall_status,
        "version": config.get("service.version", "1.0.0"),
        "uptime": health_repo.get_uptime(),
        "timestamp": time.time(),
        "response_time": round(response_time * 1000, 2),  # 毫秒
        "components": {
            "database": {
                "status": db_status,
                "details": db_check["details"] if "details" in db_check else {}
            },
            "cache": {
                "status": cache_status,
                "details": cache_check["details"] if "details" in cache_check else {}
            }
        }
    }
    
    logger.info(f"健康检查完成: 状态={overall_status}, 响应时间={response_time*1000:.2f}ms")
    return Response(content=str(health_data), status_code=status_code, media_type="application/json")


@router.get("/health/system", summary="系统信息")
async def system_info():
    """
    系统信息端点
    
    返回:
        dict: 系统信息
    """
    system_info = {
        "hostname": SystemInfo.get_hostname(),
        "platform": SystemInfo.get_platform_info(),
        "cpu": {
            "usage_percent": SystemInfo.get_cpu_usage()
        },
        "memory": SystemInfo.get_memory_usage(),
        "disk": SystemInfo.get_disk_usage(),
        "process": {
            "pid": psutil.Process().pid,
            "num_threads": psutil.Process().num_threads(),
            "memory_percent": psutil.Process().memory_percent()
        }
    }
    
    return system_info


@router.get("/health/ready", summary="就绪检查")
async def readiness_check(response: Response):
    """
    就绪检查端点，用于Kubernetes就绪性探针
    
    返回:
        dict: 就绪状态信息
    """
    # 检查服务是否已完全初始化并准备好处理请求
    ready = True
    
    # 示例检查
    health_repo = HealthCheckRepository()
    
    # 检查数据库连接
    db_check = await health_repo.check_database_connection()
    if not db_check["status"]:
        ready = False
    
    if ready:
        return {"status": "READY", "timestamp": time.time()}
    else:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "NOT_READY", "timestamp": time.time()} 