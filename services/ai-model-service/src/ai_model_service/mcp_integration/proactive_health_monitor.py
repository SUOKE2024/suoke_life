"""
主动健康干预系统
实现基于MCP理念的持续健康监控和风险评估
支持主动感知用户健康状态变化并提供及时干预
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import json
import numpy as np
from collections import defaultdict, deque
import uuid

logger = logging.getLogger(__name__)

class HealthRiskLevel(Enum):
    """健康风险等级"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

class InterventionType(Enum):
    """干预类型"""
    LIFESTYLE_ADJUSTMENT = "lifestyle_adjustment"
    MEDICAL_CONSULTATION = "medical_consultation"
    EMERGENCY_RESPONSE = "emergency_response"
    PREVENTIVE_CARE = "preventive_care"
    MENTAL_HEALTH_SUPPORT = "mental_health_support"

class MonitoringMode(Enum):
    """监控模式"""
    CONTINUOUS = "continuous"
    PERIODIC = "periodic"
    EVENT_DRIVEN = "event_driven"
    ADAPTIVE = "adaptive"

@dataclass
class HealthMetric:
    """健康指标"""
    metric_name: str
    value: Union[float, int, str]
    unit: str
    timestamp: datetime
    source_device: str
    quality_score: float
    normal_range: Tuple[float, float]
    
    def is_abnormal(self) -> bool:
        """判断是否异常"""
        if isinstance(self.value, (int, float)):
            return not (self.normal_range[0]<=self.value<=self.normal_range[1])
        return False
        
    def get_deviation_score(self) -> float:
        """获取偏离正常值的程度"""
        if not isinstance(self.value, (int, float)):
            return 0.0
            
        min_val, max_val = self.normal_range
        if self.value < min_val:
            return (min_val - self.value) / (max_val - min_val)
        elif self.value > max_val:
            return (self.value - max_val) / (max_val - min_val)
        else:
            return 0.0

@dataclass
class HealthPattern:
    """健康模式"""
    pattern_id: str
    pattern_type: str
    description: str
    indicators: List[str]
    risk_factors: List[str]
    confidence_score: float
    detected_at: datetime
    
@dataclass
class RiskAssessment:
    """风险评估"""
    assessment_id: str
    user_id: str
    risk_level: HealthRiskLevel
    risk_score: float
    risk_factors: List[Dict[str, Any]]
    affected_systems: List[str]
    predicted_outcomes: List[Dict[str, Any]]
    confidence_score: float
    assessment_time: datetime
    valid_until: datetime
    
@dataclass
class HealthIntervention:
    """健康干预"""
    intervention_id: str
    user_id: str
    intervention_type: InterventionType
    priority: str
    title: str
    description: str
    recommended_actions: List[Dict[str, Any]]
    expected_outcomes: List[str]
    timeline: Dict[str, Any]
    created_at: datetime
    status: str = "pending"
    
