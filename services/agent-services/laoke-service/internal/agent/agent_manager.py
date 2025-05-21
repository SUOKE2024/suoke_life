#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能体管理器
负责老克智能体的核心逻辑，包括中医知识传播、社群管理和教育内容生成
"""

import os
import uuid
import json
import logging
import time
import asyncio
from typing import Dict, List, Any, Optional, Tuple

from .model_factory import ModelFactory
from pkg.utils.config_loader import get_config
from pkg.utils.metrics import get_metrics_collector, track_llm_metrics

logger = logging.getLogger(__name__)

class AgentManager:
    """老克智能体管理器，负责中医知识传播平台的核心功能"""
    
    def __init__(self, session_repository = None, knowledge_repository = None):
        """
        初始化智能体管理器
        
        Args:
            session_repository: 会话存储库
            knowledge_repository: 知识库存储库
        """
        self.config = get_config()
        self.metrics = get_metrics_collector()
        
        # 设置依赖组件
        self.session_repository = session_repository
        self.knowledge_repository = knowledge_repository
        
        # 加载模型配置
        self.llm_config = self.config.get_section('models.llm')
        
        # 加载会话配置
        self.conversation_config = self.config.get_section('conversation')
        self.system_prompt = self.conversation_config.get('system_prompt', '')
        self.max_history_turns = self.conversation_config.get('max_history_turns', 20)
        
        # 设置默认模型
        self.primary_model = self.llm_config.get('primary_model', 'gpt-4o-mini')
        self.fallback_model = self.llm_config.get('fallback_model', 'llama-3-8b')
        
        # 初始化模型工厂
        self.model_factory = ModelFactory()
        
        # 活跃会话映射 session_id -> session_data
        self.active_sessions = {}
        
        # 记录活跃会话数
        self._update_active_sessions_metric()
        
        logger.info("老克智能体管理器初始化完成，主模型: %s, 备用模型: %s", 
                   self.primary_model, self.fallback_model)
    
    def _update_active_sessions_metric(self):
        """更新活跃会话数指标"""
        if hasattr(self.metrics, 'update_active_sessions'):
            self.metrics.update_active_sessions(len(self.active_sessions))
        # 设置定期更新
        asyncio.create_task(self._schedule_metric_update())
    
    async def _schedule_metric_update(self):
        """定期更新指标的任务"""
        await asyncio.sleep(60)  # 每分钟更新一次
        self._update_active_sessions_metric()
    
    @track_llm_metrics(model="primary", query_type="knowledge_sharing")
    async def process_request(self, user_id: str, request_data: Dict[str, Any], 
                            session_id: str = None) -> Dict[str, Any]:
        """
        处理用户关于中医知识、学习和社群的请求
        
        Args:
            user_id: 用户ID
            request_data: 请求数据，包含请求类型和相关信息
            session_id: 会话ID，如果为None则创建新会话
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        # 记录请求指标
        request_type = request_data.get('type', 'general')
        self.metrics.increment_request_count(request_type)
        
        # 确保会话ID存在
        if not session_id:
            session_id = str(uuid.uuid4())
            logger.info("创建新会话，用户ID: %s, 会话ID: %s", user_id, session_id)
        
        try:
            # 根据请求类型分发处理
            if request_type == 'knowledge_query':
                return await self._process_knowledge_query(user_id, request_data, session_id)
            elif request_type == 'content_creation':
                return await self._generate_educational_content(user_id, request_data, session_id)
            elif request_type == 'community_management':
                return await self._handle_community_request(user_id, request_data, session_id)
            elif request_type == 'learning_path':
                return await self._create_learning_path(user_id, request_data, session_id)
            else:
                # 默认对话处理
                return await self._process_general_inquiry(user_id, request_data, session_id)
                
        except Exception as e:
            logger.error("请求处理失败，用户ID: %s, 会话ID: %s, 错误: %s", 
                        user_id, session_id, str(e))
            
            # 返回错误响应
            return {
                'request_id': str(uuid.uuid4()),
                'success': False,
                'error': str(e),
                'message': "处理您的请求时遇到了问题，请稍后重试",
                'metadata': {
                    'session_id': session_id,
                    'timestamp': int(time.time())
                }
            }
    
    async def _process_knowledge_query(self, user_id: str, request_data: Dict[str, Any], 
                                    session_id: str) -> Dict[str, Any]:
        """处理中医知识查询"""
        # 提取查询内容
        query = request_data.get('query', '')
        knowledge_type = request_data.get('knowledge_type', 'general')
        
        # 构建提示
        prompt = f"""作为老克，请针对以下中医知识查询提供专业且易于理解的回答:

查询: {query}
知识类型: {knowledge_type}

请提供:
1. 核心概念解释
2. 历史渊源和发展
3. 现代应用和意义
4. 相关经典文献参考
5. 进一步学习建议
"""
        
        # 构建消息列表
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        # 调用LLM生成响应
        response_text, response_meta = await self.model_factory.generate_chat_completion(
            model=self.primary_model,
            messages=messages,
            temperature=0.3,  # 较低的温度，提高确定性
            max_tokens=2048
        )
        
        # 返回知识查询结果
        return {
            'request_id': str(uuid.uuid4()),
            'success': True,
            'answer': response_text,
            'query': query,
            'confidence': response_meta.get('confidence', 0.9),
            'metadata': {
                'model': response_meta.get('model', self.primary_model),
                'session_id': session_id,
                'timestamp': int(time.time())
            }
        }
    
    async def _generate_educational_content(self, user_id: str, request_data: Dict[str, Any], 
                                         session_id: str) -> Dict[str, Any]:
        """生成教育内容"""
        # 提取内容需求
        topic = request_data.get('topic', '')
        content_type = request_data.get('content_type', 'article')  # article, video_script, course
        target_audience = request_data.get('target_audience', 'beginner')
        
        # 构建提示
        prompt = f"""作为老克，请为以下中医主题创建教育内容:

主题: {topic}
内容类型: {content_type}
目标受众: {target_audience}

请提供包含以下要素的结构化内容:
1. 标题和引言
2. 核心知识点（3-5个）
3. 实践应用示例
4. 常见误区澄清
5. 进一步学习资源
6. 互动问题（如适用）
"""
        
        # 构建消息列表
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        # 调用LLM生成响应
        response_text, response_meta = await self.model_factory.generate_chat_completion(
            model=self.primary_model,
            messages=messages,
            temperature=0.7,  # 提高创造性
            max_tokens=3072
        )
        
        # 返回生成的内容
        return {
            'request_id': str(uuid.uuid4()),
            'success': True,
            'content': response_text,
            'topic': topic,
            'content_type': content_type,
            'confidence': response_meta.get('confidence', 0.9),
            'metadata': {
                'model': response_meta.get('model', self.primary_model),
                'session_id': session_id,
                'timestamp': int(time.time())
            }
        }
    
    async def _handle_community_request(self, user_id: str, request_data: Dict[str, Any], 
                                     session_id: str) -> Dict[str, Any]:
        """处理社群管理相关请求"""
        # 提取社群请求信息
        community_action = request_data.get('action', 'advice')
        community_issue = request_data.get('issue', '')
        community_context = request_data.get('context', {})
        
        # 构建提示
        prompt = f"""作为老克，请就以下社群管理请求提供专业建议:

请求类型: {community_action}
问题描述: {community_issue}
背景情况: {json.dumps(community_context, ensure_ascii=False)}

请提供:
1. 详细分析和建议
2. 具体实施步骤
3. 可能的挑战和应对策略
4. 成功案例参考
5. 社群管理资源推荐
"""
        
        # 构建消息列表
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        # 调用LLM生成响应
        response_text, response_meta = await self.model_factory.generate_chat_completion(
            model=self.primary_model,
            messages=messages,
            temperature=0.5,
            max_tokens=2048
        )
        
        # 返回社群建议
        return {
            'request_id': str(uuid.uuid4()),
            'success': True,
            'suggestion': response_text,
            'action': community_action,
            'confidence': response_meta.get('confidence', 0.9),
            'metadata': {
                'model': response_meta.get('model', self.primary_model),
                'session_id': session_id,
                'timestamp': int(time.time())
            }
        }
    
    async def _create_learning_path(self, user_id: str, request_data: Dict[str, Any], 
                                 session_id: str) -> Dict[str, Any]:
        """创建个性化学习路径"""
        # 提取学习需求信息
        learning_goal = request_data.get('goal', '')
        current_level = request_data.get('current_level', 'beginner')
        interests = request_data.get('interests', [])
        time_commitment = request_data.get('time_commitment', 'medium')
        
        # 构建提示
        prompt = f"""作为老克，请为用户创建个性化的中医学习路径:

学习目标: {learning_goal}
当前水平: {current_level}
特定兴趣: {', '.join(interests)}
时间投入: {time_commitment}

请提供:
1. 整体学习路径规划（3-6个月）
2. 分阶段学习目标和里程碑
3. 推荐学习资源（书籍、课程、实践活动）
4. 阶段性评估方法
5. 实践练习建议
6. 进阶方向指导
"""
        
        # 构建消息列表
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        # 调用LLM生成响应
        response_text, response_meta = await self.model_factory.generate_chat_completion(
            model=self.primary_model,
            messages=messages,
            temperature=0.6,
            max_tokens=3072
        )
        
        # 返回学习路径
        return {
            'request_id': str(uuid.uuid4()),
            'success': True,
            'learning_path': response_text,
            'goal': learning_goal,
            'confidence': response_meta.get('confidence', 0.9),
            'metadata': {
                'model': response_meta.get('model', self.primary_model),
                'session_id': session_id,
                'timestamp': int(time.time())
            }
        }
    
    async def _process_general_inquiry(self, user_id: str, request_data: Dict[str, Any], 
                                    session_id: str) -> Dict[str, Any]:
        """处理一般性中医知识咨询"""
        # 提取查询内容
        query = request_data.get('message', '')
        
        # 构建消息列表
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": query}
        ]
        
        # 调用LLM生成响应
        response_text, response_meta = await self.model_factory.generate_chat_completion(
            model=self.primary_model,
            messages=messages,
            temperature=0.7,
            max_tokens=2048
        )
        
        # 返回咨询响应
        return {
            'request_id': str(uuid.uuid4()),
            'success': True,
            'message': response_text,
            'confidence': response_meta.get('confidence', 0.9),
            'metadata': {
                'model': response_meta.get('model', self.primary_model),
                'session_id': session_id,
                'timestamp': int(time.time())
            }
        }
    
    async def close(self):
        """关闭智能体资源"""
        # 关闭模型工厂
        await self.model_factory.close()
        
        logger.info("老克智能体资源已清理") 