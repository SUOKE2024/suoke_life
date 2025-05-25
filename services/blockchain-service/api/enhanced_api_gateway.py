#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
区块链服务增强版API网关
提供RESTful API接口，支持多链交易、批处理、合约管理和数据索引
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# 导入服务
from services.blockchain_service.internal.service.enhanced_blockchain_service import (
    get_blockchain_service, ChainType, TransactionPriority, IndexedData
)

# 导入通用组件
from services.common.observability.tracing import (
    get_tracer, trace, SpanKind
)

logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="区块链服务API",
    description="索克生活区块链服务，提供多链支持、交易批处理、智能合约管理和链下索引功能",
    version="2.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求模型
class TransactionRequest(BaseModel):
    """交易请求"""
    to_address: str = Field(..., description="目标地址")
    data: str = Field(..., description="交易数据（十六进制）")
    value: int = Field(0, description="转账金额（wei）")
    priority: str = Field("normal", description="交易优先级：low, normal, high, urgent")
    chain: Optional[str] = Field(None, description="目标链：ethereum, bsc, polygon, private等")

class BatchTransactionRequest(BaseModel):
    """批量交易请求"""
    transactions: List[TransactionRequest] = Field(..., description="交易列表")
    priority: str = Field("normal", description="批次优先级")

class ContractDeployRequest(BaseModel):
    """合约部署请求"""
    bytecode: str = Field(..., description="合约字节码")
    abi: List[Dict[str, Any]] = Field(..., description="合约ABI")
    constructor_args: Optional[List[Any]] = Field(None, description="构造函数参数")
    chain: Optional[str] = Field(None, description="目标链")

class ContractCallRequest(BaseModel):
    """合约调用请求"""
    contract_address: str = Field(..., description="合约地址")
    method_name: str = Field(..., description="方法名")
    args: List[Any] = Field(..., description="方法参数")
    abi: List[Dict[str, Any]] = Field(..., description="合约ABI")
    chain: Optional[str] = Field(None, description="目标链")
    use_cache: bool = Field(True, description="是否使用缓存")

class IndexRequest(BaseModel):
    """索引请求"""
    transaction_hash: str = Field(..., description="交易哈希")
    user_id: str = Field(..., description="用户ID")
    data_type: str = Field(..., description="数据类型")
    data_hash: str = Field(..., description="数据哈希")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    tags: List[str] = Field(default_factory=list, description="标签")

class QueryIndexRequest(BaseModel):
    """查询索引请求"""
    user_id: Optional[str] = Field(None, description="用户ID")
    data_type: Optional[str] = Field(None, description="数据类型")
    tags: Optional[List[str]] = Field(None, description="标签过滤")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    limit: int = Field(100, description="返回数量限制")

# 响应模型
class TransactionResponse(BaseModel):
    """交易响应"""
    status: str
    transaction_hash: Optional[str] = None
    block_number: Optional[int] = None
    gas_used: Optional[int] = None
    gas_price: Optional[int] = None
    message: Optional[str] = None
    error: Optional[str] = None

class ContractDeployResponse(BaseModel):
    """合约部署响应"""
    status: str
    contract_address: Optional[str] = None
    transaction_hash: Optional[str] = None
    block_number: Optional[int] = None
    gas_used: Optional[int] = None
    error: Optional[str] = None

class HealthStatus(BaseModel):
    """健康状态"""
    service: str
    status: str
    stats: Dict[str, Any]
    chains: Dict[str, Any]
    cache: Dict[str, Any]
    batch_processing: Dict[str, Any]
    uptime: float

# 中间件
@app.middleware("http")
async def add_tracing(request, call_next):
    """添加分布式追踪"""
    tracer = get_tracer("blockchain-api")
    
    with tracer.start_span(
        f"{request.method} {request.url.path}",
        kind=SpanKind.SERVER
    ) as span:
        # 添加请求信息到span
        span.set_attribute("http.method", request.method)
        span.set_attribute("http.url", str(request.url))
        span.set_attribute("http.scheme", request.url.scheme)
        span.set_attribute("http.host", request.url.hostname)
        span.set_attribute("http.target", request.url.path)
        
        # 处理请求
        response = await call_next(request)
        
        # 添加响应信息到span
        span.set_attribute("http.status_code", response.status_code)
        
        return response

# API端点
@app.post("/api/v1/blockchain/transaction", response_model=TransactionResponse)
async def send_transaction(request: TransactionRequest):
    """
    发送单笔交易
    
    支持多链和不同优先级，低优先级交易会自动加入批处理队列
    """
    try:
        service = await get_blockchain_service()
        
        # 转换参数
        priority = TransactionPriority[request.priority.upper()]
        chain = ChainType[request.chain.upper()] if request.chain else None
        
        # 发送交易
        result = await service.send_transaction(
            to_address=request.to_address,
            data=request.data,
            value=request.value,
            priority=priority,
            chain=chain
        )
        
        return TransactionResponse(**result)
        
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"无效的参数: {e}")
    except Exception as e:
        logger.error(f"发送交易失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/blockchain/batch", response_model=List[TransactionResponse])
