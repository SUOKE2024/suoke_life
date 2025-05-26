#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek模型工厂
支持真实的DeepSeek API调用
"""

import logging
import asyncio
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    logging.warning("未安装openai库，无法使用DeepSeek API")

from pkg.utils.config_loader import get_config

logger = logging.getLogger(__name__)

class DeepSeekModelFactory:
    """DeepSeek模型工厂，支持真实的API调用"""
    
    def __init__(self):
        """初始化DeepSeek模型工厂"""
        self.config = get_config()
        self.initialized = False
        self.client = None
        
        # 获取DeepSeek配置
        self.deepseek_config = self.config.get_section('models.deepseek') or {}
        self.llm_config = self.config.get_section('models.llm') or {}
        
        # API配置 - 优先从环境变量获取
        import os
        self.api_key = (
            os.environ.get('DEEPSEEK_API_KEY') or 
            self.deepseek_config.get('api_key') or 
            self.llm_config.get('api_key')
        )
        self.api_base = self.deepseek_config.get('api_base', 'https://api.deepseek.com/v1')
        self.model = self.deepseek_config.get('model', 'deepseek-chat')
        
        # 模型参数
        self.temperature = self.deepseek_config.get('temperature', 0.7)
        self.max_tokens = self.deepseek_config.get('max_tokens', 2048)
        self.top_p = self.deepseek_config.get('top_p', 0.95)
        
        logger.info("DeepSeek模型工厂初始化完成")
    
    async def initialize(self):
        """异步初始化"""
        if not self.initialized and HAS_OPENAI:
            try:
                # 创建OpenAI客户端（DeepSeek兼容OpenAI API）
                if self.api_key:
                    self.client = openai.OpenAI(
                        api_key=self.api_key,
                        base_url=self.api_base
                    )
                    
                    # 测试连接
                    await self._test_connection()
                    self.initialized = True
                    logger.info("DeepSeek模型工厂异步初始化完成")
                else:
                    logger.error("DeepSeek API密钥未配置")
                    
            except Exception as e:
                logger.error(f"DeepSeek模型工厂初始化失败: {e}")
                raise
    
    async def _test_connection(self):
        """测试API连接"""
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个测试助手"},
                    {"role": "user", "content": "测试连接"}
                ],
                max_tokens=10
            )
            
            if response and response.choices:
                logger.info("DeepSeek API连接测试成功")
            else:
                raise Exception("API响应格式异常")
                
        except Exception as e:
            logger.error(f"DeepSeek API连接测试失败: {e}")
            raise
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return [self.model, "deepseek-chat", "deepseek-coder"]
    
    def get_model_health_status(self) -> Dict[str, Dict[str, Any]]:
        """获取模型健康状态"""
        return {
            self.model: {
                "status": "healthy" if self.initialized else "unhealthy",
                "provider": "deepseek",
                "api_base": self.api_base,
                "initialized": self.initialized
            }
        }
    
    async def generate_text(self, model: str, prompt: str, **kwargs) -> Tuple[str, Dict[str, Any]]:
        """
        生成文本响应
        
        Args:
            model: 模型名称
            prompt: 输入提示
            **kwargs: 其他参数
            
        Returns:
            Tuple[str, Dict[str, Any]]: 生成的文本和元数据
        """
        if not self.initialized:
            await self.initialize()
        
        if not self.client:
            raise Exception("DeepSeek客户端未初始化")
        
        try:
            start_time = time.time()
            
            # 调用DeepSeek API
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=model or self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                top_p=kwargs.get('top_p', self.top_p)
            )
            
            processing_time = time.time() - start_time
            
            # 提取响应内容
            content = response.choices[0].message.content
            
            # 构建元数据
            metadata = {
                "model": model or self.model,
                "provider": "deepseek",
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat(),
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                },
                "finish_reason": response.choices[0].finish_reason,
                "confidence": 0.9,  # DeepSeek通常有较高的置信度
                "suggested_actions": ["继续对话", "深入分析", "获取更多信息"]
            }
            
            logger.info(f"DeepSeek API调用成功，耗时: {processing_time:.2f}秒")
            return content, metadata
            
        except Exception as e:
            logger.error(f"DeepSeek API调用失败: {e}")
            raise
    
    async def generate_chat_completion(self, model: str, messages: List[Dict[str, str]], 
                                      temperature: float = 0.7, max_tokens: int = 2048,
                                      user_id: str = None) -> Tuple[str, Dict[str, Any]]:
        """
        生成聊天完成响应
        
        Args:
            model: 模型名称
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            user_id: 用户ID
            
        Returns:
            Tuple[str, Dict[str, Any]]: 生成的文本和元数据
        """
        if not self.initialized:
            await self.initialize()
        
        if not self.client:
            raise Exception("DeepSeek客户端未初始化")
        
        try:
            start_time = time.time()
            
            # 调用DeepSeek API
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=model or self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=self.top_p
            )
            
            processing_time = time.time() - start_time
            
            # 提取响应内容
            content = response.choices[0].message.content
            
            # 构建元数据
            metadata = {
                "model": model or self.model,
                "provider": "deepseek",
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat(),
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                },
                "finish_reason": response.choices[0].finish_reason,
                "confidence": 0.9,
                "suggested_actions": ["继续对话", "深入分析", "获取更多信息"]
            }
            
            logger.info(f"DeepSeek聊天API调用成功，耗时: {processing_time:.2f}秒，tokens: {metadata['usage']['total_tokens']}")
            return content, metadata
            
        except Exception as e:
            logger.error(f"DeepSeek聊天API调用失败: {e}")
            raise
    
    async def process_multimodal_input(self, input_type: str, data: Any, **kwargs) -> Dict[str, Any]:
        """
        处理多模态输入（目前DeepSeek主要支持文本）
        
        Args:
            input_type: 输入类型
            data: 输入数据
            **kwargs: 其他参数
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        if input_type == "text":
            # 直接处理文本
            response, metadata = await self.generate_text(self.model, str(data))
            return {
                "processed_text": str(data),
                "response": response,
                "metadata": metadata,
                "confidence": metadata.get("confidence", 0.9),
                "processing_time": metadata.get("processing_time", 0)
            }
        else:
            # 其他类型暂不支持
            return {
                "error": f"DeepSeek暂不支持输入类型: {input_type}",
                "supported_types": ["text"],
                "confidence": 0.0,
                "processing_time": 0.1
            }
    
    async def health_analysis(self, symptoms: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        健康分析（使用DeepSeek的中医知识）
        
        Args:
            symptoms: 症状列表
            context: 上下文信息
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        # 构建中医分析提示
        symptoms_text = "、".join(symptoms)
        age = context.get("age", "未知")
        gender = context.get("gender", "未知")
        
        prompt = f"""
作为一名专业的中医师，请根据以下信息进行中医辨证分析：

患者信息：
- 年龄：{age}
- 性别：{gender}
- 主要症状：{symptoms_text}

请从中医角度分析：
1. 可能的证候类型
2. 体质判断
3. 调理建议（包括饮食、生活方式、穴位等）
4. 风险评估

请用专业但易懂的语言回答，格式化输出。
"""
        
        try:
            response, metadata = await self.generate_text(self.model, prompt)
            
            # 解析响应并结构化
            analysis_result = {
                "raw_analysis": response,
                "syndrome_analysis": {
                    "primary_syndrome": "基于DeepSeek分析",
                    "confidence": metadata.get("confidence", 0.9)
                },
                "constitution_type": {
                    "type": "基于症状分析",
                    "confidence": metadata.get("confidence", 0.9)
                },
                "recommendations": {
                    "diet": ["根据分析结果调整饮食"],
                    "lifestyle": ["根据分析结果调整生活方式"],
                    "acupoints": ["根据分析结果选择穴位"],
                    "herbs": ["请咨询专业中医师"]
                },
                "risk_assessment": {
                    "level": "请咨询专业医师",
                    "suggestions": ["建议专业诊断"]
                },
                "metadata": metadata
            }
            
            logger.info("DeepSeek健康分析完成")
            return analysis_result
            
        except Exception as e:
            logger.error(f"DeepSeek健康分析失败: {e}")
            raise
    
    async def get_embeddings(self, texts: List[str], model: str = None) -> List[List[float]]:
        """
        获取文本嵌入向量（DeepSeek暂不支持，返回模拟向量）
        
        Args:
            texts: 文本列表
            model: 模型名称
            
        Returns:
            List[List[float]]: 嵌入向量列表
        """
        logger.warning("DeepSeek暂不支持嵌入向量，返回模拟数据")
        
        # 返回模拟的嵌入向量
        import random
        embeddings = []
        for text in texts:
            # 生成1536维的随机向量（模拟OpenAI格式）
            embedding = [random.uniform(-1, 1) for _ in range(1536)]
            embeddings.append(embedding)
        
        return embeddings
    
    async def close(self):
        """关闭模型工厂"""
        logger.info("DeepSeek模型工厂关闭")
        self.initialized = False
        self.client = None

# 全局实例
_deepseek_factory_instance: Optional[DeepSeekModelFactory] = None

async def get_deepseek_model_factory() -> DeepSeekModelFactory:
    """获取DeepSeek模型工厂的单例实例"""
    global _deepseek_factory_instance
    
    if _deepseek_factory_instance is None:
        _deepseek_factory_instance = DeepSeekModelFactory()
        await _deepseek_factory_instance.initialize()
    
    return _deepseek_factory_instance 