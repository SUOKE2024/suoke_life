"""
管理路由处理器

提供网关管理功能，如服务注册、配置管理等。
"""

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from ..core.config import ServiceConfig
from ..core.logging import get_logger
from ..services.health import HealthService
from ..services.metrics import MetricsService
from ..services.service_registry import ServiceRegistry

logger = get_logger(__name__)

management_router = APIRouter()

class ServiceRegistrationRequest(BaseModel):
    """服务注册请求模型"""
    name: str
    host: str
    port: int
    health_check_path: str = "/health"
    timeout: int = 30
    retry_count: int = 3

class ServiceUpdateRequest(BaseModel):
    """服务更新请求模型"""
    host: str = None
    port: int = None
    health_check_path: str = None
    timeout: int = None
    retry_count: int = None

@management_router.post("/services", status_code=status.HTTP_201_CREATED)
async def register_service(
    service_request: ServiceRegistrationRequest,
    request: Request,
):
    """注册新服务"""
    try:
        service_registry: ServiceRegistry = request.app.state.service_registry
        
        # 创建服务配置
        service_config = ServiceConfig(
            name=service_request.name,
            host=service_request.host,
            port=service_request.port,
            health_check_path=service_request.health_check_path,
            timeout=service_request.timeout,
            retry_count=service_request.retry_count,
        )
        
        # 注册服务
        instance_id = await service_registry.register_service(
            service_request.name,
            service_config,
        )
        
        logger.info(
            "Service registered via API",
            service=service_request.name,
            instance_id=instance_id,
        )
        
        return {
            "message": "Service registered successfully",
            "service_name": service_request.name,
            "instance_id": instance_id,
        }
        
    except Exception as e:
        logger.error(
            "Failed to register service",
            service=service_request.name,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register service"
        )

@management_router.delete("/services/{service_name}/instances/{instance_id}")
async def deregister_service(
    service_name: str,
    instance_id: str,
    request: Request,
):
    """注销服务实例"""
    try:
        service_registry: ServiceRegistry = request.app.state.service_registry
        
        success = await service_registry.deregister_service(service_name, instance_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service instance not found"
            )
        
        logger.info(
            "Service deregistered via API",
            service=service_name,
            instance_id=instance_id,
        )
        
        return {
            "message": "Service instance deregistered successfully",
            "service_name": service_name,
            "instance_id": instance_id,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to deregister service",
            service=service_name,
            instance_id=instance_id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deregister service"
        )

@management_router.get("/services")
async def list_all_services(request: Request):
    """列出所有服务及其详细信息"""
    service_registry: ServiceRegistry = request.app.state.service_registry
    services = service_registry.get_all_services()
    
    result = {}
    for service_name, instances in services.items():
        healthy_count = sum(1 for inst in instances if inst.healthy)
        result[service_name] = {
            "total_instances": len(instances),
            "healthy_instances": healthy_count,
            "health_ratio": healthy_count / len(instances) if instances else 0,
            "status": "healthy" if healthy_count > 0 else "unhealthy",
            "instances": [
                {
                    "id": inst.id,
                    "host": inst.host,
                    "port": inst.port,
                    "healthy": inst.healthy,
                    "failure_count": inst.failure_count,
                    "last_health_check": inst.last_health_check,
                    "weight": inst.weight,
                    "metadata": inst.metadata,
                }
                for inst in instances
            ]
        }
    
    return result

@management_router.get("/health")
async def get_gateway_health(request: Request):
    """获取网关整体健康状态"""
    try:
        health_service: HealthService = request.app.state.health_service
        health_status = await health_service.check_health()
        
        return {
            "status": health_status.status,
            "timestamp": health_status.timestamp,
            "overall_score": health_status.overall_score,
            "components": {
                name: {
                    "status": result.status,
                    "response_time": result.response_time,
                    "last_check": result.last_check,
                    "error_message": result.error_message,
                }
                for name, result in health_status.details.items()
            }
        }
        
    except Exception as e:
        logger.error("Failed to get health status", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get health status"
        )

@management_router.get("/metrics/summary")
async def get_metrics_summary(request: Request):
    """获取指标摘要"""
    try:
        metrics_service: MetricsService = getattr(request.app.state, "metrics_service", None)
        
        if not metrics_service or not metrics_service.enabled:
            return {"message": "Metrics not enabled"}
        
        summary = metrics_service.get_metrics_summary()
        
        return {
            "metrics_enabled": True,
            "summary": summary,
            "prometheus_endpoint": "/metrics",
        }
        
    except Exception as e:
        logger.error("Failed to get metrics summary", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get metrics summary"
        )

@management_router.post("/services/{service_name}/health-check")
async def trigger_health_check(service_name: str, request: Request):
    """触发特定服务的健康检查"""
    try:
        service_registry: ServiceRegistry = request.app.state.service_registry
        
        if service_name not in service_registry.services:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service '{service_name}' not found"
            )
        
        # 触发健康检查
        instances = service_registry.services[service_name]
        for instance in instances:
            await service_registry._check_instance_health(instance)
        
        # 返回更新后的健康状态
        health_info = service_registry.get_service_health(service_name)
        
        return {
            "message": "Health check completed",
            "service_name": service_name,
            "health_info": health_info,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to trigger health check",
            service=service_name,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to trigger health check"
        )

@management_router.get("/config")
async def get_gateway_config(request: Request):
    """获取网关配置信息"""
    from ..core.config import get_settings
    
    settings = get_settings()
    
    # 返回非敏感的配置信息
    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "environment": settings.environment,
        "debug": settings.debug,
        "features": {
            "rate_limiting": settings.rate_limit.enabled,
            "monitoring": settings.monitoring.enabled,
            "grpc": settings.grpc.enabled,
        },
        "limits": {
            "default_rate_limit": settings.rate_limit.default_rate,
        },
        "timeouts": {
            "default_timeout": 30,  # 可以从配置中获取
        },
    } 