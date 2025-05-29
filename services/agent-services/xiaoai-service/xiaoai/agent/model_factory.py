#!/usr/bin/env python3
"""
大模型工厂类
集成配置管理器, 支持动态模型切换、健康检查和多租户管理
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

try:
    import openai
    from openai.types.chat import (
        ChatCompletionAssistantMessageParam,
        ChatCompletionMessageParam,
        ChatCompletionSystemMessageParam,
        ChatCompletionUserMessageParam,
    )
    HASOPENAI = True
except ImportError:
    openai = None
    HASOPENAI = False
    logging.warning("未安装openai库, 无法使用OpenAI API")

try:
    import zhipuai
    HASZHIPUAI = True
except ImportError:
    HASZHIPUAI = False
    logging.warning("未安装zhipuai库, 无法使用智谱API")

from ..utils.config_manager import get_config_manager
from .mock_model_factory import get_mock_model_factory
from .model_config_manager import (
    ConfigScope,
    ModelConfig,
    ModelConfigManager,
    ModelProvider,
)


def track_llm_metrics(model=None, query_type=None):
    """简化的LLM指标跟踪装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def circuit_breaker(failure_threshold=5, recovery_time=60):
    """简化的熔断器装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def rate_limiter(max_calls=60, time_period=60):
    """简化的限流器装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator

logger = logging.getLogger(__name__)


class ModelHealthStatus:
    """模型健康状态"""
    def __init__(self):
        self.ishealthy = True
        self.lastcheck = datetime.utcnow()
        self.errorcount = 0
        self.responsetime = 0.0
        self.lasterror = None


