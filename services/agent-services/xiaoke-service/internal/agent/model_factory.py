#!/usr/bin/env python3
"""
大模型工厂类
负责创建和管理不同类型的大模型客户端，为小克智能体提供支持
"""

import asyncio
import logging
import os
import time
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

try:
    import openai
    from openai.types.chat import (
        ChatCompletionAssistantMessageParam,
        ChatCompletionMessageParam,
        ChatCompletionSystemMessageParam,
        ChatCompletionUserMessageParam,
    )

    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    logging.warning("未安装openai库，无法使用OpenAI API")

try:
    import zhipuai

    HAS_ZHIPUAI = True
except ImportError:
    HAS_ZHIPUAI = False
    logging.warning("未安装zhipuai库，无法使用智谱API")

from pkg.utils.config_loader import get_config
from pkg.utils.metrics import get_metrics_collector, track_llm_metrics
from pkg.utils.resilience import circuit_breaker, rate_limiter

logger = logging.getLogger(__name__)


class ModelFactory:
    """
    大模型工厂类，用于创建、管理和调用各种大模型服务，为小克智能体提供医疗资源调度相关能力
    """

    def __init__(self):
        """初始化大模型工厂"""
        self.config = get_config()
        self.metrics = get_metrics_collector()

        # 加载配置
        self.llm_config = self.config.get_section("models.llm")
        self.local_llm_config = self.config.get_section("models.local_llm")

        # 设置默认模型
        self.primary_model = self.llm_config.get("primary_model", "gpt-4o-mini")
        self.fallback_model = self.llm_config.get("fallback_model", "llama-3-8b")

        # 初始化客户端映射表
        self.clients = {}

        # 初始化各大模型客户端
        self._init_openai_client()
        self._init_local_llm_client()
        self._init_zhipu_client()
        self._init_baidu_client()

        logger.info(f"大模型工厂初始化完成，可用模型: {list(self.clients.keys())}")

    def _init_openai_client(self):
        """初始化OpenAI客户端"""
        if not HAS_OPENAI:
            logger.warning("未安装openai库，跳过OpenAI客户端初始化")
            return

        try:
            # 获取API密钥
            api_key = self.llm_config.get("api_key", os.getenv("OPENAI_API_KEY", ""))

            if not api_key:
                logger.warning("未配置OpenAI API密钥，跳过OpenAI客户端初始化")
                return

            # 创建客户端
            api_base = self.llm_config.get("api_base", "https://api.openai.com/v1")
            org_id = self.llm_config.get("org_id", None)

            client = openai.OpenAI(
                api_key=api_key,
                base_url=api_base,
                organization=org_id,
                timeout=httpx.Timeout(connect=10.0, read=60.0, write=10.0, pool=10.0),
            )

            # 验证连接
            if self._verify_openai_connection(client):
                # 注册客户端
                openai_models = [
                    "gpt-4o",
                    "gpt-4o-mini",
                    "gpt-4-turbo",
                    "gpt-3.5-turbo",
                ]
                for model in openai_models:
                    self.clients[model] = {
                        "client": client,
                        "type": "openai",
                        "provider": "OpenAI",
                        "max_tokens": 8192,
                    }

                logger.info(f"OpenAI客户端初始化成功，已注册模型: {openai_models}")
            else:
                logger.warning("OpenAI客户端连接验证失败，跳过注册")

        except Exception as e:
            logger.error(f"初始化OpenAI客户端失败: {e}")

    def _verify_openai_connection(self, client) -> bool:
        """验证OpenAI客户端连接"""
        try:
            # 发送一个简单请求测试连接
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "你是小克，一个专注于医疗资源调度的智能体",
                    },
                    {"role": "user", "content": "测试连接"},
                ],
                max_tokens=5,
            )

            # 检查响应是否有效
            if response and hasattr(response, "choices") and len(response.choices) > 0:
                logger.info("OpenAI连接验证成功")
                return True
            else:
                logger.warning("OpenAI连接验证响应无效")
                return False

        except Exception as e:
            logger.warning(f"OpenAI连接验证失败: {e}")
            return False

    def _init_local_llm_client(self):
        """初始化本地LLM客户端"""
        try:
            # 检查本地LLM配置
            local_llm_url = self.local_llm_config.get("endpoint_url")

            if not local_llm_url:
                logger.warning("未配置本地LLM端点URL，跳过本地LLM客户端初始化")
                return

            # 创建客户端 (使用OpenAI兼容接口)
            client = openai.OpenAI(
                base_url=local_llm_url,
                api_key="not-needed",  # 本地服务可能不需要API密钥
                timeout=httpx.Timeout(connect=5.0, read=60.0, write=5.0, pool=5.0),
            )

            # 验证连接
            if self._verify_local_llm_connection(client):
                # 注册客户端
                local_models = self.local_llm_config.get(
                    "available_models", ["llama-3-8b", "llama-3-70b"]
                )
                for model in local_models:
                    self.clients[model] = {
                        "client": client,
                        "type": "local_llm",
                        "provider": "Local",
                        "max_tokens": self.local_llm_config.get("max_tokens", 4096),
                    }

                logger.info(f"本地LLM客户端初始化成功，已注册模型: {local_models}")
            else:
                logger.warning("本地LLM客户端连接验证失败，跳过注册")

        except Exception as e:
            logger.error(f"初始化本地LLM客户端失败: {e}")

    def _verify_local_llm_connection(self, client) -> bool:
        """验证本地LLM客户端连接"""
        try:
            # 发送一个简单请求测试连接
            response = client.chat.completions.create(
                model=self.local_llm_config.get("default_model", "llama-3-8b"),
                messages=[
                    {
                        "role": "system",
                        "content": "你是小克，一个专注于医疗资源调度的智能体",
                    },
                    {"role": "user", "content": "测试连接"},
                ],
                max_tokens=5,
            )

            # 检查响应是否有效
            if response and hasattr(response, "choices") and len(response.choices) > 0:
                logger.info("本地LLM连接验证成功")
                return True
            else:
                logger.warning("本地LLM连接验证响应无效")
                return False

        except Exception as e:
            logger.warning(f"本地LLM连接验证失败: {e}")
            return False

    def _init_zhipu_client(self):
        """初始化智谱AI客户端"""
        if not HAS_ZHIPUAI:
            logger.warning("未安装zhipuai库，跳过智谱客户端初始化")
            return

        try:
            # 获取API密钥
            zhipu_config = self.config.get_section("models.zhipu")
            api_key = zhipu_config.get("api_key", os.getenv("ZHIPU_API_KEY", ""))

            if not api_key:
                logger.warning("未配置智谱API密钥，跳过智谱客户端初始化")
                return

            # 创建客户端
            client = zhipuai.ZhipuAI(api_key=api_key)

            # 验证连接
            if self._verify_zhipu_connection(client):
                # 注册客户端
                zhipu_models = ["glm-4", "glm-3-turbo"]
                for model in zhipu_models:
                    self.clients[model] = {
                        "client": client,
                        "type": "zhipu",
                        "provider": "智谱AI",
                        "max_tokens": 8192,
                    }

                logger.info(f"智谱AI客户端初始化成功，已注册模型: {zhipu_models}")
            else:
                logger.warning("智谱AI客户端连接验证失败，跳过注册")

        except Exception as e:
            logger.error(f"初始化智谱AI客户端失败: {e}")

    def _verify_zhipu_connection(self, client) -> bool:
        """验证智谱AI客户端连接"""
        try:
            # 发送一个简单请求测试连接
            response = client.chat.completions.create(
                model="glm-3-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "你是小克，一个专注于医疗资源调度的智能体",
                    },
                    {"role": "user", "content": "测试连接"},
                ],
                max_tokens=5,
            )

            # 检查响应是否有效
            if response and hasattr(response, "choices") and len(response.choices) > 0:
                logger.info("智谱AI连接验证成功")
                return True
            else:
                logger.warning("智谱AI连接验证响应无效")
                return False

        except Exception as e:
            logger.warning(f"智谱AI连接验证失败: {e}")
            return False

    def _init_baidu_client(self):
        """初始化百度文心一言客户端"""
        try:
            # 获取配置
            baidu_config = self.config.get_section("models.baidu")
            api_key = baidu_config.get("api_key", os.getenv("BAIDU_API_KEY", ""))
            secret_key = baidu_config.get(
                "secret_key", os.getenv("BAIDU_SECRET_KEY", "")
            )

            if not api_key or not secret_key:
                logger.warning("未配置百度API密钥，跳过百度客户端初始化")
                return

            # 注册HTTP客户端（百度使用自定义HTTP请求）
            baidu_models = ["ernie-bot-4", "ernie-bot"]
            for model in baidu_models:
                self.clients[model] = {
                    "client": {
                        "api_key": api_key,
                        "secret_key": secret_key,
                        "url": baidu_config.get(
                            "api_url",
                            "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/",
                        ),
                    },
                    "type": "baidu",
                    "provider": "百度智能云",
                    "max_tokens": 4096,
                }

            logger.info(f"百度文心一言客户端初始化成功，已注册模型: {baidu_models}")

        except Exception as e:
            logger.error(f"初始化百度文心一言客户端失败: {e}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.ConnectTimeout, httpx.ReadTimeout)),
    )
    @circuit_breaker(failure_threshold=5, recovery_time=60)
    @rate_limiter(max_calls=60, time_period=60)
    @track_llm_metrics(query_type="chat_completion")
    async def generate_chat_completion(
        self,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> tuple[str, dict[str, Any]]:
        """
        生成聊天完成

        Args:
            model: 模型名称
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大生成令牌数

        Returns:
            Tuple[str, Dict[str, Any]]: 生成的文本和元数据
        """
        time.time()

        # 判断模型是否可用
        if model not in self.clients:
            available_models = list(self.clients.keys())
            logger.warning(
                f"请求的模型 {model} 不可用，尝试使用 {self.fallback_model if self.fallback_model in available_models else available_models[0]}"
            )

            # 使用备用模型
            if self.fallback_model in self.clients:
                model = self.fallback_model
            elif available_models:
                model = available_models[0]
            else:
                raise ValueError("没有可用的大模型服务")

        # 获取模型客户端
        client_info = self.clients[model]
        client = client_info["client"]
        client_type = client_info["type"]

        try:
            # 根据客户端类型调用不同的API
            if client_type in {"openai", "local_llm"}:
                return await self._call_openai_compatible_api(
                    client, model, messages, temperature, max_tokens
                )
            elif client_type == "zhipu":
                return await self._call_zhipu_api(
                    client, model, messages, temperature, max_tokens
                )
            elif client_type == "baidu":
                return await self._call_baidu_api(
                    client_info, model, messages, temperature, max_tokens
                )
            else:
                raise ValueError(f"不支持的客户端类型: {client_type}")

        except Exception as e:
            logger.error(f"调用{client_info['provider']}模型 {model} 失败: {e}")

            # 记录模型调用失败指标
            self.metrics.track_llm_error(model, str(e))

            # 如果是主模型失败，尝试使用备用模型
            if (
                model == self.primary_model
                and model != self.fallback_model
                and self.fallback_model in self.clients
            ):
                logger.info(f"尝试使用备用模型 {self.fallback_model}")
                return await self.generate_chat_completion(
                    self.fallback_model, messages, temperature, max_tokens
                )

            # 返回错误信息
            return f"很抱歉，我暂时无法处理您的请求。错误: {e!s}", {
                "model": model,
                "provider": client_info["provider"],
                "error": str(e),
                "success": False,
            }

    async def _call_openai_compatible_api(
        self, client, model, messages, temperature, max_tokens
    ):
        """调用OpenAI兼容的API（包括OpenAI和本地LLM）"""
        start_time = time.time()

        # 转换消息格式
        formatted_messages = []
        for msg in messages:
            if msg["role"] == "system":
                formatted_messages.append(
                    ChatCompletionSystemMessageParam(
                        role="system", content=msg["content"]
                    )
                )
            elif msg["role"] == "user":
                formatted_messages.append(
                    ChatCompletionUserMessageParam(role="user", content=msg["content"])
                )
            elif msg["role"] == "assistant":
                formatted_messages.append(
                    ChatCompletionAssistantMessageParam(
                        role="assistant", content=msg["content"]
                    )
                )

        # 调用API
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=model,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=0.95,
            frequency_penalty=0.5,
            presence_penalty=0.3,
        )

        # 提取响应文本
        response_text = response.choices[0].message.content

        # 获取token计数
        if hasattr(response, "usage"):
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
        else:
            # 估算token数量
            prompt_tokens = sum(len(m["content"].split()) * 1.3 for m in messages)
            completion_tokens = len(response_text.split()) * 1.3

        # 计算响应时间
        latency = time.time() - start_time

        # 记录指标
        self.metrics.track_llm_latency(model, latency)
        self.metrics.track_llm_token_usage(model, prompt_tokens, completion_tokens)

        # 元数据
        metadata = {
            "model": model,
            "provider": self.clients[model]["provider"],
            "confidence": 0.95,  # OpenAI不提供置信度，使用默认值
            "latency": latency,
            "token_count": {"prompt": prompt_tokens, "completion": completion_tokens},
            "success": True,
        }

        return response_text, metadata

    async def _call_zhipu_api(self, client, model, messages, temperature, max_tokens):
        """调用智谱API"""
        start_time = time.time()

        # 调用API
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # 提取响应文本
        response_text = response.choices[0].message.content

        # 获取token计数
        if hasattr(response, "usage"):
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
        else:
            # 估算token数量
            prompt_tokens = sum(len(m["content"].split()) * 1.3 for m in messages)
            completion_tokens = len(response_text.split()) * 1.3

        # 计算响应时间
        latency = time.time() - start_time

        # 记录指标
        self.metrics.track_llm_latency(model, latency)
        self.metrics.track_llm_token_usage(model, prompt_tokens, completion_tokens)

        # 元数据
        metadata = {
            "model": model,
            "provider": "智谱AI",
            "confidence": 0.95,
            "latency": latency,
            "token_count": {"prompt": prompt_tokens, "completion": completion_tokens},
            "success": True,
        }

        return response_text, metadata

    async def _call_baidu_api(
        self, client_info, model, messages, temperature, max_tokens
    ):
        """调用百度文心一言API"""
        start_time = time.time()

        # 获取客户端配置
        api_key = client_info["client"]["api_key"]
        secret_key = client_info["client"]["secret_key"]
        base_url = client_info["client"]["url"]

        # 获取访问令牌
        access_token = await self._get_baidu_access_token(api_key, secret_key)

        # 准备请求数据
        url = f"{base_url}{model}?access_token={access_token}"
        payload = {
            "messages": messages,
            "temperature": temperature,
            "top_p": 0.95,
            "max_tokens": max_tokens,
        }

        # 发送请求
        async with httpx.AsyncClient(timeout=60.0) as http_client:
            response = await http_client.post(
                url, json=payload, headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()

        # 处理响应
        if "error_code" in result:
            raise ValueError(f"百度API错误: {result.get('error_msg', '未知错误')}")

        # 提取响应文本
        response_text = result["result"]

        # 获取token计数
        prompt_tokens = result.get("usage", {}).get("prompt_tokens", 0)
        completion_tokens = result.get("usage", {}).get("completion_tokens", 0)

        # 计算响应时间
        latency = time.time() - start_time

        # 记录指标
        self.metrics.track_llm_latency(model, latency)
        self.metrics.track_llm_token_usage(model, prompt_tokens, completion_tokens)

        # 元数据
        metadata = {
            "model": model,
            "provider": "百度智能云",
            "confidence": 0.95,
            "latency": latency,
            "token_count": {"prompt": prompt_tokens, "completion": completion_tokens},
            "success": True,
        }

        return response_text, metadata

    async def _get_baidu_access_token(self, api_key, secret_key):
        """获取百度API访问令牌"""
        url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}"

        async with httpx.AsyncClient() as client:
            response = await client.post(url)
            response.raise_for_status()
            result = response.json()

            if "access_token" not in result:
                raise ValueError("无法获取百度API访问令牌")

            return result["access_token"]

    def get_available_models(self) -> list[dict[str, Any]]:
        """
        获取所有可用的模型列表

        Returns:
            List[Dict[str, Any]]: 可用模型列表
        """
        models = []
        for model_name, info in self.clients.items():
            models.append(
                {
                    "name": model_name,
                    "provider": info["provider"],
                    "max_tokens": info["max_tokens"],
                }
            )
        return models

    def is_model_available(self, model_name: str) -> bool:
        """
        检查模型是否可用

        Args:
            model_name: 模型名称

        Returns:
            bool: 模型是否可用
        """
        return model_name in self.clients

    async def close(self):
        """关闭所有客户端连接"""
        # 目前大多数客户端不需要显式关闭
        logger.info("关闭所有模型客户端连接")
