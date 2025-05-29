#!/usr/bin/env python3
"""
索尔服务gRPC接口实现
"""
import logging
import time
import uuid
from typing import Any

import grpc

from api.grpc import soer_service_pb2, soer_service_pb2_grpc
from internal.agent.agent_manager import AgentManager
from internal.lifecycle.health_profile.profile_manager import ProfileManager

# 导入生成的proto文件
# 注：实际使用时需要先生成proto文件，此处假设已生成
# from api.grpc.soer_service_pb2 import *
# from api.grpc.soer_service_pb2_grpc import SoerServiceServicer, add_SoerServiceServicer_to_server
# 导入服务
from internal.lifecycle.health_profile.profile_service import HealthProfileService
from internal.lifecycle.plan_generator.plan_generator import PlanGenerator
from internal.lifecycle.plan_generator.plan_service import HealthPlanService
from internal.lifecycle.sensor_analyzer.sensor_analyzer import SensorAnalyzer
from internal.lifecycle.sensor_analyzer.sensor_service import SensorAnalysisService
from internal.nutrition.food_db.food_database import FoodDatabase
from internal.nutrition.recommendation.nutrition_service import NutritionService
from internal.nutrition.recommendation.recommendation_engine import RecommendationEngine
from pkg.utils.config_loader import get_config
from pkg.utils.metrics import get_metrics_collector

logger = logging.getLogger(__name__)

