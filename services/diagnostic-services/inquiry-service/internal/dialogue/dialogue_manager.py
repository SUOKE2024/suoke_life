"""
dialogue_manager - 索克生活项目模块
"""

from ..llm.llm_client import LLMClient
from ..repository.session_repository import SessionRepository
from ..repository.user_repository import UserRepository
from datetime import datetime
from typing import Any
import logging
import time
import uuid

#!/usr/bin/env python

"""
对话管理器模块，负责管理问诊会话、保存会话历史、维护对话上下文等
"""



logger = logging.getLogger(__name__)


class DialogueManager:
    """对话管理器类，负责管理问诊会话流程"""

    def __init__(
        self,
        llm_client: LLMClient,
        session_repository: SessionRepository,
        user_repository: UserRepository,
        config: dict[str, Any],
    ):
        """
        初始化对话管理器

        Args:
            llm_client: 大语言模型客户端
            session_repository: 会话存储库
            user_repository: 用户存储库
            config: 配置信息
        """
        self.llm_client = llm_client
        self.session_repository = session_repository
        self.user_repository = user_repository
        self.config = config

        # 会话配置
        self.session_timeout = (
            config.get("dialogue", {}).get("session_timeout_minutes", 60) * 60
        )
        self.max_history = config.get("dialogue", {}).get("max_session_history", 50)
        self.default_language = config.get("dialogue", {}).get(
            "default_language", "zh-CN"
        )
        self.default_follow_up_count = config.get("dialogue", {}).get(
            "default_follow_up_count", 3
        )

        # 活跃会话缓存
        self.active_sessions: dict[str, dict] = {}

        logger.info(
            "对话管理器初始化完成，支持 %d 个并发会话",
            config.get("server", {}).get("max_concurrent_sessions", 500),
        )

    async def start_session(
        self,
        user_id: str,
        session_type: str = "general",
        language: str = None,
        context_data: dict[str, str] = None,
    ) -> tuple[str, str, list[str]]:
        """
        开始一个新的问诊会话

        Args:
            user_id: 用户ID
            session_type: 会话类型 (general, targeted, follow_up)
            language: 语言偏好
            context_data: 上下文数据

        Returns:
            Tuple[session_id, welcome_message, suggested_questions]
        """
        # 确保用户存在
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            logger.warning(f"用户 {user_id} 不存在，将创建基础用户信息")
            user = {"id": user_id, "created_at": datetime.now().timestamp()}
            await self.user_repository.create_user(user)

        # 创建会话ID和初始会话数据
        session_id = str(uuid.uuid4())
        language = language or self.default_language
        context_data = context_data or {}

        # 创建会话记录
        session_data = {
            "id": session_id,
            "user_id": user_id,
            "type": session_type,
            "language": language,
            "context_data": context_data,
            "created_at": datetime.now().timestamp(),
            "last_interaction": datetime.now().timestamp(),
            "status": "active",
            "history": [],
        }

        # 保存会话
        await self.session_repository.create_session(session_data)

        # 添加到活跃会话缓存
        self.active_sessions[session_id] = session_data

        # 生成欢迎信息和建议问题
        welcome_message = await self._generate_welcome_message(
            user, session_type, language
        )
        suggested_questions = await self._generate_suggested_questions(
            user, session_type, language
        )

        logger.info(f"用户 {user_id} 开始新会话 {session_id}，类型: {session_type}")

        return session_id, welcome_message, suggested_questions

    async def _generate_welcome_message(
        self, user: dict, session_type: str, language: str
    ) -> str:
        """生成会话欢迎信息"""
        # 获取用户的健康档案和基本信息以个性化欢迎信息
        try:
            user_name = user.get("name", "您")
            time_of_day = self._get_time_of_day()

            if session_type == "general":
                welcome_template = f"您好，{user_name}，{time_of_day}好！我是您的健康顾问，请问有什么可以帮助您的吗？"
            elif session_type == "targeted":
                welcome_template = f"您好，{user_name}，{time_of_day}好！我们今天将针对特定健康问题进行问诊。请告诉我您的具体症状或疑问。"
            elif session_type == "follow_up":
                last_session = await self._get_last_session(user["id"])
                if last_session:
                    last_time = datetime.fromtimestamp(
                        last_session.get("created_at", 0)
                    )
                    days_ago = (datetime.now() - last_time).days
                    if days_ago > 0:
                        time_ref = f"{days_ago}天前"
                    else:
                        time_ref = "今天早些时候"
                    welcome_template = f"您好，{user_name}，{time_of_day}好！这是对{time_ref}问诊的跟进。您的情况有什么变化吗？"
                else:
                    welcome_template = f"您好，{user_name}，{time_of_day}好！欢迎进行跟进问诊。您的健康状况有什么变化吗？"
            else:
                welcome_template = (
                    f"您好，{user_name}，{time_of_day}好！有什么可以帮助您的吗？"
                )

            return welcome_template

        except Exception as e:
            logger.error(f"生成欢迎信息失败: {e!s}")
            return "您好！我是您的健康顾问，请问有什么可以帮助您的吗？"

    def _get_time_of_day(self) -> str:
        """根据当前时间返回合适的问候语"""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "早上"
        elif 12 <= hour < 14:
            return "中午"
        elif 14 <= hour < 18:
            return "下午"
        else:
            return "晚上"

    async def _get_last_session(self, user_id: str) -> dict | None:
        """获取用户的上一次会话"""
        sessions = await self.session_repository.get_sessions_by_user_id(
            user_id, limit=1, sort_by="created_at", sort_order="desc"
        )
        return sessions[0] if sessions else None

    async def _generate_suggested_questions(
        self, user: dict, session_type: str, language: str
    ) -> list[str]:
        """生成建议问题列表"""
        try:
            # 根据用户历史和会话类型生成个性化建议问题
            suggested_questions = []

            if session_type == "general":
                suggested_questions = [
                    "我最近总是感到疲惫，这可能是什么原因？",
                    "如何改善我的睡眠质量？",
                    "根据我的体质，有什么养生建议吗？",
                    "我应该如何调整我的饮食习惯？",
                ]
            elif session_type == "targeted":
                # 可以根据用户的健康档案个性化建议
                health_profile = user.get("health_profile", {})
                constitution = health_profile.get("constitution_type", "BALANCED")

                if constitution == "QI_DEFICIENCY":
                    suggested_questions = [
                        "气虚体质应该注意什么？",
                        "有哪些适合气虚体质的食疗方案？",
                        "我经常感到疲劳，是否与我的体质有关？",
                        "气虚体质的人适合什么运动？",
                    ]
                elif constitution == "YANG_DEFICIENCY":
                    suggested_questions = [
                        "阳虚体质怎么调理？",
                        "我总是手脚冰凉，这是阳虚的表现吗？",
                        "阳虚体质适合吃什么食物？",
                        "冬季如何保护阳虚体质？",
                    ]
                else:
                    suggested_questions = [
                        "我的体质适合什么养生方法？",
                        "如何根据体质调整饮食？",
                        "有哪些症状需要特别关注？",
                        "针对我的体质，有哪些穴位可以自我按摩？",
                    ]
            elif session_type == "follow_up":
                # 获取上次会话的症状和建议，询问效果
                last_session = await self._get_last_session(user["id"])
                if last_session and "summary" in last_session:
                    symptoms = last_session.get("summary", {}).get("symptoms", [])
                    recommendations = last_session.get("summary", {}).get(
                        "recommendations", []
                    )

                    if symptoms:
                        symptom_names = [
                            s.get("name", "symptoms") for s in symptoms[:2]
                        ]
                        suggested_questions.append(
                            f"我上次提到的{'/'.join(symptom_names)}情况有好转吗？"
                        )

                    if recommendations:
                        rec_types = [
                            r.get("type", "recommendation") for r in recommendations[:2]
                        ]
                        suggested_questions.append(
                            f"我按照建议{'/'.join(rec_types)}执行了，效果如何？"
                        )

                    suggested_questions.extend(
                        [
                            "我有新出现的症状，需要怎么处理？",
                            "我需要调整当前的调理方案吗？",
                        ]
                    )
                else:
                    suggested_questions = [
                        "上次的症状是否有所改善？",
                        "您有执行我们上次讨论的调理方案吗？",
                        "有什么新的健康问题需要讨论吗？",
                        "您对当前的调理效果满意吗？",
                    ]

            return suggested_questions[: self.default_follow_up_count]

        except Exception as e:
            logger.error(f"生成建议问题失败: {e!s}")
            return [
                "您最近有什么不适吗？",
                "您想了解哪方面的健康知识？",
                "您的饮食习惯如何？",
                "您平时有做什么运动吗？",
            ]

    async def interact(
        self,
        session_id: str,
        user_message: str,
        timestamp: int | None = None,
        attached_data_urls: list[str] = None,
    ) -> dict:
        """
        处理用户与问诊系统的交互

        Args:
            session_id: 会话ID
            user_message: 用户消息
            timestamp: 时间戳
            attached_data_urls: 附加数据URL列表

        Returns:
            Dict: 交互响应
        """
        # 检查会话是否存在
        session = await self._get_session(session_id)
        if not session:
            logger.error(f"会话 {session_id} 不存在或已过期")
            raise ValueError(f"会话 {session_id} 不存在或已过期")

        # 更新会话最后交互时间
        session["last_interaction"] = datetime.now().timestamp()

        # 准备用户消息
        timestamp = timestamp or int(time.time())
        user_message_obj = {
            "role": "user",
            "content": user_message,
            "timestamp": timestamp,
            "attached_data_urls": attached_data_urls or [],
        }

        # 添加到会话历史
        if "history" not in session:
            session["history"] = []
        session["history"].append(user_message_obj)

        # 保持历史记录在最大限制内
        if len(session["history"]) > self.max_history:
            session["history"] = session["history"][-self.max_history :]

        # 使用LLM生成回复
        try:
            # 构建LLM输入上下文
            llm_response = await self._generate_llm_response(session)

            # 从LLM响应中提取信息
            response_text = llm_response.get("response_text", "")
            response_type = llm_response.get("response_type", "TEXT")
            detected_symptoms = llm_response.get("detected_symptoms", [])
            follow_up_questions = llm_response.get("follow_up_questions", [])

            # 创建系统响应对象
            system_response = {
                "role": "system",
                "content": response_text,
                "timestamp": int(time.time()),
                "response_type": response_type,
                "detected_symptoms": detected_symptoms,
                "follow_up_questions": follow_up_questions,
            }

            # 添加到会话历史
            session["history"].append(system_response)

            # 更新会话存储
            await self.session_repository.update_session(session_id, session)

            # 更新活跃会话缓存
            self.active_sessions[session_id] = session

            # 构建响应
            response = {
                "response_text": response_text,
                "response_type": response_type,
                "detected_symptoms": detected_symptoms,
                "follow_up_questions": follow_up_questions,
                "timestamp": system_response["timestamp"],
            }

            return response

        except Exception as e:
            logger.error(f"处理用户交互失败: {e!s}")
            raise

    async def _get_session(self, session_id: str) -> dict | None:
        """获取会话数据，先从缓存获取，缓存没有再从数据库获取"""
        # 先检查活跃会话缓存
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            # 检查会话是否过期
            if time.time() - session["last_interaction"] > self.session_timeout:
                # 会话已过期，从缓存中移除
                del self.active_sessions[session_id]
                # 更新会话状态为过期
                await self.session_repository.update_session_status(
                    session_id, "expired"
                )
                return None
            return session

        # 从数据库获取会话
        session = await self.session_repository.get_session_by_id(session_id)
        if session:
            # 检查会话是否过期
            if time.time() - session["last_interaction"] > self.session_timeout:
                # 更新会话状态为过期
                await self.session_repository.update_session_status(
                    session_id, "expired"
                )
                return None

            # 添加到活跃会话缓存
            self.active_sessions[session_id] = session

        return session

    async def _generate_llm_response(self, session: dict) -> dict:
        """使用LLM生成回复"""
        try:
            # 准备LLM输入
            history = session["history"]
            user_id = session["user_id"]

            # 获取用户信息以提供上下文
            user = await self.user_repository.get_user_by_id(user_id)

            # 构建LLM请求
            llm_request = {
                "user_id": user_id,
                "session_id": session["id"],
                "history": history,
                "user_profile": user.get("health_profile", {}),
                "session_type": session["type"],
                "language": session["language"],
            }

            # 调用LLM客户端获取响应
            llm_response = await self.llm_client.generate_response(llm_request)

            return llm_response

        except Exception as e:
            logger.error(f"生成LLM响应失败: {e!s}")
            # 返回一个简单的错误响应
            return {
                "response_text": "抱歉，我暂时无法处理您的请求，请稍后再试。",
                "response_type": "TEXT",
                "detected_symptoms": [],
                "follow_up_questions": [
                    "您能换个方式描述您的问题吗？",
                    "您可以尝试问一些其他问题。",
                ],
            }

    async def end_session(self, session_id: str, feedback: str = None) -> dict:
        """
        结束问诊会话并生成会话总结

        Args:
            session_id: 会话ID
            feedback: 用户反馈

        Returns:
            Dict: 会话总结
        """
        # 检查会话是否存在
        session = await self._get_session(session_id)
        if not session:
            logger.error(f"会话 {session_id} 不存在或已过期")
            raise ValueError(f"会话 {session_id} 不存在或已过期")

        # 添加用户反馈
        if feedback:
            session["feedback"] = feedback

        # 将会话状态设置为已结束
        session["status"] = "completed"
        session["ended_at"] = datetime.now().timestamp()
        session["duration"] = session["ended_at"] - session["created_at"]

        # 生成会话总结
        try:
            summary = await self._generate_session_summary(session)
            session["summary"] = summary

            # 更新会话存储
            await self.session_repository.update_session(session_id, session)

            # 从活跃会话缓存中移除
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]

            logger.info(f"会话 {session_id} 已结束，持续时间: {session['duration']}秒")

            return summary

        except Exception as e:
            logger.error(f"结束会话失败: {e!s}")
            raise

    async def _generate_session_summary(self, session: dict) -> dict:
        """生成会话总结"""
        try:
            # 提取会话中的症状信息
            detected_symptoms = await self._extract_symptoms_from_session(session)

            # 映射到中医证型
            tcm_patterns = await self._map_to_tcm_patterns(
                detected_symptoms, session["user_id"]
            )

            # 获取用户健康档案
            user = await self.user_repository.get_user_by_id(session["user_id"])
            health_profile = user.get("health_profile", {})

            # 生成后续建议
            recommendations = await self._generate_recommendations(
                detected_symptoms, tcm_patterns, health_profile
            )

            # 构建会话总结
            summary = {
                "session_id": session["id"],
                "user_id": session["user_id"],
                "detected_symptoms": detected_symptoms,
                "tcm_patterns": tcm_patterns,
                "health_profile": health_profile,
                "recommendations": recommendations,
                "session_duration": session["duration"],
                "session_end_time": session["ended_at"],
            }

            return summary

        except Exception as e:
            logger.error(f"生成会话总结失败: {e!s}")
            # 返回一个基本的总结
            return {
                "session_id": session["id"],
                "user_id": session["user_id"],
                "detected_symptoms": [],
                "tcm_patterns": [],
                "health_profile": {},
                "recommendations": [],
                "session_duration": session.get("duration", 0),
                "session_end_time": session.get("ended_at", int(time.time())),
            }

    async def _extract_symptoms_from_session(self, session: dict) -> list[dict]:
        """从会话中提取症状信息"""
        # 这里应该实现一个更复杂的逻辑，从会话历史中提取症状
        # 为简化示例，我们直接收集会话中系统回复中的检测到的症状
        all_symptoms = []
        symptom_names = set()  # 用于去重

        for msg in session.get("history", []):
            if msg.get("role") == "system" and "detected_symptoms" in msg:
                for symptom in msg.get("detected_symptoms", []):
                    if symptom not in symptom_names:
                        # 构建更详细的症状对象
                        symptom_obj = {
                            "symptom_name": symptom,
                            "severity": "MODERATE",  # 需要更精确的分析
                            "onset_time": session["created_at"],  # 假设在会话开始时就有
                            "duration": 0,  # 未知持续时间
                            "description": f"从问诊中发现的症状：{symptom}",
                            "confidence": 0.8,  # 默认置信度
                        }
                        all_symptoms.append(symptom_obj)
                        symptom_names.add(symptom)

        return all_symptoms

    async def _map_to_tcm_patterns(
        self, symptoms: list[dict], user_id: str
    ) -> list[dict]:
        """将症状映射到中医证型"""
        # 这里需要实现更复杂的中医证型映射逻辑
        # 为简化示例，我们返回一些简单的示例证型
        if not symptoms:
            return []

        # 获取用户体质信息
        user = await self.user_repository.get_user_by_id(user_id)
        constitution = user.get("health_profile", {}).get(
            "constitution_type", "BALANCED"
        )

        # 简单的证型匹配规则
        patterns = []
        symptom_names = [s["symptom_name"] for s in symptoms]

        # 检查是否存在疲劳、疲惫等气虚症状
        if any(
            s in symptom_names for s in ["疲劳", "乏力", "气短", "少气懒言", "疲惫"]
        ):
            patterns.append(
                {
                    "pattern_name": "气虚证",
                    "category": "虚证",
                    "match_score": 0.85,
                    "related_symptoms": [
                        s
                        for s in symptom_names
                        if s in ["疲劳", "乏力", "气短", "少气懒言", "疲惫"]
                    ],
                    "description": "气虚证是指人体内气的不足所导致的一系列症状",
                }
            )

        # 检查是否存在痰湿症状
        if any(
            s in symptom_names for s in ["痰多", "浮肿", "肥胖", "胸闷", "恶心", "胃胀"]
        ):
            patterns.append(
                {
                    "pattern_name": "痰湿证",
                    "category": "实证",
                    "match_score": 0.8,
                    "related_symptoms": [
                        s
                        for s in symptom_names
                        if s in ["痰多", "浮肿", "肥胖", "胸闷", "恶心", "胃胀"]
                    ],
                    "description": "痰湿证是指体内水液代谢异常，聚湿成痰所导致的一系列症状",
                }
            )

        # 检查是否存在阴虚症状
        if any(
            s in symptom_names
            for s in ["口干", "咽干", "潮热", "盗汗", "失眠", "五心烦热"]
        ):
            patterns.append(
                {
                    "pattern_name": "阴虚证",
                    "category": "虚证",
                    "match_score": 0.75,
                    "related_symptoms": [
                        s
                        for s in symptom_names
                        if s in ["口干", "咽干", "潮热", "盗汗", "失眠", "五心烦热"]
                    ],
                    "description": "阴虚证是指人体阴液亏损所导致的一系列症状",
                }
            )

        return patterns

    async def _generate_recommendations(
        self, symptoms: list[dict], tcm_patterns: list[dict], health_profile: dict
    ) -> list[dict]:
        """生成后续建议"""
        recommendations = []

        # 根据症状和证型生成建议
        if tcm_patterns:
            # 对于每个证型生成针对性建议
            for pattern in tcm_patterns:
                if pattern["pattern_name"] == "气虚证":
                    recommendations.append(
                        {
                            "type": "TCM_INTERVENTION",
                            "description": "补气养生调理方案",
                            "rationale": "针对气虚症状，建议通过饮食调理和适当运动增强体质",
                            "suggested_timeframe": int(time.time())
                            + 7 * 24 * 3600,  # 一周后
                        }
                    )
                    recommendations.append(
                        {
                            "type": "DIETARY_ADJUSTMENT",
                            "description": "气虚体质饮食调整",
                            "rationale": "增加黄芪、党参、大枣等补气食材，少食生冷",
                            "suggested_timeframe": int(time.time())
                            + 1 * 24 * 3600,  # 一天后
                        }
                    )

                elif pattern["pattern_name"] == "痰湿证":
                    recommendations.append(
                        {
                            "type": "LIFESTYLE_CHANGE",
                            "description": "祛湿生活方式调整",
                            "rationale": "调整作息，保持环境干燥，避免湿气侵袭",
                            "suggested_timeframe": int(time.time())
                            + 3 * 24 * 3600,  # 三天后
                        }
                    )
                    recommendations.append(
                        {
                            "type": "DIETARY_ADJUSTMENT",
                            "description": "祛湿饮食建议",
                            "rationale": "减少甜食、油腻食物摄入，增加薏米、红豆等祛湿食材",
                            "suggested_timeframe": int(time.time())
                            + 1 * 24 * 3600,  # 一天后
                        }
                    )

                elif pattern["pattern_name"] == "阴虚证":
                    recommendations.append(
                        {
                            "type": "TCM_INTERVENTION",
                            "description": "滋阴调理方案",
                            "rationale": "通过滋阴降火，改善阴虚症状",
                            "suggested_timeframe": int(time.time())
                            + 7 * 24 * 3600,  # 一周后
                        }
                    )
                    recommendations.append(
                        {
                            "type": "LIFESTYLE_CHANGE",
                            "description": "阴虚体质作息调整",
                            "rationale": "早睡早起，避免熬夜，减少辛辣刺激性食物",
                            "suggested_timeframe": int(time.time())
                            + 1 * 24 * 3600,  # 一天后
                        }
                    )

        # 如果没有明确的证型，但有症状，提供一般性建议
        elif symptoms:
            recommendations.append(
                {
                    "type": "MONITORING",
                    "description": "症状监测",
                    "rationale": "记录症状变化，为下次问诊提供参考",
                    "suggested_timeframe": int(time.time()) + 3 * 24 * 3600,  # 三天后
                }
            )
            recommendations.append(
                {
                    "type": "LIFESTYLE_CHANGE",
                    "description": "健康生活方式建议",
                    "rationale": "保持规律作息，均衡饮食，适当运动",
                    "suggested_timeframe": int(time.time()) + 1 * 24 * 3600,  # 一天后
                }
            )

        # 添加一个通用的跟进建议
        recommendations.append(
            {
                "type": "MONITORING",
                "description": "健康状况跟进",
                "rationale": "定期跟进评估健康状况变化",
                "suggested_timeframe": int(time.time()) + 14 * 24 * 3600,  # 两周后
            }
        )

        return recommendations
