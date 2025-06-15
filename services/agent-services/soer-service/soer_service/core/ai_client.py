"""
AI客户端模块

提供OpenAI、Anthropic等AI服务的统一接口
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, AsyncGenerator
from enum import Enum

import openai
import anthropic
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from ..config.settings import get_settings

logger = logging.getLogger(__name__)


class AIProvider(str, Enum):
    """AI服务提供商"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


class AIMessage:
    """AI消息类"""
    
    def __init__(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        self.role = role
        self.content = content
        self.metadata = metadata or {}
    
    def to_openai_format(self) -> Dict[str, str]:
        """转换为OpenAI格式"""
        return {"role": self.role, "content": self.content}
    
    def to_anthropic_format(self) -> Dict[str, str]:
        """转换为Anthropic格式"""
        return {"role": self.role, "content": self.content}


class AIClient:
    """AI客户端基类"""
    
    def __init__(self):
        self.settings = get_settings()
        self.provider = AIProvider.OPENAI  # 默认使用OpenAI
        self._openai_client = None
        self._anthropic_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """初始化AI客户端"""
        # 初始化OpenAI客户端
        if self.settings.openai_api_key:
            self._openai_client = AsyncOpenAI(
                api_key=self.settings.openai_api_key,
                base_url=self.settings.openai_base_url
            )
            logger.info("✅ OpenAI客户端初始化成功")
        
        # 初始化Anthropic客户端
        if self.settings.anthropic_api_key:
            self._anthropic_client = AsyncAnthropic(
                api_key=self.settings.anthropic_api_key
            )
            logger.info("✅ Anthropic客户端初始化成功")
    
    async def chat_completion(
        self,
        messages: List[AIMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        provider: Optional[AIProvider] = None
    ) -> str:
        """
        聊天完成
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大令牌数
            stream: 是否流式输出
            provider: AI服务提供商
        
        Returns:
            AI响应内容
        """
        provider = provider or self.provider
        
        if provider == AIProvider.OPENAI:
            return await self._openai_chat_completion(
                messages, model, temperature, max_tokens, stream
            )
        elif provider == AIProvider.ANTHROPIC:
            return await self._anthropic_chat_completion(
                messages, model, temperature, max_tokens, stream
            )
        else:
            return await self._local_chat_completion(messages)
    
    async def _openai_chat_completion(
        self,
        messages: List[AIMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str:
        """OpenAI聊天完成"""
        if not self._openai_client:
            raise ValueError("OpenAI客户端未初始化")
        
        try:
            # 转换消息格式
            openai_messages = [msg.to_openai_format() for msg in messages]
            
            # 设置默认模型
            model = model or "gpt-3.5-turbo"
            
            # 调用OpenAI API
            response = await self._openai_client.chat.completions.create(
                model=model,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            if stream:
                # 处理流式响应
                content = ""
                async for chunk in response:
                    if chunk.choices[0].delta.content:
                        content += chunk.choices[0].delta.content
                return content
            else:
                return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {e}")
            raise
    
    async def _anthropic_chat_completion(
        self,
        messages: List[AIMessage],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> str:
        """Anthropic聊天完成"""
        if not self._anthropic_client:
            raise ValueError("Anthropic客户端未初始化")
        
        try:
            # 转换消息格式
            anthropic_messages = [msg.to_anthropic_format() for msg in messages]
            
            # 设置默认模型
            model = model or "claude-3-sonnet-20240229"
            
            # 调用Anthropic API
            response = await self._anthropic_client.messages.create(
                model=model,
                messages=anthropic_messages,
                temperature=temperature,
                max_tokens=max_tokens or 1000
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic API调用失败: {e}")
            raise
    
    async def _local_chat_completion(self, messages: List[AIMessage]) -> str:
        """本地模型聊天完成（模拟）"""
        # 这里可以集成本地模型，如Ollama等
        # 目前返回模拟响应
        last_message = messages[-1].content if messages else ""
        
        # 简单的规则响应
        if "健康" in last_message or "营养" in last_message:
            return "作为您的健康管理助手，我建议您保持均衡的饮食，多吃蔬菜水果，适量运动，保证充足的睡眠。"
        elif "运动" in last_message or "锻炼" in last_message:
            return "运动对健康非常重要。建议您每周进行至少150分钟的中等强度有氧运动，同时加入力量训练。"
        elif "睡眠" in last_message:
            return "良好的睡眠对健康至关重要。建议您每晚保持7-9小时的睡眠，建立规律的作息时间。"
        else:
            return f"我理解您提到的'{last_message}'。作为您的健康管理助手，我会根据您的具体情况提供个性化的建议。"
    
    async def generate_embedding(self, text: str, model: str = "text-embedding-ada-002") -> List[float]:
        """生成文本嵌入"""
        if not self._openai_client:
            raise ValueError("OpenAI客户端未初始化")
        
        try:
            response = await self._openai_client.embeddings.create(
                model=model,
                input=text
            )
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"生成嵌入失败: {e}")
            raise
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """情感分析"""
        messages = [
            AIMessage("system", "你是一个情感分析专家，请分析用户文本的情感倾向。"),
            AIMessage("user", f"请分析以下文本的情感：{text}")
        ]
        
        try:
            response = await self.chat_completion(messages, temperature=0.3)
            
            # 简化的情感分析结果
            if "积极" in response or "正面" in response or "开心" in response:
                sentiment = "positive"
                score = 0.8
            elif "消极" in response or "负面" in response or "难过" in response:
                sentiment = "negative"
                score = 0.8
            else:
                sentiment = "neutral"
                score = 0.5
            
            return {
                "sentiment": sentiment,
                "score": score,
                "analysis": response
            }
            
        except Exception as e:
            logger.error(f"情感分析失败: {e}")
            return {
                "sentiment": "neutral",
                "score": 0.5,
                "analysis": "情感分析暂时不可用"
            }
    
    async def extract_intent(self, text: str) -> Dict[str, Any]:
        """意图识别"""
        messages = [
            AIMessage("system", """你是一个意图识别专家。请识别用户文本的意图，返回JSON格式：
{
    "intent": "意图类型",
    "confidence": 0.95,
    "entities": {"实体类型": "实体值"}
}

可能的意图类型包括：
- health_query: 健康咨询
- nutrition_analysis: 营养分析
- exercise_plan: 运动计划
- sleep_analysis: 睡眠分析
- stress_management: 压力管理
- tcm_consultation: 中医咨询
- general_chat: 一般聊天
"""),
            AIMessage("user", f"请识别以下文本的意图：{text}")
        ]
        
        try:
            response = await self.chat_completion(messages, temperature=0.3)
            
            # 尝试解析JSON响应
            try:
                intent_data = json.loads(response)
                return intent_data
            except json.JSONDecodeError:
                # 如果无法解析JSON，返回默认结果
                return {
                    "intent": "general_chat",
                    "confidence": 0.5,
                    "entities": {}
                }
                
        except Exception as e:
            logger.error(f"意图识别失败: {e}")
            return {
                "intent": "general_chat",
                "confidence": 0.5,
                "entities": {}
            }
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "openai_available": self._openai_client is not None,
            "anthropic_available": self._anthropic_client is not None,
            "default_provider": self.provider
        }


# 全局AI客户端实例
ai_client = AIClient()