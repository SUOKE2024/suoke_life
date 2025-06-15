"""
健康检查API模块

提供服务健康状态检查接口。
"""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..config.settings import get_settings
from ..services.blockchain_client import get_blockchain_client
from ..utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str
    timestamp: str = Field(..., description="时间戳（ISO格式）")
    version: str
    environment: str
    components: dict[str, Any]


@router.get("/", response_model=HealthResponse, summary="基础健康检查")
async def health_check():
    """基础健康检查

    Returns:
        服务健康状态信息
    """
    settings = get_settings()

    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(UTC).isoformat(),
        version=settings.app_version,
        environment=settings.environment,
        components={}
    )


@router.get("/ready", response_model=HealthResponse, summary="就绪状态检查")
async def readiness_check():
    """就绪状态检查

    检查服务是否准备好接收请求，包括依赖服务的连接状态。

    Returns:
        详细的服务就绪状态信息

    Raises:
        HTTPException: 当服务未就绪时
    """
    settings = get_settings()
    components = {}
    overall_status = "healthy"

    # 检查区块链连接
    try:
        blockchain_client = await get_blockchain_client()
        if blockchain_client.is_connected():
            components["blockchain"] = {
                "status": "healthy",
                "node_url": settings.blockchain.eth_node_url,
                "chain_id": settings.blockchain.chain_id
            }
        else:
            components["blockchain"] = {
                "status": "unhealthy",
                "error": "区块链客户端未连接"
            }
            overall_status = "unhealthy"
    except Exception as e:
        components["blockchain"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_status = "unhealthy"

    # 检查数据库连接（如果需要）
    # TODO: 添加数据库连接检查
    components["database"] = {
        "status": "not_checked",
        "note": "数据库连接检查待实现"
    }

    # 检查Redis连接（如果需要）
    # TODO: 添加Redis连接检查
    components["redis"] = {
        "status": "not_checked",
        "note": "Redis连接检查待实现"
    }

    response = HealthResponse(
        status=overall_status,
        timestamp=datetime.now(UTC).isoformat(),
        version=settings.app_version,
        environment=settings.environment,
        components=components
    )

    if overall_status == "unhealthy":
        logger.warning("服务就绪检查失败", extra={"components": components})
        raise HTTPException(status_code=503, detail=response.model_dump())

    return response


@router.get("/live", summary="存活状态检查")
async def liveness_check():
    """存活状态检查

    简单的存活检查，用于Kubernetes等容器编排系统。

    Returns:
        简单的存活状态信息
    """
    return {
        "status": "alive",
        "timestamp": datetime.now(UTC).isoformat()
    }
