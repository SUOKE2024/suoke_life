#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型配置管理 REST API 处理器
提供模型配置的增删改查和管理功能
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status, Query, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from enum import Enum

from internal.agent.model_config_manager import (
    get_model_config_manager,
    ModelConfig,
    ModelProvider,
    ConfigScope
)
from internal.agent.model_factory import get_model_factory
from pkg.utils.auth import verify_token, get_current_user
from pkg.utils.validation import validate_api_key_format
from pkg.utils.metrics import get_metrics_collector

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
    model_id: str = Field(..., description="模型ID", min_length=1, max_length=100)
    provider: ModelProviderEnum = Field(..., description="模型提供商")
    api_key: Optional[str] = Field(None, description="API密钥", max_length=500)
    api_base: Optional[str] = Field(None, description="API基础URL", max_length=500)
    model_name: str = Field(..., description="模型名称", min_length=1, max_length=100)
    max_tokens: int = Field(2048, description="最大token数", ge=1, le=32768)
    temperature: float = Field(0.7, description="温度参数", ge=0.0, le=2.0)
    enabled: bool = Field(True, description="是否启用")
    priority: int = Field(1, description="优先级", ge=1, le=100)
    rate_limit: int = Field(60, description="每分钟请求数", ge=1, le=10000)
    timeout: int = Field(30, description="超时时间（秒）", ge=5, le=300)
    extra_params: Dict[str, Any] = Field(default_factory=dict, description="额外参数")

    @validator('api_key')
    def validate_api_key(cls, v, values):
        """验证API密钥格式"""
        if v and not validate_api_key_format(v, values.get('provider')):
            raise ValueError(f"API密钥格式不正确")
        return v

    @validator('api_base')
    def validate_api_base(cls, v):
        """验证API基础URL"""
        if v and not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError("API基础URL必须以http://或https://开头")
        return v


class ModelConfigResponse(BaseModel):
    """模型配置响应模型"""
    model_id: str
    provider: str
    api_base: Optional[str]
    model_name: str
    max_tokens: int
    temperature: float
    enabled: bool
    priority: int
    rate_limit: int
    timeout: int
    extra_params: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    has_api_key: bool  # 不返回实际密钥，只返回是否有密钥


class ModelListResponse(BaseModel):
    """模型列表响应模型"""
    models: List[ModelConfigResponse]
    total: int
    page: int
    page_size: int


class ModelHealthResponse(BaseModel):
    """模型健康状态响应模型"""
    model_id: str
    provider: str
    is_healthy: bool
    last_check: datetime
    error_count: int
    response_time: float
    last_error: Optional[str]


class ModelValidationResponse(BaseModel):
    """模型配置验证响应模型"""
    valid: bool
    errors: List[str]
    warnings: List[str]


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """获取当前用户ID"""
    try:
        user_info = verify_token(credentials.credentials)
        return user_info.get('user_id', 'anonymous')
    except Exception as e:
        logger.warning(f"Token验证失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌"
        )


def convert_config_to_response(config: ModelConfig) -> ModelConfigResponse:
    """将ModelConfig转换为响应模型"""
    return ModelConfigResponse(
        model_id=config.model_id,
        provider=config.provider.value,
        api_base=config.api_base,
        model_name=config.model_name,
        max_tokens=config.max_tokens,
        temperature=config.temperature,
        enabled=config.enabled,
        priority=config.priority,
        rate_limit=config.rate_limit,
        timeout=config.timeout,
        extra_params=config.extra_params,
        created_at=config.created_at,
        updated_at=config.updated_at,
        has_api_key=bool(config.api_key)
    )


