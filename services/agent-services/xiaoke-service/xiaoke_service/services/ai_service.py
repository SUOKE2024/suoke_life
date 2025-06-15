"""
AI服务模块

提供AI模型接入、对话管理和智能分析功能。
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, AsyncGenerator
from xiaoke_service.core.config import settings
from xiaoke_service.core.logging import get_ai_logger
from xiaoke_service.core.exceptions import AIServiceError
# 可选的AI库导入
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    openai = None
    HAS_OPENAI = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    anthropic = None
    HAS_ANTHROPIC = False
from dataclasses import dataclass

logger = get_ai_logger(__name__)


@dataclass
class ChatMessage:
    """聊天消息数据类"""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AIResponse:
    """
AI响应数据类
"""
    content: str
    model: str
    usage: Dict[str, int]
    confidence: float
    processing_time: float
    metadata: Optional[Dict[str, Any]] = None


class AIService:
    """
AI服务类
    
    统一管理各种AI模型的接入，包括OpenAI、Anthropic等。
    提供对话管理、流式响应和智能分析功能。
    """

    def __init__(self):
        """初始化AI服务"""
        self.openai_client: Optional[openai.AsyncOpenAI] = None
        self.anthropic_client: Optional[anthropic.AsyncAnthropic] = None
        self.conversation_history: Dict[str, List[ChatMessage]] = {}
        self.max_history_length = 50

    async def initialize(self) -> None:
        """初始化AI客户端"""
        try:
            # 初始化OpenAI客户端
            if HAS_OPENAI and hasattr(settings, 'ai') and hasattr(settings.ai, 'openai_api_key') and settings.ai.openai_api_key:
                self.openai_client = openai.AsyncOpenAI(
                    api_key=settings.ai.openai_api_key,
                    base_url=getattr(settings.ai, 'openai_base_url', None),
                    timeout=30.0,
                    max_retries=3,
                )
                logger.info("OpenAI客户端初始化成功")

            # 初始化Anthropic客户端
            if HAS_ANTHROPIC and hasattr(settings, 'ai') and hasattr(settings.ai, 'anthropic_api_key') and settings.ai.anthropic_api_key:
                self.anthropic_client = anthropic.AsyncAnthropic(
                    api_key=settings.ai.anthropic_api_key,
                    timeout=30.0,
                    max_retries=3,
                )
                logger.info("Anthropic客户端初始化成功")

            if not self.openai_client and not self.anthropic_client:
                logger.warning("未配置AI API密钥，使用模拟模式")

        except Exception as e:
            logger.error("AI服务初始化失败", error=str(e))
            raise AIServiceError(f"AI服务初始化失败: {e}") from e

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        session_id: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> AIResponse:
        """聊天完成
        
        Args:
            messages: 消息列表
            session_id: 会话 ID
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大 token 数
            stream: 是否流式响应
            
        Returns:
            AIResponse: AI 响应
        """
        start_time = time.time()
        
        try:
            # 选择模型和客户端
            if not model:
                model = getattr(settings, 'ai', None) and getattr(settings.ai, 'openai_model', None) or "gpt-3.5-turbo"
            
            # 优先使用 OpenAI
            if self.openai_client and model.startswith(("gpt-", "o1-")):
                response = await self._openai_chat_completion(
                    messages, model, temperature, max_tokens, stream
                )
            # 使用 Anthropic
            elif self.anthropic_client and model.startswith("claude-"):
                response = await self._anthropic_chat_completion(
                    messages, model, temperature, max_tokens
                )
            else:
                # 模拟响应
                response = await self._mock_chat_completion(messages, model)
            
            # 记录对话历史
            self._save_conversation_history(session_id, messages, response)
            
            # 记录日志
            processing_time = time.time() - start_time
            logger.log_inference(
                model_name=model,
                input_tokens=response.usage.get("prompt_tokens", 0),
                output_tokens=response.usage.get("completion_tokens", 0),
                duration=processing_time,
                session_id=session_id
            )
            
            return response
            
        except Exception as e:
            logger.error("聊天完成失败", error=str(e), session_id=session_id)
            raise AIServiceError(f"聊天完成失败: {e}") from e

    async def _openai_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: Optional[int],
        stream: bool
    ) -> AIResponse:
        """
OpenAI 聊天完成
        """
        if not self.openai_client:
            raise AIServiceError("OpenAI 客户端未初始化")
        
        start_time = time.time()
        
        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )
        
        processing_time = time.time() - start_time
        
        return AIResponse(
            content=response.choices[0].message.content,
            model=model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            confidence=0.9,  # OpenAI 不提供置信度，使用默认值
            processing_time=processing_time,
            metadata={"provider": "openai"}
        )

    async def _anthropic_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: Optional[int]
    ) -> AIResponse:
        """
