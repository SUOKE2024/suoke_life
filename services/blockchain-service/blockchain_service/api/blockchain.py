"""
区块链API模块

提供区块链相关的HTTP API接口。
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..core.exceptions import BlockchainServiceError
from ..services.blockchain_client import BlockchainClient, get_blockchain_client
from ..utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


class HealthDataRequest(BaseModel):
    """健康数据存储请求"""
    user_id: UUID = Field(..., description="用户ID")
    data_type: str = Field(..., description="数据类型")
    data_content: dict[str, Any] = Field(..., description="数据内容")
    metadata: dict[str, Any] | None = Field(None, description="元数据")


class HealthDataResponse(BaseModel):
    """健康数据存储响应"""
    success: bool = Field(..., description="操作是否成功")
    transaction_hash: str | None = Field(None, description="交易哈希")
    block_number: int | None = Field(None, description="区块号")
    data_id: str | None = Field(None, description="数据ID")
    message: str = Field(..., description="响应消息")


class TransactionStatusRequest(BaseModel):
    """交易状态查询请求"""
    transaction_hash: str = Field(..., description="交易哈希")


class TransactionStatusResponse(BaseModel):
    """交易状态查询响应"""
    transaction_hash: str = Field(..., description="交易哈希")
    status: str = Field(..., description="交易状态")
    block_number: int | None = Field(None, description="区块号")
    confirmations: int | None = Field(None, description="确认数")
    gas_used: int | None = Field(None, description="使用的Gas")


class ContractInfoResponse(BaseModel):
    """合约信息响应"""
    contracts: list[dict[str, Any]] = Field(..., description="合约列表")


async def get_client() -> BlockchainClient:
    """获取区块链客户端依赖"""
    try:
        return await get_blockchain_client()
    except Exception as e:
        logger.error("获取区块链客户端失败", extra={"error": str(e)})
        raise HTTPException(
            status_code=503,
            detail="区块链服务暂时不可用"
        )


@router.post("/store-health-data", response_model=HealthDataResponse, summary="存储健康数据")
async def store_health_data(
    request: HealthDataRequest,
    client: BlockchainClient = Depends(get_client)
):
    """存储健康数据到区块链

    Args:
        request: 健康数据存储请求
        client: 区块链客户端

    Returns:
        存储结果

    Raises:
        HTTPException: 当存储失败时
    """
    try:
        logger.info("开始存储健康数据", extra={
            "user_id": str(request.user_id),
            "data_type": request.data_type
        })

        # 这里应该调用智能合约存储数据
        # 目前返回模拟响应
        # TODO: 实现实际的区块链存储逻辑

        response = HealthDataResponse(
            success=True,
            transaction_hash="0x" + "0" * 64,  # 模拟交易哈希
            block_number=12345,
            data_id=str(request.user_id),
            message="健康数据存储成功（模拟）"
        )

        logger.info("健康数据存储完成", extra={
            "user_id": str(request.user_id),
            "transaction_hash": response.transaction_hash
        })

        return response

    except BlockchainServiceError as e:
        logger.error("存储健康数据失败", extra={
            "user_id": str(request.user_id),
            "error": str(e)
        })
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("存储健康数据时发生未知错误", extra={
            "user_id": str(request.user_id),
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail="内部服务器错误")


@router.get("/transaction/{transaction_hash}", response_model=TransactionStatusResponse, summary="查询交易状态")
async def get_transaction_status(
    transaction_hash: str,
    client: BlockchainClient = Depends(get_client)
):
    """查询交易状态

    Args:
        transaction_hash: 交易哈希
        client: 区块链客户端

    Returns:
        交易状态信息

    Raises:
        HTTPException: 当查询失败时
    """
    try:
        logger.info("查询交易状态", extra={"transaction_hash": transaction_hash})

        # TODO: 实现实际的交易状态查询逻辑
        # 目前返回模拟响应

        response = TransactionStatusResponse(
            transaction_hash=transaction_hash,
            status="confirmed",
            block_number=12345,
            confirmations=6,
            gas_used=21000
        )

        return response

    except Exception as e:
        logger.error("查询交易状态失败", extra={
            "transaction_hash": transaction_hash,
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail="查询交易状态失败")


@router.get("/contracts", response_model=ContractInfoResponse, summary="获取合约信息")
async def get_contracts_info(client: BlockchainClient = Depends(get_client)):
    """获取已部署的智能合约信息

    Args:
        client: 区块链客户端

    Returns:
        合约信息列表
    """
    try:
        contracts = []

        for _name, contract_info in client.contracts.items():
            contracts.append({
                "name": contract_info.name,
                "address": contract_info.address,
                "functions": [func["name"] for func in contract_info.abi if func.get("type") == "function"]
            })

        return ContractInfoResponse(contracts=contracts)

    except Exception as e:
        logger.error("获取合约信息失败", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="获取合约信息失败")


@router.get("/balance/{address}", summary="查询地址余额")
async def get_address_balance(
    address: str,
    client: BlockchainClient = Depends(get_client)
):
    """查询指定地址的余额

    Args:
        address: 以太坊地址
        client: 区块链客户端

    Returns:
        地址余额信息

    Raises:
        HTTPException: 当查询失败时
    """
    try:
        balance = await client.get_balance(address)

        return {
            "address": address,
            "balance": str(balance),
            "unit": "ETH",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error("查询地址余额失败", extra={
            "address": address,
            "error": str(e)
        })
        raise HTTPException(status_code=400, detail="查询地址余额失败")