class HealthDataProcessor:
    """健康数据处理器"""
    
    def __init__(self):
        self.metric_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.pattern_detectors: Dict[str, Any] = {}
        self.baseline_profiles: Dict[str, Dict[str, Any]] = {}
        
    async def process_health_data(self, user_id: str, metrics: List[HealthMetric]) -> Dict[str, Any]:
        """处理健康数据"""
        processed_data = {
            "user_id": user_id,
            "timestamp": datetime.utcnow(),
            "metrics_processed": len(metrics),
            "anomalies": [],
            "patterns": [],
            "trends": {}
        }
        
        for metric in metrics:
            # 存储历史数据
            self.metric_history[f"{user_id}_{metric.metric_name}"].append(metric)
            
            # 检测异常
            if metric.is_abnormal():
                anomaly = {
                    "metric_name": metric.metric_name,
                    "value": metric.value,
                    "normal_range": metric.normal_range,
                    "deviation_score": metric.get_deviation_score(),
                    "timestamp": metric.timestamp.isoformat()
                }
                processed_data["anomalies"].append(anomaly)
                
        # 检测模式
        patterns = await self._detect_patterns(user_id, metrics)
        processed_data["patterns"] = patterns
        
        # 分析趋势
        trends = await self._analyze_trends(user_id)
        processed_data["trends"] = trends
        
        return processed_data
        
    async def _detect_patterns(self, user_id: str, metrics: List[HealthMetric]) -> List[HealthPattern]:
        """检测健康模式"""
        patterns = []
        
        # 检测心率变异性模式
        heart_rate_metrics = [m for m in metrics if m.metric_name=="heart_rate"]
        if len(heart_rate_metrics)>=5:
            pattern = await self._detect_heart_rate_pattern(user_id, heart_rate_metrics)
            if pattern:
                patterns.append(pattern)
                
        # 检测睡眠模式
        sleep_metrics = [m for m in metrics if "sleep" in m.metric_name]
        if sleep_metrics:
            pattern = await self._detect_sleep_pattern(user_id, sleep_metrics)
            if pattern:
                patterns.append(pattern)
                
        # 检测活动模式
        activity_metrics = [m for m in metrics if m.metric_name in ["steps", "calories", "distance"]]
        if activity_metrics:
            pattern = await self._detect_activity_pattern(user_id, activity_metrics)
            if pattern:
                patterns.append(pattern)
                
        return patterns
        
    async def _detect_heart_rate_pattern(self, user_id: str, metrics: List[HealthMetric]) -> Optional[HealthPattern]:
        """检测心率模式"""
        values = [m.value for m in metrics if isinstance(m.value, (int, float))]
        if len(values) < 5:
            return None
            
        # 计算心率变异性
        hrv = np.std(values)
        mean_hr = np.mean(values)
        
        # 检测异常模式
        if hrv > 15 and mean_hr > 100:
            return HealthPattern(
                pattern_id=str(uuid.uuid4()),
                pattern_type="heart_rate_stress",
                description="检测到心率异常升高和变异性增大，可能存在压力或健康问题",
                indicators=["高心率变异性", "心率偏高"],
                risk_factors=["压力", "心血管疾病风险"],
                confidence_score=0.8,
                detected_at=datetime.utcnow()
            )
            
        return None
        
    async def _detect_sleep_pattern(self, user_id: str, metrics: List[HealthMetric]) -> Optional[HealthPattern]:
        """检测睡眠模式"""
        sleep_duration_metrics = [m for m in metrics if m.metric_name=="sleep_duration"]
        sleep_quality_metrics = [m for m in metrics if m.metric_name=="sleep_quality"]
        
        if not sleep_duration_metrics:
            return None
            
        # 分析睡眠时长
        durations = [m.value for m in sleep_duration_metrics if isinstance(m.value, (int, float))]
        if durations:
            avg_duration = np.mean(durations)
            if avg_duration < 6:  # 少于6小时
                return HealthPattern(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type="sleep_deprivation",
                    description="检测到睡眠不足模式，平均睡眠时间少于6小时",
                    indicators=["睡眠时间不足"],
                    risk_factors=["免疫力下降", "认知功能影响", "心血管风险"],
                    confidence_score=0.9,
                    detected_at=datetime.utcnow()
                )
                
        return None
        
    async def _detect_activity_pattern(self, user_id: str, metrics: List[HealthMetric]) -> Optional[HealthPattern]:
        """检测活动模式"""
        steps_metrics = [m for m in metrics if m.metric_name=="steps"]
        
        if not steps_metrics:
            return None
            
        # 分析步数
        steps = [m.value for m in steps_metrics if isinstance(m.value, (int, float))]
        if steps:
            avg_steps = np.mean(steps)
            if avg_steps < 5000:  # 少于5000步
                return HealthPattern(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type="sedentary_lifestyle",
                    description="检测到久坐生活方式，日均步数少于5000步",
                    indicators=["活动量不足"],
                    risk_factors=["肥胖风险", "心血管疾病", "糖尿病风险"],
                    confidence_score=0.85,
                    detected_at=datetime.utcnow()
                )
                
        return None
        
    async def _analyze_trends(self, user_id: str) -> Dict[str, Any]:
        """分析健康趋势"""
        trends = {}
        
        # 分析各指标的趋势
        for key, history in self.metric_history.items():
            if not key.startswith(user_id):
                continue
                
            metric_name = key.split("_", 1)[1]
            if len(history)>=7:  # 至少7个数据点
                values = [m.value for m in list(history)[-7:] if isinstance(m.value, (int, float))]
                if len(values)>=5:
                    # 计算趋势
                    x = np.arange(len(values))
                    slope = np.polyfit(x, values, 1)[0]
                    
                    trend_direction = "stable"
                    if slope > 0.1:
                        trend_direction = "increasing"
                    elif slope < -0.1:
                        trend_direction = "decreasing"
                        
                    trends[metric_name] = {
                        "direction": trend_direction,
                        "slope": float(slope),
                        "recent_average": float(np.mean(values)),
                        "data_points": len(values)
                    }
                    
        return trends