async def send_batch_transactions(request: BatchTransactionRequest):
    """
    批量发送交易
    
    将多笔交易作为一个批次处理，提高效率
    """
    try:
        service = await get_blockchain_service()
        
        # 转换优先级
        priority = TransactionPriority[request.priority.upper()]
        
        # 发送所有交易
        results = []
        for tx_request in request.transactions:
            chain = ChainType[tx_request.chain.upper()] if tx_request.chain else None
            
            result = await service.send_transaction(
                to_address=tx_request.to_address,
                data=tx_request.data,
                value=tx_request.value,
                priority=priority,
                chain=chain
            )
            results.append(TransactionResponse(**result))
        
        return results
        
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"无效的参数: {e}")
    except Exception as e:
        logger.error(f"批量发送交易失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/blockchain/contract/deploy", response_model=ContractDeployResponse)
async def deploy_contract(request: ContractDeployRequest):
    """
    部署智能合约
    
    支持在不同链上部署合约，自动进行gas估算和优化
    """
    try:
        service = await get_blockchain_service()
        
        # 转换链类型
        chain = ChainType[request.chain.upper()] if request.chain else None
        
        # 部署合约
        result = await service.deploy_contract(
            bytecode=request.bytecode,
            abi=request.abi,
            constructor_args=request.constructor_args,
            chain=chain
        )
        
        return ContractDeployResponse(**result)
        
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"无效的链类型: {e}")
    except Exception as e:
        logger.error(f"部署合约失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/blockchain/contract/call")
async def call_contract_method(request: ContractCallRequest):
    """
    调用合约方法
    
    支持缓存常用查询结果，提高响应速度
    """
    try:
        service = await get_blockchain_service()
        
        # 转换链类型
        chain = ChainType[request.chain.upper()] if request.chain else None
        
        # 调用合约方法
        result = await service.call_contract_method(
            contract_address=request.contract_address,
            method_name=request.method_name,
            args=request.args,
            abi=request.abi,
            chain=chain,
            use_cache=request.use_cache
        )
        
        return {"result": result}
        
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"无效的链类型: {e}")
    except Exception as e:
        logger.error(f"调用合约方法失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/blockchain/index")
async def index_transaction(request: IndexRequest):
    """
    索引交易数据
    
    将交易数据存储到链下索引，支持快速查询
    """
    try:
        service = await get_blockchain_service()
        
        # 索引数据
        success = await service.index_transaction_data(
            tx_hash=request.transaction_hash,
            user_id=request.user_id,
            data_type=request.data_type,
            data_hash=request.data_hash,
            metadata=request.metadata,
            tags=request.tags
        )
        
        if success:
            return {"status": "success", "message": "交易数据已索引"}
        else:
            raise HTTPException(status_code=500, detail="索引失败")
            
    except Exception as e:
        logger.error(f"索引交易数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/blockchain/index/query")
async def query_indexed_data(request: QueryIndexRequest):
    """
    查询索引数据
    
    支持按用户、数据类型、标签和时间范围查询
    """
    try:
        service = await get_blockchain_service()
        
        # 查询索引
        results = await service.query_indexed_data(
            user_id=request.user_id,
            data_type=request.data_type,
            tags=request.tags,
            start_time=request.start_time,
            end_time=request.end_time,
            limit=request.limit
        )
        
        # 转换为字典列表
        data = []
        for item in results:
            data.append({
                'user_id': item.user_id,
                'data_type': item.data_type,
                'data_hash': item.data_hash,
                'transaction_hash': item.transaction_hash,
                'block_number': item.block_number,
                'timestamp': item.timestamp.isoformat(),
                'metadata': item.metadata,
                'tags': item.tags
            })
        
        return {
            "total": len(data),
            "data": data
        }
        
    except Exception as e:
        logger.error(f"查询索引数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/blockchain/chain/switch")
async def switch_chain(chain: str = Query(..., description="目标链")):
    """
    切换当前活动链
    
    支持在多个区块链之间切换
    """
    try:
        service = await get_blockchain_service()
        
        # 转换链类型
        chain_type = ChainType[chain.upper()]
        
        # 切换链
        success = await service.switch_chain(chain_type)
        
        if success:
            return {
                "status": "success",
                "message": f"已切换到{chain}链",
                "current_chain": chain
            }
        else:
            raise HTTPException(status_code=400, detail=f"无法切换到{chain}链")
            
    except KeyError:
        raise HTTPException(status_code=400, detail=f"无效的链类型: {chain}")
    except Exception as e:
        logger.error(f"切换链失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/blockchain/chains")
