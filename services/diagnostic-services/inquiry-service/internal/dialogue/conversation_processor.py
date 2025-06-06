"""
conversation_processor - 索克生活项目模块
"""

from internal.knowledge.knowledge_connector import KnowledgeConnector
from internal.llm.llm_client import LLMClient
import json
import logging
import os
import time

#!/usr/bin/env python3

"""
问诊会话处理模块 - 管理对话流程与知识增强

本模块负责处理问诊对话的完整生命周期，包括消息处理、症状提取、知识增强、
辨证分析、医学实体识别等核心功能，使LLM能更精准地进行中医诊断分析。
"""



logger = logging.getLogger(__name__)


class ConversationProcessor:
    """问诊会话处理器，管理对话流程与知识增强"""

    def __init__(
        self,
        config: dict,
        llm_client: LLMClient,
        knowledge_connector: KnowledgeConnector,
    ):
        """
        初始化会话处理器

        Args:
            config: 配置字典
            llm_client: LLM客户端
            knowledge_connector: 知识库连接器
        """
        self.config = config
        self.llm_client = llm_client
        self.knowledge_connector = knowledge_connector

        # 会话设置
        self.max_history_length = config.get("max_history_length", 20)
        self.system_prompt = self._load_system_prompt(
            config.get("system_prompt_path", "")
        )
        self.default_language = config.get("default_language", "zh-CN")

        # 辨证设置
        self.auto_extract_symptoms = config.get("auto_extract_symptoms", True)
        self.syndrome_threshold = config.get("syndrome_threshold", 0.8)

        # 内部状态
        self._active_sessions = {}

        logger.info("会话处理器初始化完成")

    async def process_message(
        self, session_id: str, user_id: str, message: str, metadata: dict = None
    ) -> dict:
        """
        处理用户消息

        Args:
            session_id: 会话ID
            user_id: 用户ID
            message: 用户消息
            metadata: 元数据，包含上下文信息

        Returns:
            Dict: 包含回复和会话状态的响应
        """
        # 获取或创建会话
        session = self._get_or_create_session(session_id, user_id, metadata)

        # 更新会话状态
        session["last_active"] = time.time()
        session["message_count"] += 1

        # 添加用户消息到历史
        session["history"].append({"role": "user", "content": message})

        # 限制历史长度
        if (
            len(session["history"]) > self.max_history_length * 2
        ):  # 因为每次对话有用户和助手两条消息
            session["history"] = session["history"][-self.max_history_length * 2 :]

        try:
            # 处理症状提取
            if self.auto_extract_symptoms:
                await self._extract_symptoms(session, message)

            # 知识增强
            enhanced_context = await self._enhance_with_knowledge(session, message)

            # 生成回复
            response = await self._generate_response(session, message, enhanced_context)

            # 提取辨证结果（如果回复中包含）
            await self._extract_syndrome_patterns(session, response)

            # 添加助手回复到历史
            session["history"].append({"role": "assistant", "content": response})

            # 更新会话状态
            session["state"] = self._determine_session_state(session)

            return {
                "session_id": session_id,
                "response": response,
                "session_state": session["state"],
                "extracted_symptoms": session.get("symptoms", []),
                "syndrome_patterns": session.get("syndrome_patterns", []),
                "confidence": session.get("diagnosis_confidence", 0.0),
            }

        except Exception as e:
            logger.error(f"处理消息失败: {e!s}", exc_info=True)
            error_response = f"很抱歉，我现在无法处理您的问题。错误：{e!s}"
            session["history"].append({"role": "assistant", "content": error_response})

            return {
                "session_id": session_id,
                "response": error_response,
                "session_state": "error",
                "error": str(e),
            }

    async def get_session_info(self, session_id: str) -> dict:
        """
        获取会话信息

        Args:
            session_id: 会话ID

        Returns:
            Dict: 会话信息
        """
        if session_id not in self._active_sessions:
            return {"error": "会话不存在"}

        session = self._active_sessions[session_id]

        # 构建会话摘要，不包含完整历史
        return {
            "session_id": session_id,
            "user_id": session.get("user_id"),
            "created_at": session.get("created_at"),
            "last_active": session.get("last_active"),
            "message_count": session.get("message_count"),
            "state": session.get("state"),
            "symptoms": session.get("symptoms", []),
            "syndrome_patterns": session.get("syndrome_patterns", []),
            "diagnosis_confidence": session.get("diagnosis_confidence", 0.0),
            "language": session.get("language"),
            "metadata": session.get("metadata"),
        }

    async def reset_session(self, session_id: str) -> dict:
        """
        重置会话状态

        Args:
            session_id: 会话ID

        Returns:
            Dict: 重置结果
        """
        if session_id not in self._active_sessions:
            return {"error": "会话不存在", "success": False}

        session = self._active_sessions[session_id]
        user_id = session["user_id"]
        metadata = session["metadata"]

        # 保留一些元数据，重置会话
        self._active_sessions[session_id] = self._create_new_session(user_id, metadata)
        self._active_sessions[session_id]["previous_session_count"] = (
            session.get("previous_session_count", 0) + 1
        )

        return {"session_id": session_id, "success": True, "message": "会话已重置"}

    def _get_or_create_session(
        self, session_id: str, user_id: str, metadata: dict = None
    ) -> dict:
        """获取或创建会话"""
        if session_id in self._active_sessions:
            return self._active_sessions[session_id]

        # 创建新会话
        session = self._create_new_session(user_id, metadata)
        self._active_sessions[session_id] = session
        return session

    def _create_new_session(self, user_id: str, metadata: dict = None) -> dict:
        """创建新会话"""
        now = time.time()
        return {
            "user_id": user_id,
            "created_at": now,
            "last_active": now,
            "message_count": 0,
            "history": [],
            "state": "initial",
            "symptoms": [],
            "syndrome_patterns": [],
            "diagnosis_confidence": 0.0,
            "language": self.default_language,
            "metadata": metadata or {},
            "previous_session_count": 0,
        }

    def _load_system_prompt(self, prompt_path: str) -> str:
        """加载系统提示词"""
        default_prompt = """
你是索克生活的中医智能问诊助手，具有专业的中医理论知识和问诊技能。请使用礼貌、专业的语气与用户交流，帮助用户了解自己的健康状况。

在问诊过程中，请注意以下几点：
1. 询问用户的主要症状、发病时间、加重或缓解因素等信息
2. 根据中医理论进行辨证，考虑病因、病机和证型
3. 明确告知这只是辅助诊断，重要健康问题应当到医院就诊
4. 不要轻易下结论，应当全面收集信息后再给出辨证意见
5. 使用用户易于理解的语言解释中医术语

你应当在保持专业性的同时，表达温暖和关怀，让用户感到被重视和理解。
""".strip()

        if not prompt_path or not os.path.exists(prompt_path):
            logger.warning(f"未找到系统提示词文件: {prompt_path}，使用默认提示词")
            return default_prompt

        try:
            with open(prompt_path, encoding="utf-8") as f:
                prompt = f.read().strip()
                return prompt if prompt else default_prompt
        except Exception as e:
            logger.error(f"读取系统提示词文件失败: {e!s}")
            return default_prompt

    async def _extract_symptoms(self, session: dict, message: str) -> None:
        """从用户消息中提取症状"""
        # 使用LLM提取症状
        extraction_prompt = f"""
分析以下用户描述，提取用户提到的所有健康症状。仅输出JSON格式的症状列表，无需其他内容。

用户描述: '{message}'

仅输出如下JSON格式：
{{
  "symptoms": ["症状1", "症状2", ...]
}}
""".strip()

        try:
            response = await self.llm_client.generate(
                prompt=extraction_prompt,
                model="gpt-3.5-turbo",  # 使用更轻量的模型提取症状
                temperature=0.0,
                max_tokens=150,
            )

            # 解析JSON响应
            try:
                result = json.loads(response)
                if "symptoms" in result and isinstance(result["symptoms"], list):
                    # 添加新症状到会话（去重）
                    existing_symptoms = set(session.get("symptoms", []))
                    new_symptoms = [
                        s
                        for s in result["symptoms"]
                        if s and s not in existing_symptoms
                    ]

                    if new_symptoms:
                        session["symptoms"] = list(
                            existing_symptoms.union(new_symptoms)
                        )
                        logger.info(f"从消息中提取到新症状: {new_symptoms}")
            except json.JSONDecodeError:
                logger.warning(f"解析症状JSON失败: {response}")

        except Exception as e:
            logger.error(f"提取症状失败: {e!s}")

    async def _enhance_with_knowledge(self, session: dict, message: str) -> str:
        """使用医学知识增强上下文"""
        # 如果没有症状，返回空增强上下文
        symptoms = session.get("symptoms", [])
        if not symptoms:
            return ""

        try:
            # 为每个症状获取分析信息
            symptom_analyses = []
            for symptom in symptoms[:5]:  # 限制分析的症状数量
                analysis = await self.knowledge_connector.get_symptom_analysis(symptom)
                if "error" not in analysis:
                    symptom_analyses.append(analysis)

            # 获取可能相关的证型
            syndrome_patterns = []
            if symptoms:
                symptoms_query = ", ".join(symptoms[:5])
                tcm_results = await self.knowledge_connector.search_knowledge(
                    symptoms_query, knowledge_type="tcm", context={"symptoms": symptoms}
                )
                syndrome_patterns = tcm_results

            # 构建增强上下文
            if symptom_analyses or syndrome_patterns:
                context_parts = ["## 医学知识库相关信息"]

                # 添加症状分析
                if symptom_analyses:
                    context_parts.append("### 症状分析")
                    for analysis in symptom_analyses:
                        tcm_analysis = analysis.get("tcm_analysis", {})
                        causes = ", ".join(tcm_analysis.get("common_causes", ["未知"]))
                        diff = tcm_analysis.get("differentiation", "无分析数据")

                        context_parts.append(
                            f"- 症状 [{analysis['name']}] 可能的病因: {causes}"
                        )
                        context_parts.append(f"  鉴别要点: {diff}")

                # 添加相关证型
                if syndrome_patterns:
                    context_parts.append("### 相关证型参考")
                    for pattern in syndrome_patterns[:2]:  # 限制显示的证型数量
                        context_parts.append(
                            f"- {pattern['title']}: {pattern['content']}"
                        )

                return "\n".join(context_parts)

            return ""

        except Exception as e:
            logger.error(f"知识增强失败: {e!s}")
            return ""

    async def _generate_response(
        self, session: dict, message: str, enhanced_context: str
    ) -> str:
        """生成回复"""
        # 构建完整的消息历史
        messages = [{"role": "system", "content": self.system_prompt}]

        # 添加对话历史
        messages.extend(session["history"])

        # 添加知识增强上下文（如果有）
        if enhanced_context:
            messages.append({"role": "system", "content": enhanced_context})

        # 调用LLM生成回复
        try:
            # 确保最后一条消息是用户消息
            if messages[-1]["role"] != "user":
                messages.append({"role": "user", "content": message})

            response = await self.llm_client.chat_completion(
                messages=messages,
                model=self.config.get("llm_model", "gpt-4o"),
                temperature=self.config.get("temperature", 0.7),
                max_tokens=self.config.get("max_tokens", 800),
            )

            return response.get("content", "抱歉，我无法生成回复")

        except Exception as e:
            logger.error(f"生成回复失败: {e!s}")
            return f"抱歉，我现在无法回答您的问题。技术原因：{e!s}"

    async def _extract_syndrome_patterns(self, session: dict, response: str) -> None:
        """从回复中提取辨证结果"""
        # 仅当回复足够长且可能包含辨证结果时才提取
        if len(response) < 100:
            return

        extraction_prompt = f"""
从以下中医助手的回复中提取辨证结果。仅输出JSON格式，包含证型列表及对应的置信度。如果没有明确的辨证结果，则返回空列表。

助手回复:
{response}

仅输出如下JSON格式：
{{
  "syndrome_patterns": [
    {{"name": "证型名称", "confidence": 0.95, "description": "证型简短描述"}}
  ],
  "overall_confidence": 0.8
}}
""".strip()

        try:
            result = await self.llm_client.generate(
                prompt=extraction_prompt,
                model="gpt-3.5-turbo",  # 使用更轻量的模型提取辨证
                temperature=0.0,
                max_tokens=200,
            )

            # 解析JSON响应
            try:
                data = json.loads(result)
                if "syndrome_patterns" in data and isinstance(
                    data["syndrome_patterns"], list
                ):
                    # 更新会话中的辨证结果
                    session["syndrome_patterns"] = data["syndrome_patterns"]
                    session["diagnosis_confidence"] = data.get(
                        "overall_confidence", 0.0
                    )

                    # 如果有辨证结果，尝试从知识库获取详细信息
                    if session["syndrome_patterns"]:
                        await self._enrich_syndrome_patterns(session)

                        logger.info(f"提取到辨证结果: {session['syndrome_patterns']}")
            except json.JSONDecodeError:
                logger.warning(f"解析辨证JSON失败: {result}")

        except Exception as e:
            logger.error(f"提取辨证结果失败: {e!s}")

    async def _enrich_syndrome_patterns(self, session: dict) -> None:
        """为辨证结果添加详细信息"""
        if not session.get("syndrome_patterns"):
            return

        for pattern in session["syndrome_patterns"]:
            try:
                # 获取证型详细信息
                if "name" in pattern:
                    info = await self.knowledge_connector.get_syndrome_information(
                        pattern["name"]
                    )

                    # 添加详细信息但保留原始置信度
                    pattern["details"] = info
            except Exception as e:
                logger.error(f"获取证型详细信息失败: {e!s}")

    def _determine_session_state(self, session: dict) -> str:
        """确定会话状态"""
        # 如果有足够的症状和辨证结果，则认为诊断完成
        if len(session.get("symptoms", [])) >= 3 and session.get("syndrome_patterns"):
            if session.get("diagnosis_confidence", 0) >= self.syndrome_threshold:
                return "diagnosed"
            return "partially_diagnosed"

        # 如果有症状但没有辨证结果，则认为正在问诊
        if session.get("symptoms"):
            return "inquiring"

        # 如果消息数很少，则认为初始状态
        if session.get("message_count", 0) <= 2:
            return "initial"

        # 默认为对话中
        return "conversing"