class RiskAssessmentEngine:
    """风险评估引擎"""
    
    def __init__(self):
        self.risk_models: Dict[str, Any] = {}
        self.assessment_history: List[RiskAssessment] = []
        self._initialize_risk_models()
        
    def _initialize_risk_models(self):
        """初始化风险模型"""
        self.risk_models = {
            "cardiovascular": {
                "weight_factors": {
                    "heart_rate": 0.3,
                    "blood_pressure": 0.4,
                    "cholesterol": 0.2,
                    "activity_level": 0.1
                },
                "risk_thresholds": {
                    "low": 0.3,
                    "moderate": 0.6,
                    "high": 0.8
                }
            },
            "diabetes": {
                "weight_factors": {
                    "blood_glucose": 0.4,
                    "bmi": 0.3,
                    "activity_level": 0.2,
                    "family_history": 0.1
                },
                "risk_thresholds": {
                    "low": 0.25,
                    "moderate": 0.5,
                    "high": 0.75
                }
            },
            "mental_health": {
                "weight_factors": {
                    "sleep_quality": 0.3,
                    "stress_level": 0.4,
                    "social_interaction": 0.2,
                    "physical_activity": 0.1
                },
                "risk_thresholds": {
                    "low": 0.3,
                    "moderate": 0.6,
                    "high": 0.8
                }
            }
        }
        
    async def assess_health_risks(self, user_id: str, health_data: Dict[str, Any], 
                                patterns: List[HealthPattern]) -> List[RiskAssessment]:
        """评估健康风险"""
        assessments = []
        
        # 评估各类风险
        for risk_type, model in self.risk_models.items():
            assessment = await self._assess_specific_risk(user_id, risk_type, model, health_data, patterns)
            if assessment:
                assessments.append(assessment)
                
        # 保存评估历史
        self.assessment_history.extend(assessments)
        
        return assessments
        
    async def _assess_specific_risk(self, user_id: str, risk_type: str, model: Dict[str, Any],
                                  health_data: Dict[str, Any], patterns: List[HealthPattern]) -> Optional[RiskAssessment]:
        """评估特定类型的风险"""
        risk_score = 0.0
        risk_factors = []
        confidence_score = 0.0
        
        # 基于健康数据计算风险分数
        weight_factors = model["weight_factors"]
        available_factors = 0
        
        for factor, weight in weight_factors.items():
            factor_score = await self._get_factor_score(factor, health_data, patterns)
            if factor_score is not None:
                risk_score+=factor_score * weight
                available_factors+=1
                
                if factor_score > 0.6:  # 高风险因子
                    risk_factors.append({
                        "factor": factor,
                        "score": factor_score,
                        "description": self._get_factor_description(factor, factor_score)
                    })
                    
        if available_factors==0:
            return None
            
        # 调整风险分数
        risk_score = risk_score * (available_factors / len(weight_factors))
        confidence_score = available_factors / len(weight_factors)
        
        # 确定风险等级
        thresholds = model["risk_thresholds"]
        if risk_score>=thresholds["high"]:
            risk_level = HealthRiskLevel.HIGH
        elif risk_score>=thresholds["moderate"]:
            risk_level = HealthRiskLevel.MODERATE
        else:
            risk_level = HealthRiskLevel.LOW
            
        # 预测结果
        predicted_outcomes = await self._predict_outcomes(risk_type, risk_score, risk_factors)
        
        return RiskAssessment(
            assessment_id=str(uuid.uuid4()),
            user_id=user_id,
            risk_level=risk_level,
            risk_score=risk_score,
            risk_factors=risk_factors,
            affected_systems=[risk_type],
            predicted_outcomes=predicted_outcomes,
            confidence_score=confidence_score,
            assessment_time=datetime.utcnow(),
            valid_until=datetime.utcnow() + timedelta(hours=24)
        )
        
    async def _get_factor_score(self, factor: str, health_data: Dict[str, Any], 
                              patterns: List[HealthPattern]) -> Optional[float]:
        """获取风险因子分数"""
        # 从健康数据中获取指标
        trends = health_data.get("trends", {})
        anomalies = health_data.get("anomalies", [])
        
        # 基础分数
        base_score = 0.0
        
        # 检查异常
        for anomaly in anomalies:
            if factor in anomaly["metric_name"]:
                base_score+=anomaly["deviation_score"] * 0.3
                
        # 检查趋势
        if factor in trends:
            trend = trends[factor]
            if trend["direction"]=="increasing" and factor in ["heart_rate", "blood_pressure", "stress_level"]:
                base_score+=abs(trend["slope"]) * 0.2
            elif trend["direction"]=="decreasing" and factor in ["activity_level", "sleep_quality"]:
                base_score+=abs(trend["slope"]) * 0.2
                
        # 检查模式
        for pattern in patterns:
            if factor in pattern.indicators or factor in pattern.risk_factors:
                base_score+=pattern.confidence_score * 0.3
                
        return min(base_score, 1.0)  # 限制在0-1范围内
        
    def _get_factor_description(self, factor: str, score: float) -> str:
        """获取风险因子描述"""
        descriptions = {
            "heart_rate": f"心率异常，风险分数: {score:.2f}",
            "blood_pressure": f"血压偏高，风险分数: {score:.2f}",
            "sleep_quality": f"睡眠质量下降，风险分数: {score:.2f}",
            "stress_level": f"压力水平升高，风险分数: {score:.2f}",
            "activity_level": f"活动量不足，风险分数: {score:.2f}",
            "bmi": f"体重指数异常，风险分数: {score:.2f}"
        }
        return descriptions.get(factor, f"{factor}异常，风险分数: {score:.2f}")
        
    async def _predict_outcomes(self, risk_type: str, risk_score: float, 
                              risk_factors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """预测健康结果"""
        outcomes = []
        
        if risk_type=="cardiovascular":
            if risk_score > 0.8:
                outcomes.append({
                    "outcome": "心血管事件风险",
                    "probability": risk_score,
                    "timeframe": "6个月内",
                    "severity": "高"
                })
            elif risk_score > 0.6:
                outcomes.append({
                    "outcome": "心血管健康恶化",
                    "probability": risk_score,
                    "timeframe": "1年内",
                    "severity": "中等"
                })
                
        elif risk_type=="diabetes":
            if risk_score > 0.7:
                outcomes.append({
                    "outcome": "糖尿病前期或糖尿病",
                    "probability": risk_score,
                    "timeframe": "1年内",
                    "severity": "高"
                })
                
        elif risk_type=="mental_health":
            if risk_score > 0.6:
                outcomes.append({
                    "outcome": "心理健康问题",
                    "probability": risk_score,
                    "timeframe": "3个月内",
                    "severity": "中等"
                })
                
        return outcomes

class InterventionEngine:
    """干预引擎"""
    
    def __init__(self):
        self.intervention_templates: Dict[str, Dict[str, Any]] = {}
        self.active_interventions: Dict[str, List[HealthIntervention]] = defaultdict(list)
        self._initialize_intervention_templates()
        
    def _initialize_intervention_templates(self):
        """初始化干预模板"""
        self.intervention_templates = {
            "cardiovascular_high_risk": {
                "type": InterventionType.MEDICAL_CONSULTATION,
                "priority": "high",
                "title": "心血管高风险预警",
                "description": "检测到心血管疾病高风险，建议立即咨询医生",
                "actions": [
                    {"action": "预约心血管专科医生", "urgency": "immediate"},
                    {"action": "进行心电图检查", "urgency": "within_24h"},
                    {"action": "监测血压和心率", "urgency": "daily"},
                    {"action": "调整饮食和运动", "urgency": "immediate"}
                ],
                "timeline": {"immediate": "立即", "follow_up": "1周后复查"}
            },
            "sleep_deprivation": {
                "type": InterventionType.LIFESTYLE_ADJUSTMENT,
                "priority": "medium",
                "title": "睡眠不足干预",
                "description": "检测到睡眠不足模式，建议调整睡眠习惯",
                "actions": [
                    {"action": "建立规律睡眠时间", "urgency": "today"},
                    {"action": "优化睡眠环境", "urgency": "within_week"},
                    {"action": "减少睡前屏幕时间", "urgency": "today"},
                    {"action": "考虑睡眠监测", "urgency": "within_week"}
                ],
                "timeline": {"start": "今天开始", "evaluation": "2周后评估"}
            },
            "sedentary_lifestyle": {
                "type": InterventionType.LIFESTYLE_ADJUSTMENT,
                "priority": "medium",
                "title": "久坐生活方式改善",
                "description": "检测到活动量不足，建议增加日常活动",
                "actions": [
                    {"action": "设定每日步数目标", "urgency": "today"},
                    {"action": "每小时起身活动", "urgency": "immediate"},
                    {"action": "选择喜欢的运动", "urgency": "within_week"},
                    {"action": "使用活动提醒", "urgency": "today"}
                ],
                "timeline": {"start": "立即开始", "goal": "4周内达到目标"}
            },
            "stress_management": {
                "type": InterventionType.MENTAL_HEALTH_SUPPORT,
                "priority": "medium",
                "title": "压力管理支持",
                "description": "检测到压力水平升高，建议进行压力管理",
                "actions": [
                    {"action": "学习放松技巧", "urgency": "today"},
                    {"action": "安排休息时间", "urgency": "daily"},
                    {"action": "考虑心理咨询", "urgency": "within_week"},
                    {"action": "改善工作生活平衡", "urgency": "ongoing"}
                ],
                "timeline": {"immediate": "立即开始", "support": "持续支持"}
            }
        }
        
    async def generate_interventions(self, user_id: str, risk_assessments: List[RiskAssessment],
                                   patterns: List[HealthPattern]) -> List[HealthIntervention]:
        """生成健康干预建议"""
        interventions = []
        
        # 基于风险评估生成干预
        for assessment in risk_assessments:
            intervention = await self._generate_risk_based_intervention(user_id, assessment)
            if intervention:
                interventions.append(intervention)
                
        # 基于健康模式生成干预
        for pattern in patterns:
            intervention = await self._generate_pattern_based_intervention(user_id, pattern)
            if intervention:
                interventions.append(intervention)
                
        # 保存活跃干预
        self.active_interventions[user_id].extend(interventions)
        
        return interventions
        
    async def _generate_risk_based_intervention(self, user_id: str, 
                                             assessment: RiskAssessment) -> Optional[HealthIntervention]:
        """基于风险评估生成干预"""
        if assessment.risk_level==HealthRiskLevel.HIGH:
            # 高风险需要医疗干预
            template_key = f"{assessment.affected_systems[0]}_high_risk"
            template = self.intervention_templates.get(template_key)
            
            if template:
                return HealthIntervention(
                    intervention_id=str(uuid.uuid4()),
                    user_id=user_id,
                    intervention_type=template["type"],
                    priority=template["priority"],
                    title=template["title"],
                    description=template["description"],
                    recommended_actions=template["actions"],
                    expected_outcomes=[f"降低{assessment.affected_systems[0]}风险"],
                    timeline=template["timeline"],
                    created_at=datetime.utcnow()
                )
                
        return None
        
    async def _generate_pattern_based_intervention(self, user_id: str, 
                                                 pattern: HealthPattern) -> Optional[HealthIntervention]:
        """基于健康模式生成干预"""
        template = self.intervention_templates.get(pattern.pattern_type)
        
        if template:
            return HealthIntervention(
                intervention_id=str(uuid.uuid4()),
                user_id=user_id,
                intervention_type=template["type"],
                priority=template["priority"],
                title=template["title"],
                description=template["description"],
                recommended_actions=template["actions"],
                expected_outcomes=[f"改善{pattern.pattern_type}模式"],
                timeline=template["timeline"],
                created_at=datetime.utcnow()
            )
            
        return None

class ProactiveHealthMonitor:
    """主动健康监控器"""
    
    def __init__(self):
        self.data_processor = HealthDataProcessor()
        self.risk_engine = RiskAssessmentEngine()
        self.intervention_engine = InterventionEngine()
        self.monitoring_sessions: Dict[str, Dict[str, Any]] = {}
        self.alert_thresholds: Dict[str, float] = {
            "critical_risk": 0.9,
            "high_risk": 0.7,
            "pattern_confidence": 0.8
        }
        
    async def start_monitoring(self, user_id: str, monitoring_mode: MonitoringMode = MonitoringMode.ADAPTIVE,
                             custom_config: Dict[str, Any] = None) -> str:
        """开始健康监控"""
        session_id = f"monitor_{user_id}_{int(datetime.utcnow().timestamp())}"
        
        session_config = {
            "session_id": session_id,
            "user_id": user_id,
            "monitoring_mode": monitoring_mode,
            "start_time": datetime.utcnow(),
            "status": "active",
            "config": custom_config or {},
            "last_assessment": None,
            "alert_count": 0
        }
        
        self.monitoring_sessions[session_id] = session_config
        
        # 启动监控任务
        asyncio.create_task(self._monitoring_loop(session_id))
        
        logger.info(f"开始健康监控: {session_id}, 模式: {monitoring_mode.value}")
        
        return session_id
        
    async def _monitoring_loop(self, session_id: str):
        """监控循环"""
        session = self.monitoring_sessions.get(session_id)
        if not session:
            return
            
        try:
            while session["status"]=="active":
                # 获取健康数据
                health_metrics = await self._collect_health_data(session["user_id"])
                
                if health_metrics:
                    # 处理健康数据
                    processed_data = await self.data_processor.process_health_data(
                        session["user_id"], health_metrics
                    )
                    
                    # 评估风险
                    patterns = processed_data.get("patterns", [])
                    risk_assessments = await self.risk_engine.assess_health_risks(
                        session["user_id"], processed_data, patterns
                    )
                    
                    # 检查是否需要干预
                    if await self._should_intervene(risk_assessments, patterns):
                        interventions = await self.intervention_engine.generate_interventions(
                            session["user_id"], risk_assessments, patterns
                        )
                        
                        # 发送干预建议
                        await self._send_interventions(session["user_id"], interventions)
                        session["alert_count"]+=len(interventions)
                        
                    session["last_assessment"] = datetime.utcnow()
                    
                # 根据监控模式确定下次检查间隔
                interval = self._get_monitoring_interval(session["monitoring_mode"])
                await asyncio.sleep(interval)
                
        except Exception as e:
            logger.error(f"监控循环异常: {session_id}, {str(e)}")
            session["status"] = "error"
            
    async def _collect_health_data(self, user_id: str) -> List[HealthMetric]:
        """收集健康数据"""
        # 模拟从各种设备收集健康数据
        current_time = datetime.utcnow()
        
        # 模拟数据
        metrics = [
            HealthMetric(
                metric_name="heart_rate",
                value=72 + np.random.normal(0, 5),
                unit="bpm",
                timestamp=current_time,
                source_device="apple_watch",
                quality_score=0.95,
                normal_range=(60, 100)
            ),
            HealthMetric(
                metric_name="steps",
                value=int(8000 + np.random.normal(0, 2000)),
                unit="steps",
                timestamp=current_time,
                source_device="smartphone",
                quality_score=0.9,
                normal_range=(5000, 15000)
            ),
            HealthMetric(
                metric_name="sleep_duration",
                value=7.5 + np.random.normal(0, 1),
                unit="hours",
                timestamp=current_time - timedelta(hours=8),
                source_device="fitbit",
                quality_score=0.85,
                normal_range=(7, 9)
            )
        ]
        
        return metrics
        
    async def _should_intervene(self, risk_assessments: List[RiskAssessment], 
                              patterns: List[HealthPattern]) -> bool:
        """判断是否需要干预"""
        # 检查高风险评估
        for assessment in risk_assessments:
            if assessment.risk_level in [HealthRiskLevel.HIGH, HealthRiskLevel.CRITICAL]:
                return True
            if assessment.risk_score>=self.alert_thresholds["high_risk"]:
                return True
                
        # 检查高置信度模式
        for pattern in patterns:
            if pattern.confidence_score>=self.alert_thresholds["pattern_confidence"]:
                return True
                
        return False
        
    async def _send_interventions(self, user_id: str, interventions: List[HealthIntervention]):
        """发送干预建议"""
        for intervention in interventions:
            # 模拟发送通知
            logger.info(f"发送干预建议给用户 {user_id}: {intervention.title}")
            
            # 这里可以集成实际的通知系统
            # await notification_service.send_health_alert(user_id, intervention)
            
    def _get_monitoring_interval(self, mode: MonitoringMode) -> int:
        """获取监控间隔（秒）"""
        intervals = {
            MonitoringMode.CONTINUOUS: 60,      # 1分钟
            MonitoringMode.PERIODIC: 3600,     # 1小时
            MonitoringMode.EVENT_DRIVEN: 300,  # 5分钟
            MonitoringMode.ADAPTIVE: 1800       # 30分钟
        }
        return intervals.get(mode, 1800)
        
    async def get_monitoring_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取监控状态"""
        session = self.monitoring_sessions.get(session_id)
        if not session:
            return None
            
        return {
            "session_id": session_id,
            "user_id": session["user_id"],
            "status": session["status"],
            "monitoring_mode": session["monitoring_mode"].value,
            "start_time": session["start_time"].isoformat(),
            "last_assessment": session["last_assessment"].isoformat() if session["last_assessment"] else None,
            "alert_count": session["alert_count"],
            "uptime": (datetime.utcnow() - session["start_time"]).total_seconds()
        }
        
    async def stop_monitoring(self, session_id: str) -> bool:
        """停止监控"""
        session = self.monitoring_sessions.get(session_id)
        if not session:
            return False
            
        session["status"] = "stopped"
        session["end_time"] = datetime.utcnow()
        
        logger.info(f"停止健康监控: {session_id}")
        return True
        
    async def get_health_summary(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """获取健康摘要"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        # 获取风险评估历史
        user_assessments = [
            a for a in self.risk_engine.assessment_history
            if a.user_id==user_id and start_time<=a.assessment_time<=end_time
        ]
        
        # 获取干预历史
        user_interventions = self.intervention_engine.active_interventions.get(user_id, [])
        recent_interventions = [
            i for i in user_interventions
            if start_time<=i.created_at<=end_time
        ]
        
        # 统计分析
        risk_distribution = defaultdict(int)
        for assessment in user_assessments:
            risk_distribution[assessment.risk_level.value]+=1
            
        intervention_types = defaultdict(int)
        for intervention in recent_interventions:
            intervention_types[intervention.intervention_type.value]+=1
            
        summary = {
            "user_id": user_id,
            "period": f"{days}天",
            "start_date": start_time.isoformat(),
            "end_date": end_time.isoformat(),
            "risk_assessments": {
                "total": len(user_assessments),
                "distribution": dict(risk_distribution),
                "latest_risk_level": user_assessments[-1].risk_level.value if user_assessments else "unknown"
            },
            "interventions": {
                "total": len(recent_interventions),
                "types": dict(intervention_types),
                "pending": len([i for i in recent_interventions if i.status=="pending"])
            },
            "health_trends": {
                "improving": len([a for a in user_assessments if a.risk_level==HealthRiskLevel.LOW]),
                "stable": len([a for a in user_assessments if a.risk_level==HealthRiskLevel.MODERATE]),
                "concerning": len([a for a in user_assessments if a.risk_level in [HealthRiskLevel.HIGH, HealthRiskLevel.CRITICAL]])
            }
        }
        
        return summary 