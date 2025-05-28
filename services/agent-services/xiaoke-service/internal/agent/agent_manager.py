#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能体管理器
负责小克智能体的核心逻辑，包括医疗资源调度、治疗计划生成和用药管理
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
from pkg.cache.cache_manager import get_cache_manager, CacheStrategy
from pkg.resilience.retry_manager import retry, circuit_breaker, RetryStrategy
from pkg.observability.enhanced_metrics import (
    get_metrics_collector as get_enhanced_metrics,
)

logger = logging.getLogger(__name__)


class AgentManager:
    """小克智能体管理器，负责医疗资源调度、治疗方案生成和药品管理"""

    def __init__(self, session_repository=None):
        """
        初始化智能体管理器

        Args:
            session_repository: 会话存储库
        """
        self.config = get_config()
        self.metrics = get_metrics_collector()
        self.enhanced_metrics = get_enhanced_metrics()

        # 设置依赖组件
        self.session_repository = session_repository

        # 初始化缓存管理器
        self.cache_manager = None
        asyncio.create_task(self._init_cache_manager())

        # 加载模型配置
        self.llm_config = self.config.get_section("models.llm")

        # 加载会话配置
        self.conversation_config = self.config.get_section("conversation")
        self.system_prompt = self.conversation_config.get("system_prompt", "")
        self.max_history_turns = self.conversation_config.get("max_history_turns", 20)

        # 设置默认模型
        self.primary_model = self.llm_config.get("primary_model", "gpt-4o-mini")
        self.fallback_model = self.llm_config.get("fallback_model", "llama-3-8b")

        # 初始化模型工厂
        self.model_factory = ModelFactory()

        # 活跃会话映射 session_id -> session_data
        self.active_sessions = {}

        # 记录活跃会话数
        self._update_active_sessions_metric()

        logger.info(
            "小克智能体管理器初始化完成，主模型: %s, 备用模型: %s",
            self.primary_model,
            self.fallback_model,
        )

    async def _init_cache_manager(self):
        """初始化缓存管理器"""
        try:
            self.cache_manager = await get_cache_manager()
            logger.info("缓存管理器初始化成功")
        except Exception as e:
            logger.error("缓存管理器初始化失败: %s", str(e))

    def _update_active_sessions_metric(self):
        """更新活跃会话数指标"""
        if hasattr(self.metrics, "update_active_sessions"):
            self.metrics.update_active_sessions(len(self.active_sessions))
        # 设置定期更新
        asyncio.create_task(self._schedule_metric_update())

    async def _schedule_metric_update(self):
        """定期更新指标的任务"""
        await asyncio.sleep(60)  # 每分钟更新一次
        self._update_active_sessions_metric()

    @track_llm_metrics(model="primary", query_type="resource_management")
    @retry(
        max_attempts=3,
        strategy=RetryStrategy.EXPONENTIAL,
        circuit_breaker_name="agent_processing",
    )
    async def process_request(
        self, user_id: str, request_data: Dict[str, Any], session_id: str = None
    ) -> Dict[str, Any]:
        """
        处理用户关于医疗资源和治疗的请求

        Args:
            user_id: 用户ID
            request_data: 请求数据，包含请求类型和相关信息
            session_id: 会话ID，如果为None则创建新会话

        Returns:
            Dict[str, Any]: 处理结果
        """
        # 记录请求指标
        request_type = request_data.get("type", "general")
        self.metrics.increment_request_count(request_type)
        self.enhanced_metrics.increment_business_metric("user_sessions")

        # 确保会话ID存在
        if not session_id:
            session_id = str(uuid.uuid4())
            logger.info("创建新会话，用户ID: %s, 会话ID: %s", user_id, session_id)

        # 尝试从缓存获取结果
        cache_key = f"request:{user_id}:{hash(str(request_data))}"
        if self.cache_manager:
            cached_result = await self.cache_manager.get(cache_key, CacheStrategy.TTL)
            if cached_result:
                logger.info("从缓存获取到结果，用户ID: %s", user_id)
                self.enhanced_metrics.record_cache_operation("get", "hit")
                return cached_result
            else:
                self.enhanced_metrics.record_cache_operation("get", "miss")

        try:
            # 根据请求类型分发处理
            if request_type == "treatment_plan":
                result = await self._generate_treatment_plan(
                    user_id, request_data, session_id
                )
            elif request_type == "medicine_info":
                result = await self._provide_medicine_info(
                    user_id, request_data, session_id
                )
            elif request_type == "resource_allocation":
                result = await self._allocate_medical_resource(
                    user_id, request_data, session_id
                )
                self.enhanced_metrics.increment_business_metric("resource_allocations")
            elif request_type == "emergency_response":
                result = await self._handle_emergency(user_id, request_data, session_id)
            else:
                # 默认对话处理
                result = await self._process_general_inquiry(
                    user_id, request_data, session_id
                )

            # 缓存结果
            if self.cache_manager and result.get("success", False):
                await self.cache_manager.set(cache_key, result, ttl=1800)  # 缓存30分钟
                self.enhanced_metrics.record_cache_operation("set", "success")

            return result

        except Exception as e:
            logger.error(
                "请求处理失败，用户ID: %s, 会话ID: %s, 错误: %s",
                user_id,
                session_id,
                str(e),
            )

            # 返回错误响应
            return {
                "request_id": str(uuid.uuid4()),
                "success": False,
                "error": str(e),
                "message": "处理您的请求时遇到了问题，请稍后重试",
                "metadata": {"session_id": session_id, "timestamp": int(time.time())},
            }

    async def _generate_treatment_plan(
        self, user_id: str, request_data: Dict[str, Any], session_id: str
    ) -> Dict[str, Any]:
        """生成治疗方案"""
        # 提取请求中的诊断信息和患者状况
        diagnosis = request_data.get("diagnosis", {})
        patient_condition = request_data.get("patient_condition", {})
        medical_history = request_data.get("medical_history", {})

        # 构建提示
        prompt = f"""作为小克，你需要生成一个个性化的治疗方案。
请基于以下信息生成详细的治疗计划:

诊断: {json.dumps(diagnosis, ensure_ascii=False)}
患者状况: {json.dumps(patient_condition, ensure_ascii=False)}
病史: {json.dumps(medical_history, ensure_ascii=False)}

请提供:
1. 治疗目标
2. 治疗方式选择（中医、西医或结合方案）
3. 具体治疗措施
4. 用药建议
5. 生活调理建议
6. 后续随访计划
"""

        # 构建消息列表
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt},
        ]

        # 调用LLM生成响应
        (
            response_text,
            response_meta,
        ) = await self.model_factory.generate_chat_completion(
            model=self.primary_model,
            messages=messages,
            temperature=0.4,  # 较低的温度，提高确定性
            max_tokens=2048,
        )

        # 返回治疗方案
        return {
            "request_id": str(uuid.uuid4()),
            "success": True,
            "plan": response_text,
            "confidence": response_meta.get("confidence", 0.9),
            "metadata": {
                "model": response_meta.get("model", self.primary_model),
                "session_id": session_id,
                "timestamp": int(time.time()),
            },
        }

    async def _provide_medicine_info(
        self, user_id: str, request_data: Dict[str, Any], session_id: str
    ) -> Dict[str, Any]:
        """提供药品信息"""
        # 提取药品名称或其他查询信息
        medicine_name = request_data.get("medicine_name", "")
        query_type = request_data.get("query_type", "general")  # 可能是用法、副作用等

        # 构建提示
        prompt = f"""作为小克，请提供关于药品"{medicine_name}"的详细信息。
查询类型: {query_type}

请提供:
1. 药品基本信息（成分、规格）
2. 适应症和主要功效
3. 用法用量
4. 常见副作用
5. 禁忌症和注意事项
6. 中西药配伍禁忌（如适用）
"""

        # 构建消息列表
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt},
        ]

        # 调用LLM生成响应
        (
            response_text,
            response_meta,
        ) = await self.model_factory.generate_chat_completion(
            model=self.primary_model,
            messages=messages,
            temperature=0.3,  # 较低的温度，提高确定性
            max_tokens=1024,
        )

        # 返回药品信息
        return {
            "request_id": str(uuid.uuid4()),
            "success": True,
            "medicine_info": response_text,
            "medicine_name": medicine_name,
            "confidence": response_meta.get("confidence", 0.9),
            "metadata": {
                "model": response_meta.get("model", self.primary_model),
                "session_id": session_id,
                "timestamp": int(time.time()),
            },
        }

    async def _allocate_medical_resource(
        self, user_id: str, request_data: Dict[str, Any], session_id: str
    ) -> Dict[str, Any]:
        """医疗资源调度"""
        # 提取资源需求信息
        resource_needs = request_data.get("resource_needs", {})
        urgency_level = request_data.get("urgency", "normal")
        location = request_data.get("location", {})

        # 构建提示
        prompt = f"""作为小克，你需要进行医疗资源调度。
请基于以下信息进行最优资源分配:

资源需求: {json.dumps(resource_needs, ensure_ascii=False)}
紧急程度: {urgency_level}
位置信息: {json.dumps(location, ensure_ascii=False)}

请提供:
1. 推荐的医疗机构和科室
2. 所需医疗设备和专家
3. 预计等待时间
4. 替代方案（如首选资源不可用）
5. 预约建议
"""

        # 构建消息列表
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt},
        ]

        # 调用LLM生成响应
        (
            response_text,
            response_meta,
        ) = await self.model_factory.generate_chat_completion(
            model=self.primary_model,
            messages=messages,
            temperature=0.4,
            max_tokens=1024,
        )

        # 返回资源调度结果
        return {
            "request_id": str(uuid.uuid4()),
            "success": True,
            "allocation_plan": response_text,
            "urgency_level": urgency_level,
            "confidence": response_meta.get("confidence", 0.9),
            "metadata": {
                "model": response_meta.get("model", self.primary_model),
                "session_id": session_id,
                "timestamp": int(time.time()),
            },
        }

    async def _handle_emergency(
        self, user_id: str, request_data: Dict[str, Any], session_id: str
    ) -> Dict[str, Any]:
        """处理医疗紧急情况"""
        # 提取紧急情况信息
        emergency_type = request_data.get("emergency_type", "")
        symptoms = request_data.get("symptoms", [])
        vital_signs = request_data.get("vital_signs", {})

        # 构建提示
        prompt = f"""作为小克，你需要处理一个医疗紧急情况。
请基于以下信息提供紧急响应指导:

紧急情况类型: {emergency_type}
症状: {", ".join(symptoms)}
生命体征: {json.dumps(vital_signs, ensure_ascii=False)}

请提供:
1. 初步应急处理建议
2. 最近的急救资源推荐
3. 紧急联系方式
4. 转运建议
5. 注意事项和禁忌
"""

        # 构建消息列表
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt},
        ]

        # 调用LLM生成响应
        (
            response_text,
            response_meta,
        ) = await self.model_factory.generate_chat_completion(
            model=self.primary_model,
            messages=messages,
            temperature=0.2,  # 更低的温度，提高确定性
            max_tokens=1024,
        )

        # 返回紧急响应
        return {
            "request_id": str(uuid.uuid4()),
            "success": True,
            "emergency_response": response_text,
            "urgency_level": "high",
            "confidence": response_meta.get("confidence", 0.9),
            "metadata": {
                "model": response_meta.get("model", self.primary_model),
                "session_id": session_id,
                "timestamp": int(time.time()),
            },
        }

    async def _process_general_inquiry(
        self, user_id: str, request_data: Dict[str, Any], session_id: str
    ) -> Dict[str, Any]:
        """处理一般性医疗咨询"""
        # 提取查询内容
        query = request_data.get("message", "")

        # 构建消息列表
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": query},
        ]

        # 调用LLM生成响应
        (
            response_text,
            response_meta,
        ) = await self.model_factory.generate_chat_completion(
            model=self.primary_model,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )

        # 返回咨询响应
        return {
            "request_id": str(uuid.uuid4()),
            "success": True,
            "message": response_text,
            "confidence": response_meta.get("confidence", 0.9),
            "metadata": {
                "model": response_meta.get("model", self.primary_model),
                "session_id": session_id,
                "timestamp": int(time.time()),
            },
        }

    async def close(self):
        """关闭智能体资源"""
        # 关闭模型工厂
        await self.model_factory.close()

        logger.info("小克智能体资源已清理")
