#!/usr/bin/env python3
"""
情绪分析服务gRPC处理器
处理情绪分析相关的gRPC请求
"""

import logging
import time
import uuid
from datetime import datetime
from typing import Any

from google.protobuf.timestamp_pb2 import Timestamp

from internal.lifecycle.emotional_analyzer.emotional_service import EmotionalService

logger = logging.getLogger(__name__)

class EmotionalServiceHandler:
    """情绪分析服务gRPC处理器"""

    def __init__(self, emotional_service: EmotionalService):
        """初始化处理器"""
        self.emotional_service = emotional_service

    async def analyze_emotional_state(self, request, context):
        """
        处理情绪状态分析请求

        Args:
            request: AnalyzeEmotionalStateRequest gRPC请求
            context: gRPC上下文

        Returns:
            EmotionalStateResponse: 情绪分析结果
        """
        try:
            user_id = request.user_id
            logger.info(f"收到情绪分析请求 - 用户ID: {user_id}")

            # 转换输入数据
            inputs = []
            for input_data in request.inputs:
                inputs.append({
                    "input_type": input_data.input_type,
                    "data": input_data.data,
                    "metadata": dict(input_data.metadata.items()),
                    "capture_time": datetime.fromtimestamp(
                        input_data.capture_time.seconds +
                        input_data.capture_time.nanos / 1e9
                    ) if input_data.HasField("capture_time") else datetime.now()
                })

            # 调用情绪分析服务
            analysis_result = await self.emotional_service.analyze_emotional_state(
                user_id=user_id,
                inputs=inputs
            )

            # 创建响应
            response = self._create_emotional_state_response(
                user_id=user_id,
                analysis_result=analysis_result
            )

            logger.info(f"情绪分析完成 - 用户ID: {user_id}, 主要情绪: {analysis_result['primary_emotion']}")
            return response

        except Exception as e:
            logger.error(f"情绪分析失败: {str(e)}", exc_info=True)
            # 可以根据错误类型设置不同的gRPC状态码
            context.set_code(13)  # INTERNAL
            context.set_details(f"情绪分析服务错误: {str(e)}")
            return None

    async def get_emotional_history(self, request, context):
        """
        获取情绪历史记录

        Args:
            request: GetEmotionalHistoryRequest gRPC请求
            context: gRPC上下文

        Returns:
            EmotionalHistoryResponse: 情绪历史记录
        """
        try:
            user_id = request.user_id
            logger.info(f"获取情绪历史 - 用户ID: {user_id}")

            # 转换日期参数
            start_date = None
            end_date = None

            if request.HasField("start_date"):
                start_date = datetime.fromtimestamp(
                    request.start_date.seconds +
                    request.start_date.nanos / 1e9
                )

            if request.HasField("end_date"):
                end_date = datetime.fromtimestamp(
                    request.end_date.seconds +
                    request.end_date.nanos / 1e9
                )

            emotion_type = request.emotion_type if request.emotion_type else None

            # TODO: 实现实际的历史查询
            # 这里只是一个示例实现，实际应该从数据库或缓存中查询情绪历史数据

            # 创建响应
            response = self._create_mock_emotional_history_response(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                emotion_type=emotion_type
            )

            logger.info(f"情绪历史查询完成 - 用户ID: {user_id}")
            return response

        except Exception as e:
            logger.error(f"获取情绪历史失败: {str(e)}", exc_info=True)
            context.set_code(13)  # INTERNAL
            context.set_details(f"情绪历史服务错误: {str(e)}")
            return None

    async def get_emotional_insights(self, request, context):
        """
        获取情绪洞察

        Args:
            request: GetEmotionalInsightsRequest gRPC请求
            context: gRPC上下文

        Returns:
            EmotionalInsightsResponse: 情绪洞察响应
        """
        try:
            user_id = request.user_id
            lookback_days = request.lookback_days if request.lookback_days > 0 else 30

            logger.info(f"获取情绪洞察 - 用户ID: {user_id}, 回溯天数: {lookback_days}")

            # TODO: 实现实际的情绪洞察分析
            # 这里只是一个示例实现，实际应该分析用户的历史情绪数据，
            # 找出模式和触发因素，并提供个性化的长期建议

            # 创建响应
            response = self._create_mock_emotional_insights_response(
                user_id=user_id,
                lookback_days=lookback_days
            )

            logger.info(f"情绪洞察分析完成 - 用户ID: {user_id}")
            return response

        except Exception as e:
            logger.error(f"获取情绪洞察失败: {str(e)}", exc_info=True)
            context.set_code(13)  # INTERNAL
            context.set_details(f"情绪洞察服务错误: {str(e)}")
            return None

    def _create_emotional_state_response(self, user_id: str, analysis_result: dict[str, Any]):
        """创建情绪状态响应"""
        from api.grpc import soer_service_pb2

        response = soer_service_pb2.EmotionalStateResponse()
        response.user_id = user_id
        response.analysis_id = str(uuid.uuid4())

        # 设置情绪得分
        for emotion, score in analysis_result.get("emotion_scores", {}).items():
            response.emotion_scores[emotion] = score

        # 设置主要情绪和趋势
        response.primary_emotion = analysis_result.get("primary_emotion", "")
        response.emotional_tendency = analysis_result.get("emotional_tendency", "")

        # 设置健康影响
        health_impact = analysis_result.get("health_impact", {})
        if health_impact:
            for system in health_impact.get("affected_systems", []):
                response.health_impact.affected_systems.append(system)

            response.health_impact.tcm_interpretation = health_impact.get("tcm_interpretation", "")
            response.health_impact.severity = health_impact.get("severity", 0.0)

        # 设置干预建议
        for suggestion in analysis_result.get("suggestions", []):
            suggestion_pb = soer_service_pb2.EmotionalSuggestion()
            suggestion_pb.intervention_type = suggestion.get("intervention_type", "")
            suggestion_pb.description = suggestion.get("description", "")
            suggestion_pb.estimated_effectiveness = suggestion.get("estimated_effectiveness", 0.0)
            suggestion_pb.is_urgent = suggestion.get("is_urgent", False)

            response.suggestions.append(suggestion_pb)

        # 设置分析时间
        now = Timestamp()
        now.GetCurrentTime()
        response.analysis_date.CopyFrom(now)

        return response

    def _create_mock_emotional_history_response(self, user_id: str, start_date: datetime,
                                              end_date: datetime, emotion_type: str):
        """创建模拟情绪历史响应"""
        from api.grpc import soer_service_pb2

        response = soer_service_pb2.EmotionalHistoryResponse()
        response.user_id = user_id

        # 创建模拟情绪状态记录
        emotions = ["愤怒", "快乐", "忧郁", "恐惧", "平静"]

        # 如果指定了情绪类型，仅返回该类型的记录
        if emotion_type and emotion_type in emotions:
            emotions = [emotion_type]

        # 为简单起见，仅创建5条记录
        for i in range(5):
            record = soer_service_pb2.EmotionalStateRecord()
            record.analysis_id = f"mock_analysis_{i}"
            record.primary_emotion = emotions[i % len(emotions)]

            # 设置模拟的情绪得分
            primary_score = 0.7
            for emotion in emotions:
                if emotion == record.primary_emotion:
                    record.emotion_scores[emotion] = primary_score
                else:
                    record.emotion_scores[emotion] = (1.0 - primary_score) / (len(emotions) - 1)

            # 设置记录时间，每条记录间隔1天
            record_date = Timestamp()
            seconds = int(time.time()) - (i * 86400)  # 86400秒 = 1天
            record_date.seconds = seconds
            record.record_date.CopyFrom(record_date)

            response.emotional_states.append(record)

        # 设置情绪趋势分析
        trend = soer_service_pb2.EmotionalTrendAnalysis()
        trend.dominant_emotion = emotions[0]
        trend.trend_direction = "stable"
        trend.volatility = 0.3
        trend.interpretation = "情绪整体平稳，无明显波动趋势"

        response.trend_analysis.CopyFrom(trend)

        return response

    def _create_mock_emotional_insights_response(self, user_id: str, lookback_days: int):
        """创建模拟情绪洞察响应"""
        from api.grpc import soer_service_pb2

        response = soer_service_pb2.EmotionalInsightsResponse()
        response.user_id = user_id

        # 创建模拟情绪模式
        pattern1 = soer_service_pb2.EmotionalPattern()
        pattern1.pattern_type = "周期性"
        pattern1.description = "工作日压力增加，周末情绪改善的周期性模式"
        pattern1.confidence = 0.85
        pattern1.related_emotions.extend(["忧郁", "愤怒", "快乐"])

        pattern2 = soer_service_pb2.EmotionalPattern()
        pattern2.pattern_type = "触发性"
        pattern2.description = "与特定工作任务相关的压力情绪模式"
        pattern2.confidence = 0.75
        pattern2.related_emotions.extend(["恐惧", "忧郁"])

        response.emotional_patterns.extend([pattern1, pattern2])

        # 创建模拟情绪触发因素
        trigger1 = soer_service_pb2.EmotionalTrigger()
        trigger1.trigger_source = "工作压力"
        trigger1.description = "工作期限临近时情绪波动明显"
        trigger1.associated_emotions.extend(["忧郁", "恐惧"])
        trigger1.confidence = 0.9

        trigger2 = soer_service_pb2.EmotionalTrigger()
        trigger2.trigger_source = "社交互动"
        trigger2.description = "社交活动后情绪改善"
        trigger2.associated_emotions.extend(["快乐"])
        trigger2.confidence = 0.8

        response.emotional_triggers.extend([trigger1, trigger2])

        # 创建情绪平衡评估
        balance = soer_service_pb2.EmotionalBalanceAssessment()
        balance.overall_status = "轻度失衡"

        # 设置五行平衡评分
        balance.element_balance["木"] = 0.3  # 较弱
        balance.element_balance["火"] = 0.6  # 适中
        balance.element_balance["土"] = 0.7  # 较强
        balance.element_balance["金"] = 0.5  # 适中
        balance.element_balance["水"] = 0.4  # 较弱

        balance.tcm_interpretation = "肝气郁滞，脾气有余，肾气不足"

        # 设置脏腑影响
        balance.organ_system_impact["肝"] = 0.7  # 较大影响
        balance.organ_system_impact["心"] = 0.3  # 轻微影响
        balance.organ_system_impact["脾"] = 0.2  # 轻微影响
        balance.organ_system_impact["肺"] = 0.4  # 中等影响
        balance.organ_system_impact["肾"] = 0.6  # 中等影响

        response.balance_assessment.CopyFrom(balance)

        # 创建长期建议
        suggestion1 = soer_service_pb2.EmotionalSuggestion()
        suggestion1.intervention_type = "lifestyle"
        suggestion1.description = "增加有氧运动，每周至少3次，每次30分钟以上"
        suggestion1.estimated_effectiveness = 0.85
        suggestion1.is_urgent = False

        suggestion2 = soer_service_pb2.EmotionalSuggestion()
        suggestion2.intervention_type = "relaxation"
        suggestion2.description = "工作日融入短暂冥想，缓解压力积累"
        suggestion2.estimated_effectiveness = 0.75
        suggestion2.is_urgent = False

        suggestion3 = soer_service_pb2.EmotionalSuggestion()
        suggestion3.intervention_type = "social"
        suggestion3.description = "保持规律社交活动，增加积极情绪体验"
        suggestion3.estimated_effectiveness = 0.8
        suggestion3.is_urgent = False

        response.long_term_suggestions.extend([suggestion1, suggestion2, suggestion3])

        return response
