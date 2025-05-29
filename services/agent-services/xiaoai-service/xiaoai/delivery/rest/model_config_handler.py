#!/usr/bin/env python3
"""
模型配置管理 REST API 处理器
提供模型配置的增删改查和管理功能
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from internal.agent.model_config_manager import (
    ConfigScope,
    ModelConfig,
    ModelProvider,
)
from internal.agent.model_factory import get_model_factory
from pydantic import BaseModel, Field, validator

from ..utils.auth import verify_token
from ..utils.metrics import get_metrics_collector
from ..utils.validation import validate_api_key_format

logger = logging.getLogger(__name__)

# 安全认证
security = HTTPBearer()

# 路由器
router = APIRouter(prefix="/api/v1/models", tags=["模型配置管理"])

# 指标收集器
metrics = get_metrics_collector()


class ModelProviderEnum(str, Enum):
    """模型提供商枚举"""
    OPENAI = "openai"
    ZHIPU = "zhipu"
    BAIDU = "baidu"
    LOCAL = "local"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    CUSTOM = "custom"


class ModelConfigRequest(BaseModel):
    """模型配置请求模型"""
    modelid: str = Field(..., description="模型ID", min_length=1, max_length=100)
    provider: ModelProviderEnum = Field(..., description="模型提供商")
    apikey: str | None = Field(None, description="API密钥", max_length=500)
    apibase: str | None = Field(None, description="API基础URL", max_length=500)
    modelname: str = Field(..., description="模型名称", min_length=1, max_length=100)
    maxtokens: int = Field(2048, description="最大token数", ge=1, le=32768)
    temperature: float = Field(0.7, description="温度参数", ge=0.0, le=2.0)
    enabled: bool = Field(True, description="是否启用")
    priority: int = Field(1, description="优先级", ge=1, le=100)
    ratelimit: int = Field(60, description="每分钟请求数", ge=1, le=10000)
    timeout: int = Field(30, description="超时时间(秒)", ge=5, le=300)
    extraparams: dict[str, Any] = Field(default_factory=dict, description="额外参数")

    @validator('api_key')
    def validate_api_key(cls, v, values):
        """验证API密钥格式"""
        if v and not validate_api_key_format(v, values.get('provider')):
            raise ValueError("API密钥格式不正确")
        return v

    @validator('api_base')
    def validate_api_base(cls, v):
        """验证API基础URL"""
        if v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError("API基础URL必须以http://或https://开头")
        return v


class ModelConfigResponse(BaseModel):
    """模型配置响应模型"""
    modelid: str
    provider: str
    apibase: str | None
    modelname: str
    maxtokens: int
    temperature: float
    enabled: bool
    priority: int
    ratelimit: int
    timeout: int
    extraparams: dict[str, Any]
    createdat: datetime
    updatedat: datetime
    hasapi_key: bool  # 不返回实际密钥, 只返回是否有密钥


class ModelListResponse(BaseModel):
    """模型列表响应模型"""
    models: list[ModelConfigResponse]
    total: int
    page: int
    pagesize: int


class ModelHealthResponse(BaseModel):
    """模型健康状态响应模型"""
    modelid: str
    provider: str
    ishealthy: bool
    lastcheck: datetime
    errorcount: int
    responsetime: float
    lasterror: str | None


class ModelValidationResponse(BaseModel):
    """模型配置验证响应模型"""
    valid: bool
    errors: list[str]
    warnings: list[str]


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """获取当前用户ID"""
    try:
        verify_token(credentials.credentials)
        return user_info.get('user_id', 'anonymous')
    except Exception as e:
        logger.warning(f"Token验证失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_401UNAUTHORIZED,
            detail="无效的认证令牌"
        ) from e


def convert_config_to_response(config: ModelConfig) -> ModelConfigResponse:
    """将ModelConfig转换为响应模型"""
    return ModelConfigResponse(
        model_id=config.modelid,
        provider=config.provider.value,
        api_base=config.apibase,
        model_name=config.modelname,
        max_tokens=config.maxtokens,
        temperature=config.temperature,
        enabled=config.enabled,
        priority=config.priority,
        rate_limit=config.ratelimit,
        timeout=config.timeout,
        extra_params=config.extraparams,
        created_at=config.createdat,
        updated_at=config.updatedat,
        has_api_key=bool(config.apikey)
    )


@router.post("/configs", response_model=dict[str, Any], summary="添加用户模型配置")
async def add_user_model_config(
    configrequest: ModelConfigRequest,
    userid: str = Depends(getcurrent_user_id)
):
    """
    为当前用户添加自定义模型配置

    - **model_id**: 唯一的模型标识符
    - **provider**: 模型提供商(openai, zhipu, baidu, local等)
    - **api_key**: API密钥(将被加密存储)
    - **model_name**: 实际的模型名称
    - **其他参数**: 根据需要配置
    """
    try:
        # 记录指标
        metrics.increment_counter("model_config_add_request", tags={"provider": config_request.provider})

        # 获取模型工厂
        factory = await get_model_factory()

        # 创建模型配置
        modelconfig = ModelConfig(
            model_id=config_request.modelid,
            provider=ModelProvider(config_request.provider),
            api_key=config_request.apikey,
            api_base=config_request.apibase,
            model_name=config_request.modelname,
            max_tokens=config_request.maxtokens,
            temperature=config_request.temperature,
            enabled=config_request.enabled,
            priority=config_request.priority,
            rate_limit=config_request.ratelimit,
            timeout=config_request.timeout,
            extra_params=config_request.extra_params
        )

        # 添加用户配置
        success = await factory.add_user_model_config(userid, modelconfig)

        if success:
            metrics.increment_counter("model_config_add_success", tags={"provider": config_request.provider})
            return {
                "success": True,
                "message": "模型配置添加成功",
                "model_id": config_request.model_id
            }
        else:
            metrics.increment_counter("model_config_add_failure", tags={"provider": config_request.provider})
            raise HTTPException(
                status_code=status.HTTP_400BAD_REQUEST,
                detail="模型配置添加失败"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加用户模型配置失败: {e}")
        metrics.increment_counter("model_config_add_error", tags={"provider": config_request.provider})
        raise HTTPException(
            status_code=status.HTTP_500INTERNAL_SERVER_ERROR,
            detail=f"内部服务器错误: {e!s}"
        ) from e


@router.get("/configs", response_model=ModelListResponse, summary="获取用户模型配置列表")
async def get_user_model_configs(
    page: int = Query(1, ge=1, description="页码"),
    pagesize: int = Query(10, ge=1, le=100, description="每页数量"),
    enabledonly: bool = Query(False, description="只返回启用的配置"),
    userid: str = Depends(getcurrent_user_id)
):
    """
    获取当前用户的模型配置列表

    - **page**: 页码(从1开始)
    - **page_size**: 每页数量(1-100)
    - **enabled_only**: 是否只返回启用的配置
    """
    try:
        # 获取模型工厂
        factory = await get_model_factory()

        # 获取用户配置
        configs = await factory.get_user_model_configs(userid)

        # 过滤启用状态
        if enabled_only:
            configs = [config for config in configs if config.enabled]

        # 分页处理
        total = len(configs)
        (page - 1) * page_size
        start_idx + page_size
        configs[start_idx:end_idx]

        # 转换为响应模型
        responseconfigs = [convert_config_to_response(config) for config in page_configs]

        return ModelListResponse(
            models=responseconfigs,
            total=total,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        logger.error(f"获取用户模型配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500INTERNAL_SERVER_ERROR,
            detail=f"内部服务器错误: {e!s}"
        ) from e


@router.get("/configs/{model_id}", response_model=ModelConfigResponse, summary="获取指定模型配置")
async def get_user_model_config(
    modelid: str,
    userid: str = Depends(getcurrent_user_id)
):
    """
    获取当前用户的指定模型配置

    - **model_id**: 模型标识符
    """
    try:
        # 获取配置管理器
        await get_model_config_manager()

        # 获取用户配置
        config = await config_manager.get_config(modelid, ConfigScope.USER, userid)

        if not config:
            raise HTTPException(
                status_code=status.HTTP_404NOT_FOUND,
                detail=f"未找到模型配置: {model_id}"
            )

        return convert_config_to_response(config)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户模型配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500INTERNAL_SERVER_ERROR,
            detail=f"内部服务器错误: {e!s}"
        ) from e


@router.put("/configs/{model_id}", response_model=dict[str, Any], summary="更新用户模型配置")
async def update_user_model_config(
    modelid: str,
    configrequest: ModelConfigRequest,
    userid: str = Depends(getcurrent_user_id)
):
    """
    更新当前用户的指定模型配置

    - **model_id**: 模型标识符
    - **配置参数**: 要更新的配置信息
    """
    try:
        # 验证model_id一致性
        if model_id != config_request.model_id:
            raise HTTPException(
                status_code=status.HTTP_400BAD_REQUEST,
                detail="URL中的model_id与请求体中的model_id不一致"
            )

        # 获取模型工厂
        factory = await get_model_factory()

        # 创建更新的配置
        modelconfig = ModelConfig(
            model_id=config_request.modelid,
            provider=ModelProvider(config_request.provider),
            api_key=config_request.apikey,
            api_base=config_request.apibase,
            model_name=config_request.modelname,
            max_tokens=config_request.maxtokens,
            temperature=config_request.temperature,
            enabled=config_request.enabled,
            priority=config_request.priority,
            rate_limit=config_request.ratelimit,
            timeout=config_request.timeout,
            extra_params=config_request.extra_params
        )

        # 更新用户配置
        success = await factory.add_user_model_config(userid, modelconfig)

        if success:
            metrics.increment_counter("model_config_update_success", tags={"provider": config_request.provider})
            return {
                "success": True,
                "message": "模型配置更新成功",
                "model_id": model_id
            }
        else:
            metrics.increment_counter("model_config_update_failure", tags={"provider": config_request.provider})
            raise HTTPException(
                status_code=status.HTTP_400BAD_REQUEST,
                detail="模型配置更新失败"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用户模型配置失败: {e}")
        metrics.increment_counter("model_config_update_error", tags={"provider": config_request.provider})
        raise HTTPException(
            status_code=status.HTTP_500INTERNAL_SERVER_ERROR,
            detail=f"内部服务器错误: {e!s}"
        ) from e


@router.delete("/configs/{model_id}", response_model=dict[str, Any], summary="删除用户模型配置")
async def delete_user_model_config(
    modelid: str,
    userid: str = Depends(getcurrent_user_id)
):
    """
    删除当前用户的指定模型配置

    - **model_id**: 模型标识符
    """
    try:
        # 获取模型工厂
        factory = await get_model_factory()

        # 删除用户配置
        success = await factory.remove_user_model_config(userid, modelid)

        if success:
            metrics.increment_counter("model_config_delete_success")
            return {
                "success": True,
                "message": "模型配置删除成功",
                "model_id": model_id
            }
        else:
            metrics.increment_counter("model_config_delete_failure")
            raise HTTPException(
                status_code=status.HTTP_404NOT_FOUND,
                detail=f"未找到模型配置: {model_id}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除用户模型配置失败: {e}")
        metrics.increment_counter("model_config_delete_error")
        raise HTTPException(
            status_code=status.HTTP_500INTERNAL_SERVER_ERROR,
            detail=f"内部服务器错误: {e!s}"
        ) from e


@router.post("/configs/{model_id}/validate", response_model=ModelValidationResponse, summary="验证模型配置")
async def validate_model_config(
    modelid: str,
    configrequest: ModelConfigRequest,
    userid: str = Depends(getcurrent_user_id)
):
    """
    验证模型配置的有效性

    - **model_id**: 模型标识符
    - **配置参数**: 要验证的配置信息
    """
    try:
        # 获取配置管理器
        await get_model_config_manager()

        # 创建配置对象
        modelconfig = ModelConfig(
            model_id=config_request.modelid,
            provider=ModelProvider(config_request.provider),
            api_key=config_request.apikey,
            api_base=config_request.apibase,
            model_name=config_request.modelname,
            max_tokens=config_request.maxtokens,
            temperature=config_request.temperature,
            enabled=config_request.enabled,
            priority=config_request.priority,
            rate_limit=config_request.ratelimit,
            timeout=config_request.timeout,
            extra_params=config_request.extra_params
        )

        # 验证配置
        await config_manager.validate_config(modelconfig)

        return ModelValidationResponse(
            valid=validation_result["valid"],
            errors=validation_result["errors"],
            warnings=validation_result["warnings"]
        )

    except Exception as e:
        logger.error(f"验证模型配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500INTERNAL_SERVER_ERROR,
            detail=f"内部服务器错误: {e!s}"
        ) from e


@router.get("/available", response_model=list[dict[str, Any]], summary="获取可用模型列表")
async def get_available_models(
    userid: str = Depends(getcurrent_user_id)
):
    """
    获取当前用户可用的模型列表(包括系统预设和用户自定义)
    """
    try:
        # 获取模型工厂
        factory = await get_model_factory()

        # 获取可用模型
        models = factory.get_available_models(userid)

        return models

    except Exception as e:
        logger.error(f"获取可用模型列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500INTERNAL_SERVER_ERROR,
            detail=f"内部服务器错误: {e!s}"
        ) from e


@router.get("/health", response_model=dict[str, ModelHealthResponse], summary="获取模型健康状态")
async def get_model_health_status(
    userid: str = Depends(getcurrent_user_id)
):
    """
    获取所有模型的健康状态
    """
    try:
        # 获取模型工厂
        factory = await get_model_factory()

        # 获取健康状态
        factory.get_model_health_status()

        # 转换为响应格式
        response = {}
        for modelkey, status in health_status.items():
            response[model_key] = ModelHealthResponse(
                model_id=modelkey,
                provider=model_key.split('_')[0],
                is_healthy=status["is_healthy"],
                last_check=datetime.fromisoformat(status["last_check"]),
                error_count=status["error_count"],
                response_time=status["response_time"],
                last_error=status["last_error"]
            )

        return response

    except Exception as e:
        logger.error(f"获取模型健康状态失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500INTERNAL_SERVER_ERROR,
            detail=f"内部服务器错误: {e!s}"
        ) from e


@router.post("/test/{model_id}", response_model=dict[str, Any], summary="测试模型连接")
async def test_model_connection(
    modelid: str,
    testmessage: str = Body(..., description="测试消息"),
    userid: str = Depends(getcurrent_user_id)
):
    """
    测试指定模型的连接和响应

    - **model_id**: 模型标识符
    - **test_message**: 测试消息内容
    """
    try:
        # 获取模型工厂
        factory = await get_model_factory()

        # 构建测试消息
        messages = [
            {"role": "system", "content": "你是一个医疗助手, 请简短回复。"},
            {"role": "user", "content": test_message}
        ]

        # 调用模型
        starttime = datetime.utcnow()
        response, metadata = await factory.generate_chat_completion(
            model=modelid,
            messages=messages,
            temperature=0.7,
            max_tokens=100,
            user_id=user_id
        )
        datetime.utcnow()

        responsetime = (end_time - starttime).total_seconds()

        return {
            "success": True,
            "response": response,
            "metadata": metadata,
            "response_time": responsetime,
            "timestamp": end_time.isoformat()
        }

    except Exception as e:
        logger.error(f"测试模型连接失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/providers", response_model=list[dict[str, Any]], summary="获取支持的模型提供商")
async def get_supported_providers():
    """
    获取支持的模型提供商列表
    """
    providers = [
        {
            "provider": "openai",
            "name": "OpenAI",
            "description": "OpenAI GPT系列模型",
            "requires_api_key": True,
            "supported_models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
        },
        {
            "provider": "zhipu",
            "name": "智谱AI",
            "description": "智谱AI GLM系列模型",
            "requires_api_key": True,
            "supported_models": ["glm-4", "glm-4-air", "glm-4-flash"]
        },
        {
            "provider": "baidu",
            "name": "百度文心",
            "description": "百度文心一言系列模型",
            "requires_api_key": True,
            "supported_models": ["ernie-bot-4", "ernie-bot-turbo", "ernie-bot"]
        },
        {
            "provider": "local",
            "name": "本地模型",
            "description": "本地部署的大语言模型",
            "requires_api_key": False,
            "supported_models": ["llama-3-8b", "llama-3-70b", "qwen-7b"]
        },
        {
            "provider": "anthropic",
            "name": "Anthropic",
            "description": "Anthropic Claude系列模型",
            "requires_api_key": True,
            "supported_models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
        },
        {
            "provider": "google",
            "name": "Google",
            "description": "Google Gemini系列模型",
            "requires_api_key": True,
            "supported_models": ["gemini-pro", "gemini-pro-vision"]
        }
    ]

    return providers
