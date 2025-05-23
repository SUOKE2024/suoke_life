#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
健康检查模块

提供服务健康状态检查和报告功能。
"""
import logging
import asyncio
from fastapi import FastAPI


class HealthCheck:
    """健康检查服务类"""
    
    def __init__(self, app: FastAPI):
        """
        初始化健康检查服务
        
        Args:
            app: FastAPI应用实例
        """
        self.app = app
        self.ready = False
        self.services = {}
        self.dependencies = []
        
        # 启动后标记为就绪
        app.add_event_handler("startup", self._mark_ready)
        app.add_event_handler("shutdown", self._mark_not_ready)
    
    async def _mark_ready(self):
        """标记服务为就绪状态"""
        self.ready = True
        logging.info("服务已就绪")
    
    async def _mark_not_ready(self):
        """标记服务为非就绪状态"""
        self.ready = False
        logging.info("服务已关闭")
    
    def register_dependency(self, name, check_func):
        """
        注册一个依赖项检查
        
        Args:
            name: 依赖项名称
            check_func: 检查函数，应返回布尔值
        """
        self.dependencies.append((name, check_func))
    
    async def liveness_check(self):
        """
        存活检查 - 判断服务是否在运行
        
        Returns:
            dict: 健康状态
        """
        return {"status": "ok", "alive": True}
    
    async def readiness_check(self):
        """
        就绪检查 - 判断服务是否已准备好处理请求
        
        Returns:
            dict: 就绪状态
        """
        return {"status": "ok" if self.ready else "not_ready", "ready": self.ready}
    
    async def dependency_check(self):
        """
        依赖项检查 - 检查所有注册的依赖项
        
        Returns:
            dict: 依赖项状态
        """
        results = {}
        
        for name, check_func in self.dependencies:
            try:
                result = await check_func()
                status = "ok" if result else "error"
            except Exception as e:
                logging.exception(f"依赖项检查异常: {name}")
                result = False
                status = "error"
            
            results[name] = {"status": status, "healthy": result}
        
        all_healthy = all(item["healthy"] for item in results.values())
        
        return {
            "status": "ok" if all_healthy else "error",
            "dependencies": results
        }
    
    async def full_health_check(self):
        """
        完整健康检查 - 包括存活、就绪和依赖项检查
        
        Returns:
            dict: 完整健康状态
        """
        liveness = await self.liveness_check()
        readiness = await self.readiness_check()
        dependencies = await self.dependency_check()
        
        all_healthy = (
            liveness["alive"] and 
            readiness["ready"] and 
            dependencies["status"] == "ok"
        )
        
        return {
            "status": "ok" if all_healthy else "error",
            "liveness": liveness,
            "readiness": readiness,
            "dependencies": dependencies["dependencies"]
        }