@router.post("/configs", response_model=Dict[str, Any], summary="添加用户模型配置")
async def add_user_model_config(
    config_request: ModelConfigRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    为当前用户添加自定义模型配置
    
    - **model_id**: 唯一的模型标识符
    - **provider**: 模型提供商（openai, zhipu, baidu, local等）
    - **api_key**: API密钥（将被加密存储）
    - **model_name**: 实际的模型名称
    - **其他参数**: 根据需要配置
    """
    try:
        # 记录指标
        metrics.increment_counter("model_config_add_request", tags={"provider": config_request.provider})
        
        # 获取模型工厂
        factory = await get_model_factory()
        
        # 创建模型配置
        model_config = ModelConfig(
            model_id=config_request.model_id,
            provider=ModelProvider(config_request.provider),
            api_key=config_request.api_key,
            api_base=config_request.api_base,
            model_name=config_request.model_name,
            max_tokens=config_request.max_tokens,
            temperature=config_request.temperature,
            enabled=config_request.enabled,
            priority=config_request.priority,
            rate_limit=config_request.rate_limit,
            timeout=config_request.timeout,
            extra_params=config_request.extra_params
        )
        
        # 添加用户配置
        success = await factory.add_user_model_config(user_id, model_config)
        
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
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="模型配置添加失败"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加用户模型配置失败: {e}")
        metrics.increment_counter("model_config_add_error", tags={"provider": config_request.provider})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"内部服务器错误: {str(e)}"
        )


@router.get("/configs", response_model=ModelListResponse, summary="获取用户模型配置列表")
async def get_user_model_configs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    enabled_only: bool = Query(False, description="只返回启用的配置"),
    user_id: str = Depends(get_current_user_id)
):
    """
    获取当前用户的模型配置列表
    
    - **page**: 页码（从1开始）
    - **page_size**: 每页数量（1-100）
    - **enabled_only**: 是否只返回启用的配置
    """
    try:
        # 获取模型工厂
        factory = await get_model_factory()
        
        # 获取用户配置
        configs = await factory.get_user_model_configs(user_id)
        
        # 过滤启用状态
        if enabled_only:
            configs = [config for config in configs if config.enabled]
        
        # 分页处理
        total = len(configs)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_configs = configs[start_idx:end_idx]
        
        # 转换为响应模型
        response_configs = [convert_config_to_response(config) for config in page_configs]
        
        return ModelListResponse(
            models=response_configs,
            total=total,
            page=page,
            page_size=page_size
        )
    
    except Exception as e:
        logger.error(f"获取用户模型配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"内部服务器错误: {str(e)}"
        )


@router.get("/configs/{model_id}", response_model=ModelConfigResponse, summary="获取指定模型配置")
async def get_user_model_config(
    model_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    获取当前用户的指定模型配置
    
    - **model_id**: 模型标识符
    """
    try:
        # 获取配置管理器
        config_manager = await get_model_config_manager()
        
        # 获取用户配置
        config = await config_manager.get_config(model_id, ConfigScope.USER, user_id)
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"未找到模型配置: {model_id}"
            )
        
        return convert_config_to_response(config)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户模型配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"内部服务器错误: {str(e)}"
        )


@router.put("/configs/{model_id}", response_model=Dict[str, Any], summary="更新用户模型配置")
async def update_user_model_config(
    model_id: str,
    config_request: ModelConfigRequest,
    user_id: str = Depends(get_current_user_id)
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
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL中的model_id与请求体中的model_id不一致"
            )
        
        # 获取模型工厂
        factory = await get_model_factory()
        
        # 创建更新的配置
        model_config = ModelConfig(
            model_id=config_request.model_id,
            provider=ModelProvider(config_request.provider),
            api_key=config_request.api_key,
            api_base=config_request.api_base,
            model_name=config_request.model_name,
            max_tokens=config_request.max_tokens,
            temperature=config_request.temperature,
            enabled=config_request.enabled,
            priority=config_request.priority,
            rate_limit=config_request.rate_limit,
            timeout=config_request.timeout,
            extra_params=config_request.extra_params
        )
        
        # 更新用户配置
        success = await factory.add_user_model_config(user_id, model_config)
        
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
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="模型配置更新失败"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新用户模型配置失败: {e}")
        metrics.increment_counter("model_config_update_error", tags={"provider": config_request.provider})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"内部服务器错误: {str(e)}"
        )


