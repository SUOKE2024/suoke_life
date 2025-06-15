#!/usr/bin/env python3
"""
索克生活 API 网关路由

处理代理请求和负载均衡。
"""

from ..core.config import get_settings
from ..core.logging import get_logger
from ..services.service_registry import ServiceRegistry
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import StreamingResponse
from typing import Any, Dict, Optional
import httpx
import time

logger = get_logger(__name__)

# 创建网关路由器
gateway_router = APIRouter()


async def get_service_registry() -> ServiceRegistry:
    """获取服务注册表依赖"""
    # 这里应该从应用状态获取
    # 暂时返回一个新实例，实际应该是单例
    settings = get_settings()
    registry = ServiceRegistry(settings)
    await registry.initialize()
    return registry


@gateway_router.api_route(
    "/{service_name}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
    summary="代理请求到后端服务",
    description="将请求代理到指定的后端服务"
)
async def proxy_request(
    service_name: str,
    path: str,
    request: Request,
    registry: ServiceRegistry = Depends(get_service_registry)
) -> Response:
    """代理请求到后端服务"""
    start_time = time.time()
    
    try:
        # 获取服务实例
        instance = registry.get_service_instance(service_name)
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Service '{service_name}' is not available"
            )

        # 构建目标URL
        target_url = f"http://{instance.host}:{instance.port}/{path}"
        if request.url.query:
            target_url += f"?{request.url.query}"

        # 准备请求头
        headers = dict(request.headers)
        # 移除可能导致问题的头部
        headers.pop("host", None)
        headers.pop("content-length", None)

        # 读取请求体
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()

        # 发送代理请求
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                follow_redirects=False
            )

            # 记录响应时间
            response_time = time.time() - start_time
            registry.record_response_time(service_name, f"{instance.host}:{instance.port}", response_time)

            # 准备响应头
            response_headers = dict(response.headers)
            # 移除可能导致问题的头部
            response_headers.pop("content-length", None)
            response_headers.pop("transfer-encoding", None)

            # 添加代理信息头
            response_headers["X-Proxy-Service"] = service_name
            response_headers["X-Proxy-Instance"] = instance.id
            response_headers["X-Response-Time"] = str(response_time)

            # 返回响应
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=response_headers,
                media_type=response.headers.get("content-type")
            )

    except httpx.TimeoutException:
        # 标记实例为不健康
        if 'instance' in locals():
            registry.mark_unhealthy(service_name, f"{instance.host}:{instance.port}")
        
        logger.error(
            "Proxy request timeout",
            service=service_name,
            path=path,
            method=request.method,
            duration=time.time() - start_time
        )
        
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Service request timeout"
        )

    except httpx.ConnectError:
        # 标记实例为不健康
        if 'instance' in locals():
            registry.mark_unhealthy(service_name, f"{instance.host}:{instance.port}")
        
        logger.error(
            "Proxy request connection error",
            service=service_name,
            path=path,
            method=request.method,
            duration=time.time() - start_time
        )
        
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service connection failed"
        )

    except Exception as e:
        logger.error(
            "Proxy request failed",
            service=service_name,
            path=path,
            method=request.method,
            error=str(e),
            duration=time.time() - start_time,
            exc_info=True
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal proxy error"
        )


@gateway_router.get(
    "/services",
    summary="获取所有服务",
    description="获取所有注册的服务及其实例信息"
)
async def list_services(
    registry: ServiceRegistry = Depends(get_service_registry)
) -> Dict[str, Any]:
    """获取所有服务"""
    services = registry.get_all_services()
    
    result = {}
    for service_name, instances in services.items():
        result[service_name] = {
            "total_instances": len(instances),
            "healthy_instances": sum(1 for instance in instances if instance.healthy),
            "instances": [
                {
                    "id": instance.id,
                    "host": instance.host,
                    "port": instance.port,
                    "healthy": instance.healthy,
                    "weight": instance.weight,
                    "failure_count": instance.failure_count,
                    "last_health_check": instance.last_health_check.isoformat() if instance.last_health_check else None
                }
                for instance in instances
            ]
        }
    
    return {
        "services": result,
        "total_services": len(services),
        "timestamp": time.time()
    }


@gateway_router.get(
    "/services/{service_name}",
    summary="获取指定服务信息",
    description="获取指定服务的详细信息"
)
async def get_service_info(
    service_name: str,
    registry: ServiceRegistry = Depends(get_service_registry)
) -> Dict[str, Any]:
    """获取指定服务信息"""
    health_info = registry.get_service_health(service_name)
    
    if health_info.get("status") == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service '{service_name}' not found"
        )
    
    return {
        "service_name": service_name,
        "health": health_info,
        "timestamp": time.time()
    }


@gateway_router.post(
    "/services/{service_name}/instances",
    summary="注册服务实例",
    description="动态注册新的服务实例"
)
async def register_service_instance(
    service_name: str,
    instance_data: Dict[str, Any],
    registry: ServiceRegistry = Depends(get_service_registry)
) -> Dict[str, Any]:
    """注册服务实例"""
    try:
        # 验证必需字段
        required_fields = ["host", "port"]
        for field in required_fields:
            if field not in instance_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}"
                )

        # 创建服务配置
        from ..core.config import ServiceConfig
        service_config = ServiceConfig(
            name=service_name,
            url=f"http://{instance_data['host']}:{instance_data['port']}",
            weight=instance_data.get("weight", 1),
            timeout=instance_data.get("timeout", 30.0),
            health_check_path=instance_data.get("health_check_path", "/health")
        )

        # 注册服务
        instance_id = await registry.register_service(
            service_name,
            service_config,
            instance_data.get("instance_id")
        )

        logger.info(
            "Service instance registered via API",
            service=service_name,
            instance_id=instance_id,
            host=instance_data["host"],
            port=instance_data["port"]
        )

        return {
            "message": "Service instance registered successfully",
            "service_name": service_name,
            "instance_id": instance_id,
            "timestamp": time.time()
        }

    except Exception as e:
        logger.error(
            "Failed to register service instance",
            service=service_name,
            error=str(e),
            exc_info=True
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register service instance: {str(e)}"
        )


@gateway_router.delete(
    "/services/{service_name}/instances/{instance_id}",
    summary="注销服务实例",
    description="动态注销服务实例"
)
async def deregister_service_instance(
    service_name: str,
    instance_id: str,
    registry: ServiceRegistry = Depends(get_service_registry)
) -> Dict[str, Any]:
    """注销服务实例"""
    try:
        success = await registry.deregister_service(service_name, instance_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service instance '{instance_id}' not found in service '{service_name}'"
            )

        logger.info(
            "Service instance deregistered via API",
            service=service_name,
            instance_id=instance_id
        )

        return {
            "message": "Service instance deregistered successfully",
            "service_name": service_name,
            "instance_id": instance_id,
            "timestamp": time.time()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "Failed to deregister service instance",
            service=service_name,
            instance_id=instance_id,
            error=str(e),
            exc_info=True
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deregister service instance: {str(e)}"
        )