"""
翻译服务gRPC处理器
"""

import logging
import time
from collections.abc import Iterator
from typing import Any

import grpc

from internal.service.optimized_accessibility_service import (
    OptimizedAccessibilityService,
)

logger = logging.getLogger(__name__)


class TranslationHandler:
    """翻译服务gRPC处理器类"""

    def __init__(self, service: OptimizedAccessibilityService):
        """初始化翻译服务处理器

        Args:
            service: 无障碍服务实例
        """
        self.service = service
        logger.info("翻译服务处理器初始化完成")

    async def speech_translation(
        self, request: pb2.SpeechTranslationRequest, context: grpc.aio.ServicerContext
    ) -> pb2.SpeechTranslationResponse:
        """处理语音翻译请求

        Args:
            request: 翻译请求
            context: gRPC服务上下文

        Returns:
            pb2.SpeechTranslationResponse: 翻译响应
        """
        logger.info(
            f"接收到语音翻译请求: 用户={request.user_id}, 源语言={request.source_language}, 目标语言={request.target_language}"
        )
        start_time = time.time()

        try:
            # 提取请求参数
            user_preferences = None
            if request.HasField("preferences"):
                user_preferences = {
                    "voice_type": request.preferences.voice_type,
                    "speech_rate": request.preferences.speech_rate,
                    "language": request.preferences.language,
                    "dialect": request.preferences.dialect,
                }

            # 调用服务处理
            result = self.service.speech_translation(
                request.audio_data,
                request.user_id,
                request.source_language,
                request.target_language,
                request.source_dialect if request.source_dialect else None,
                request.target_dialect if request.target_dialect else None,
                user_preferences,
            )

            # 构造响应
            response = pb2.SpeechTranslationResponse(
                source_text=result.get("source_text", ""),
                translated_text=result.get("translated_text", ""),
                translated_audio=result.get("translated_audio", b""),
                source_confidence=result.get("source_confidence", 0.0),
                translation_confidence=result.get("translation_confidence", 0.0),
                processing_time_ms=result.get("processing_time_ms", 0),
            )

            # 如果有错误，设置错误字段
            if "error" in result:
                response.error = result["error"]

            logger.info(
                f"语音翻译请求处理完成: 用户={request.user_id}, 耗时={(time.time() - start_time):.2f}秒"
            )
            return response

        except Exception as e:
            logger.error(f"语音翻译处理异常: {e!s}", exc_info=True)
            # 设置gRPC错误状态
            await context.set_code(grpc.StatusCode.INTERNAL)
            await context.set_details(f"翻译服务内部错误: {e!s}")
            return pb2.SpeechTranslationResponse(
                error=str(e),
                source_text="",
                translated_text="",
                translated_audio=b"",
                source_confidence=0.0,
                translation_confidence=0.0,
                processing_time_ms=int((time.time() - start_time) * 1000),
            )

    async def create_translation_session(
        self, request: pb2.CreateSessionRequest, context: grpc.aio.ServicerContext
    ) -> pb2.CreateSessionResponse:
        """创建翻译会话

        Args:
            request: 会话创建请求
            context: gRPC服务上下文

        Returns:
            pb2.CreateSessionResponse: 会话创建响应
        """
        logger.info(
            f"接收到创建翻译会话请求: 用户={request.user_id}, 源语言={request.source_language}, 目标语言={request.target_language}"
        )

        try:
            # 提取请求参数
            user_preferences = None
            if request.HasField("preferences"):
                user_preferences = {
                    "voice_type": request.preferences.voice_type,
                    "speech_rate": request.preferences.speech_rate,
                    "language": request.preferences.language,
                    "dialect": request.preferences.dialect,
                }

            # 调用服务处理
            result = self.service.create_translation_session(
                request.user_id,
                request.source_language,
                request.target_language,
                request.source_dialect if request.source_dialect else None,
                request.target_dialect if request.target_dialect else None,
                user_preferences,
            )

            # 构造响应
            response = pb2.CreateSessionResponse(
                session_id=result.get("session_id", ""),
                success=result.get("success", False),
                message=result.get("message", ""),
            )

            logger.info(
                f"创建翻译会话请求处理完成: 用户={request.user_id}, 会话ID={response.session_id}"
            )
            return response

        except Exception as e:
            logger.error(f"创建翻译会话异常: {e!s}", exc_info=True)
            # 设置gRPC错误状态
            await context.set_code(grpc.StatusCode.INTERNAL)
            await context.set_details(f"会话创建服务内部错误: {e!s}")
            return pb2.CreateSessionResponse(
                session_id="", success=False, message=str(e)
            )

    async def get_session_status(
        self, request: pb2.SessionStatusRequest, context: grpc.aio.ServicerContext
    ) -> pb2.SessionStatusResponse:
        """获取会话状态

        Args:
            request: 会话状态请求
            context: gRPC服务上下文

        Returns:
            pb2.SessionStatusResponse: 会话状态响应
        """
        logger.info(
            f"接收到获取会话状态请求: 会话ID={request.session_id}, 用户={request.user_id}"
        )

        try:
            # 调用服务处理
            result = self.service.get_session_status(
                request.session_id, request.user_id
            )

            # 构造基本响应
            response = pb2.SessionStatusResponse(session_id=request.session_id)

            # 如果有错误，设置错误字段并返回
            if "error" in result:
                response.error = result["error"]
                return response

            # 填充详细信息
            response.user_id = result.get("user_id", request.user_id)
            response.source_language = result.get("source_language", "")
            response.target_language = result.get("target_language", "")
            response.is_active = result.get("is_active", False)
            response.created_at = int(result.get("created_at", 0))
            response.last_activity = int(result.get("last_activity", 0))
            response.segment_count = result.get("segment_count", 0)
            response.duration_seconds = int(result.get("duration_seconds", 0))

            logger.info(f"获取会话状态请求处理完成: 会话ID={request.session_id}")
            return response

        except Exception as e:
            logger.error(f"获取会话状态异常: {e!s}", exc_info=True)
            # 设置gRPC错误状态
            await context.set_code(grpc.StatusCode.INTERNAL)
            await context.set_details(f"会话状态服务内部错误: {e!s}")
            return pb2.SessionStatusResponse(
                session_id=request.session_id, error=str(e)
            )

    async def streaming_speech_translation(
        self,
        request_iterator: Iterator[pb2.SpeechTranslationChunk],
        context: grpc.aio.ServicerContext,
    ) -> Iterator[pb2.SpeechTranslationResult]:
        """流式语音翻译处理

        Args:
            request_iterator: 请求迭代器
            context: gRPC服务上下文

        Yields:
            pb2.SpeechTranslationResult: 翻译结果
        """
        session_id = None
        user_id = None
        config = None

        try:
            # 处理流式请求
            async for request in request_iterator:
                # 提取请求信息
                if session_id is None:
                    session_id = request.session_id
                    user_id = request.user_id
                    logger.info(
                        f"开始处理流式翻译请求: 会话ID={session_id}, 用户ID={user_id}"
                    )

                    # 首个请求应包含配置信息
                    if request.HasField("config"):
                        config = request.config
                        logger.info(
                            f"流式翻译配置: 源语言={config.source_language}, 目标语言={config.target_language}"
                        )

                # 处理音频数据块
                if not session_id:
                    # 如果没有会话ID，创建一个新会话
                    if not config:
                        error_result = pb2.SpeechTranslationResult(
                            error="missing_configuration", is_final=True
                        )
                        yield error_result
                        return

                    # 创建会话
                    session_creation_result = await self.create_session_from_config(
                        user_id, config
                    )
                    if not session_creation_result.get("success", False):
                        error_result = pb2.SpeechTranslationResult(
                            error=session_creation_result.get(
                                "message", "session_creation_failed"
                            ),
                            is_final=True,
                        )
                        yield error_result
                        return

                    session_id = session_creation_result.get("session_id", "")

                # 处理数据块
                result = self.service.process_streaming_translation(
                    session_id, request.audio_chunk, user_id, request.is_final
                )

                # 如果有结果，生成响应
                if result:
                    response = pb2.SpeechTranslationResult(
                        source_text=result.get("source_text", ""),
                        translated_text=result.get("translated_text", ""),
                        translated_audio=result.get("translated_audio", b""),
                        is_final=result.get("is_final", False),
                        segment_id=result.get("segment_id", ""),
                    )

                    # 如果有错误，设置错误字段
                    if "error" in result:
                        response.error = result["error"]

                    yield response

            logger.info(f"流式翻译请求完成: 会话ID={session_id}, 用户ID={user_id}")

        except Exception as e:
            logger.error(f"流式翻译处理异常: {e!s}", exc_info=True)
            # 返回错误响应
            error_result = pb2.SpeechTranslationResult(error=str(e), is_final=True)
            yield error_result

    async def create_session_from_config(
        self, user_id: str, config: pb2.TranslationConfig
    ) -> dict[str, Any]:
        """根据配置创建会话

        Args:
            user_id: 用户ID
            config: 翻译配置

        Returns:
            Dict[str, Any]: 会话创建结果
        """
        # 提取请求参数
        user_preferences = None
        if config.HasField("preferences"):
            user_preferences = {
                "voice_type": config.preferences.voice_type,
                "speech_rate": config.preferences.speech_rate,
                "language": config.preferences.language,
                "dialect": config.preferences.dialect,
            }

        # 调用服务处理
        return self.service.create_translation_session(
            user_id,
            config.source_language,
            config.target_language,
            config.source_dialect if config.source_dialect else None,
            config.target_dialect if config.target_dialect else None,
            user_preferences,
        )

    async def get_supported_languages(
        self, request: pb2.SupportedLanguagesRequest, context: grpc.aio.ServicerContext
    ) -> pb2.SupportedLanguagesResponse:
        """获取支持的语言和方言列表

        Args:
            request: 语言支持请求
            context: gRPC服务上下文

        Returns:
            pb2.SupportedLanguagesResponse: 语言支持响应
        """
        logger.info(
            f"接收到获取支持语言请求: 用户={request.user_id}, 包含方言={request.include_dialects}"
        )

        try:
            # 调用服务处理
            result = self.service.get_supported_languages(
                request.user_id, request.include_dialects
            )

            # 构造响应
            response = pb2.SupportedLanguagesResponse()

            # 如果有错误，设置错误并返回
            if "error" in result:
                logger.error(f"获取支持语言失败: {result['error']}")
                await context.set_code(grpc.StatusCode.INTERNAL)
                await context.set_details(result["error"])
                return response

            # 添加语言列表
            for lang in result.get("languages", []):
                language_pb = pb2.Language(
                    code=lang.get("code", ""),
                    name=lang.get("name", ""),
                    supports_speech=lang.get("supports_speech", False),
                )
                response.languages.append(language_pb)

            # 添加语言对列表
            for pair in result.get("language_pairs", []):
                language_pair_pb = pb2.LanguagePair(
                    source_code=pair.get("source_code", ""),
                    source_name=pair.get("source_name", ""),
                    target_code=pair.get("target_code", ""),
                    target_name=pair.get("target_name", ""),
                    supports_speech=pair.get("supports_speech", False),
                )
                response.language_pairs.append(language_pair_pb)

            # 添加支持的方言列表
            for dialect in result.get("supported_dialects", []):
                if isinstance(dialect, dict):
                    # 如果是字典，提取dialect.code
                    response.supported_dialects.append(dialect.get("code", ""))
                else:
                    # 如果是字符串
                    response.supported_dialects.append(dialect)

            logger.info(
                f"获取支持语言请求处理完成: 语言数量={len(response.languages)}, 语言对数量={len(response.language_pairs)}"
            )
            return response

        except Exception as e:
            logger.error(f"获取支持语言异常: {e!s}", exc_info=True)
            # 设置gRPC错误状态
            await context.set_code(grpc.StatusCode.INTERNAL)
            await context.set_details(f"语言支持服务内部错误: {e!s}")
            return pb2.SupportedLanguagesResponse()
