"""
健康服务类

处理健康数据分析、健康趋势监测、个性化建议等业务逻辑
"""

import uuid
import numpy as np
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from statistics import mean, median

from .base_service import BaseService
from ..models.health import HealthData, HealthAnalysis, HealthRecommendation


class HealthService(BaseService):
    """健康服务类"""

    def __init__(self):
        super().__init__()
        self.collection_name = "health_data"
        self.analysis_collection = "health_analyses"
        self.recommendations_collection = "health_recommendations"

    async def submit_health_data(self, user_id: str, health_data: Dict[str, Any]) -> HealthData:
        """提交健康数据"""
        try:
            # 创建健康数据对象
            data = HealthData(
                data_id=str(uuid.uuid4()),
                user_id=user_id,
                timestamp=datetime.now(),
                **health_data
            )

            # 数据验证和清洗
            validated_data = self._validate_health_data(data)

            # 保存到数据库
            if self.mongodb:
                await self.mongodb[self.collection_name].insert_one(validated_data.dict())

            # 触发实时分析
            await self._trigger_real_time_analysis(user_id, validated_data)

            await self.log_operation("submit_health_data", True, {"user_id": user_id})
            return validated_data

        except Exception as e:
            await self.log_operation("submit_health_data", False, {"error": str(e)})
            raise

    async def analyze_health_data(self, user_id: str, analysis_type: str = "comprehensive") -> HealthAnalysis:
        """分析健康数据"""
        try:
            # 获取用户历史健康数据
            health_history = await self._get_health_history(user_id, days=30)
            
            if not health_history:
                raise ValueError("没有足够的健康数据进行分析")

            # 执行不同类型的分析
            if analysis_type == "comprehensive":
                analysis_result = await self._comprehensive_analysis(user_id, health_history)
            elif analysis_type == "cardiovascular":
                analysis_result = await self._cardiovascular_analysis(health_history)
            elif analysis_type == "metabolic":
                analysis_result = await self._metabolic_analysis(health_history)
            elif analysis_type == "sleep":
                analysis_result = await self._sleep_analysis(health_history)
            else:
                analysis_result = await self._basic_analysis(health_history)

            # 创建分析对象
            analysis = HealthAnalysis(
                analysis_id=str(uuid.uuid4()),
                user_id=user_id,
                analysis_type=analysis_type,
                **analysis_result,
                created_at=datetime.now()
            )

            # 保存分析结果
            if self.mongodb:
                await self.mongodb[self.analysis_collection].insert_one(analysis.dict())

            await self.log_operation("analyze_health_data", True, {"user_id": user_id, "type": analysis_type})
            return analysis

        except Exception as e:
            await self.log_operation("analyze_health_data", False, {"error": str(e)})
            raise

    async def get_health_dashboard(self, user_id: str) -> Dict[str, Any]:
        """获取健康仪表板数据"""
        try:
            # 获取最新健康数据
            latest_data = await self._get_latest_health_data(user_id)
            
            # 获取健康趋势
            trends = await self._get_health_trends(user_id, days=7)
            
            # 获取健康评分
            health_score = await self._calculate_health_score(user_id)
            
            # 获取风险评估
            risk_assessment = await self._assess_health_risks(user_id)
            
            # 获取建议
            recommendations = await self._get_active_recommendations(user_id)

            dashboard = {
                "user_id": user_id,
                "last_updated": datetime.now(),
                "health_score": health_score,
                "latest_metrics": latest_data,
                "trends": trends,
                "risk_assessment": risk_assessment,
                "recommendations": recommendations,
                "alerts": await self._get_health_alerts(user_id),
                "goals_progress": await self._get_goals_progress(user_id)
            }

            await self.log_operation("get_health_dashboard", True, {"user_id": user_id})
            return dashboard

        except Exception as e:
            await self.log_operation("get_health_dashboard", False, {"error": str(e)})
            return {}

    async def get_health_trends(self, user_id: str, metric: str, days: int = 30) -> Dict[str, Any]:
        """获取健康趋势分析"""
        try:
            # 获取指定时间范围的数据
            health_data = await self._get_health_history(user_id, days)
            
            if not health_data:
                return {"error": "没有足够的数据"}

            # 提取指定指标的数据
            metric_data = self._extract_metric_data(health_data, metric)
            
            if not metric_data:
                return {"error": f"没有找到指标 {metric} 的数据"}

            # 计算趋势
            trend_analysis = self._analyze_trend(metric_data)
            
            # 生成预测
            prediction = self._predict_trend(metric_data, days=7)
            
            # 识别异常值
            anomalies = self._detect_anomalies(metric_data)

            result = {
                "metric": metric,
                "period_days": days,
                "data_points": len(metric_data),
                "current_value": metric_data[-1]["value"] if metric_data else None,
                "trend": trend_analysis,
                "prediction": prediction,
                "anomalies": anomalies,
                "statistics": self._calculate_statistics(metric_data),
                "recommendations": self._generate_trend_recommendations(metric, trend_analysis)
            }

            await self.log_operation("get_health_trends", True, {"user_id": user_id, "metric": metric})
            return result

        except Exception as e:
            await self.log_operation("get_health_trends", False, {"error": str(e)})
            return {"error": str(e)}

    async def generate_health_recommendations(self, user_id: str) -> List[HealthRecommendation]:
        """生成个性化健康建议"""
        try:
            # 获取用户健康数据和分析结果
            latest_analysis = await self._get_latest_analysis(user_id)
            health_history = await self._get_health_history(user_id, days=14)
            user_profile = await self._get_user_profile(user_id)

            recommendations = []

            # 基于最新分析生成建议
            if latest_analysis:
                recommendations.extend(await self._generate_analysis_based_recommendations(latest_analysis))

            # 基于健康趋势生成建议
            if health_history:
                recommendations.extend(await self._generate_trend_based_recommendations(health_history))

            # 基于用户档案生成建议
            if user_profile:
                recommendations.extend(await self._generate_profile_based_recommendations(user_profile))

            # 去重和优先级排序
            unique_recommendations = self._deduplicate_recommendations(recommendations)
            prioritized_recommendations = self._prioritize_recommendations(unique_recommendations)

            # 保存建议
            for rec in prioritized_recommendations:
                rec.recommendation_id = str(uuid.uuid4())
                rec.user_id = user_id
                rec.created_at = datetime.now()
                
                if self.mongodb:
                    await self.mongodb[self.recommendations_collection].insert_one(rec.dict())

            await self.log_operation("generate_health_recommendations", True, {"user_id": user_id, "count": len(prioritized_recommendations)})
            return prioritized_recommendations

        except Exception as e:
            await self.log_operation("generate_health_recommendations", False, {"error": str(e)})
            return []

    async def _comprehensive_analysis(self, user_id: str, health_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """综合健康分析"""
        analysis = {
            "overall_score": 0.0,
            "category_scores": {},
            "key_findings": [],
            "risk_factors": [],
            "positive_indicators": []
        }

        # 心血管健康分析
        cv_analysis = await self._cardiovascular_analysis(health_data)
        analysis["category_scores"]["cardiovascular"] = cv_analysis.get("score", 0)

        # 代谢健康分析
        metabolic_analysis = await self._metabolic_analysis(health_data)
        analysis["category_scores"]["metabolic"] = metabolic_analysis.get("score", 0)

        # 睡眠质量分析
        sleep_analysis = await self._sleep_analysis(health_data)
        analysis["category_scores"]["sleep"] = sleep_analysis.get("score", 0)

        # 活动水平分析
        activity_analysis = await self._activity_analysis(health_data)
        analysis["category_scores"]["activity"] = activity_analysis.get("score", 0)

        # 计算总体评分
        scores = list(analysis["category_scores"].values())
        analysis["overall_score"] = mean(scores) if scores else 0

        # 汇总关键发现
        analysis["key_findings"].extend(cv_analysis.get("findings", []))
        analysis["key_findings"].extend(metabolic_analysis.get("findings", []))
        analysis["key_findings"].extend(sleep_analysis.get("findings", []))
        analysis["key_findings"].extend(activity_analysis.get("findings", []))

        return analysis

    async def _cardiovascular_analysis(self, health_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """心血管健康分析"""
        analysis = {
            "score": 0.0,
            "findings": [],
            "metrics": {}
        }

        # 提取心血管相关指标
        bp_data = self._extract_metric_data(health_data, "blood_pressure")
        hr_data = self._extract_metric_data(health_data, "heart_rate")
        hrv_data = self._extract_metric_data(health_data, "heart_rate_variability")

        score_components = []

        # 血压分析
        if bp_data:
            bp_analysis = self._analyze_blood_pressure(bp_data)
            analysis["metrics"]["blood_pressure"] = bp_analysis
            score_components.append(bp_analysis["score"])
            analysis["findings"].extend(bp_analysis["findings"])

        # 心率分析
        if hr_data:
            hr_analysis = self._analyze_heart_rate(hr_data)
            analysis["metrics"]["heart_rate"] = hr_analysis
            score_components.append(hr_analysis["score"])
            analysis["findings"].extend(hr_analysis["findings"])

        # 心率变异性分析
        if hrv_data:
            hrv_analysis = self._analyze_heart_rate_variability(hrv_data)
            analysis["metrics"]["heart_rate_variability"] = hrv_analysis
            score_components.append(hrv_analysis["score"])
            analysis["findings"].extend(hrv_analysis["findings"])

        # 计算综合评分
        analysis["score"] = mean(score_components) if score_components else 0

        return analysis

    async def _metabolic_analysis(self, health_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """代谢健康分析"""
        analysis = {
            "score": 0.0,
            "findings": [],
            "metrics": {}
        }

        # 提取代谢相关指标
        glucose_data = self._extract_metric_data(health_data, "blood_glucose")
        weight_data = self._extract_metric_data(health_data, "weight")
        bmi_data = self._extract_metric_data(health_data, "bmi")

        score_components = []

        # 血糖分析
        if glucose_data:
            glucose_analysis = self._analyze_blood_glucose(glucose_data)
            analysis["metrics"]["blood_glucose"] = glucose_analysis
            score_components.append(glucose_analysis["score"])
            analysis["findings"].extend(glucose_analysis["findings"])

        # 体重趋势分析
        if weight_data:
            weight_analysis = self._analyze_weight_trend(weight_data)
            analysis["metrics"]["weight"] = weight_analysis
            score_components.append(weight_analysis["score"])
            analysis["findings"].extend(weight_analysis["findings"])

        # BMI分析
        if bmi_data:
            bmi_analysis = self._analyze_bmi(bmi_data)
            analysis["metrics"]["bmi"] = bmi_analysis
            score_components.append(bmi_analysis["score"])
            analysis["findings"].extend(bmi_analysis["findings"])

        # 计算综合评分
        analysis["score"] = mean(score_components) if score_components else 0

        return analysis

    async def _sleep_analysis(self, health_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """睡眠质量分析"""
        analysis = {
            "score": 0.0,
            "findings": [],
            "metrics": {}
        }

        # 提取睡眠相关数据
        sleep_data = self._extract_metric_data(health_data, "sleep_duration")
        sleep_quality_data = self._extract_metric_data(health_data, "sleep_quality")

        score_components = []

        # 睡眠时长分析
        if sleep_data:
            duration_analysis = self._analyze_sleep_duration(sleep_data)
            analysis["metrics"]["duration"] = duration_analysis
            score_components.append(duration_analysis["score"])
            analysis["findings"].extend(duration_analysis["findings"])

        # 睡眠质量分析
        if sleep_quality_data:
            quality_analysis = self._analyze_sleep_quality(sleep_quality_data)
            analysis["metrics"]["quality"] = quality_analysis
            score_components.append(quality_analysis["score"])
            analysis["findings"].extend(quality_analysis["findings"])

        # 计算综合评分
        analysis["score"] = mean(score_components) if score_components else 0

        return analysis

    def _validate_health_data(self, data: HealthData) -> HealthData:
        """验证和清洗健康数据"""
        # 基本范围检查
        if data.heart_rate and (data.heart_rate < 30 or data.heart_rate > 220):
            data.heart_rate = None
        
        if data.blood_pressure_systolic and (data.blood_pressure_systolic < 70 or data.blood_pressure_systolic > 250):
            data.blood_pressure_systolic = None
            
        if data.blood_pressure_diastolic and (data.blood_pressure_diastolic < 40 or data.blood_pressure_diastolic > 150):
            data.blood_pressure_diastolic = None

        if data.weight and (data.weight < 20 or data.weight > 300):
            data.weight = None

        if data.sleep_duration and (data.sleep_duration < 0 or data.sleep_duration > 24):
            data.sleep_duration = None

        return data

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        status = {
            "service": "HealthService",
            "status": "healthy",
            "mongodb_connected": self.mongodb is not None,
            "redis_connected": self.redis is not None
        }

        # 测试数据库连接
        if self.mongodb:
            try:
                await self.mongodb.command("ping")
                status["mongodb_ping"] = True
            except Exception:
                status["mongodb_ping"] = False
                status["status"] = "degraded"

        return status