async def get_supported_chains():
    """
    获取支持的区块链列表
    
    返回所有配置的区块链及其连接状态
    """
    try:
        service = await get_blockchain_service()
        status = service.get_health_status()
        
        chains = []
        for chain_name, chain_info in status['chains'].items():
            chains.append({
                'name': chain_name,
                'connected': chain_info['connected'],
                'chain_id': chain_info['config']['chain_id'],
                'block_time': chain_info['config']['block_time'],
                'confirmations': chain_info['config']['confirmations']
            })
        
        return {
            "total": len(chains),
            "chains": chains,
            "current_chain": service.current_chain.value
        }
        
    except Exception as e:
        logger.error(f"获取链列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/blockchain/status", response_model=HealthStatus)
async def get_health_status():
    """
    获取服务健康状态
    
    返回服务运行状态、统计信息、缓存状态和批处理队列信息
    """
    try:
        service = await get_blockchain_service()
        status = service.get_health_status()
        return HealthStatus(**status)
    except Exception as e:
        logger.error(f"获取健康状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/blockchain/metrics")
async def get_metrics():
    """
    获取Prometheus格式的指标
    
    用于监控系统集成
    """
    try:
        service = await get_blockchain_service()
        stats = service.stats
        
        # 构建Prometheus格式的指标
        metrics = []
        
        # 计数器指标
        metrics.append(f'# HELP blockchain_total_transactions Total number of transactions')
        metrics.append(f'# TYPE blockchain_total_transactions counter')
        metrics.append(f'blockchain_total_transactions {stats["total_transactions"]}')
        
        metrics.append(f'# HELP blockchain_batch_transactions Total number of batch transactions')
        metrics.append(f'# TYPE blockchain_batch_transactions counter')
        metrics.append(f'blockchain_batch_transactions {stats["batch_transactions"]}')
        
        metrics.append(f'# HELP blockchain_failed_transactions Total number of failed transactions')
        metrics.append(f'# TYPE blockchain_failed_transactions counter')
        metrics.append(f'blockchain_failed_transactions {stats["failed_transactions"]}')
        
        metrics.append(f'# HELP blockchain_cache_hits Total number of cache hits')
        metrics.append(f'# TYPE blockchain_cache_hits counter')
        metrics.append(f'blockchain_cache_hits {stats["cache_hits"]}')
        
        metrics.append(f'# HELP blockchain_cache_misses Total number of cache misses')
        metrics.append(f'# TYPE blockchain_cache_misses counter')
        metrics.append(f'blockchain_cache_misses {stats["cache_misses"]}')
        
        metrics.append(f'# HELP blockchain_indexed_records Total number of indexed records')
        metrics.append(f'# TYPE blockchain_indexed_records counter')
        metrics.append(f'blockchain_indexed_records {stats["indexed_records"]}')
        
        # 仪表盘指标
        metrics.append(f'# HELP blockchain_average_gas_price Average gas price')
        metrics.append(f'# TYPE blockchain_average_gas_price gauge')
        metrics.append(f'blockchain_average_gas_price {stats["average_gas_price"]}')
        
        metrics.append(f'# HELP blockchain_average_confirmation_time Average confirmation time in seconds')
        metrics.append(f'# TYPE blockchain_average_confirmation_time gauge')
        metrics.append(f'blockchain_average_confirmation_time {stats["average_confirmation_time"]}')
        
        # 活跃链数量
        metrics.append(f'# HELP blockchain_active_chains Number of active blockchain connections')
        metrics.append(f'# TYPE blockchain_active_chains gauge')
        metrics.append(f'blockchain_active_chains {len(stats["active_chains"])}')
        
        return "\n".join(metrics)
        
    except Exception as e:
        logger.error(f"获取指标失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 健康检查端点
@app.get("/health")
async def health_check():
    """基本健康检查"""
    return {"status": "healthy"}

@app.get("/ready")
async def readiness_check():
    """就绪检查"""
    try:
        service = await get_blockchain_service()
        status = service.get_health_status()
        
        # 检查是否有活跃的链连接
        if not status['stats']['active_chains']:
            raise HTTPException(status_code=503, detail="没有活跃的区块链连接")
        
        return {"status": "ready"}
    except Exception as e:
        logger.error(f"就绪检查失败: {e}")
        raise HTTPException(status_code=503, detail=str(e))

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("区块链服务API启动中...")
    
    # 初始化服务
    try:
        service = await get_blockchain_service()
        logger.info("区块链服务初始化成功")
    except Exception as e:
        logger.error(f"区块链服务初始化失败: {e}")
        raise

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("区块链服务API关闭中...")
    
    # 清理资源
    try:
        service = await get_blockchain_service()
        await service.cleanup()
        logger.info("区块链服务清理完成")
    except Exception as e:
        logger.error(f"区块链服务清理失败: {e}")

# 主函数
if __name__ == "__main__":
    uvicorn.run(
        "enhanced_api_gateway:app",
        host="0.0.0.0",
        port=8084,
        reload=True,
        log_level="info"
    ) 