class SoerServiceImpl(soer_service_pb2_grpc.SoerServiceServicer):
    """索尔服务gRPC接口实现"""

    def __init__(self):
        """初始化服务实现"""
        logger.info("初始化索尔服务gRPC接口实现")
        self.config = get_config()
        self.metrics = get_metrics_collector()

        # 初始化各个子服务
        self.health_profile_service = HealthProfileService(self.config, {})
        self.health_plan_service = HealthPlanService(self.config, {})
        self.sensor_analysis_service = SensorAnalysisService(self.config, {})
        self.nutrition_service = NutritionService(self.config, {})

        # 初始化依赖组件
        self.agent_manager = AgentManager()
        self.profile_manager = ProfileManager()
        self.plan_generator = PlanGenerator()
        self.sensor_analyzer = SensorAnalyzer()
        self.food_db = FoodDatabase()
        self.recommendation_engine = RecommendationEngine()

        logger.info("索尔服务gRPC接口实现初始化完成")

    async def GenerateHealthPlan(self, request, context):
        """生成个性化健康计划"""
        logger.info("接收到健康计划生成请求，用户ID: %s", request.user_id)
        start_time = time.time()

        try:
            # 构建健康计划请求
            plan_request = {
                "user_id": request.user_id,
                "type": "health_plan",
                "health_goals": list(request.health_goals),
                "constitution_type": request.constitution_type,
                "current_season": request.current_season,
                "preferences": {k: list(v.value) for k, v in request.preferences.items()}
            }

            # 获取用户健康数据
            health_data = self.profile_manager.get_health_data(request.user_id)
            plan_request["health_data"] = health_data

            # 调用智能体生成计划
            session_id = str(uuid.uuid4())
            result = await self.agent_manager.process_request(
                request.user_id, plan_request, session_id
            )

            # 构建响应
            response = soer_service_pb2.HealthPlanResponse(
                plan_id=str(uuid.uuid4()),
                confidence_score=result.get("confidence", 0.9)
            )

            # 解析健康计划文本到结构化响应
            health_plan = result.get("health_plan", "")
            plan_sections = self._parse_health_plan(health_plan)

            # 设置响应字段
            if "diet" in plan_sections:
                response.diet_recommendations.extend(plan_sections["diet"])

            if "exercise" in plan_sections:
                response.exercise_recommendations.extend(plan_sections["exercise"])

            if "lifestyle" in plan_sections:
                response.lifestyle_recommendations.extend(plan_sections["lifestyle"])

            if "supplements" in plan_sections:
                response.supplement_recommendations.extend(plan_sections["supplements"])

            if "schedule" in plan_sections:
                for k, v in plan_sections["schedule"].items():
                    response.schedule[k] = v

            # 记录指标
            elapsed_time = time.time() - start_time
            self.metrics.record_request_latency("GenerateHealthPlan", elapsed_time)
            self.metrics.increment_success_count("GenerateHealthPlan")

            logger.info("健康计划生成成功，用户ID: %s，耗时: %.2f秒", request.user_id, elapsed_time)
            return response

        except Exception as e:
            logger.error("健康计划生成失败，用户ID: %s，错误: %s", request.user_id, str(e))
            self.metrics.increment_error_count("GenerateHealthPlan")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"健康计划生成失败: {str(e)}")
            return soer_service_pb2.HealthPlanResponse()

    def _parse_health_plan(self, plan_text: str) -> dict[str, Any]:
        """解析健康计划文本到结构化数据"""
        # 简单的解析逻辑，实际应用中可能需要更复杂的NLP处理
        sections = {}
        current_section = None
        lines = plan_text.strip().split('\n')

        section_mapping = {
            "饮食建议": "diet",
            "运动建议": "exercise",
            "生活作息": "lifestyle",
            "营养补充": "supplements",
            "日程安排": "schedule"
        }

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 检查是否是章节标题
            is_section_header = False
            for zh_title, en_name in section_mapping.items():
                if zh_title in line:
                    current_section = en_name
                    sections[current_section] = [] if current_section != "schedule" else {}
                    is_section_header = True
                    break

            if is_section_header:
                continue

            # 添加内容到当前章节
            if current_section:
                if current_section == "schedule":
                    # 尝试解析日程安排格式为 "时间段: 内容"
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        sections[current_section][parts[0].strip()] = parts[1].strip()
                else:
                    # 列表项处理
                    if line.startswith(('- ', '• ', '* ')):
                        line = line[2:].strip()
                    elif line.startswith(('1. ', '2. ', '3. ')):
                        line = line[3:].strip()

                    sections[current_section].append(line)

        return sections

    async def GetLifestyleRecommendation(self, request, context):
        """获取生活方式建议"""
        logger.info("接收到生活方式建议请求，用户ID: %s", request.user_id)
        start_time = time.time()

        try:
            # 提取请求信息
            location = request.location
            env_data = dict(request.environment_data.items())

            # 构建生活方式建议请求
            advice_request = {
                "user_id": request.user_id,
                "type": "lifestyle_advice",
                "current_habits": {},  # 从用户档案获取
                "living_environment": {
                    "location": location,
                    **env_data
                },
                "work_schedule": "",  # 从用户档案获取
                "pain_points": []  # 从用户档案获取
            }

            # 获取用户档案信息
            user_profile = self.profile_manager.get_user_profile(request.user_id)
            advice_request["current_habits"] = user_profile.get("habits", {})
            advice_request["work_schedule"] = user_profile.get("work_schedule", "")
            advice_request["pain_points"] = user_profile.get("pain_points", [])
            advice_request["constitution_type"] = user_profile.get("constitution_type", "未知")

            # 调用智能体生成建议
            session_id = str(uuid.uuid4())
            result = await self.agent_manager.process_request(
                request.user_id, advice_request, session_id
            )

            # 解析建议文本
            advice_text = result.get("lifestyle_advice", "")
            advice_sections = self._parse_lifestyle_advice(advice_text)

            # 构建响应
            response = soer_service_pb2.LifestyleResponse()

            # 添加建议
            priority = 1.0
            for category, items in advice_sections.items():
                for item in items:
                    rec = response.recommendations.add()
                    rec.category = category
                    rec.content = item
                    rec.priority = priority
                    rec.reasoning = f"基于您的{request.context}情境和{user_profile.get('constitution_type', '体质')}特点定制"
                    priority -= 0.05  # 降低优先级
                    if priority < 0.5:
                        priority = 0.5

            # 记录指标
            elapsed_time = time.time() - start_time
            self.metrics.record_request_latency("GetLifestyleRecommendation", elapsed_time)
            self.metrics.increment_success_count("GetLifestyleRecommendation")

            logger.info("生活方式建议生成成功，用户ID: %s，耗时: %.2f秒", request.user_id, elapsed_time)
            return response

        except Exception as e:
            logger.error("生活方式建议生成失败，用户ID: %s，错误: %s", request.user_id, str(e))
            self.metrics.increment_error_count("GetLifestyleRecommendation")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"生活方式建议生成失败: {str(e)}")
            return soer_service_pb2.LifestyleResponse()

    def _parse_lifestyle_advice(self, advice_text: str) -> dict[str, list[str]]:
        """解析生活方式建议文本到结构化数据"""
        sections = {}
        current_section = None
        lines = advice_text.strip().split('\n')

        section_mapping = {
            "作息时间": "schedule",
            "工作效率": "productivity",
            "家居环境": "environment",
            "压力管理": "stress_management",
            "社交健康": "social_wellness"
        }

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 检查是否是章节标题
            is_section_header = False
            for zh_title, en_name in section_mapping.items():
                if zh_title in line:
                    current_section = en_name
                    sections[current_section] = []
                    is_section_header = True
                    break

            if is_section_header:
                continue

            # 添加内容到当前章节
            if current_section:
                # 列表项处理
                if line.startswith(('- ', '• ', '* ')):
                    line = line[2:].strip()
                elif line.startswith(('1. ', '2. ', '3. ')):
                    line = line[3:].strip()

                sections[current_section].append(line)

        return sections

    async def AnalyzeSensorData(self, request, context):
        """分析传感器数据"""
        logger.info("接收到传感器数据分析请求，用户ID: %s", request.user_id)
        start_time = time.time()

        try:
            # 处理传感器数据
            sensor_data = []
            for data_entry in request.data:
                data_points = []
                for point in data_entry.data_points:
                    data_points.append({
                        'timestamp': point.timestamp,
                        'values': dict(point.values.items()),
                        'metadata': dict(point.metadata.items())
                    })

                sensor_data.append({
                    'sensor_type': data_entry.sensor_type,
                    'device_id': data_entry.device_id,
                    'data_points': data_points
                })

            # 调用传感器分析服务
            analysis_result = self.sensor_analyzer.analyze_data(request.user_id, sensor_data)

            # 构建响应
            response = soer_service_pb2.SensorDataResponse()

            # 添加健康指标
            for metric in analysis_result.get('metrics', []):
                health_metric = response.metrics.add()
                health_metric.metric_name = metric['name']
                health_metric.current_value = metric['value']
                health_metric.reference_min = metric.get('ref_min', 0)
                health_metric.reference_max = metric.get('ref_max', 0)
                health_metric.interpretation = metric.get('interpretation', '')
                health_metric.trend = metric.get('trend', 'stable')

            # 添加见解
            for insight in analysis_result.get('insights', []):
                insight_entry = response.insights.add()
                insight_entry.category = insight['category']
                insight_entry.description = insight['description']
                insight_entry.confidence = insight.get('confidence', 0.8)
                insight_entry.suggestions.extend(insight.get('suggestions', []))

            # 记录指标
            elapsed_time = time.time() - start_time
            self.metrics.record_request_latency("AnalyzeSensorData", elapsed_time)
            self.metrics.increment_success_count("AnalyzeSensorData")

            logger.info("传感器数据分析成功，用户ID: %s，耗时: %.2f秒", request.user_id, elapsed_time)
            return response

        except Exception as e:
            logger.error("传感器数据分析失败，用户ID: %s，错误: %s", request.user_id, str(e))
            self.metrics.increment_error_count("AnalyzeSensorData")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"传感器数据分析失败: {str(e)}")
            return soer_service_pb2.SensorDataResponse()

    async def TrackNutrition(self, request, context):
        """追踪并分析用户营养摄入"""
        logger.info("接收到营养追踪请求，用户ID: %s", request.user_id)
        start_time = time.time()

        try:
            # 处理食物条目
            food_entries = []
            for entry in request.food_entries:
                food_entries.append({
                    'food_name': entry.food_name,
                    'quantity': entry.quantity,
                    'unit': entry.unit,
                    'timestamp': entry.timestamp,
                    'properties': dict(entry.properties.items())
                })

            # 获取用户体质信息
            user_profile = self.profile_manager.get_user_profile(request.user_id)
            constitution_type = user_profile.get("constitution_type", "未知")

            # 调用营养分析服务
            nutrition_result = self.recommendation_engine.analyze_nutrition(
                request.user_id,
                food_entries,
                request.analysis_type,
                constitution_type
            )

            # 构建响应
            response = soer_service_pb2.NutritionResponse()

            # 添加营养摘要
            for nutrient, value in nutrition_result.get('nutrient_summary', {}).items():
                response.nutrient_summary[nutrient] = value

            # 添加营养平衡情况
            for balance in nutrition_result.get('balance', []):
                balance_entry = response.balance.add()
                balance_entry.nutrient = balance['nutrient']
                balance_entry.current = balance['current']
                balance_entry.target = balance['target']
                balance_entry.status = balance['status']

            # 添加食物建议
            for suggestion in nutrition_result.get('suggestions', []):
                suggestion_entry = response.suggestions.add()
                suggestion_entry.food = suggestion['food']
                suggestion_entry.benefits.extend(suggestion['benefits'])
                suggestion_entry.recommendation_strength = suggestion['strength']
                suggestion_entry.reason = suggestion['reason']

            # 添加体质分析
            if 'constitutional_analysis' in nutrition_result:
                const_analysis = nutrition_result['constitutional_analysis']

                # 五行平衡
                for element, value in const_analysis.get('five_elements_balance', {}).items():
                    response.constitutional_analysis.five_elements_balance[element] = value

                # 五味分布
                for taste, value in const_analysis.get('five_tastes_distribution', {}).items():
                    response.constitutional_analysis.five_tastes_distribution[taste] = value

                # 不平衡修正
                response.constitutional_analysis.imbalance_corrections.extend(
                    const_analysis.get('imbalance_corrections', [])
                )

            # 记录指标
            elapsed_time = time.time() - start_time
            self.metrics.record_request_latency("TrackNutrition", elapsed_time)
            self.metrics.increment_success_count("TrackNutrition")

            logger.info("营养追踪分析成功，用户ID: %s，耗时: %.2f秒", request.user_id, elapsed_time)
            return response

        except Exception as e:
            logger.error("营养追踪分析失败，用户ID: %s，错误: %s", request.user_id, str(e))
            self.metrics.increment_error_count("TrackNutrition")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"营养追踪分析失败: {str(e)}")
            return soer_service_pb2.NutritionResponse()

    async def DetectAbnormalPattern(self, request, context):
        """检测异常健康模式"""
        logger.info("接收到异常模式检测请求，用户ID: %s", request.user_id)
        # TODO: 实现异常模式检测逻辑
        return soer_service_pb2.AbnormalPatternResponse()

    async def PredictHealthTrend(self, request, context):
        """预测健康趋势"""
        logger.info("接收到健康趋势预测请求，用户ID: %s", request.user_id)
        # TODO: 实现健康趋势预测逻辑
        return soer_service_pb2.HealthTrendResponse()

    async def GetSleepRecommendation(self, request, context):
        """获取个性化睡眠建议"""
        logger.info("接收到睡眠建议请求，用户ID: %s", request.user_id)
        # TODO: 实现睡眠建议生成逻辑
        return soer_service_pb2.SleepResponse()

    async def AnalyzeEmotionalState(self, request, context):
        """分析情绪状态"""
        logger.info("接收到情绪状态分析请求，用户ID: %s", request.user_id)
        # TODO: 实现情绪状态分析逻辑
        return soer_service_pb2.EmotionalStateResponse()
