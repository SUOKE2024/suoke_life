#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能体管理器
负责小艾智能体的核心逻辑，包括多模态处理、LLM推理和会话管理
"""

import os
import uuid
import json
import logging
import time
import asyncio
from typing import Dict, List, Any, Optional, Tuple
import openai
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory

from .model_factory import ModelFactory
from ..repository.session_repository import SessionRepository
from pkg.utils.config_loader import get_config
from pkg.utils.metrics import get_metrics_collector, track_llm_metrics

logger = logging.getLogger(__name__)

class AgentManager:
    """智能体管理器，负责处理多模态输入，管理会话和生成响应"""
    
    def __init__(self, session_repository: SessionRepository = None):
        """
        初始化智能体管理器
        
        Args:
            session_repository: 会话存储库
        """
        self.config = get_config()
        self.metrics = get_metrics_collector()
        
        # 设置依赖组件
        self.session_repository = session_repository or SessionRepository()
        
        # 加载模型配置
        self.llm_config = self.config.get_section('models.llm')
        self.local_llm_config = self.config.get_section('models.local_llm')
        self.embedding_config = self.config.get_section('models.embedding')
        self.speech_config = self.config.get_section('models.speech')
        self.vision_config = self.config.get_section('models.vision')
        
        # 加载会话配置
        self.conversation_config = self.config.get_section('conversation')
        self.system_prompt = self.conversation_config.get('system_prompt', '')
        self.max_history_turns = self.conversation_config.get('max_history_turns', 20)
        self.context_window_size = self.conversation_config.get('context_window_size', 4096)
        
        # 设置默认模型
        self.primary_model = self.llm_config.get('primary_model', 'gpt-4o-mini')
        self.fallback_model = self.llm_config.get('fallback_model', 'llama-3-8b')
        
        # 初始化模型工厂
        self.model_factory = ModelFactory()
        
        # 活跃会话映射 session_id -> session_data
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        # 定期更新活跃会话数指标
        self._update_active_sessions_metric()
        
        logger.info("智能体管理器初始化完成，主模型: %s, 备用模型: %s", 
                   self.primary_model, self.fallback_model)
    
    def _update_active_sessions_metric(self):
        """更新活跃会话数指标"""
        self.metrics.update_active_sessions(len(self.active_sessions))
        # 设置定期更新
        asyncio.create_task(self._schedule_metric_update())
    
    async def _schedule_metric_update(self):
        """定期更新指标的任务"""
        await asyncio.sleep(60)  # 每分钟更新一次
        self._update_active_sessions_metric()
    
    @track_llm_metrics(model="primary", query_type="chat")
    async def chat(self, user_id: str, message: str, session_id: str = None, 
                 context_size: int = None) -> Dict[str, Any]:
        """
        处理用户聊天消息并生成响应
        
        Args:
            user_id: 用户ID
            message: 用户消息
            session_id: 会话ID，如果为None则创建新会话
            context_size: 上下文大小，如果为None则使用默认值
            
        Returns:
            Dict[str, Any]: 包含响应消息和元数据的字典
        """
        # 记录聊天消息指标
        self.metrics.increment_chat_message_count("received", "text")
        
        # 确保会话ID存在
        if not session_id:
            session_id = str(uuid.uuid4())
            logger.info("创建新会话，用户ID: %s, 会话ID: %s", user_id, session_id)
            self.metrics.increment_session_count("started")
        
        # 获取会话上下文
        context = await self._get_or_create_session(user_id, session_id)
        
        # 获取要使用的上下文大小
        ctx_size = context_size or self.max_history_turns
        
        try:
            # 准备聊天上下文和提示
            chat_context = self._prepare_chat_context(context, message, ctx_size)
            
            # 调用LLM生成响应
            response_text, response_meta = await self._generate_llm_response(chat_context)
            
            # 更新会话历史
            await self._update_session_history(context, message, response_text)
            
            # 记录指标
            self.metrics.increment_chat_message_count("sent", "text")
            
            # 构建响应对象
            response = {
                'message_id': str(uuid.uuid4()),
                'message': response_text,
                'confidence': response_meta.get('confidence', 0.9),
                'suggested_actions': response_meta.get('suggested_actions', []),
                'metadata': {
                    'model': response_meta.get('model', self.primary_model),
                    'provider': response_meta.get('provider', '未知'),
                    'session_id': session_id,
                    'timestamp': int(time.time())
                }
            }
            
            return response
            
        except Exception as e:
            logger.error("聊天处理失败，用户ID: %s, 会话ID: %s, 错误: %s", 
                        user_id, session_id, str(e))
            
            # 返回错误响应
            return {
                'message_id': str(uuid.uuid4()),
                'message': f"抱歉，我处理您的消息时遇到了问题: {str(e)}",
                'confidence': 0.5,
                'suggested_actions': ["重试", "联系客服"],
                'metadata': {
                    'error': str(e),
                    'session_id': session_id,
                    'timestamp': int(time.time())
                }
            }
    
    async def process_multimodal_input(self, user_id: str, input_data: Dict[str, Any], 
                                      session_id: str = None) -> Dict[str, Any]:
        """
        处理多模态输入（语音、图像、文本、手语等）
        
        Args:
            user_id: 用户ID
            input_data: 多模态输入数据
            session_id: 会话ID
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        start_time = time.time()
        
        # 确保会话ID存在
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # 判断输入类型
        input_type = self._determine_input_type(input_data)
        input_size = self._calculate_input_size(input_data)
        
        try:
            # 根据输入类型调用相应的处理方法
            if input_type == 'voice':
                result = await self._process_voice_input(input_data, user_id, session_id)
            elif input_type == 'image':
                result = await self._process_image_input(input_data, user_id, session_id)
            elif input_type == 'text':
                result = await self._process_text_input(input_data, user_id, session_id)
            elif input_type == 'sign':
                result = await self._process_sign_language_input(input_data, user_id, session_id)
            else:
                raise ValueError(f"不支持的输入类型: {input_type}")
            
            # 记录处理指标
            latency = time.time() - start_time
            self.metrics.track_multimodal_process(input_type, "success", latency, input_size)
            
            return result
            
        except Exception as e:
            logger.error("多模态处理失败，类型: %s, 用户ID: %s, 错误: %s", 
                        input_type, user_id, str(e))
            
            # 记录处理指标
            latency = time.time() - start_time
            self.metrics.track_multimodal_process(input_type, "failure", latency, input_size)
            
            # 返回错误结果
            return {
                'request_id': str(uuid.uuid4()),
                'error_message': f"处理失败: {str(e)}",
                'confidence': 0.0,
                'metadata': {
                    'session_id': session_id,
                    'timestamp': int(time.time())
                }
            }
    
    async def generate_health_summary(self, user_id: str, health_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成用户健康摘要
        
        Args:
            user_id: 用户ID
            health_data: 健康数据
            
        Returns:
            Dict[str, Any]: 健康摘要
        """
        # TODO: 实现健康摘要生成
        # 这里会结合用户健康记录和LLM生成个性化健康摘要
        return {
            'summary_id': str(uuid.uuid4()),
            'text_summary': '这里是您的健康摘要...',
            'trends': [],
            'metrics': [],
            'recommendations': [],
            'generated_at': int(time.time())
        }
    
    async def _get_or_create_session(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """获取或创建会话"""
        # 检查是否在活跃会话中
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        
        # 尝试从存储库加载
        session = await self.session_repository.get_session(session_id)
        
        if not session:
            # 创建新会话
            session = {
                'session_id': session_id,
                'user_id': user_id,
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
    
    def _prepare_chat_context(self, session: Dict[str, Any], message: str, context_size: int) -> Dict[str, Any]:
        """准备聊天上下文"""
        # 获取历史消息，限制数量
        history = session['history'][-context_size:] if len(session['history']) > context_size else session['history']
        
        # 构建上下文对象
        return {
            'system_prompt': self.system_prompt,
            'history': history,
            'current_message': message,
            'user_id': session['user_id'],
            'session_id': session['session_id'],
            'timestamp': int(time.time())
        }
    
    async def _generate_llm_response(self, context: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """
        使用LLM生成响应
        
        Args:
            context: 聊天上下文
            
        Returns:
            Tuple[str, Dict[str, Any]]: 响应文本和元数据
        """
        # 构建提示
        messages = self._build_prompt_messages(context)
        
        # 使用模型工厂生成响应
        return await self.model_factory.generate_chat_completion(
            model=self.primary_model,
            messages=messages,
            temperature=self.llm_config.get('temperature', 0.7),
            max_tokens=self.llm_config.get('max_tokens', 2048)
        )
    
    def _build_prompt_messages(self, context: Dict[str, Any]) -> List[Dict[str, str]]:
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
    
    async def _update_session_history(self, session: Dict[str, Any], user_message: str, assistant_message: str):
        """
        更新会话历史
        
        Args:
            session: 会话对象
            user_message: 用户消息
            assistant_message: 助手响应
        """
        # 添加新的对话记录
        session['history'].append({
            'user_message': user_message,
            'assistant_message': assistant_message,
            'timestamp': int(time.time())
        })
        
        # 如果历史记录过长，删除最早的记录
        max_history = self.max_history_turns * 2  # 考虑到每轮对话有用户和助手两条消息
        if len(session['history']) > max_history:
            session['history'] = session['history'][-max_history:]
        
        # 更新会话最后活跃时间
        session['last_active'] = int(time.time())
        
        # 保存会话更新
        if self.conversation_config.get('persist_history', True):
            await self.session_repository.save_session(session)
    
    def _determine_input_type(self, input_data: Dict[str, Any]) -> str:
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
    
    def _calculate_input_size(self, input_data: Dict[str, Any]) -> int:
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
    
    async def _process_voice_input(self, input_data: Dict[str, Any], user_id: str, session_id: str) -> Dict[str, Any]:
        """处理语音输入"""
        logger.info("处理语音输入，用户ID: %s, 会话ID: %s, 数据大小: %d", 
                   user_id, session_id, len(input_data.get('voice', b'')))
        
        # TODO: 实现语音处理逻辑，利用语音识别将语音转换为文本
        # 这里是简化处理，实际应该调用语音处理服务
        transcribed_text = "这是测试用的语音转文本结果"
        
        # 处理文本内容
        chat_result = await self.chat(user_id, transcribed_text, session_id)
        
        # 返回处理结果
        return {
            'request_id': str(uuid.uuid4()),
            'transcription': transcribed_text,
            'response': chat_result['message'],
            'confidence': chat_result['confidence'],
            'metadata': {
                'session_id': session_id,
                'timestamp': int(time.time())
            }
        }
    
    async def _process_image_input(self, input_data: Dict[str, Any], user_id: str, session_id: str) -> Dict[str, Any]:
        """处理图像输入"""
        logger.info("处理图像输入，用户ID: %s, 会话ID: %s, 数据大小: %d", 
                   user_id, session_id, len(input_data.get('image', b'')))
        
        # TODO: 实现图像处理逻辑，可以是舌象分析、面色分析等
        # 这里是简化处理，实际应该调用图像处理服务
        image_description = "这是一张舌象图像，舌体淡红，舌苔薄白"
        
        # 构建包含图像分析的提示
        prompt = f"根据以下图像分析结果，给出中医健康建议。图像分析: {image_description}"
        
        # 处理提示内容
        chat_result = await self.chat(user_id, prompt, session_id)
        
        # 返回处理结果
        return {
            'request_id': str(uuid.uuid4()),
            'image_analysis': image_description,
            'response': chat_result['message'],
            'confidence': chat_result['confidence'],
            'metadata': {
                'session_id': session_id,
                'timestamp': int(time.time())
            }
        }
    
    async def _process_text_input(self, input_data: Dict[str, Any], user_id: str, session_id: str) -> Dict[str, Any]:
        """处理文本输入"""
        text = input_data.get('text', '')
        logger.info("处理文本输入，用户ID: %s, 会话ID: %s, 文本长度: %d", 
                   user_id, session_id, len(text))
        
        # 直接处理文本内容
        chat_result = await self.chat(user_id, text, session_id)
        
        # 返回处理结果
        return {
            'request_id': str(uuid.uuid4()),
            'input_text': text,
            'response': chat_result['message'],
            'confidence': chat_result['confidence'],
            'metadata': {
                'session_id': session_id,
                'timestamp': int(time.time())
            }
        }
    
    async def _process_sign_language_input(self, input_data: Dict[str, Any], user_id: str, session_id: str) -> Dict[str, Any]:
        """处理手语输入"""
        logger.info("处理手语输入，用户ID: %s, 会话ID: %s, 数据大小: %d", 
                   user_id, session_id, len(input_data.get('sign', b'')))
        
        # TODO: 实现手语识别逻辑
        # 这里是简化处理，实际应该调用手语识别服务
        sign_text = "这是测试用的手语识别文本"
        
        # 处理识别出的文本
        chat_result = await self.chat(user_id, sign_text, session_id)
        
        # 返回处理结果
        return {
            'request_id': str(uuid.uuid4()),
            'sign_text': sign_text,
            'response': chat_result['message'],
            'confidence': chat_result['confidence'],
            'metadata': {
                'session_id': session_id,
                'timestamp': int(time.time())
            }
        }
    
    async def close_session(self, session_id: str) -> bool:
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
            
            logger.info("会话已关闭: %s", session_id)
            self.metrics.increment_session_count("closed")
            return True
        else:
            logger.warning("尝试关闭不存在的会话: %s", session_id)
            return False
    
    async def close(self):
        """关闭智能体资源"""
        # 保存所有活跃会话
        for session_id, session in self.active_sessions.items():
            try:
                await self.session_repository.save_session(session)
            except Exception as e:
                logger.error("保存会话失败: %s, 错误: %s", session_id, str(e))
        
        # 关闭模型工厂
        await self.model_factory.close()
        
        logger.info("智能体资源已清理") 