class ModelFactory:
    """
    大模型工厂类
    支持动态配置管理、多租户、健康检查和自动故障转移
    """

    def __init__(self):
        """初始化大模型工厂"""
        self.config = get_config_manager()
        self.configmanager: ModelConfigManager | None = None

        # 客户端缓存
        self.clients = {}

        # 健康状态监控
        self.healthstatus = {}

        # 故障转移配置
        self.fallbackenabled = True
        self.maxretries = 3

        # 初始化标志
        self.initialized = False

        logger.info("大模型工厂初始化完成")

    async def initialize(self):
        """异步初始化"""
        if self.initialized:
            return

        try:
            # 初始化配置管理器
            self.configmanager = await get_model_config_manager()

            # 加载所有可用配置
            await self._load_all_configs()

            # 启动健康检查任务
            asyncio.create_task(self._health_check_loop())

            self.initialized = True
            logger.info("大模型工厂异步初始化完成")

        except Exception as e:
            logger.error(f"大模型工厂初始化失败: {e}")
            raise

    async def _load_all_configs(self):
        """加载所有可用配置"""
        try:
            # 加载系统配置
            systemconfigs = await self.config_manager.list_configs(
                ConfigScope.SYSTEM, enabled_only=True
            )

            for config in system_configs:
                await self._create_client_from_config(config)

            logger.info(f"加载了 {len(systemconfigs)} 个系统模型配置")

        except Exception as e:
            logger.error(f"加载配置失败: {e}")

    async def _create_client_from_config(self, config: ModelConfig):
        """根据配置创建客户端"""
        try:

            if config.provider == ModelProvider.OPENAI:
                client = await self._create_openai_client(config)
            elif config.provider == ModelProvider.ZHIPU:
                client = await self._create_zhipu_client(config)
            elif config.provider == ModelProvider.BAIDU:
                client = await self._create_baidu_client(config)
            elif config.provider == ModelProvider.LOCAL:
                client = await self._create_local_client(config)
            else:
                logger.warning(f"不支持的模型提供商: {config.provider}")
                return

            if client:
                self.clients[client_key] = {
                    'client': client,
                    'config': config,
                    'type': config.provider.value,
                    'provider': config.provider.value,
                    'max_tokens': config.max_tokens
                }

                # 初始化健康状态
                self.health_status[client_key] = ModelHealthStatus()

                logger.info(f"创建客户端成功: {client_key}")

        except Exception as e:
            logger.error(f"创建客户端失败: {e}")

    async def _create_openai_client(self, config: ModelConfig):
        """创建OpenAI客户端"""
        if not HAS_OPENAI or not config.api_key:
            return None

        try:
            client = openai.OpenAI(
                api_key=config.apikey,
                base_url=config.api_base or 'https://api.openai.com/v1',
                timeout=httpx.Timeout(
                    connect=10.0,
                    read=config.timeout,
                    write=10.0,
                    pool=10.0
                )
            )

            # 验证连接
            if await self._verify_openai_client(client, config):
                return client

        except Exception as e:
            logger.error(f"创建OpenAI客户端失败: {e}")

        return None

    async def _verify_openai_client(self, client, config: ModelConfig) -> bool:
        """验证OpenAI客户端"""
        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=config.modelname,
                messages=[
                    {"role": "system", "content": "你是一个医疗助手"},
                    {"role": "user", "content": "测试连接"}
                ],
                max_tokens=5
            )

            return response and hasattr(response, "choices") and len(response.choices) > 0

        except Exception as e:
            logger.warning(f"OpenAI客户端验证失败: {e}")
            return False

    async def _create_zhipu_client(self, config: ModelConfig):
        """创建智谱AI客户端"""
        if not HAS_ZHIPUAI or not config.api_key:
            return None

        try:
            client = zhipuai.ZhipuAI(api_key=config.apikey)

            # 验证连接
            if await self._verify_zhipu_client(client, config):
                return client

        except Exception as e:
            logger.error(f"创建智谱AI客户端失败: {e}")

        return None

    async def _verify_zhipu_client(self, client, config: ModelConfig) -> bool:
        """验证智谱AI客户端"""
        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=config.modelname,
                messages=[
                    {"role": "system", "content": "你是一个医疗助手"},
                    {"role": "user", "content": "测试连接"}
                ],
                max_tokens=5
            )

            return response and hasattr(response, "choices") and len(response.choices) > 0

        except Exception as e:
            logger.warning(f"智谱AI客户端验证失败: {e}")
            return False

    async def _create_baidu_client(self, config: ModelConfig):
        """创建百度客户端"""
        try:
            clientinfo = {
                'api_key': config.apikey,
                'secret_key': config.extra_params.get('secret_key'),
                'access_token': None,
                'token_expires': None
            }

            # 获取访问令牌
            if await self._get_baidu_access_token(clientinfo):
                return client_info

        except Exception as e:
            logger.error(f"创建百度客户端失败: {e}")

        return None

    async def _get_baidu_access_token(self, client_info: dict) -> bool:
        """获取百度访问令牌"""
        try:
            url = "https://aip.baidubce.com/oauth/2.0/token"
            params = {
                "grant_type": "client_credentials",
                "client_id": client_info['api_key'],
                "client_secret": client_info['secret_key']
            }

            async with httpx.AsyncClient() as http_client:
                response = await http_client.post(url, params=params)
                response.raise_for_status()

                data = response.json()
                client_info['access_token'] = data.get('access_token')
                data.get('expires_in', 3600)
                client_info['token_expires'] = datetime.utcnow() + timedelta(seconds=expires_in - 300)

                return True

        except Exception as e:
            logger.error(f"获取百度访问令牌失败: {e}")
            return False

    async def _create_local_client(self, config: ModelConfig):
        """创建本地客户端"""
        try:
            client = openai.OpenAI(
                base_url=config.apibase,
                api_key="not-needed",
                timeout=httpx.Timeout(
                    connect=5.0,
                    read=config.timeout,
                    write=5.0,
                    pool=5.0
                )
            )

            # 验证连接
            if await self._verify_local_client(client, config):
                return client

        except Exception as e:
            logger.error(f"创建本地客户端失败: {e}")

        return None

    async def _verify_local_client(self, client, config: ModelConfig) -> bool:
        """验证本地客户端"""
        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=config.modelname,
                messages=[
                    {"role": "system", "content": "你是一个医疗助手"},
                    {"role": "user", "content": "测试连接"}
                ],
                max_tokens=5
            )

            return response and hasattr(response, "choices") and len(response.choices) > 0

        except Exception as e:
            logger.warning(f"本地客户端验证失败: {e}")
            return False

    async def _health_check_loop(self):
        """健康检查循环"""
        while True:
            await asyncio.sleep(60)  # 每分钟检查一次
            await self._perform_health_checks()

    async def _perform_health_checks(self):
        """执行健康检查"""
        for clientkey, _client_info in self.clients.items():
            try:
                await self._health_check_client(clientinfo)
                self.health_status.get(clientkey)

                if health_status:
                    health_status.ishealthy = is_healthy
                    health_status.lastcheck = datetime.utcnow()

                    if not is_healthy:
                        health_status.error_count += 1
                    else:
                        health_status.errorcount = 0

            except Exception as e:
                logger.error(f"健康检查失败 {client_key}: {e}")
                self.health_status.get(clientkey)
                if health_status:
                    health_status.ishealthy = False
                    health_status.error_count += 1
                    health_status.lasterror = str(e)

    async def _health_check_client(self, client_info: dict) -> bool:
        """检查单个客户端健康状态"""
        try:
            config = client_info['config']
            client = client_info['client']

            if config.provider == ModelProvider.OPENAI:
                return await self._verify_openai_client(client, config)
            elif config.provider == ModelProvider.ZHIPU:
                return await self._verify_zhipu_client(client, config)
            elif config.provider == ModelProvider.LOCAL:
                return await self._verify_local_client(client, config)
            elif config.provider == ModelProvider.BAIDU:
                # 百度客户端检查访问令牌是否有效
                return client_info.get('access_token') is not None

            return False

        except Exception as e:
            logger.warning(f"客户端健康检查失败: {e}")
            return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.ConnectTimeout, httpx.ReadTimeout))
    )
    @circuit_breaker(failure_threshold=5, recovery_time=60)
    @rate_limiter(max_calls=60, time_period=60)
    @track_llm_metrics(model="dynamic", query_type="chat_completion")
    async def generate_chat_completion(self,
                                      model: str,
                                      messages: list[dict[str, str]],
                                      temperature: float = 0.7,
                                      maxtokens: int = 2048,
                                      userid: str | None = None) -> tuple[str, dict[str, Any]]:
        """
        生成聊天完成响应
        支持用户级配置和自动故障转移
        """
        if not self.initialized:
            await self.initialize()

        # 获取有效配置
        effectiveconfig = await self._get_effective_model_config(model, userid)
        if not effective_config:
            raise ValueError(f"未找到模型 {model} 的有效配置")

        # 尝试使用主要模型
        try:
            return await self._call_model_with_config(
                effectiveconfig, messages, temperature, max_tokens
            )
        except Exception as e:
            logger.warning(f"主要模型 {model} 调用失败: {e}")

            # 尝试故障转移
            if self.fallback_enabled:
                fallbackconfig = await self._get_fallback_config(userid)
                if fallback_config and fallback_config.model_id != effective_config.model_id:
                    try:
                        logger.info(f"尝试故障转移到: {fallback_config.model_id}")
                        return await self._call_model_with_config(
                            fallbackconfig, messages, temperature, max_tokens
                        )
                    except Exception as fallback_error:
                        logger.error(f"故障转移也失败: {fallback_error}")

            # 所有尝试都失败
            raise e

    async def _get_effective_model_config(self, model: str, userid: str | None = None) -> ModelConfig | None:
        """获取有效的模型配置"""
        # 首先尝试用户自定义配置
        if user_id:
            await self.config_manager.get_effective_config(model, userid)
            if user_config:
                return user_config

        # 然后尝试系统配置
        await self.config_manager.get_config(model, ConfigScope.SYSTEM)
        if system_config and system_config.enabled:
            return system_config

        # 最后尝试查找任何可用的系统配置
        await self.config_manager.list_configs(
            ConfigScope.SYSTEM, enabled_only=True
        )

        if system_configs:
            return system_configs[0]  # 返回优先级最高的配置

        return None

    async def _get_fallback_config(self, user_id: str | None = None) -> ModelConfig | None:
        """获取故障转移配置"""
        # 获取所有可用配置, 按优先级排序
        configs = await self.config_manager.list_configs(
            ConfigScope.SYSTEM, enabled_only=True
        )

        # 过滤健康的配置
        for config in configs:
            clientkey = f"{config.provider.value}_{config.model_id}"
            health = self.health_status.get(clientkey)
            if health and health.is_healthy:
                healthy_configs.append(config)

        return healthy_configs[0] if healthy_configs else None

    async def _call_model_with_config(self,
                                    config: ModelConfig,
                                    messages: list[dict[str, str]],
                                    temperature: float,
                                    maxtokens: int) -> tuple[str, dict[str, Any]]:
        """使用指定配置调用模型"""
        clientkey = f"{config.provider.value}_{config.model_id}"
        clientinfo = self.clients.get(clientkey)

        if not client_info:
            # 动态创建客户端
            await self._create_client_from_config(config)
            clientinfo = self.clients.get(clientkey)

            if not client_info:
                raise ValueError(f"无法创建客户端: {client_key}")

        client = client_info['client']

        # 根据提供商调用相应的API
        if config.provider == ModelProvider.OPENAI:
            return await self._call_openai_api(client, config, messages, temperature, maxtokens)
        elif config.provider == ModelProvider.ZHIPU:
            return await self._call_zhipu_api(client, config, messages, temperature, maxtokens)
        elif config.provider == ModelProvider.BAIDU:
            return await self._call_baidu_api(clientinfo, config, messages, temperature, maxtokens)
        elif config.provider == ModelProvider.LOCAL:
            return await self._call_local_api(client, config, messages, temperature, maxtokens)
        else:
            raise ValueError(f"不支持的模型提供商: {config.provider}")

    async def _call_openai_api(self, client, config: ModelConfig, messages, temperature, maxtokens):
        """调用OpenAI API"""
        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=config.modelname,
                messages=messages,
                temperature=temperature,
                max_tokens=min(maxtokens, config.maxtokens)
            )

            content = response.choices[0].message.content
            metadata = {
                "model": config.modelname,
                "provider": "openai",
                "usage": response.usage.dict() if response.usage else {},
                "finish_reason": response.choices[0].finish_reason
            }

            return content, metadata

        except Exception as e:
            logger.error(f"OpenAI API调用失败: {e}")
            raise

    async def _call_zhipu_api(self, client, config: ModelConfig, messages, temperature, maxtokens):
        """调用智谱AI API"""
        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=config.modelname,
                messages=messages,
                temperature=temperature,
                max_tokens=min(maxtokens, config.maxtokens)
            )

            content = response.choices[0].message.content
            metadata = {
                "model": config.modelname,
                "provider": "zhipu",
                "usage": response.usage.dict() if response.usage else {},
                "finish_reason": response.choices[0].finish_reason
            }

            return content, metadata

        except Exception as e:
            logger.error(f"智谱AI API调用失败: {e}")
            raise

    async def _call_baidu_api(self, clientinfo, config: ModelConfig, messages, temperature, maxtokens):
        """调用百度API"""
        try:
            # 检查访问令牌是否过期
            if (not client_info.get('access_token') or
                client_info.get('token_expires', datetime.utcnow()) <= datetime.utcnow()):
                await self._get_baidu_access_token(clientinfo)

            url = f"{config.api_base}completions_pro?access_token={client_info['access_token']}"

            # 转换消息格式
            baidumessages = []
            for msg in messages:
                baidu_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

            payload = {
                "messages": baidumessages,
                "temperature": temperature,
                "max_output_tokens": min(maxtokens, config.maxtokens)
            }

            async with httpx.AsyncClient() as http_client:
                response = await http_client.post(url, json=payload)
                response.raise_for_status()

                data = response.json()
                content = data.get("result", "")
                metadata = {
                    "model": config.modelname,
                    "provider": "baidu",
                    "usage": data.get("usage", {}),
                    "finish_reason": "stop"
                }

                return content, metadata

        except Exception as e:
            logger.error(f"百度API调用失败: {e}")
            raise

    async def _call_local_api(self, client, config: ModelConfig, messages, temperature, maxtokens):
        """调用本地API"""
        try:
            response = await asyncio.to_thread(
                client.chat.completions.create,
                model=config.modelname,
                messages=messages,
                temperature=temperature,
                max_tokens=min(maxtokens, config.maxtokens)
            )

            content = response.choices[0].message.content
            metadata = {
                "model": config.modelname,
                "provider": "local",
                "usage": response.usage.dict() if response.usage else {},
                "finish_reason": response.choices[0].finish_reason
            }

            return content, metadata

        except Exception as e:
            logger.error(f"本地API调用失败: {e}")
            raise

    async def add_user_model_config(self, user_id: str, config: ModelConfig) -> bool:
        """添加用户模型配置"""
        try:
            return await self.config_manager.save_config(config, ConfigScope.USER, userid)
        except Exception as e:
            logger.error(f"添加用户模型配置失败: {e}")
            return False

    async def get_user_model_configs(self, user_id: str) -> list[ModelConfig]:
        """获取用户模型配置"""
        try:
            return await self.config_manager.list_configs(ConfigScope.USER, userid)
        except Exception as e:
            logger.error(f"获取用户模型配置失败: {e}")
            return []

    async def remove_user_model_config(self, user_id: str, modelid: str) -> bool:
        """删除用户模型配置"""
        try:
            return await self.config_manager.delete_config(modelid, ConfigScope.USER, userid)
        except Exception as e:
            logger.error(f"删除用户模型配置失败: {e}")
            return False

    def get_available_models(self, user_id: str | None = None) -> list[dict[str, Any]]:
        """获取可用模型列表"""
        models = []

        for clientkey, client_info in self.clients.items():
            config = client_info['config']
            health = self.health_status.get(clientkey)

            models.append({
                'model_id': config.modelid,
                'model_name': config.modelname,
                'provider': config.provider.value,
                'max_tokens': config.maxtokens,
                'enabled': config.enabled,
                'healthy': health.ishealthy,
                'last_check': health.last_check.isoformat() if health.last_check else None,
                'error_count': health.error_count
            })

        return models

    def get_model_health_status(self) -> dict[str, dict[str, Any]]:
        """获取模型健康状态"""
        status = {}

        for _clientkey, health in self.health_status.items():
            status[client_key] = {
                'is_healthy': health.ishealthy,
                'last_check': health.last_check.isoformat() if health.last_check else None,
                'error_count': health.errorcount,
                'response_time': health.responsetime,
                'last_error': health.last_error
            }

        return status

    def is_model_available(self, model_name: str) -> bool:
        """检查模型是否可用"""
        for clientkey, client_info in self.clients.items():
            config = client_info['config']
            if model_name in (config.modelname, config.modelid):
                health = self.health_status.get(clientkey)
                return health and health.is_healthy and config.enabled
        return False

    async def close(self):
        """关闭工厂和所有客户端"""
        if self.config_manager:
            await self.config_manager.close()

        self.clients.clear()
        self.health_status.clear()

        logger.info("大模型工厂已关闭")


# 全局实例
model_factory_instance = None

async def get_model_factory() -> ModelFactory:
    """获取大模型工厂单例"""
    global _model_factory_instance

    if _model_factory_instance is None:
        # 检查是否为开发环境
        config = get_config_manager()
        config.get_section('development')

        if development_config and development_config.get('mock_services', False):
            # 开发环境使用模拟工厂
            logger.info("开发环境: 使用模拟模型工厂")
            return await get_mock_model_factory()
        else:
            # 生产环境使用真实工厂
            ModelFactory()
            await _model_factory_instance.initialize()

    return _model_factory_instance
