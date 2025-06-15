"""
conversation_manager - 索克生活项目模块
"""

from ..common.base import BaseService
from ..common.cache import cached
from ..common.exceptions import InquiryServiceError
from ..common.metrics import counter, memory_optimized, timer
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from loguru import logger
from typing import Any
import uuid

#! / usr / bin / env python3

"""
智能对话管理器

该模块实现智能化的对话管理，包括上下文感知、情感识别、
个性化回复生成和对话策略优化，提供更自然的问诊对话体验。
"""





class ConversationState(Enum):
    """对话状态"""

    GREETING = "greeting"
    INFORMATION_GATHERING = "information_gathering"
    CLARIFICATION = "clarification"
    EMPATHY = "empathy"
    GUIDANCE = "guidance"
    CONCLUSION = "conclusion"
    EMERGENCY = "emergency"


class EmotionType(Enum):
    """情感类型"""

    NEUTRAL = "neutral"
    ANXIOUS = "anxious"
    WORRIED = "worried"
    FRUSTRATED = "frustrated"
    HOPEFUL = "hopeful"
    RELIEVED = "relieved"
    CONFUSED = "confused"
    URGENT = "urgent"


class ResponseStyle(Enum):
    """回复风格"""

    PROFESSIONAL = "professional"
    EMPATHETIC = "empathetic"
    REASSURING = "reassuring"
    DIRECT = "direct"
    EDUCATIONAL = "educational"
    URGENT = "urgent"


@dataclass
class ConversationTurn:
    """对话轮次"""

    turn_id: str
    user_message: str
    bot_response: str
    emotion_detected: EmotionType
    response_style: ResponseStyle
    confidence: float
    timestamp: datetime = field(default_factory = datetime.now)
    metadata: dict[str, Any] = field(default_factory = dict)


@dataclass
class ConversationContext:
    """对话上下文"""

    session_id: str
    patient_id: str
    current_state: ConversationState
    conversation_history: list[ConversationTurn] = field(default_factory = list)
    patient_profile: dict[str, Any] = field(default_factory = dict)
    emotional_state: EmotionType = EmotionType.NEUTRAL
    conversation_goals: list[str] = field(default_factory = list)
    achieved_goals: list[str] = field(default_factory = list)
    preferred_style: ResponseStyle = ResponseStyle.PROFESSIONAL
    urgency_level: int = 0  # 0 - 10
    metadata: dict[str, Any] = field(default_factory = dict)


@dataclass
class ResponseGeneration:
    """回复生成结果"""

    response_text: str
    response_style: ResponseStyle
    emotion_addressed: EmotionType
    confidence: float
    follow_up_questions: list[str] = field(default_factory = list)
    suggested_actions: list[str] = field(default_factory = list)
    metadata: dict[str, Any] = field(default_factory = dict)


