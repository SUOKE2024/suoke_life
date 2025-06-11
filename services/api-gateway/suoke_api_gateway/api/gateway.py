from typing import Dict, List, Any, Optional, Union

"""
gateway - 索克生活项目模块
"""

from ..core.logging import get_logger
from ..services.service_registry import ServiceRegistry
from fastapi import APIRouter, HTTPException, Request, Response, status
import httpx
import time

"""
网关路由处理器

处理请求转发、负载均衡等核心网关功能。
"""




logger = get_logger(__name__)

gateway_router = APIRouter()

@gateway_router.api_route(
    " / {service_name} / {path:path}",
    methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
)
async def proxy_request(
    service_name: str,
    path: str,
    request: Request,
) -> Response:
    """代理请求到后端服务"""
    start_time = time.time()

    try:
# 获取服务注册表
service_registry: ServiceRegistry = request.app.state.service_registry

# 获取服务实例
service_instance = service_registry.get_service_instance(service_name)
if not service_instance:
            raise HTTPException(
                status_code = status.HTTP_503_SERVICE_UNAVAILABLE,
                detail = f"Service '{service_name}' is not available"
            )

# 构建目标URL
target_url = f"http: / /{service_instance.host}:{service_instance.port} / {path}"
if request.url.query:
            target_url += f"?{request.url.query}"

# 准备请求头
headers = dict(request.headers)
# 移除可能导致问题的头部
headers.pop("host", None)
headers.pop("content - length", None)

# 添加代理头
headers["X - Forwarded - For"] = request.client.host if request.client else "unknown"
headers["X - Forwarded - Proto"] = request.url.scheme
headers["X - Forwarded - Host"] = request.headers.get("host", "")
headers["X - Gateway - Service"] = service_name

# 添加用户信息（如果有）
user_id = getattr(request.state, "user_id", None)
if user_id:
            headers["X - User - ID"] = user_id

request_id = getattr(request.state, "request_id", None)
if request_id:
            headers["X - Request - ID"] = request_id

# 读取请求体
body = await request.body() if request.method in ["POST", "PUT", "PATCH"] else None

# 发送请求到后端服务
async with httpx.AsyncClient(timeout = 30.0) as client:
            response = await client.request(
                method = request.method,
                url = target_url,
                headers = headers,
                content = body,
            )

# 记录指标
duration = time.time() - start_time
metrics_service = getattr(request.app.state, "metrics_service", None)
if metrics_service:
            metrics_service.record_service_request(
                service = service_name,
                method = request.method,
                status_code = response.status_code,
                duration = duration,
            )

# 准备响应头
response_headers = dict(response.headers)
# 移除可能导致问题的头部
response_headers.pop("content - length", None)
response_headers.pop("transfer - encoding", None)

# 添加网关信息
response_headers["X - Gateway - Service"] = service_name
response_headers["X - Gateway - Instance"] = service_instance.id
response_headers["X - Gateway - Duration"] = f"{duration:.4f}"

# 返回响应
return Response(
            content = response.content,
            status_code = response.status_code,
            headers = response_headers,
            media_type = response.headers.get("content - type"),
)

    except httpx.TimeoutException:
logger.error(
            "Request timeout",
            service = service_name,
            path = path,
            method = request.method,
)
raise HTTPException(
            status_code = status.HTTP_504_GATEWAY_TIMEOUT,
            detail = "Request timeout"
)

    except httpx.ConnectError:
logger.error(
            "Connection error",
            service = service_name,
            path = path,
            method = request.method,
)
raise HTTPException(
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE,
            detail = "Service connection failed"
)

    except Exception as e:
logger.error(
            "Proxy request failed",
            service = service_name,
            path = path,
            method = request.method,
            error = str(e),
            exc_info = True,
)
raise HTTPException(
            status_code = status.HTTP_502_BAD_GATEWAY,
            detail = "Gateway error"
)

@gateway_router.get(" / services")
async def list_services(request: Request):
    """列出所有可用服务"""
    service_registry: ServiceRegistry = request.app.state.service_registry
    services = service_registry.get_all_services()

    result = {}
    for service_name, instances in services.items():
healthy_instances = [inst for inst in instances if inst.healthy]
result[service_name] = {
            "total_instances": len(instances),
            "healthy_instances": len(healthy_instances),
            "status": "healthy" if healthy_instances else "unhealthy",
            "instances": [
                {
                    "id": inst.id,
                    "host": inst.host,
                    "port": inst.port,
                    "healthy": inst.healthy,
                    "weight": inst.weight,
                }
                for inst in instances
            ]
}

    return result

@gateway_router.get(" / services / {service_name} / health")
async def get_service_health(service_name: str, request: Request):
    """获取特定服务的健康状态"""
    service_registry: ServiceRegistry = request.app.state.service_registry
    health_info = service_registry.get_service_health(service_name)

    if health_info["status"] == "not_found":
raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"Service '{service_name}' not found"
)

    return health_info