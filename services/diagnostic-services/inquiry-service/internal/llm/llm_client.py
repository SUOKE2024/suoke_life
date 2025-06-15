"""
LLM客户端模块 - 处理与大语言模型的交互
"""

import asyncio
import logging
import os
import random
from typing import Any

import aiohttp

from ..common.exceptions import ServiceTimeoutError

logger = logging.getLogger(__name__)


class LLMClient:
    """大语言模型客户端"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化LLM客户端
        
        Args:
            config: 配置信息
        """
        self.config = config
        self.llm_config = config.get("llm", {})

        # 配置参数
        self.model_type = self.llm_config.get("model_type", "llama3")
        self.temperature = self.llm_config.get("temperature", 0.7)
        self.top_p = self.llm_config.get("top_p", 0.95)
        self.max_tokens = self.llm_config.get("response_max_tokens", 1024)
        self.timeout = self.llm_config.get("timeout_seconds", 30)
        self.use_mock_mode = self.llm_config.get("use_mock_mode", True)
        self.remote_endpoint = self.llm_config.get("remote_endpoint", "")

        # 加载系统提示词
        self.system_prompt = self._load_system_prompt()

        # 初始化会话
        self.session = None

        logger.info(f"LLM客户端初始化完成，模型类型: {self.model_type}, Mock模式: {self.use_mock_mode}")

    def _load_system_prompt(self) -> str:
        """加载系统提示词"""
        system_prompt_path = self.llm_config.get("system_prompt_path", "./config/prompts/system_prompt.txt")

        try:
            if os.path.exists(system_prompt_path):
                with open(system_prompt_path, encoding='utf-8') as f:
                    return f.read().strip()
            else:
                logger.warning(f"系统提示词文件不存在: {system_prompt_path}")
                return self._get_default_system_prompt()
        except Exception as e:
            logger.error(f"加载系统提示词失败: {e}")
            return self._get_default_system_prompt()

    def _get_default_system_prompt(self) -> str:
        """获取默认系统提示词"""
        return """你是索克生活平台的智能健康顾问，专门负责问诊服务。你具备以下能力：

1. 中医理论知识：熟悉中医基础理论、辨证论治、体质学说等
2. 症状分析：能够从用户描述中准确提取症状信息
3. 证型判断：根据症状表现进行中医证型分析
4. 健康建议：提供个性化的养生调理建议

请遵循以下原则：
- 以用户健康为中心，提供专业、准确的建议
- 使用温和、关怀的语调与用户交流
- 不做明确的疾病诊断，建议用户咨询专业医师
- 注重中医"治未病"理念，强调预防和调理
- 根据用户体质特点给出个性化建议

请用中文回复，语言简洁明了，易于理解。"""

    async def initialize(self) -> None:
        """初始化客户端连接"""
        if not self.use_mock_mode and self.remote_endpoint:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
            logger.info("LLM客户端连接已初始化")

    async def close(self) -> None:
        """关闭客户端连接"""
        if self.session:
            await self.session.close()
            logger.info("LLM客户端连接已关闭")

    async def generate_response(self, request: dict[str, Any]) -> dict[str, Any]:
        """
        生成LLM响应
        
        Args:
            request: 请求参数，包含用户ID、会话历史等
            
        Returns:
            Dict: LLM响应结果
        """
        try:
            if self.use_mock_mode:
                return await self._generate_mock_response(request)
            else:
                return await self._generate_real_response(request)
        except Exception as e:
            logger.error(f"生成LLM响应失败: {e}")
            return self._get_error_response(str(e))

    async def _generate_mock_response(self, request: dict[str, Any]) -> dict[str, Any]:
        """生成模拟响应"""
        # 模拟网络延迟
        await asyncio.sleep(0.2)

        user_message = ""
        history = request.get("history", [])

        # 获取最新的用户消息
        for msg in reversed(history):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break

        # 根据用户消息内容生成不同类型的响应
        response_text, detected_symptoms, follow_up_questions = self._generate_contextual_response(user_message)

        return {
            "response_text": response_text,
            "response_type": "TEXT",
            "detected_symptoms": detected_symptoms,
            "follow_up_questions": follow_up_questions,
            "confidence": 0.85,
            "processing_time": 0.2
        }

    def _generate_contextual_response(self, user_message: str) -> tuple[str, list[str], list[str]]:
        """根据用户消息生成上下文相关的响应"""
        user_message_lower = user_message.lower()

        # 症状相关关键词检测
        symptom_keywords = {
            "头痛": ["头痛", "头疼", "脑袋疼"],
            "疲劳": ["累", "疲劳", "乏力", "没精神", "疲惫"],
            "失眠": ["失眠", "睡不着", "睡眠不好", "多梦"],
            "胃痛": ["胃痛", "胃疼", "肚子疼", "腹痛"],
            "咳嗽": ["咳嗽", "咳痰", "嗓子疼"],
            "发热": ["发烧", "发热", "体温高"],
            "腹泻": ["拉肚子", "腹泻", "大便稀"],
            "便秘": ["便秘", "大便干", "排便困难"]
        }

        detected_symptoms = []
        for symptom, keywords in symptom_keywords.items():
            if any(keyword in user_message for keyword in keywords):
                detected_symptoms.append(symptom)

        # 生成响应文本
        if detected_symptoms:
            main_symptom = detected_symptoms[0]
            if main_symptom == "头痛":
                response_text = "我了解您有头痛的困扰。头痛可能与多种因素有关，比如睡眠不足、压力大、颈椎问题等。请问您的头痛是什么时候开始的？疼痛的性质是怎样的？"
                follow_up_questions = [
                    "头痛是持续性的还是间歇性的？",
                    "疼痛主要在头部的哪个位置？",
                    "最近睡眠质量如何？",
                    "是否伴有其他症状？"
                ]
            elif main_symptom == "疲劳":
                response_text = "您提到感到疲劳乏力，这在现代生活中很常见。从中医角度来看，疲劳可能与气虚、血虚或脾胃功能不佳有关。请问这种疲劳感持续多久了？"
                follow_up_questions = [
                    "疲劳感是全天都有还是特定时间段？",
                    "休息后是否能缓解？",
                    "最近饮食和睡眠规律吗？",
                    "是否伴有其他不适？"
                ]
            elif main_symptom == "失眠":
                response_text = "失眠确实会影响生活质量。从中医角度，失眠常与心神不宁、肝郁化火、脾胃不和等有关。请问您主要是入睡困难还是容易醒？"
                follow_up_questions = [
                    "大概什么时候开始出现睡眠问题？",
                    "睡前通常在做什么？",
                    "是否有焦虑或压力？",
                    "白天精神状态如何？"
                ]
            else:
                response_text = f"我注意到您提到了{main_symptom}的症状。为了更好地了解您的情况，我需要了解一些详细信息。"
                follow_up_questions = [
                    "这个症状出现多长时间了？",
                    "症状的严重程度如何？",
                    "是否有诱发因素？",
                    "之前是否有类似情况？"
                ]
        else:
            # 通用响应
            greetings = ["您好", "你好", "早上好", "下午好", "晚上好"]
            if any(greeting in user_message for greeting in greetings):
                response_text = "您好！我是您的健康顾问，很高兴为您服务。请问今天有什么健康方面的问题需要咨询吗？"
                follow_up_questions = [
                    "最近身体有什么不适吗？",
                    "想了解哪方面的健康知识？",
                    "有特定的健康目标吗？",
                    "需要体质调理建议吗？"
                ]
            else:
                response_text = "我理解您的关切。为了给您提供更准确的建议，请详细描述一下您的具体情况。"
                follow_up_questions = [
                    "能详细描述一下您的症状吗？",
                    "这种情况持续多长时间了？",
                    "是否影响了日常生活？",
                    "之前有过类似经历吗？"
                ]

        return response_text, detected_symptoms, follow_up_questions

    async def _generate_real_response(self, request: dict[str, Any]) -> dict[str, Any]:
        """生成真实的LLM响应"""
        if not self.session:
            await self.initialize()

        # 构建请求数据
        messages = self._build_messages(request)

        payload = {
            "model": self.model_type,
            "messages": messages,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
            "stream": False
        }

        try:
            async with self.session.post(
                f"{self.remote_endpoint}/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return self._parse_llm_response(result)
                else:
                    error_text = await response.text()
                    logger.error(f"LLM API请求失败: {response.status}, {error_text}")
                    return self._get_error_response(f"API请求失败: {response.status}")

        except (asyncio.TimeoutError, ServiceTimeoutError):
            logger.error("LLM API请求超时")
            return self._get_error_response("请求超时")
        except Exception as e:
            logger.error(f"LLM API请求异常: {e}")
            return self._get_error_response(str(e))

    def _build_messages(self, request: dict[str, Any]) -> list[dict[str, str]]:
        """构建消息列表"""
        messages = [{"role": "system", "content": self.system_prompt}]

        # 添加历史消息
        history = request.get("history", [])
        for msg in history[-10:]:  # 只保留最近10条消息
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role in ["user", "assistant"] and content:
                messages.append({"role": role, "content": content})

        return messages

    def _parse_llm_response(self, response: dict[str, Any]) -> dict[str, Any]:
        """解析LLM响应"""
        try:
            choices = response.get("choices", [])
            if not choices:
                return self._get_error_response("无效的响应格式")

            message = choices[0].get("message", {})
            content = message.get("content", "")

            # 简单的症状提取（实际应该使用更复杂的NLP处理）
            detected_symptoms = self._extract_symptoms_from_response(content)

            # 生成跟进问题
            follow_up_questions = self._generate_follow_up_questions(content)

            return {
                "response_text": content,
                "response_type": "TEXT",
                "detected_symptoms": detected_symptoms,
                "follow_up_questions": follow_up_questions,
                "confidence": 0.9,
                "processing_time": response.get("usage", {}).get("total_tokens", 0) * 0.001
            }

        except Exception as e:
            logger.error(f"解析LLM响应失败: {e}")
            return self._get_error_response("响应解析失败")

    def _extract_symptoms_from_response(self, content: str) -> list[str]:
        """从响应中提取症状"""
        # 简单的关键词匹配，实际应该使用更复杂的NLP
        symptom_keywords = ["头痛", "疲劳", "失眠", "胃痛", "咳嗽", "发热", "腹泻", "便秘"]
        detected = []

        for symptom in symptom_keywords:
            if symptom in content:
                detected.append(symptom)

        return detected

    def _generate_follow_up_questions(self, content: str) -> list[str]:
        """生成跟进问题"""
        # 根据响应内容生成相关的跟进问题
        default_questions = [
            "还有其他症状需要说明吗？",
            "这种情况持续多长时间了？",
            "是否影响了您的日常生活？",
            "您希望了解哪方面的调理建议？"
        ]

        return random.sample(default_questions, min(3, len(default_questions)))

    def _get_error_response(self, error_message: str) -> dict[str, Any]:
        """获取错误响应"""
        return {
            "response_text": "抱歉，我暂时无法处理您的请求。请稍后再试，或者换个方式描述您的问题。",
            "response_type": "TEXT",
            "detected_symptoms": [],
            "follow_up_questions": [
                "您可以尝试重新描述一下问题",
                "是否需要其他方面的帮助？"
            ],
            "confidence": 0.0,
            "error": error_message
        }

    async def extract_symptoms(self, text: str) -> dict[str, Any]:
        """提取症状信息"""
        request = {
            "history": [{"role": "user", "content": f"请从以下文本中提取症状信息：{text}"}],
            "task": "symptom_extraction"
        }

        return await self.generate_response(request)

    async def map_tcm_patterns(self, symptoms: list[str], user_profile: dict[str, Any]) -> dict[str, Any]:
        """映射中医证型"""
        symptoms_text = "、".join(symptoms)
        constitution = user_profile.get("constitution_type", "平和质")

        request = {
            "history": [
                {
                    "role": "user",
                    "content": f"用户体质：{constitution}，症状：{symptoms_text}。请进行中医证型分析。"
                }
            ],
            "task": "tcm_pattern_mapping"
        }

        return await self.generate_response(request)

    async def assess_health_risks(self, symptoms: list[str], medical_history: dict[str, Any]) -> dict[str, Any]:
        """评估健康风险"""
        symptoms_text = "、".join(symptoms)

        request = {
            "history": [
                {
                    "role": "user",
                    "content": f"症状：{symptoms_text}。请评估健康风险并提供预防建议。"
                }
            ],
            "task": "health_risk_assessment"
        }

        return await self.generate_response(request)
