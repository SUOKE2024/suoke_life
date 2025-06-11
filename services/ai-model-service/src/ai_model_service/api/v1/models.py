"""模型管理API"""

import uuid
from typing import List, Optional

import structlog
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field

from ...models.config import ModelConfig
from ...models.deployment import DeploymentInfo
from ...models.inference import InferenceRequest, InferenceResult

logger = structlog.get_logger(__name__)
router = APIRouter()


class DeployModelRequest(BaseModel):
    """部署模型请求"""

    config: ModelConfig = Field(..., description="模型配置")


class DeployModelResponse(BaseModel):
    """部署模型响应"""

    deployment_id: str = Field(..., description="部署ID")
    message: str = Field(..., description="响应消息")


class ScaleModelRequest(BaseModel):
    """扩缩容模型请求"""

    replicas: int = Field(..., ge=0, le=100, description="目标副本数")


class UpdateModelRequest(BaseModel):
    """更新模型请求"""

    config: ModelConfig = Field(..., description="新的模型配置")


class InferenceRequestAPI(BaseModel):
    """API推理请求"""

    input_data: dict = Field(..., description="输入数据")
    parameters: dict = Field(default_factory=dict, description="推理参数")
    timeout: int = Field(default=30, ge=1, le=300, description="超时时间(秒)")
    priority: str = Field(default="normal", description="优先级")


class BatchInferenceRequest(BaseModel):
    """批量推理请求"""

    requests: List[InferenceRequestAPI] = Field(..., description="推理请求列表")


@router.post("/models/deploy", response_model=DeployModelResponse)
async def deploy_model(
    request: Request, deploy_request: DeployModelRequest
) -> DeployModelResponse:
    """部署模型到Kubernetes集群

    Args:
        request: FastAPI请求对象
        deploy_request: 部署请求

    Returns:
        部署响应
    """
    manager = request.app.state.manager
    metrics = request.app.state.metrics

    try:
        logger.info("收到模型部署请求", model_id=deploy_request.config.model_id)

        # 记录部署开始时间
        start_time = None
        if metrics:
            start_time = __import__("time").time()

        # 部署模型
        deployment_id = await manager.deploy_model(deploy_request.config)

        # 记录部署指标
        if metrics and start_time:
            duration = __import__("time").time() - start_time
            metrics.record_deployment(
                model_id=deploy_request.config.model_id,
                model_type=deploy_request.config.model_type.value,
                status="started",
                duration=duration,
            )

        return DeployModelResponse(
            deployment_id=deployment_id,
            message=f"模型 {deploy_request.config.model_id} 部署已启动",
        )

    except Exception as e:
        logger.error(
            "模型部署失败", model_id=deploy_request.config.model_id, error=str(e)
        )

        # 记录失败指标
        if metrics:
            metrics.record_deployment(
                model_id=deploy_request.config.model_id,
                model_type=deploy_request.config.model_type.value,
                status="failed",
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"模型部署失败: {str(e)}",
        )


@router.post("/models/{model_id}/inference", response_model=InferenceResult)
async def inference(
    request: Request, model_id: str, inference_request: InferenceRequestAPI
) -> InferenceResult:
    """执行模型推理

    Args:
        request: FastAPI请求对象
        model_id: 模型ID
        inference_request: 推理请求

    Returns:
        推理结果
    """
    manager = request.app.state.manager

    try:
        # 生成请求ID
        request_id = str(uuid.uuid4())

        # 构建推理请求
        inference_req = InferenceRequest(
            request_id=request_id,
            model_id=model_id,
            input_data=inference_request.input_data,
            parameters=inference_request.parameters,
            timeout=inference_request.timeout,
            priority=inference_request.priority,
        )

        logger.debug("收到推理请求", request_id=request_id, model_id=model_id)

        # 执行推理
        result = await manager.inference(inference_req)

        return result  # type: ignore

    except Exception as e:
        logger.error("推理执行失败", model_id=model_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"推理执行失败: {str(e)}",
        )