@router.delete("/configs/{model_id}", response_model=Dict[str, Any], summary="删除用户模型配置")
async def delete_user_model_config(
    model_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    删除当前用户的指定模型配置
    
    - **model_id**: 模型标识符
    """
    try:
        # 获取模型工厂
        factory = await get_model_factory()
        
        # 删除用户配置
        success = await factory.remove_user_model_config(user_id, model_id)
        
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
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"未找到模型配置: {model_id}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除用户模型配置失败: {e}")
        metrics.increment_counter("model_config_delete_error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"内部服务器错误: {str(e)}"
        )


@router.post("/configs/{model_id}/validate", response_model=ModelValidationResponse, summary="验证模型配置")
async def validate_model_config(
    model_id: str,
    config_request: ModelConfigRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    验证模型配置的有效性
    
    - **model_id**: 模型标识符
    - **配置参数**: 要验证的配置信息
    """
    try:
        # 获取配置管理器
        config_manager = await get_model_config_manager()
        
        # 创建配置对象
        model_config = ModelConfig(
            model_id=config_request.model_id,
            provider=ModelProvider(config_request.provider),
            api_key=config_request.api_key,
            api_base=config_request.api_base,
            model_name=config_request.model_name,
            max_tokens=config_request.max_tokens,
            temperature=config_request.temperature,
            enabled=config_request.enabled,
            priority=config_request.priority,
            rate_limit=config_request.rate_limit,
            timeout=config_request.timeout,
            extra_params=config_request.extra_params
        )
        
        # 验证配置
        validation_result = await config_manager.validate_config(model_config)
        
        return ModelValidationResponse(
            valid=validation_result["valid"],
            errors=validation_result["errors"],
            warnings=validation_result["warnings"]
        )
    
    except Exception as e:
        logger.error(f"验证模型配置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"内部服务器错误: {str(e)}"
        )


@router.get("/available", response_model=List[Dict[str, Any]], summary="获取可用模型列表")
async def get_available_models(
    user_id: str = Depends(get_current_user_id)
):
    """
    获取当前用户可用的模型列表（包括系统预设和用户自定义）
    """
    try:
        # 获取模型工厂
        factory = await get_model_factory()
        
        # 获取可用模型
        models = factory.get_available_models(user_id)
        
        return models
    
    except Exception as e:
        logger.error(f"获取可用模型列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"内部服务器错误: {str(e)}"
        )


@router.get("/health", response_model=Dict[str, ModelHealthResponse], summary="获取模型健康状态")
async def get_model_health_status(
    user_id: str = Depends(get_current_user_id)
):
    """
    获取所有模型的健康状态
    """
    try:
        # 获取模型工厂
        factory = await get_model_factory()
        
        # 获取健康状态
        health_status = factory.get_model_health_status()
        
        # 转换为响应格式
        response = {}
        for model_key, status in health_status.items():
            response[model_key] = ModelHealthResponse(
                model_id=model_key,
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"内部服务器错误: {str(e)}"
        )


@router.post("/test/{model_id}", response_model=Dict[str, Any], summary="测试模型连接")
async def test_model_connection(
    model_id: str,
    test_message: str = Body(..., description="测试消息"),
    user_id: str = Depends(get_current_user_id)
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
            {"role": "system", "content": "你是一个医疗助手，请简短回复。"},
            {"role": "user", "content": test_message}
        ]
        
        # 调用模型
        start_time = datetime.utcnow()
        response, metadata = await factory.generate_chat_completion(
            model=model_id,
            messages=messages,
            temperature=0.7,
            max_tokens=100,
            user_id=user_id
        )
        end_time = datetime.utcnow()
        
        response_time = (end_time - start_time).total_seconds()
        
        return {
            "success": True,
            "response": response,
            "metadata": metadata,
            "response_time": response_time,
            "timestamp": end_time.isoformat()
        }
    
    except Exception as e:
        logger.error(f"测试模型连接失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.get("/providers", response_model=List[Dict[str, Any]], summary="获取支持的模型提供商")
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