class ConversationManager(BaseService):
    """智能对话管理器"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化对话管理器

        Args:
            config: 配置信息
        """
        super().__init__(config)

        # 对话配置
        self.conversation_config = {
            "max_conversation_length": 50,
            "emotion_detection_enabled": True,
            "personalization_enabled": True,
            "empathy_threshold": 0.7,
            "urgency_detection_enabled": True,
            "context_window_size": 10,
            "response_templates_enabled": True,
        }

        # 活跃对话
        self.active_conversations: dict[str, ConversationContext] = {}

        # 回复模板
        self.response_templates = self._initialize_response_templates()

        # 情感识别模型（简化实现）
        self.emotion_keywords = self._initialize_emotion_keywords()

        # 对话策略
        self.conversation_strategies = self._initialize_conversation_strategies()

        # 性能统计
        self.stats = {
            "total_conversations": 0,
            "active_conversations": 0,
            "emotion_detections": 0,
            "personalized_responses": 0,
            "average_conversation_length": 0.0,
            "satisfaction_score": 0.0,
            "response_generation_time": 0.0,
        }

        logger.info("智能对话管理器初始化完成")

    def _initialize_response_templates(self)-> dict[str, dict[str, list[str]]]:
        """初始化回复模板"""
        return {
            ConversationState.GREETING.value: {
                ResponseStyle.PROFESSIONAL.value: [
                    "您好，我是您的健康助手。请告诉我您今天有什么不适吗？",
                    "欢迎使用智能问诊服务。请详细描述您的症状。",
                    "您好，我将协助您进行健康咨询。请说明您的主要症状。",
                ],
                ResponseStyle.EMPATHETIC.value: [
                    "您好，我理解您可能正在经历一些不适。请放心告诉我您的症状，我会认真倾听。",
                    "欢迎您，我知道身体不适会让人担心。请详细告诉我您的情况。",
                    "您好，我在这里帮助您。请不要担心，慢慢告诉我您的症状。",
                ],
            },
            ConversationState.INFORMATION_GATHERING.value: {
                ResponseStyle.PROFESSIONAL.value: [
                    "我需要了解更多细节。{question}",
                    "为了更好地帮助您，请告诉我{question}",
                    "请详细描述{question}",
                ],
                ResponseStyle.EMPATHETIC.value: [
                    "我理解这可能不太舒服，但为了帮助您，我需要了解{question}",
                    "请不要担心，这些信息对诊断很重要。{question}",
                    "我知道回忆这些可能不容易，但请告诉我{question}",
                ],
            },
            ConversationState.EMPATHY.value: {
                ResponseStyle.EMPATHETIC.value: [
                    "我理解您的担心，这种情况确实会让人焦虑。",
                    "您的感受是完全可以理解的，很多人在这种情况下都会有类似的担心。",
                    "我能感受到您的不安，请相信我们会一起找到解决方案。",
                ],
                ResponseStyle.REASSURING.value: [
                    "请不要过度担心，我们会仔细分析您的情况。",
                    "根据您的描述，这种情况通常是可以改善的。",
                    "请保持冷静，我们会逐步了解并解决问题。",
                ],
            },
            ConversationState.EMERGENCY.value: {
                ResponseStyle.URGENT.value: [
                    "根据您的症状，建议您立即就医。请尽快前往最近的医院急诊科。",
                    "这种情况需要紧急处理，请立即拨打120或前往医院。",
                    "您的症状提示可能存在紧急情况，请不要延误，立即就医。",
                ]
            },
        }

    def _initialize_emotion_keywords(self)-> dict[EmotionType, list[str]]:
        """初始化情感关键词"""
        return {
            EmotionType.ANXIOUS: [
                "担心",
                "焦虑",
                "紧张",
                "害怕",
                "不安",
                "恐惧",
                "忧虑",
            ],
            EmotionType.WORRIED: ["担心", "忧虑", "不放心", "疑虑", "顾虑", "挂念"],
            EmotionType.FRUSTRATED: ["烦躁", "郁闷", "烦恼", "气愤", "不耐烦", "厌烦"],
            EmotionType.HOPEFUL: ["希望", "期待", "乐观", "相信", "盼望", "憧憬"],
            EmotionType.RELIEVED: ["放心", "安心", "轻松", "舒缓", "缓解", "好转"],
            EmotionType.CONFUSED: ["困惑", "迷惑", "不明白", "搞不清", "糊涂", "疑惑"],
            EmotionType.URGENT: ["急", "紧急", "马上", "立即", "赶紧", "快", "严重"],
        }

    def _initialize_conversation_strategies(self)-> dict[str, dict[str, Any]]:
        """初始化对话策略"""
        return {
            "empathy_first": {
                "description": "优先表达共情",
                "conditions": ["high_emotion", "first_time_user"],
                "actions": ["acknowledge_emotion", "provide_reassurance"],
            },
            "information_focused": {
                "description": "专注信息收集",
                "conditions": ["low_emotion", "returning_user"],
                "actions": ["direct_questions", "efficient_gathering"],
            },
            "educational": {
                "description": "提供教育信息",
                "conditions": ["user_confusion", "complex_symptoms"],
                "actions": ["explain_concepts", "provide_context"],
            },
            "urgent_response": {
                "description": "紧急情况处理",
                "conditions": ["emergency_keywords", "high_urgency"],
                "actions": ["immediate_guidance", "emergency_protocol"],
            },
        }

    @timer("conversation.start_conversation")
    @counter("conversation.conversations_started")
    async def start_conversation(
        self,
        session_id: str,
        patient_id: str,
        patient_profile: dict[str, Any] | None = None,
    )-> ConversationContext:
        """
        开始对话

        Args:
            session_id: 会话ID
            patient_id: 患者ID
            patient_profile: 患者档案

        Returns:
            对话上下文
        """
        try:
            # 创建对话上下文
            context = ConversationContext(
                session_id = session_id,
                patient_id = patient_id,
                current_state = ConversationState.GREETING,
                patient_profile = patient_profile or {},
                conversation_goals = [
                    "收集主要症状",
                    "了解症状详情",
                    "评估紧急程度",
                    "提供初步建议",
                ],
            )

            # 个性化设置
            if patient_profile:
                context.preferred_style = await self._determine_preferred_style(
                    patient_profile
                )

            # 注册对话
            self.active_conversations[session_id] = context
            self.stats["total_conversations"] + = 1
            self.stats["active_conversations"] + = 1

            logger.info(f"对话已开始: {session_id}")
            return context

        except Exception as e:
            logger.error(f"开始对话失败: {e}")
            raise InquiryServiceError(f"开始对话失败: {e}")

    @timer("conversation.process_message")
    @counter("conversation.messages_processed")
    async def process_message(
        self,
        session_id: str,
        user_message: str,
        context_data: dict[str, Any] | None = None,
    )-> ResponseGeneration:
        """
        处理用户消息并生成回复

        Args:
            session_id: 会话ID
            user_message: 用户消息
            context_data: 上下文数据

        Returns:
            回复生成结果
        """
        try:
            start_time = datetime.now()

            # 获取对话上下文
            context = self.active_conversations.get(session_id)
            if not context:
                raise InquiryServiceError(f"对话不存在: {session_id}")

            # 情感检测
            detected_emotion = await self._detect_emotion(user_message)

            # 紧急程度评估
            urgency_level = await self._assess_urgency(user_message)
            context.urgency_level = max(context.urgency_level, urgency_level)

            # 更新对话状态
            await self._update_conversation_state(
                context, user_message, detected_emotion
            )

            # 选择对话策略
            strategy = await self._select_conversation_strategy(
                context, detected_emotion
            )

            # 生成回复
            response = await self._generate_response(
                context, user_message, detected_emotion, strategy
            )

            # 记录对话轮次
            turn = ConversationTurn(
                turn_id = str(uuid.uuid4()),
                user_message = user_message,
                bot_response = response.response_text,
                emotion_detected = detected_emotion,
                response_style = response.response_style,
                confidence = response.confidence,
            )
            context.conversation_history.append(turn)

            # 更新统计
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            self._update_response_stats(processing_time)

            logger.debug(f"消息处理完成: {session_id}")
            return response

        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            raise InquiryServiceError(f"处理消息失败: {e}")

    async def _detect_emotion(self, message: str)-> EmotionType:
        """检测情感"""
        if not self.conversation_config["emotion_detection_enabled"]:
            return EmotionType.NEUTRAL

        message_lower = message.lower()
        emotion_scores = {}

        # 基于关键词的情感检测
        for emotion, keywords in self.emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                emotion_scores[emotion] = score

        # 返回得分最高的情感
        if emotion_scores:
            detected_emotion = max(emotion_scores.items(), key = lambda x: x[1])[0]
            self.stats["emotion_detections"] + = 1
            return detected_emotion

        return EmotionType.NEUTRAL

    async def _assess_urgency(self, message: str)-> int:
        """评估紧急程度"""
        urgent_keywords = [
            "急",
            "紧急",
            "严重",
            "剧烈",
            "无法忍受",
            "马上",
            "立即",
            "呼吸困难",
            "胸痛",
            "大出血",
            "昏迷",
            "休克",
            "抽搐",
        ]

        urgency_score = 0
        message_lower = message.lower()

        for keyword in urgent_keywords:
            if keyword in message_lower:
                urgency_score + = 2

        # 基于症状严重程度的评估
        severity_indicators = ["10分", "9分", "8分", "无法", "不能", "极其"]
        for indicator in severity_indicators:
            if indicator in message_lower:
                urgency_score + = 1

        return min(urgency_score, 10)

    async def _update_conversation_state(
        self, context: ConversationContext, message: str, emotion: EmotionType
    ):
        """更新对话状态"""
        current_state = context.current_state

        # 紧急情况检测
        if context.urgency_level > = 8:
            context.current_state = ConversationState.EMERGENCY
            return

        # 情感状态转换
        if emotion in [
            EmotionType.ANXIOUS,
            EmotionType.WORRIED,
            EmotionType.FRUSTRATED,
        ]:
            if current_state ! = ConversationState.EMPATHY:
                context.current_state = ConversationState.EMPATHY
                return

        # 正常状态转换
        if (
            current_state == ConversationState.GREETING
            or current_state == ConversationState.EMPATHY
        ):
            context.current_state = ConversationState.INFORMATION_GATHERING
        elif current_state == ConversationState.INFORMATION_GATHERING:
            # 检查是否需要澄清
            if await self._needs_clarification(message):
                context.current_state = ConversationState.CLARIFICATION

        # 更新情感状态
        context.emotional_state = emotion

    async def _needs_clarification(self, message: str)-> bool:
        """判断是否需要澄清"""
        unclear_indicators = [
            "不清楚",
            "不确定",
            "可能",
            "大概",
            "好像",
            "似乎",
            "模糊",
        ]

        return any(indicator in message for indicator in unclear_indicators)

    async def _select_conversation_strategy(
        self, context: ConversationContext, emotion: EmotionType
    )-> str:
        """选择对话策略"""
        # 紧急情况
        if context.current_state == ConversationState.EMERGENCY:
            return "urgent_response"

        # 高情感状态
        if emotion in [
            EmotionType.ANXIOUS,
            EmotionType.WORRIED,
            EmotionType.FRUSTRATED,
        ]:
            return "empathy_first"

        # 困惑状态
        if emotion == EmotionType.CONFUSED:
            return "educational"

        # 默认信息收集策略
        return "information_focused"

    async def _generate_response(
        self,
        context: ConversationContext,
        user_message: str,
        emotion: EmotionType,
        strategy: str,
    )-> ResponseGeneration:
        """生成回复"""
        try:
            # 确定回复风格
            response_style = await self._determine_response_style(
                context, emotion, strategy
            )

            # 生成主要回复
            response_text = await self._generate_main_response(
                context, user_message, response_style
            )

            # 生成后续问题
            follow_up_questions = await self._generate_follow_up_questions(
                context, user_message
            )

            # 生成建议行动
            suggested_actions = await self._generate_suggested_actions(context, emotion)

            # 计算置信度
            confidence = await self._calculate_response_confidence(
                context, response_text, emotion
            )

            # 个性化调整
            if self.conversation_config["personalization_enabled"]:
                response_text = await self._personalize_response(
                    response_text, context.patient_profile
                )
                self.stats["personalized_responses"] + = 1

            return ResponseGeneration(
                response_text = response_text,
                response_style = response_style,
                emotion_addressed = emotion,
                confidence = confidence,
                follow_up_questions = follow_up_questions,
                suggested_actions = suggested_actions,
                metadata = {
                    "strategy_used": strategy,
                    "conversation_state": context.current_state.value,
                    "generation_time": datetime.now().isoformat(),
                },
            )

        except Exception as e:
            logger.error(f"生成回复失败: {e}")
            # 返回默认回复
            return ResponseGeneration(
                response_text = "我理解您的情况，请继续告诉我更多详细信息。",
                response_style = ResponseStyle.PROFESSIONAL,
                emotion_addressed = emotion,
                confidence = 0.5,
            )

    async def _determine_response_style(
        self, context: ConversationContext, emotion: EmotionType, strategy: str
    )-> ResponseStyle:
        """确定回复风格"""
        # 紧急情况
        if context.current_state == ConversationState.EMERGENCY:
            return ResponseStyle.URGENT

        # 高情感状态
        if emotion in [EmotionType.ANXIOUS, EmotionType.WORRIED]:
            return ResponseStyle.EMPATHETIC

        if emotion == EmotionType.FRUSTRATED:
            return ResponseStyle.REASSURING

        if emotion == EmotionType.CONFUSED:
            return ResponseStyle.EDUCATIONAL

        # 考虑患者偏好
        return context.preferred_style

    async def _generate_main_response(
        self,
        context: ConversationContext,
        user_message: str,
        response_style: ResponseStyle,
    )-> str:
        """生成主要回复"""
        state = context.current_state

        # 获取模板
        templates = self.response_templates.get(state.value, {}).get(
            response_style.value, []
        )

        if templates:
            # 选择合适的模板
            template = templates[0]  # 简化实现，选择第一个

            # 模板变量替换
            if "{question}" in template:
                question = await self._generate_contextual_question(
                    context, user_message
                )
                template = template.replace("{question}", question)

            return template

        # 默认回复
        return "我理解您的情况，请告诉我更多详细信息。"

    async def _generate_contextual_question(
        self, context: ConversationContext, user_message: str
    )-> str:
        """生成上下文相关的问题"""
        # 基于对话历史和当前消息生成问题
        # 简化实现
        common_questions = [
            "这个症状持续多长时间了？",
            "症状的严重程度如何？",
            "是否有其他伴随症状？",
            "什么情况下症状会加重或缓解？",
            "您之前有过类似的情况吗？",
        ]

        # 根据已问过的问题选择新问题
        asked_questions = [turn.bot_response for turn in context.conversation_history]

        for question in common_questions:
            if not any(question in asked for asked in asked_questions):
                return question

        return "还有其他需要了解的情况吗？"

    async def _generate_follow_up_questions(
        self, context: ConversationContext, user_message: str
    )-> list[str]:
        """生成后续问题"""
        questions = []

        # 基于症状生成相关问题
        if "头痛" in user_message:
            questions.extend(
                [
                    "头痛的位置具体在哪里？",
                    "是持续性疼痛还是间歇性的？",
                    "有没有恶心或呕吐的症状？",
                ]
            )

        if "发热" in user_message:
            questions.extend(
                ["体温大概是多少度？", "发热持续多长时间了？", "有没有寒战的感觉？"]
            )

        return questions[:3]  # 限制数量

    async def _generate_suggested_actions(
        self, context: ConversationContext, emotion: EmotionType
    )-> list[str]:
        """生成建议行动"""
        actions = []

        # 基于情感状态的建议
        if emotion == EmotionType.ANXIOUS:
            actions.append("请保持冷静，深呼吸放松")

        if emotion == EmotionType.WORRIED:
            actions.append("不要过度担心，我们会仔细分析您的情况")

        # 基于紧急程度的建议
        if context.urgency_level > = 6:
            actions.append("建议尽快就医检查")
        elif context.urgency_level > = 3:
            actions.append("建议关注症状变化，必要时就医")

        return actions

    async def _calculate_response_confidence(
        self, context: ConversationContext, response_text: str, emotion: EmotionType
    )-> float:
        """计算回复置信度"""
        confidence = 0.7  # 基础置信度

        # 基于对话历史长度调整
        history_length = len(context.conversation_history)
        if history_length > 5:
            confidence + = 0.1

        # 基于情感匹配度调整
        if emotion ! = EmotionType.NEUTRAL:
            confidence + = 0.1

        # 基于回复长度调整
        if len(response_text) > 20:
            confidence + = 0.05

        return min(confidence, 1.0)

    async def _personalize_response(
        self, response: str, patient_profile: dict[str, Any]
    )-> str:
        """个性化回复"""
        # 基于患者年龄调整语言风格
        age = patient_profile.get("age", 0)
        if age < 18:
            # 对儿童使用更简单的语言
            response = response.replace("症状", "不舒服的地方")
        elif age > 65:
            # 对老年人使用更关怀的语言
            response = "您好，" + response

        # 基于性别调整称呼
        gender = patient_profile.get("gender", "")
        if gender == "male":
            response = response.replace("您", "先生您")
        elif gender == "female":
            response = response.replace("您", "女士您")

        return response

    async def _determine_preferred_style(
        self, patient_profile: dict[str, Any]
    )-> ResponseStyle:
        """确定偏好的回复风格"""
        # 基于患者特征确定风格
        age = patient_profile.get("age", 0)
        education = patient_profile.get("education", "")

        if age < 30:
            return ResponseStyle.DIRECT
        elif age > 60:
            return ResponseStyle.EMPATHETIC
        elif "medical" in education.lower():
            return ResponseStyle.PROFESSIONAL
        else:
            return ResponseStyle.EMPATHETIC

    def _update_response_stats(self, processing_time: float):
        """更新回复统计"""
        current_avg = self.stats["response_generation_time"]
        total_responses = sum(
            len(conv.conversation_history)
            for conv in self.active_conversations.values()
        )

        if total_responses == 1:
            self.stats["response_generation_time"] = processing_time
        else:
            self.stats["response_generation_time"] = (
                current_avg * (total_responses - 1) + processing_time
            ) / total_responses

    @cached(ttl = 300)
    async def get_conversation_summary(self, session_id: str)-> dict[str, Any]:
        """获取对话摘要"""
        context = self.active_conversations.get(session_id)
        if not context:
            raise InquiryServiceError(f"对话不存在: {session_id}")

        return {
            "session_id": session_id,
            "patient_id": context.patient_id,
            "current_state": context.current_state.value,
            "emotional_state": context.emotional_state.value,
            "conversation_length": len(context.conversation_history),
            "urgency_level": context.urgency_level,
            "goals_achieved": len(context.achieved_goals),
            "total_goals": len(context.conversation_goals),
            "preferred_style": context.preferred_style.value,
            "last_interaction": context.conversation_history[ - 1].timestamp.isoformat()
            if context.conversation_history
            else None,
        }

    @memory_optimized
    async def get_conversation_history(
        self, session_id: str, limit: int = 20
    )-> list[dict[str, Any]]:
        """获取对话历史"""
        context = self.active_conversations.get(session_id)
        if not context:
            raise InquiryServiceError(f"对话不存在: {session_id}")

        history = context.conversation_history[ - limit:]

        return [
            {
                "turn_id": turn.turn_id,
                "user_message": turn.user_message,
                "bot_response": turn.bot_response,
                "emotion_detected": turn.emotion_detected.value,
                "response_style": turn.response_style.value,
                "confidence": turn.confidence,
                "timestamp": turn.timestamp.isoformat(),
            }
            for turn in history
        ]

    async def end_conversation(self, session_id: str)-> dict[str, Any]:
        """结束对话"""
        try:
            context = self.active_conversations.get(session_id)
            if not context:
                raise InquiryServiceError(f"对话不存在: {session_id}")

            # 生成对话摘要
            summary = await self.get_conversation_summary(session_id)

            # 更新统计
            conversation_length = len(context.conversation_history)
            self._update_conversation_stats(conversation_length)

            # 清理对话
            del self.active_conversations[session_id]
            self.stats["active_conversations"] - = 1

            logger.info(f"对话已结束: {session_id}")
            return summary

        except Exception as e:
            logger.error(f"结束对话失败: {e}")
            raise InquiryServiceError(f"结束对话失败: {e}")

    def _update_conversation_stats(self, conversation_length: int):
        """更新对话统计"""
        current_avg = self.stats["average_conversation_length"]
        total_conversations = self.stats["total_conversations"]

        if total_conversations == 1:
            self.stats["average_conversation_length"] = conversation_length
        else:
            self.stats["average_conversation_length"] = (
                current_avg * (total_conversations - 1) + conversation_length
            ) / total_conversations

    async def get_service_stats(self)-> dict[str, Any]:
        """获取服务统计"""
        return {
            * *self.stats,
            "active_conversations_count": len(self.active_conversations),
            "emotion_detection_rate": (
                self.stats["emotion_detections"]
                / max(self.stats["total_conversations"], 1)
            ),
            "personalization_rate": (
                self.stats["personalized_responses"]
                / max(self.stats["total_conversations"], 1)
            ),
        }
