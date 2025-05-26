#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟模型工厂
用于开发环境的模拟实现，避免真实模型依赖
"""

import logging
import asyncio
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class MockModelFactory:
    """模拟模型工厂，用于开发环境测试"""
    
    def __init__(self):
        """初始化模拟模型工厂"""
        self.initialized = False
        self.available_models = {
            "gpt-4o-mini": {"status": "healthy", "provider": "openai"},
            "mock": {"status": "healthy", "provider": "mock"},
            "llama-3-8b": {"status": "healthy", "provider": "local"},
        }
        logger.info("模拟模型工厂初始化完成")
    
    async def initialize(self):
        """异步初始化"""
        if not self.initialized:
            # 模拟初始化延迟
            await asyncio.sleep(0.1)
            self.initialized = True
            logger.info("模拟模型工厂异步初始化完成")
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return list(self.available_models.keys())
    
    def get_model_health_status(self) -> Dict[str, Dict[str, Any]]:
        """获取模型健康状态"""
        return self.available_models.copy()
    
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
        # 模拟处理延迟
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # 生成模拟响应
        responses = [
            "您好！我是小艾，很高兴为您提供健康咨询服务。请告诉我您的具体情况，我会根据中医理论为您分析。",
            "根据您的描述，建议您注意休息，保持良好的作息习惯。如有需要，我可以为您安排四诊检查。",
            "从中医角度来看，您的症状可能与体质有关。建议您多喝温水，避免生冷食物。",
            "我理解您的担心。让我为您详细分析一下症状，并提供相应的调理建议。",
            "这种情况在中医理论中比较常见，通过适当的调理可以得到改善。"
        ]
        
        response_text = random.choice(responses)
        
        metadata = {
            "model": model,
            "provider": "mock",
            "confidence": random.uniform(0.8, 0.95),
            "processing_time": random.uniform(0.1, 0.5),
            "timestamp": datetime.now().isoformat(),
            "suggested_actions": ["继续对话", "安排四诊", "查看健康建议"]
        }
        
        logger.debug("模拟文本生成完成，模型: %s", model)
        return response_text, metadata
    
    async def process_multimodal_input(self, input_type: str, data: Any, **kwargs) -> Dict[str, Any]:
        """
        处理多模态输入
        
        Args:
            input_type: 输入类型 (voice, image, text, sign)
            data: 输入数据
            **kwargs: 其他参数
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        # 模拟处理延迟
        await asyncio.sleep(random.uniform(0.2, 0.8))
        
        if input_type == "voice":
            return {
                "transcription": "用户说：我最近感觉有点疲劳，想咨询一下健康问题。",
                "confidence": random.uniform(0.85, 0.95),
                "language": "zh-CN",
                "emotion": "neutral",
                "processing_time": random.uniform(0.2, 0.5)
            }
        
        elif input_type == "image":
            return {
                "analysis": "图像分析：舌质偏红，苔薄白，边缘略有齿痕",
                "features": ["舌质红", "苔薄白", "有齿痕"],
                "confidence": random.uniform(0.75, 0.90),
                "processing_time": random.uniform(0.3, 0.8)
            }
        
        elif input_type == "text":
            return {
                "processed_text": str(data),
                "intent": "health_consultation",
                "entities": ["疲劳", "健康咨询"],
                "confidence": random.uniform(0.80, 0.95),
                "processing_time": random.uniform(0.1, 0.3)
            }
        
        elif input_type == "sign":
            return {
                "interpretation": "手语识别：用户询问健康相关问题",
                "confidence": random.uniform(0.70, 0.85),
                "processing_time": random.uniform(0.4, 0.9)
            }
        
        else:
            return {
                "error": f"不支持的输入类型: {input_type}",
                "confidence": 0.0,
                "processing_time": 0.1
            }
    
    async def get_embeddings(self, texts: List[str], model: str = "mock") -> List[List[float]]:
        """
        获取文本嵌入向量
        
        Args:
            texts: 文本列表
            model: 模型名称
            
        Returns:
            List[List[float]]: 嵌入向量列表
        """
        # 模拟处理延迟
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        # 生成模拟嵌入向量
        embeddings = []
        for text in texts:
            # 生成384维的随机向量（模拟all-MiniLM-L6-v2）
            embedding = [random.uniform(-1, 1) for _ in range(384)]
            embeddings.append(embedding)
        
        logger.debug("模拟嵌入向量生成完成，文本数: %d", len(texts))
        return embeddings
    
    async def health_analysis(self, symptoms: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        健康分析
        
        Args:
            symptoms: 症状列表
            context: 上下文信息
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        # 模拟处理延迟
        await asyncio.sleep(random.uniform(0.3, 0.7))
        
        # 模拟中医分析结果
        analysis_results = {
            "syndrome_analysis": {
                "primary_syndrome": "气虚证",
                "secondary_syndrome": "血瘀证",
                "confidence": random.uniform(0.75, 0.90)
            },
            "constitution_type": {
                "type": "气虚质",
                "characteristics": ["容易疲劳", "气短懒言", "自汗"],
                "confidence": random.uniform(0.80, 0.95)
            },
            "recommendations": {
                "diet": ["多食用补气食物", "避免生冷食物", "规律饮食"],
                "lifestyle": ["适量运动", "保证充足睡眠", "避免过度劳累"],
                "acupoints": ["足三里", "气海", "关元"],
                "herbs": ["人参", "黄芪", "白术"]
            },
            "risk_assessment": {
                "level": "低风险",
                "factors": ["轻度疲劳", "体质偏虚"],
                "suggestions": ["定期体检", "注意调理"]
            }
        }
        
        logger.debug("模拟健康分析完成，症状数: %d", len(symptoms))
        return analysis_results
    
    async def generate_chat_completion(self, model: str, messages: List[Dict[str, str]], 
                                      temperature: float = 0.7, max_tokens: int = 2048,
                                      user_id: str = None) -> Tuple[str, Dict[str, Any]]:
        """
        生成聊天完成响应（兼容接口）
        
        Args:
            model: 模型名称
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            user_id: 用户ID
            
        Returns:
            Tuple[str, Dict[str, Any]]: 生成的文本和元数据
        """
        # 提取最后一条用户消息作为提示
        prompt = ""
        for msg in messages:
            if msg.get("role") == "user":
                prompt = msg.get("content", "")
        
        return await self.generate_text(model, prompt, temperature=temperature, max_tokens=max_tokens)
    
    async def close(self):
        """关闭模型工厂"""
        logger.info("模拟模型工厂关闭")
        self.initialized = False

# 全局实例
_mock_factory_instance: Optional[MockModelFactory] = None

async def get_mock_model_factory() -> MockModelFactory:
    """获取模拟模型工厂的单例实例"""
    global _mock_factory_instance
    
    if _mock_factory_instance is None:
        _mock_factory_instance = MockModelFactory()
        await _mock_factory_instance.initialize()
    
    return _mock_factory_instance 