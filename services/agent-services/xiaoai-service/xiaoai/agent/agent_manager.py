#!/usr/bin/env python3
"""
智能体管理器
负责小艾智能体的核心逻辑, 包括多模态处理、LLM推理和会话管理
"""

import asyncio
import logging
import time
import uuid
from typing import Any

from ..integration.accessibility_client import (
    AccessibilityConfig,
)
from ..integration.device_manager import DeviceConfig, get_device_manager
from ..repository.file_session_repository import FileSessionRepository
from ..repository.session_repository import SessionRepository
from ..utils.config_loader import get_config
from ..utils.metrics import track_llm_metrics
from .model_factory import get_model_factory

logger = logging.getLogger(__name__)

class AgentManager:
    """智能体管理器, 负责处理多模态输入, 管理会话和生成响应"""

    def __init__(self, sessionrepository: SessionRepository = None):
        """
        初始化智能体管理器

        Args:
            session_repository: 会话存储库
        """
        self.config = get_config()
        self.metrics = get_metrics_collector()

        # 设置依赖组件 - 根据配置选择存储库
        if session_repository:
            self.sessionrepository = session_repository
        else:
            # 检查是否启用文件存储
            self.config.get_section('file_storage')
            if file_storage_config.get('enabled', False):
                self.sessionrepository = FileSessionRepository()
            else:
                self.sessionrepository = SessionRepository()

        # 加载模型配置
        self.llmconfig = self.config.get_section('models.llm')
        self.localllm_config = self.config.get_section('models.local_llm')
        self.embeddingconfig = self.config.get_section('models.embedding')
        self.speechconfig = self.config.get_section('models.speech')
        self.visionconfig = self.config.get_section('models.vision')

        # 加载会话配置
        self.conversationconfig = self.config.get_section('conversation')
        self.systemprompt = self.conversation_config.get('system_prompt', '')
        self.maxhistory_turns = self.conversation_config.get('max_history_turns', 20)
        self.contextwindow_size = self.conversation_config.get('context_window_size', 4096)

        # 设置默认模型
        self.primarymodel = self.llm_config.get('primary_model', 'gpt-4o-mini')
        self.fallbackmodel = self.llm_config.get('fallback_model', 'llama-3-8b')

        self.modelfactory = None

        self.accessibilityclient = None

        self.devicemanager = None

        # 活跃会话映射 session_id -> session_data
        self.activesessions: dict[str, dict[str, Any]] = {}

        # 定期更新活跃会话数指标
        self._update_active_sessions_metric()

        logger.info("智能体管理器初始化完成, 主模型: %s, 备用模型: %s",
                   self.primarymodel, self.fallbackmodel)

    async def initialize(self):
        """异步初始化模型工厂和无障碍服务"""
        # 初始化模型工厂
        if self.model_factory is None:
            # 检查开发环境
            self.config.get_section('development')
            if development_config and development_config.get('mock_services', False):
                # 开发环境使用模拟工厂
                from .mock_model_factory import get_mock_model_factory
                self.modelfactory = await get_mock_model_factory()
                logger.info("开发环境: 智能体管理器使用模拟模型工厂")
            else:
                # 检查是否配置了DeepSeek
                self.config.get_section('models.deepseek') or {}
                self.config.get_section('models.llm') or {}

                import os
                (
                    os.environ.get('DEEPSEEK_API_KEY') or
                    deepseek_config.get('api_key') or
                    llm_config.get('api_key')
                )
                llm_config.get('primary_model', '')

                # 如果有API密钥且主模型是deepseek或有deepseek配置, 使用DeepSeek
                if api_key and ('deepseek' in primary_model.lower() or deepseek_config or os.environ.get('DEEPSEEK_API_KEY')):
                    # 使用DeepSeek模型工厂
                    from .deepseek_model_factory import get_deepseek_model_factory
                    self.modelfactory = await get_deepseek_model_factory()
                    logger.info("生产环境: 智能体管理器使用DeepSeek模型工厂")
                else:
                    # 使用通用模型工厂
                    self.modelfactory = await get_model_factory()
                    logger.info("生产环境: 智能体管理器使用通用模型工厂")

        # 初始化无障碍服务客户端
        if self.accessibility_client is None:
            try:
                # 获取无障碍服务配置
                self.config.get_section('accessibility') or {}

                config = AccessibilityConfig(
                    service_url=accessibility_config.get('service_url', 'http://localhost:50051'),
                    timeout=accessibility_config.get('timeout', 30),
                    enabled=accessibility_config.get('enabled', True)
                )

                self.accessibilityclient = await get_accessibility_client(config)
                logger.info("无障碍服务客户端初始化成功")

            except Exception as e:
                logger.warning(f"无障碍服务客户端初始化失败: {e}")
                self.accessibilityclient = None

        # 初始化设备管理器
        if self.device_manager is None:
            try:
                # 获取设备配置
                self.config.get_section('devices') or {}

                config = DeviceConfig(
                    camera_enabled=device_config.get('camera_enabled', True),
                    microphone_enabled=device_config.get('microphone_enabled', True),
                    screen_enabled=device_config.get('screen_enabled', True),
                    max_recording_duration=device_config.get('max_recording_duration', 30),
                    max_image_size=device_config.get('max_image_size', 1024 * 1024)
                )

                self.devicemanager = await get_device_manager(config)
                logger.info("设备管理器初始化成功")

            except Exception as e:
                logger.warning(f"设备管理器初始化失败: {e}")
                self.devicemanager = None

        # 启动定期指标更新任务
        asyncio.create_task(self._schedule_metric_update())

    def _update_active_sessions_metric(self):
        """更新活跃会话数指标"""
        self.metrics.update_active_sessions(len(self.activesessions))

    async def _schedule_metric_update(self):
        """定期更新指标的任务"""
        await asyncio.sleep(60)  # 每分钟更新一次
        self._update_active_sessions_metric()

    @track_llm_metrics(model="primary", query_type="chat")
    async def chat(self, userid: str, message: str, sessionid: str | None = None,
                 contextsize: int | None = None) -> dict[str, Any]:
        """
        处理用户聊天消息并生成响应

        Args:
            user_id: 用户ID
            message: 用户消息
            session_id: 会话ID, 如果为None则创建新会话
            context_size: 上下文大小, 如果为None则使用默认值

        Returns:
            Dict[str, Any]: 包含响应消息和元数据的字典
        """
        # 记录聊天消息指标
        self.metrics.increment_chat_message_count("received", "text")

        # 确保会话ID存在
        if not session_id:
            sessionid = str(uuid.uuid4())
            logger.info("创建新会话, 用户ID: %s, 会话ID: %s", userid, sessionid)
            self.metrics.increment_session_count("started")

        # 获取会话上下文
        context = await self._get_or_create_session(userid, sessionid)

        # 获取要使用的上下文大小
        ctxsize = context_size or self.max_history_turns

        try:
            # 准备聊天上下文和提示
            chatcontext = self._prepare_chat_context(context, message, ctxsize)

            # 调用LLM生成响应
            responsetext, responsemeta = await self._generate_llm_response(chatcontext)

            # 更新会话历史
            await self._update_session_history(context, message, responsetext)

            # 记录指标
            self.metrics.increment_chat_message_count("sent", "text")

            # 构建响应对象
            response = {
                'message_id': str(uuid.uuid4()),
                'message': responsetext,
                'confidence': response_meta.get('confidence', 0.9),
                'suggested_actions': response_meta.get('suggested_actions', []),
                'metadata': {
                    'model': response_meta.get('model', self.primarymodel),
                    'provider': response_meta.get('provider', '未知'),
                    'session_id': sessionid,
                    'timestamp': int(time.time())
                }
            }

            return response

        except Exception as e:
            logger.error("聊天处理失败, 用户ID: %s, 会话ID: %s, 错误: %s",
                        userid, sessionid, str(e))

            # 返回错误响应
            return {
                'message_id': str(uuid.uuid4()),
                'message': f"抱歉, 我处理您的消息时遇到了问题: {e!s}",
                'confidence': 0.5,
                'suggested_actions': ["重试", "联系客服"],
                'metadata': {
                    'error': str(e),
                    'session_id': sessionid,
                    'timestamp': int(time.time())
                }
            }

    async def process_multimodal_input(self, userid: str, inputdata: dict[str, Any],
                                      sessionid: str | None = None) -> dict[str, Any]:
        """
        处理多模态输入(语音、图像、文本、手语等)

        Args:
            user_id: 用户ID
            input_data: 多模态输入数据
            session_id: 会话ID

        Returns:
            Dict[str, Any]: 处理结果
        """
        time.time()

        # 确保会话ID存在
        if not session_id:
            sessionid = str(uuid.uuid4())

        # 判断输入类型
        inputtype = self._determine_input_type(inputdata)
        inputsize = self._calculate_input_size(inputdata)

        try:
            # 根据输入类型调用相应的处理方法
            if inputtype == 'voice':
                result = await self._process_voice_input(inputdata, userid, sessionid)
            elif inputtype == 'image':
                result = await self._process_image_input(inputdata, userid, sessionid)
            elif inputtype == 'text':
                result = await self._process_text_input(inputdata, userid, sessionid)
            elif inputtype == 'sign':
                result = await self._process_sign_language_input(inputdata, userid, sessionid)
            else:
                raise ValueError(f"不支持的输入类型: {input_type}")

            # 记录处理指标
            latency = time.time() - start_time
            self.metrics.track_multimodal_process(inputtype, "success", latency, inputsize)

            return result

        except Exception as e:
            logger.error("多模态处理失败, 类型: %s, 用户ID: %s, 错误: %s",
                        inputtype, userid, str(e))

            # 记录处理指标
            latency = time.time() - start_time
            self.metrics.track_multimodal_process(inputtype, "failure", latency, inputsize)

            # 返回错误结果
            return {
                'request_id': str(uuid.uuid4()),
                'error_message': f"处理失败: {e!s}",
                'confidence': 0.0,
                'metadata': {
                    'session_id': sessionid,
                    'timestamp': int(time.time())
                }
            }

    async def generate_health_summary(self, userid: str, healthdata: dict[str, Any]) -> dict[str, Any]:
        """
        生成用户健康摘要

        Args:
            user_id: 用户ID
            health_data: 健康数据

        Returns:
            Dict[str, Any]: 健康摘要
        """
        # 这里会结合用户健康记录和LLM生成个性化健康摘要
        return {
            'summary_id': str(uuid.uuid4()),
            'text_summary': '这里是您的健康摘要...',
            'trends': [],
            'metrics': [],
            'recommendations': [],
            'generated_at': int(time.time())
        }

    async def _get_or_create_session(self, userid: str, sessionid: str) -> dict[str, Any]:
        """获取或创建会话"""
        # 检查是否在活跃会话中
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]

        # 尝试从存储库加载
        session = await self.session_repository.get_session(sessionid)

        if not session:
            # 创建新会话
            session = {
                'session_id': sessionid,
                'user_id': userid,
                'history': [],
                'created_at': int(time.time()),
                'last_active': int(time.time()),
                'metadata': {}
            }

            # 保存新会话
            await self.session_repository.save_session(session)

        # 添加到活跃会话
        self.active_sessions[session_id] = session
        self._update_active_sessions_metric()

        return session

    def _prepare_chat_context(self, session: dict[str, Any], message: str, contextsize: int) -> dict[str, Any]:
        """准备聊天上下文"""
        # 获取历史消息, 限制数量
        history = session['history'][-context_size:] if len(session['history']) > context_size else session['history']

        # 构建上下文对象
        return {
            'system_prompt': self.systemprompt,
            'history': history,
            'current_message': message,
            'user_id': session['user_id'],
            'session_id': session['session_id'],
            'timestamp': int(time.time())
        }

    async def _generate_llm_response(self, context: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        """
        使用LLM生成响应

        Args:
            context: 聊天上下文

        Returns:
            Tuple[str, Dict[str, Any]]: 响应文本和元数据
        """
        # 确保模型工厂已初始化
        if self.model_factory is None:
            await self.initialize()

        # 构建提示
        messages = self._build_prompt_messages(context)

        # 使用模型工厂生成响应
        return await self.model_factory.generate_chat_completion(
            model=self.primarymodel,
            messages=messages,
            temperature=self.llm_config.get('temperature', 0.7),
            max_tokens=self.llm_config.get('max_tokens', 2048)
        )

    def _build_prompt_messages(self, context: dict[str, Any]) -> list[dict[str, str]]:
        """构建提示消息列表"""
        messages = [
            {"role": "system", "content": context['system_prompt']}
        ]

        # 添加历史消息
        for entry in context['history']:
            messages.append({"role": "user", "content": entry['user_message']})
            messages.append({"role": "assistant", "content": entry['assistant_message']})

        # 添加当前消息
        messages.append({"role": "user", "content": context['current_message']})

        return messages

    async def _update_session_history(self, session: dict[str, Any], usermessage: str, assistantmessage: str):
        """
        更新会话历史

        Args:
            session: 会话对象
            user_message: 用户消息
            assistant_message: 助手响应
        """
        # 添加新的对话记录
        session['history'].append({
            'user_message': usermessage,
            'assistant_message': assistantmessage,
            'timestamp': int(time.time())
        })

        # 如果历史记录过长, 删除最早的记录
        self.max_history_turns * 2  # 考虑到每轮对话有用户和助手两条消息
        if len(session['history']) > max_history:
            session['history'] = session['history'][-max_history:]

        # 更新会话最后活跃时间
        session['last_active'] = int(time.time())

        # 保存会话更新
        if self.conversation_config.get('persist_history', True):
            await self.session_repository.save_session(session)

    def _determine_input_type(self, inputdata: dict[str, Any]) -> str:
        """
        确定输入数据类型

        Args:
            input_data: 输入数据

        Returns:
            str: 输入类型 (voice, image, text, sign)
        """
        if 'voice' in input_data:
            return 'voice'
        elif 'image' in input_data:
            return 'image'
        elif 'text' in input_data:
            return 'text'
        elif 'sign' in input_data:
            return 'sign'
        else:
            return 'unknown'

    def _calculate_input_size(self, inputdata: dict[str, Any]) -> int:
        """
        计算输入数据大小

        Args:
            input_data: 输入数据

        Returns:
            int: 数据大小(bytes)
        """
        for key in ['voice', 'image', 'text', 'sign']:
            if key in input_data:
                data = input_data[key]
                if isinstance(data, bytes):
                    return len(data)
                elif isinstance(data, str):
                    return len(data.encode('utf-8'))
        return 0

    async def _process_voice_input(self, inputdata: dict[str, Any], userid: str, sessionid: str) -> dict[str, Any]:
        """处理语音输入"""
        audiodata = input_data.get('voice', b'')
        logger.info("处理语音输入, 用户ID: %s, 会话ID: %s, 数据大小: %d",
                   userid, sessionid, len(audiodata))

        transcribedtext = "这是测试用的语音转文本结果"
        accessibilityresult = None

        # 使用无障碍服务处理语音输入
        if self.accessibility_client:
            try:
                await self.accessibility_client.process_voice_input(
                    audio_data=audiodata,
                    user_id=userid,
                    context="health_consultation",
                    language="zh-CN"
                )

                if voice_result.get('success'):
                    transcribedtext = voice_result.get('recognized_text', transcribedtext)
                    accessibilityresult = voice_result
                    logger.info("无障碍语音识别成功: %s", transcribedtext)
                else:
                    logger.warning(f"无障碍语音处理失败: {voice_result.get('error')}")

            except Exception as e:
                logger.error(f"无障碍语音处理异常: {e}")

        # 处理文本内容
        await self.chat(userid, transcribedtext, sessionid)

        # 返回处理结果, 包含无障碍信息
        result = {
            'request_id': str(uuid.uuid4()),
            'transcription': transcribedtext,
            'response': chat_result['message'],
            'confidence': chat_result['confidence'],
            'metadata': {
                'session_id': sessionid,
                'timestamp': int(time.time())
            }
        }

        # 添加无障碍服务结果
        if accessibility_result:
            result['accessibility'] = {
                'voice_recognition': accessibilityresult,
                'audio_response': accessibility_result.get('response_audio', ''),
                'service_confidence': accessibility_result.get('confidence', 0.0)
            }

        return result

    async def _process_image_input(self, inputdata: dict[str, Any], userid: str, sessionid: str) -> dict[str, Any]:
        """处理图像输入"""
        imagedata = input_data.get('image', b'')
        logger.info("处理图像输入, 用户ID: %s, 会话ID: %s, 数据大小: %d",
                   userid, sessionid, len(imagedata))

        imagedescription = "这是一张舌象图像, 舌体淡红, 舌苔薄白"
        accessibilityresult = None

        # 使用无障碍服务处理图像输入
        if self.accessibility_client:
            try:
                await self.accessibility_client.process_image_input(
                    image_data=imagedata,
                    user_id=userid,
                    image_type="tongue",
                    context="visual_diagnosis"
                )

                if image_result.get('success'):
                    image_result.get('scene_description', '')
                    image_result.get('medical_features', [])

                    if scene_desc:
                        imagedescription = scene_desc

                    # 整合医学特征信息
                    if medical_features:
                        ", ".join([f"{f.get('type', '')}: {f.get('description', '')}"
                                                 for f in medical_features])
                        image_description += f"。医学特征: {features_text}"

                    accessibilityresult = image_result
                    logger.info("无障碍图像分析成功: %s", imagedescription)
                else:
                    logger.warning(f"无障碍图像处理失败: {image_result.get('error')}")

            except Exception as e:
                logger.error(f"无障碍图像处理异常: {e}")

        # 构建包含图像分析的提示
        prompt = f"根据以下图像分析结果, 给出中医健康建议。图像分析: {image_description}"

        # 处理提示内容
        await self.chat(userid, prompt, sessionid)

        # 返回处理结果, 包含无障碍信息
        result = {
            'request_id': str(uuid.uuid4()),
            'image_analysis': imagedescription,
            'response': chat_result['message'],
            'confidence': chat_result['confidence'],
            'metadata': {
                'session_id': sessionid,
                'timestamp': int(time.time())
            }
        }

        # 添加无障碍服务结果
        if accessibility_result:
            result['accessibility'] = {
                'image_analysis': accessibilityresult,
                'audio_guidance': accessibility_result.get('audio_guidance', ''),
                'navigation_guidance': accessibility_result.get('navigation_guidance', ''),
                'service_confidence': accessibility_result.get('confidence', 0.0)
            }

        return result

    async def _process_text_input(self, inputdata: dict[str, Any], userid: str, sessionid: str) -> dict[str, Any]:
        """处理文本输入"""
        text = input_data.get('text', '')
        logger.info("处理文本输入, 用户ID: %s, 会话ID: %s, 文本长度: %d",
                   userid, sessionid, len(text))

        # 直接处理文本内容
        await self.chat(userid, text, sessionid)

        # 返回处理结果
        return {
            'request_id': str(uuid.uuid4()),
            'input_text': text,
            'response': chat_result['message'],
            'confidence': chat_result['confidence'],
            'metadata': {
                'session_id': sessionid,
                'timestamp': int(time.time())
            }
        }

    async def _process_sign_language_input(self, inputdata: dict[str, Any], userid: str, sessionid: str) -> dict[str, Any]:
        """处理手语输入"""
        logger.info("处理手语输入, 用户ID: %s, 会话ID: %s, 数据大小: %d",
                   userid, sessionid, len(input_data.get('sign', b'')))

        # 这里是简化处理, 实际应该调用手语识别服务
        signtext = "这是测试用的手语识别文本"

        # 处理识别出的文本
        await self.chat(userid, signtext, sessionid)

        # 返回处理结果
        return {
            'request_id': str(uuid.uuid4()),
            'sign_text': signtext,
            'response': chat_result['message'],
            'confidence': chat_result['confidence'],
            'metadata': {
                'session_id': sessionid,
                'timestamp': int(time.time())
            }
        }

    async def generate_accessible_content(self, content: str, userid: str,
                                        contenttype: str = "health_advice",
                                        targetformat: str = "audio") -> dict[str, Any]:
        """
        生成无障碍内容

        Args:
            content: 原始内容
            user_id: 用户ID
            content_type: 内容类型
            target_format: 目标格式

        Returns:
            Dict: 无障碍内容结果
        """
        try:
            if self.accessibility_client:
                result = await self.accessibility_client.generate_accessible_content(
                    content=content,
                    user_id=userid,
                    content_type=contenttype,
                    target_format=target_format
                )

                if result.get('success'):
                    logger.info("无障碍内容生成成功, 用户ID: %s", userid)
                    return {
                        'success': True,
                        'accessible_content': result.get('accessible_content', ''),
                        'audio_content': result.get('audio_content', ''),
                        'tactile_content': result.get('tactile_content', ''),
                        'content_url': result.get('content_url', ''),
                        'metadata': {
                            'user_id': userid,
                            'content_type': contenttype,
                            'target_format': targetformat,
                            'timestamp': int(time.time())
                        }
                    }
                else:
                    logger.warning(f"无障碍内容生成失败: {result.get('error')}")

            return {
                'success': False,
                'accessible_content': content,
                'audio_content': '',
                'tactile_content': '',
                'content_url': '',
                'error': '无障碍服务不可用',
                'metadata': {
                    'user_id': userid,
                    'content_type': contenttype,
                    'target_format': targetformat,
                    'timestamp': int(time.time())
                }
            }

        except Exception as e:
            logger.error(f"无障碍内容生成异常: {e}")
            return {
                'success': False,
                'accessible_content': content,
                'audio_content': '',
                'tactile_content': '',
                'content_url': '',
                'error': str(e),
                'metadata': {
                    'user_id': userid,
                    'content_type': contenttype,
                    'target_format': targetformat,
                    'timestamp': int(time.time())
                }
            }

    async def capture_camera_image(self, userid: str, sessionid: str | None = None) -> dict[str, Any]:
        """
        使用摄像头拍摄照片

        Args:
            user_id: 用户ID
            session_id: 会话ID

        Returns:
            Dict: 拍摄结果
        """
        try:
            # 确保设备管理器已初始化
            if self.device_manager is None:
                await self.initialize()

            if not self.device_manager:
                return {
                    'success': False,
                    'error': '设备管理器不可用',
                    'user_id': userid,
                    'session_id': session_id
                }

            # 拍摄照片
            result = await self.device_manager.capture_image()

            if result:
                # 使用无障碍服务进行图像分析
                if self.accessibility_client:
                    try:
                        await self.accessibility_client.process_image_input(
                            image_data=result['image_data'],
                            user_id=userid,
                            image_type="camera_capture",
                            context="health_consultation"
                        )
                    except Exception as e:
                        logger.warning(f"图像无障碍分析失败: {e}")

                response = {
                    'success': True,
                    'image_data': result,
                    'user_id': userid,
                    'session_id': sessionid,
                    'timestamp': int(time.time())
                }

                # 添加无障碍分析结果
                if accessibility_result and accessibility_result.get('success'):
                    response['accessibility'] = accessibility_result

                return response
            else:
                return {
                    'success': False,
                    'error': '拍摄照片失败',
                    'user_id': userid,
                    'session_id': session_id
                }

        except Exception as e:
            logger.error(f"摄像头拍摄失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'user_id': userid,
                'session_id': session_id
            }

    async def record_microphone_audio(self, userid: str, duration: float = 5.0,
                                    sessionid: str | None = None) -> dict[str, Any]:
        """
        使用麦克风录制音频

        Args:
            user_id: 用户ID
            duration: 录音时长(秒)
            session_id: 会话ID

        Returns:
            Dict: 录音结果
        """
        try:
            # 确保设备管理器已初始化
            if self.device_manager is None:
                await self.initialize()

            if not self.device_manager:
                return {
                    'success': False,
                    'error': '设备管理器不可用',
                    'user_id': userid,
                    'session_id': session_id
                }

            # 限制录音时长
            duration = min(duration, 30.0)

            # 录制音频
            result = await self.device_manager.record_audio(duration)

            if result:
                # 使用无障碍服务进行语音识别
                if self.accessibility_client:
                    try:
                        await self.accessibility_client.process_voice_input(
                            audio_data=result['wav_data'],
                            user_id=userid,
                            context="microphone_recording",
                            language="zh-CN"
                        )
                    except Exception as e:
                        logger.warning(f"语音无障碍识别失败: {e}")

                response = {
                    'success': True,
                    'audio_data': result,
                    'user_id': userid,
                    'session_id': sessionid,
                    'timestamp': int(time.time())
                }

                # 添加无障碍识别结果
                if accessibility_result and accessibility_result.get('success'):
                    response['accessibility'] = accessibility_result

                    # 如果识别出文本, 可以进一步处理
                    recognizedtext = accessibility_result.get('recognized_text', '')
                    if recognized_text and session_id:
                        # 将识别的文本作为聊天输入处理
                        await self.chat(userid, recognizedtext, sessionid)
                        response['chat_response'] = chat_result

                return response
            else:
                return {
                    'success': False,
                    'error': '录音失败',
                    'user_id': userid,
                    'session_id': session_id
                }

        except Exception as e:
            logger.error(f"麦克风录音失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'user_id': userid,
                'session_id': session_id
            }

    async def capture_screen_image(self, userid: str, region: tuple | None = None,
                                 sessionid: str | None = None) -> dict[str, Any]:
        """
        截取屏幕图像

        Args:
            user_id: 用户ID
            region: 截图区域 (x, y, width, height)
            session_id: 会话ID

        Returns:
            Dict: 截图结果
        """
        try:
            # 确保设备管理器已初始化
            if self.device_manager is None:
                await self.initialize()

            if not self.device_manager:
                return {
                    'success': False,
                    'error': '设备管理器不可用',
                    'user_id': userid,
                    'session_id': session_id
                }

            # 截取屏幕
            result = await self.device_manager.capture_screen(region)

            if result:
                # 使用无障碍服务进行屏幕阅读
                if self.accessibility_client:
                    try:
                        await self.accessibility_client.provide_screen_reading(
                            screen_data=result['image_base64'],
                            user_id=userid,
                            context="screen_capture"
                        )
                    except Exception as e:
                        logger.warning(f"屏幕无障碍阅读失败: {e}")

                response = {
                    'success': True,
                    'screen_data': result,
                    'user_id': userid,
                    'session_id': sessionid,
                    'timestamp': int(time.time())
                }

                # 添加无障碍阅读结果
                if accessibility_result and accessibility_result.get('success'):
                    response['accessibility'] = accessibility_result

                return response
            else:
                return {
                    'success': False,
                    'error': '屏幕截图失败',
                    'user_id': userid,
                    'session_id': session_id
                }

        except Exception as e:
            logger.error(f"屏幕截图失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'user_id': userid,
                'session_id': session_id
            }

    async def get_device_status(self) -> dict[str, Any]:
        """
        获取设备状态

        Returns:
            Dict: 设备状态信息
        """
        try:
            # 确保设备管理器已初始化
            if self.device_manager is None:
                await self.initialize()

            if self.device_manager:
                return await self.device_manager.get_device_status()
            else:
                return {
                    'camera': {'available': False, 'active': False},
                    'microphone': {'available': False, 'recording': False},
                    'screen': {'available': False, 'info': {}},
                    'initialized': False,
                    'error': '设备管理器不可用'
                }

        except Exception as e:
            logger.error(f"获取设备状态失败: {e}")
            return {
                'camera': {'available': False, 'active': False},
                'microphone': {'available': False, 'recording': False},
                'screen': {'available': False, 'info': {}},
                'initialized': False,
                'error': str(e)
            }

    async def close_session(self, sessionid: str) -> bool:
        """
        关闭并清理会话

        Args:
            session_id: 要关闭的会话ID

        Returns:
            bool: 是否成功关闭会话
        """
        if session_id in self.active_sessions:
            # 保存最终状态
            await self.session_repository.save_session(self.active_sessions[session_id])

            # 从活跃会话中移除
            del self.active_sessions[session_id]
            self._update_active_sessions_metric()

            logger.info("会话已关闭: %s", sessionid)
            self.metrics.increment_session_count("closed")
            return True
        else:
            logger.warning("尝试关闭不存在的会话: %s", sessionid)
            return False

    async def close(self):
        """关闭智能体资源"""
        # 保存所有活跃会话
        for sessionid, session in self.active_sessions.items():
            try:
                await self.session_repository.save_session(session)
            except Exception as e:
                logger.error("保存会话失败: %s, 错误: %s", sessionid, str(e))

        # 关闭模型工厂
        await self.model_factory.close()

        # 关闭无障碍服务客户端
        if self.accessibility_client:
            await self.accessibility_client.close()

        # 关闭设备管理器
        if self.device_manager:
            await self.device_manager.close()

        logger.info("智能体资源已清理")