@router.post("/models/{model_id}/batch_inference", response_model=List[InferenceResult])
async def batch_inference(
    request: Request, model_id: str, batch_request: BatchInferenceRequest
) -> List[InferenceResult]:
    """批量推理

    Args:
        request: FastAPI请求对象
        model_id: 模型ID
        batch_request: 批量推理请求

    Returns:
        推理结果列表
    """
    manager = request.app.state.manager

    try:
        # 构建推理请求列表
        inference_requests = []
        for req in batch_request.requests:
            request_id = str(uuid.uuid4())
            inference_req = InferenceRequest(
                request_id=request_id,
                model_id=model_id,
                input_data=req.input_data,
                parameters=req.parameters,
                timeout=req.timeout,
                priority=req.priority,
            )
            inference_requests.append(inference_req)

        logger.info(
            "收到批量推理请求", model_id=model_id, batch_size=len(inference_requests)
        )

        # 执行批量推理
        results = []
        for inference_req in inference_requests:
            result = await manager.inference(inference_req)
            results.append(result)

        return results

    except Exception as e:
        logger.error("批量推理失败", model_id=model_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量推理失败: {str(e)}",
        )


@router.post("/models/{model_id}/scale")
async def scale_model(
    request: Request, model_id: str, scale_request: ScaleModelRequest
) -> dict:
    """扩缩容模型

    Args:
        request: FastAPI请求对象
        model_id: 模型ID
        scale_request: 扩缩容请求

    Returns:
        操作结果
    """
    manager = request.app.state.manager

    try:
        logger.info(
            "收到模型扩缩容请求", model_id=model_id, replicas=scale_request.replicas
        )

        await manager.scale_model(model_id, scale_request.replicas)

        return {
            "message": f"模型 {model_id} 扩缩容到 {scale_request.replicas} 个副本已启动"
        }

    except Exception as e:
        logger.error("模型扩缩容失败", model_id=model_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"模型扩缩容失败: {str(e)}",
        )


@router.put("/models/{model_id}", response_model=DeployModelResponse)
async def update_model(
    request: Request, model_id: str, update_request: UpdateModelRequest
) -> DeployModelResponse:
    """更新模型版本

    Args:
        request: FastAPI请求对象
        model_id: 模型ID
        update_request: 更新请求

    Returns:
        更新响应
    """
    manager = request.app.state.manager

    try:
        logger.info(
            "收到模型更新请求",
            model_id=model_id,
            new_version=update_request.config.version,
        )

        new_deployment_id = await manager.update_model(model_id, update_request.config)

        return DeployModelResponse(
            deployment_id=new_deployment_id,
            message=f"模型 {model_id} 更新到版本 {update_request.config.version} 已启动",
        )

    except Exception as e:
        logger.error("模型更新失败", model_id=model_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"模型更新失败: {str(e)}",
        )


@router.get("/models/{model_id}/status", response_model=Optional[DeploymentInfo])
async def get_model_status(request: Request, model_id: str) -> Optional[DeploymentInfo]:
    """获取模型状态

    Args:
        request: FastAPI请求对象
        model_id: 模型ID

    Returns:
        模型部署信息
    """
    manager = request.app.state.manager

    try:
        deployment_info = await manager.get_model_status(model_id)

        if not deployment_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"模型 {model_id} 未找到"
            )

        return deployment_info  # type: ignore

    except HTTPException:
        raise
    except Exception as e:
        logger.error("获取模型状态失败", model_id=model_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取模型状态失败: {str(e)}",
        )


@router.get("/models", response_model=List[DeploymentInfo])
async def list_models(request: Request) -> List[DeploymentInfo]:
    """列出所有部署的模型

    Args:
        request: FastAPI请求对象

    Returns:
        模型部署信息列表
    """
    manager = request.app.state.manager

    try:
        deployments = await manager.list_models()
        return deployments  # type: ignore

    except Exception as e:
        logger.error("列出模型失败", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"列出模型失败: {str(e)}",
        )


@router.delete("/models/{model_id}")
async def delete_model(request: Request, model_id: str) -> dict:
    """删除模型部署

    Args:
        request: FastAPI请求对象
        model_id: 模型ID

    Returns:
        操作结果
    """
    manager = request.app.state.manager

    try:
        logger.info("收到模型删除请求", model_id=model_id)

        await manager.delete_model(model_id)

        return {"message": f"模型 {model_id} 删除成功"}

    except Exception as e:
        logger.error("模型删除失败", model_id=model_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"模型删除失败: {str(e)}",
        )
