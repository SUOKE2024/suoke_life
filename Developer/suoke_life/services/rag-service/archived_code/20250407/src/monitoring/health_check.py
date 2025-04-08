"""
健康检查模块
"""

import asyncio
from typing import Dict, List, Optional
from loguru import logger
from config.monitoring_config import HEALTH_CHECK_CONFIG
from monitoring.metrics import metrics

class HealthCheck:
    def __init__(self):
        self.timeout = HEALTH_CHECK_CONFIG["TIMEOUT"]
        self.components = HEALTH_CHECK_CONFIG["COMPONENTS"]
        self._status = {comp: True for comp in self.components}
        self._details = {comp: "OK" for comp in self.components}
    
    async def check_vector_store(self) -> bool:
        """检查向量存储健康状态"""
        try:
            # TODO: 实现向量存储健康检查
            # 例如：测试连接、简单查询等
            is_healthy = True
            metrics.vector_store_health.set(1 if is_healthy else 0)
            self._details["vector_store"] = "OK" if is_healthy else "Connection failed"
            return is_healthy
        except Exception as e:
            logger.error(f"Vector store health check failed: {e}")
            self._details["vector_store"] = str(e)
            metrics.vector_store_health.set(0)
            return False
    
    async def check_knowledge_graph(self) -> bool:
        """检查知识图谱健康状态"""
        try:
            # TODO: 实现知识图谱健康检查
            # 例如：测试Neo4j连接等
            is_healthy = True
            self._details["knowledge_graph"] = "OK" if is_healthy else "Connection failed"
            return is_healthy
        except Exception as e:
            logger.error(f"Knowledge graph health check failed: {e}")
            self._details["knowledge_graph"] = str(e)
            return False
    
    async def check_llm_service(self) -> bool:
        """检查LLM服务健康状态"""
        try:
            # TODO: 实现LLM服务健康检查
            # 例如：测试API连接等
            is_healthy = True
            self._details["llm_service"] = "OK" if is_healthy else "Service unavailable"
            return is_healthy
        except Exception as e:
            logger.error(f"LLM service health check failed: {e}")
            self._details["llm_service"] = str(e)
            return False
    
    async def check_cache(self) -> bool:
        """检查缓存健康状态"""
        try:
            # TODO: 实现缓存健康检查
            # 例如：测试Redis连接等
            is_healthy = True
            self._details["cache"] = "OK" if is_healthy else "Connection failed"
            return is_healthy
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            self._details["cache"] = str(e)
            return False
    
    async def check_component(self, component: str) -> bool:
        """检查单个组件健康状态"""
        check_methods = {
            "vector_store": self.check_vector_store,
            "knowledge_graph": self.check_knowledge_graph,
            "llm_service": self.check_llm_service,
            "cache": self.check_cache
        }
        
        if component not in check_methods:
            logger.warning(f"Unknown component: {component}")
            return False
        
        try:
            async with asyncio.timeout(self.timeout):
                is_healthy = await check_methods[component]()
                self._status[component] = is_healthy
                return is_healthy
        except asyncio.TimeoutError:
            logger.error(f"Health check timeout for {component}")
            self._status[component] = False
            self._details[component] = "Timeout"
            return False
    
    async def check_all(self) -> Dict[str, bool]:
        """检查所有组件健康状态"""
        tasks = [
            self.check_component(component)
            for component in self.components
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return dict(zip(self.components, results))
    
    def get_status(self) -> Dict[str, Any]:
        """获取健康状态报告"""
        overall_healthy = all(self._status.values())
        return {
            "healthy": overall_healthy,
            "status": self._status,
            "details": self._details,
            "timestamp": datetime.datetime.now().isoformat()
        }

# 创建全局健康检查实例
health_checker = HealthCheck() 