Anthropic 聊天完成
        """
        if not self.anthropic_client:
            raise AIServiceError("Anthropic 客户端未初始化")
        
        start_time = time.time()
        
        # 转换消息格式
        anthropic_messages = []
        system_message = None
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                anthropic_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        response = await self.anthropic_client.messages.create(
            model=model,
            messages=anthropic_messages,
            system=system_message,
            temperature=temperature,
            max_tokens=max_tokens or 1000
        )
        
        processing_time = time.time() - start_time
        
        return AIResponse(
            content=response.content[0].text,
            model=model,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            },
            confidence=0.9,
            processing_time=processing_time,
            metadata={"provider": "anthropic"}
        )

    async def _mock_chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str
    ) -> AIResponse:
        """模拟聊天完成（用于测试）"""
        start_time = time.time()
        
        # 模拟处理时间
        await asyncio.sleep(0.5)
        
        last_message = messages[-1]["content"] if messages else ""
        
        # 简单的模拟响应
        mock_responses = [
            f"小克收到您的消息：{last_message[:50]}{'...' if len(last_message) > 50 else ''}",
            "根据中医理论，您的情况需要综合调理。建议您保持规律作息，适当运动。",
            "我可以为您提供个性化的健康建议，请告诉我您的具体症状或关切的健康问题。"
        ]
        
        import random
        response_content = random.choice(mock_responses)
        
        processing_time = time.time() - start_time
        
        return AIResponse(
            content=response_content,
            model=f"mock-{model}",
            usage={
                "prompt_tokens": len(last_message) // 4,
                "completion_tokens": len(response_content) // 4,
                "total_tokens": (len(last_message) + len(response_content)) // 4
            },
            confidence=0.8,
            processing_time=processing_time,
            metadata={"provider": "mock"}
        )

    def _save_conversation_history(
        self,
        session_id: str,
        messages: List[Dict[str, str]],
        response: AIResponse
    ) -> None:
        """保存对话历史"""
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        # 添加用户消息
        if messages:
            last_message = messages[-1]
            self.conversation_history[session_id].append(
                ChatMessage(
                    role=last_message["role"],
                    content=last_message["content"],
                    timestamp=time.time()
                )
            )
        
        # 添加助手响应
        self.conversation_history[session_id].append(
            ChatMessage(
                role="assistant",
                content=response.content,
                timestamp=time.time(),
                metadata={
                    "model": response.model,
                    "confidence": response.confidence,
                    "processing_time": response.processing_time
                }
            )
        )
        
        # 限制历史长度
        if len(self.conversation_history[session_id]) > self.max_history_length:
            self.conversation_history[session_id] = self.conversation_history[session_id][-self.max_history_length:]

    def get_conversation_history(self, session_id: str) -> List[ChatMessage]:
        """获取对话历史"""
        return self.conversation_history.get(session_id, [])

    async def analyze_health_data(
        self,
        symptoms: List[str],
        constitution_data: Optional[Dict[str, Any]] = None,
        lifestyle_data: Optional[Dict[str, Any]] = None,
        medical_history: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """健康数据分析
        
        Args:
            symptoms: 症状列表
            constitution_data: 体质数据
            lifestyle_data: 生活方式数据
            medical_history: 病史
            
        Returns:
            Dict: 分析结果
        """
        try:
            # 构建分析提示
            analysis_prompt = self._build_health_analysis_prompt(
                symptoms, constitution_data, lifestyle_data, medical_history
            )
            
            # 调用AI分析
            messages = [
                {"role": "system", "content": "您是一位专业的中医健康顾问，擅长辛证论治和个性化健康管理。"},
                {"role": "user", "content": analysis_prompt}
            ]
            
            response = await self.chat_completion(
                messages=messages,
                session_id="health_analysis",
                temperature=0.3  # 使用较低的温度以获得更一致的结果
            )
            
            # 解析响应并结构化
            return self._parse_health_analysis(response.content, response.confidence)
            
        except Exception as e:
            logger.error("健康数据分析失败", error=str(e))
            raise AIServiceError(f"健康数据分析失败: {e}") from e

    def _build_health_analysis_prompt(
        self,
        symptoms: List[str],
        constitution_data: Optional[Dict[str, Any]],
        lifestyle_data: Optional[Dict[str, Any]],
        medical_history: Optional[List[str]]
    ) -> str:
        """构建健康分析提示"""
        prompt_parts = [
            "请根据以下信息进行中医辛证分析：",
            f"症状：{', '.join(symptoms)}"
        ]
        
        if constitution_data:
            prompt_parts.append(f"体质数据：{json.dumps(constitution_data, ensure_ascii=False)}")
        
        if lifestyle_data:
            prompt_parts.append(f"生活方式：{json.dumps(lifestyle_data, ensure_ascii=False)}")
        
        if medical_history:
            prompt_parts.append(f"病史：{', '.join(medical_history)}")
        
        prompt_parts.extend([
            "请提供：",
            "1. 中医辛证分析（证型、病因、病机）",
            "2. 健康风险评估",
            "3. 个性化建议（饮食、运动、作息、情绪管理）",
            "4. 预防措施和注意事项"
        ])
        
        return "\n".join(prompt_parts)

    def _parse_health_analysis(self, content: str, confidence: float) -> Dict[str, Any]:
        """解析健康分析结果"""
        # 这里可以实现更复杂的解析逻辑
        # 目前返回简化结果
        return {
            "analysis_id": f"analysis_{int(time.time())}",
            "tcm_diagnosis": {
                "syndrome": "气血两虚",  # 默认证型
                "constitution": "气虚质",
                "meridians": ["脾经", "胃经"],
                "severity": "轻度"
            },
            "recommendations": [
                {
                    "type": "diet",
                    "title": "饮食建议",
                    "content": "建议多食用补气血的食物，如红枣、桂圆、山药等"
                },
                {
                    "type": "exercise",
                    "title": "运动建议",
                    "content": "适量进行有氧运动，如太极拳、八段锦等"
                }
            ],
            "risk_assessment": {
                "overall_risk": "低",
                "specific_risks": ["心血管风险: 低", "代谢风险: 中"],
                "follow_up_needed": True
            },
            "confidence": confidence,
            "analysis_content": content
        }

    async def close(self) -> None:
        """关闭AI服务"""
        # 清理资源
        if self.openai_client:
            await self.openai_client.close()
        
        logger.info("AI服务已关闭")