"""
health_data_analyzer - 索克生活项目模块
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from loguru import logger
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Any, Optional, Tuple, Union
import statistics

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
健康数据分析器 - 提供全面的健康数据分析和个性化建议
"""


class HealthDataType(Enum):
    """健康数据类型"""
    VITAL_SIGNS = "vital_signs"          # 生命体征
    SYMPTOMS = "symptoms"                # 症状
    LIFESTYLE = "lifestyle"              # 生活方式
    MEDICAL_HISTORY = "medical_history"  # 病史
    LAB_RESULTS = "lab_results"          # 检验结果
    BIOMETRIC = "biometric"              # 生物测量
    MENTAL_HEALTH = "mental_health"      # 心理健康
    NUTRITION = "nutrition"              # 营养
    EXERCISE = "exercise"                # 运动
    SLEEP = "sleep"                      # 睡眠

class RiskLevel(Enum):
    """风险等级"""
    LOW = "low"          # 低风险
    MODERATE = "moderate" # 中等风险
    HIGH = "high"        # 高风险
    CRITICAL = "critical" # 危急

class TrendDirection(Enum):
    """趋势方向"""
    IMPROVING = "improving"    # 改善
    STABLE = "stable"         # 稳定
    DECLINING = "declining"   # 恶化
    FLUCTUATING = "fluctuating" # 波动

@dataclass
class HealthMetric:
    """健康指标"""
    name: str
    value: Union[float, int, str]
    unit: str
    timestamp: datetime
    reference_range: Optional[Tuple[float, float]] = None
    category: Optional[str] = None
    source: Optional[str] = None

@dataclass
class HealthTrend:
    """健康趋势"""
    metric_name: str
    direction: TrendDirection
    change_rate: float
    confidence: float
    time_period: timedelta
    significant_changes: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class RiskAssessment:
    """风险评估"""
    risk_factor: str
    risk_level: RiskLevel
    probability: float
    contributing_factors: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    time_horizon: Optional[str] = None

@dataclass
class HealthInsight:
    """健康洞察"""
    title: str
    description: str
    category: str
    importance: int  # 1-5级重要性
    actionable: bool
    recommendations: List[str] = field(default_factory=list)
    related_metrics: List[str] = field(default_factory=list)

@dataclass
class HealthReport:
    """健康报告"""
    user_id: str
    report_date: datetime
    overall_score: float
    risk_assessments: List[RiskAssessment] = field(default_factory=list)
    trends: List[HealthTrend] = field(default_factory=list)
    insights: List[HealthInsight] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    next_checkup_date: Optional[datetime] = None
    summary: Optional[str] = None

class HealthDataAnalyzer:
    """健康数据分析器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化健康数据分析器
        
        Args:
            config: 配置信息
        """
        self.config = config
        
        # 参考范围定义
        self.reference_ranges = self._load_reference_ranges()
        
        # 风险因子权重
        self.risk_weights = self._load_risk_weights()
        
        # 中医体质分析器
        self.constitution_analyzer = self._init_constitution_analyzer()
        
        # 异常检测器
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        
        # 聚类分析器
        self.cluster_analyzer = KMeans(n_clusters=5, random_state=42)
        
        # 数据标准化器
        self.scaler = StandardScaler()
    
    def _load_reference_ranges(self) -> Dict[str, Dict[str, Any]]:
        """加载参考范围"""
        return {
            "blood_pressure_systolic": {
                "normal": (90, 120),
                "elevated": (120, 129),
                "high_stage1": (130, 139),
                "high_stage2": (140, 180),
                "crisis": (180, float('inf'))
            },
            "blood_pressure_diastolic": {
                "normal": (60, 80),
                "elevated": (80, 89),
                "high_stage1": (90, 99),
                "high_stage2": (100, 120),
                "crisis": (120, float('inf'))
            },
            "heart_rate": {
                "bradycardia": (0, 60),
                "normal": (60, 100),
                "tachycardia": (100, float('inf'))
            },
            "body_temperature": {
                "hypothermia": (0, 36.0),
                "normal": (36.0, 37.5),
                "fever": (37.5, 40.0),
                "hyperthermia": (40.0, float('inf'))
            },
            "bmi": {
                "underweight": (0, 18.5),
                "normal": (18.5, 24.9),
                "overweight": (25.0, 29.9),
                "obese": (30.0, float('inf'))
            },
            "blood_glucose": {
                "hypoglycemia": (0, 3.9),
                "normal": (3.9, 6.1),
                "prediabetes": (6.1, 7.0),
                "diabetes": (7.0, float('inf'))
            }
        }
    
    def _load_risk_weights(self) -> Dict[str, float]:
        """加载风险因子权重"""
        return {
            "age": 0.15,
            "gender": 0.05,
            "family_history": 0.20,
            "smoking": 0.15,
            "alcohol": 0.10,
            "exercise": 0.10,
            "diet": 0.10,
            "stress": 0.08,
            "sleep": 0.07
        }
    
    def _init_constitution_analyzer(self) -> Dict[str, Any]:
        """初始化中医体质分析器"""
        return {
            "constitution_types": [
                "平和质", "气虚质", "阳虚质", "阴虚质", "痰湿质",
                "湿热质", "血瘀质", "气郁质", "特禀质"
            ],
            "symptom_mapping": {
                "气虚质": ["乏力", "气短", "容易疲劳", "声音低微"],
                "阳虚质": ["怕冷", "手脚冰凉", "精神不振", "面色苍白"],
                "阴虚质": ["口干", "盗汗", "五心烦热", "失眠"],
                "痰湿质": ["身体沉重", "胸闷", "痰多", "容易困倦"],
                "湿热质": ["面部油腻", "口苦", "身体困重", "小便黄"],
                "血瘀质": ["面色晦暗", "皮肤粗糙", "容易健忘", "舌质紫暗"],
                "气郁质": ["情绪不稳定", "胸闷", "叹气", "咽部异物感"],
                "特禀质": ["过敏体质", "鼻塞", "喷嚏", "皮肤过敏"]
            }
        }
    
    async def analyze_health_data(
        self,
        user_id: str,
        health_data: List[HealthMetric],
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> HealthReport:
        """
        分析健康数据，生成健康报告
        
        Args:
            user_id: 用户ID
            health_data: 健康数据列表
            time_range: 时间范围
            
        Returns:
            健康报告
        """
        logger.info(f"Analyzing health data for user: {user_id}")
        
        # 数据预处理
        processed_data = await self._preprocess_data(health_data, time_range)
        
        # 计算整体健康评分
        overall_score = await self._calculate_overall_score(processed_data)
        
        # 风险评估
        risk_assessments = await self._assess_risks(processed_data)
        
        # 趋势分析
        trends = await self._analyze_trends(processed_data)
        
        # 生成洞察
        insights = await self._generate_insights(processed_data, risk_assessments, trends)
        
        # 生成建议
        recommendations = await self._generate_recommendations(
            processed_data, risk_assessments, insights
        )
        
        # 预测下次检查时间
        next_checkup_date = await self._predict_next_checkup(risk_assessments)
        
        # 生成摘要
        summary = await self._generate_summary(
            overall_score, risk_assessments, trends, insights
        )
        
        report = HealthReport(
            user_id=user_id,
            report_date=datetime.now(),
            overall_score=overall_score,
            risk_assessments=risk_assessments,
            trends=trends,
            insights=insights,
            recommendations=recommendations,
            next_checkup_date=next_checkup_date,
            summary=summary
        )
        
        logger.info(f"Health analysis completed for user: {user_id}")
        return report
    
    async def _preprocess_data(
        self,
        health_data: List[HealthMetric],
        time_range: Optional[Tuple[datetime, datetime]]
    ) -> Dict[str, List[HealthMetric]]:
        """数据预处理"""
        # 按时间范围过滤
        if time_range:
            start_time, end_time = time_range
            health_data = [
                metric for metric in health_data
                if start_time <= metric.timestamp <= end_time
            ]
        
        # 按类型分组
        grouped_data = {}
        for metric in health_data:
            category = metric.category or "general"
            if category not in grouped_data:
                grouped_data[category] = []
            grouped_data[category].append(metric)
        
        # 数据清洗和验证
        for category, metrics in grouped_data.items():
            # 去除异常值
            grouped_data[category] = await self._remove_outliers(metrics)
            
            # 按时间排序
            grouped_data[category].sort(key=lambda x: x.timestamp)
        
        return grouped_data
    
    async def _remove_outliers(self, metrics: List[HealthMetric]) -> List[HealthMetric]:
        """移除异常值"""
        if len(metrics) < 3:
            return metrics
        
        # 提取数值型数据
        numeric_values = []
        for metric in metrics:
            if isinstance(metric.value, (int, float)):
                numeric_values.append(metric.value)
        
        if not numeric_values:
            return metrics
        
        # 使用IQR方法检测异常值
        q1 = np.percentile(numeric_values, 25)
        q3 = np.percentile(numeric_values, 75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        # 过滤异常值
        filtered_metrics = []
        for metric in metrics:
            if isinstance(metric.value, (int, float)):
                if lower_bound <= metric.value <= upper_bound:
                    filtered_metrics.append(metric)
            else:
                filtered_metrics.append(metric)
        
        return filtered_metrics
    
    async def _calculate_overall_score(
        self,
        processed_data: Dict[str, List[HealthMetric]]
    ) -> float:
        """计算整体健康评分"""
        total_score = 0.0
        total_weight = 0.0
        
        # 各类别权重
        category_weights = {
            "vital_signs": 0.25,
            "lab_results": 0.20,
            "lifestyle": 0.20,
            "symptoms": 0.15,
            "mental_health": 0.10,
            "exercise": 0.05,
            "nutrition": 0.05
        }
        
        for category, metrics in processed_data.items():
            if not metrics:
                continue
            
            category_score = await self._calculate_category_score(category, metrics)
            weight = category_weights.get(category, 0.1)
            
            total_score += category_score * weight
            total_weight += weight
        
        # 标准化到0-100分
        if total_weight > 0:
            overall_score = (total_score / total_weight) * 100
        else:
            overall_score = 50.0  # 默认分数
        
        return min(max(overall_score, 0.0), 100.0)
    
    async def _calculate_category_score(
        self,
        category: str,
        metrics: List[HealthMetric]
    ) -> float:
        """计算类别评分"""
        if not metrics:
            return 0.5
        
        scores = []
        
        for metric in metrics:
            if isinstance(metric.value, (int, float)):
                score = await self._calculate_metric_score(metric)
                scores.append(score)
        
        if scores:
            return statistics.mean(scores)
        else:
            return 0.5
    
    async def _calculate_metric_score(self, metric: HealthMetric) -> float:
        """计算单个指标评分"""
        if metric.name in self.reference_ranges:
            ranges = self.reference_ranges[metric.name]
            value = float(metric.value)
            
            # 检查在哪个范围内
            if "normal" in ranges:
                normal_min, normal_max = ranges["normal"]
                if normal_min <= value <= normal_max:
                    return 1.0  # 正常范围内得满分
                else:
                    # 计算偏离程度
                    if value < normal_min:
                        deviation = (normal_min - value) / normal_min
                    else:
                        deviation = (value - normal_max) / normal_max
                    
                    # 偏离越大，分数越低
                    score = max(0.0, 1.0 - deviation)
                    return score
        
        # 如果没有参考范围，返回中性分数
        return 0.5
    
    async def _assess_risks(
        self,
        processed_data: Dict[str, List[HealthMetric]]
    ) -> List[RiskAssessment]:
        """风险评估"""
        risk_assessments = []
        
        # 心血管疾病风险
        cvd_risk = await self._assess_cardiovascular_risk(processed_data)
        if cvd_risk:
            risk_assessments.append(cvd_risk)
        
        # 糖尿病风险
        diabetes_risk = await self._assess_diabetes_risk(processed_data)
        if diabetes_risk:
            risk_assessments.append(diabetes_risk)
        
        # 高血压风险
        hypertension_risk = await self._assess_hypertension_risk(processed_data)
        if hypertension_risk:
            risk_assessments.append(hypertension_risk)
        
        # 肥胖风险
        obesity_risk = await self._assess_obesity_risk(processed_data)
        if obesity_risk:
            risk_assessments.append(obesity_risk)
        
        # 中医体质风险
        constitution_risk = await self._assess_constitution_risk(processed_data)
        if constitution_risk:
            risk_assessments.append(constitution_risk)
        
        return risk_assessments
    
    async def _assess_cardiovascular_risk(
        self,
        processed_data: Dict[str, List[HealthMetric]]
    ) -> Optional[RiskAssessment]:
        """评估心血管疾病风险"""
        risk_factors = []
        risk_score = 0.0
        
        # 检查血压
        bp_metrics = self._get_metrics_by_name(processed_data, ["blood_pressure_systolic", "blood_pressure_diastolic"])
        if bp_metrics:
            for metric in bp_metrics:
                if metric.name == "blood_pressure_systolic" and metric.value > 140:
                    risk_factors.append("高血压")
                    risk_score += 0.3
                elif metric.name == "blood_pressure_diastolic" and metric.value > 90:
                    risk_factors.append("舒张压偏高")
                    risk_score += 0.2
        
        # 检查胆固醇
        cholesterol_metrics = self._get_metrics_by_name(processed_data, ["total_cholesterol", "ldl_cholesterol"])
        if cholesterol_metrics:
            for metric in cholesterol_metrics:
                if metric.name == "total_cholesterol" and metric.value > 6.2:
                    risk_factors.append("总胆固醇偏高")
                    risk_score += 0.25
                elif metric.name == "ldl_cholesterol" and metric.value > 4.1:
                    risk_factors.append("低密度脂蛋白偏高")
                    risk_score += 0.3
        
        # 检查生活方式因素
        lifestyle_metrics = self._get_metrics_by_category(processed_data, "lifestyle")
        for metric in lifestyle_metrics:
            if metric.name == "smoking" and metric.value == "yes":
                risk_factors.append("吸烟")
                risk_score += 0.4
            elif metric.name == "exercise_frequency" and metric.value < 3:
                risk_factors.append("运动不足")
                risk_score += 0.2
        
        if risk_score > 0:
            # 确定风险等级
            if risk_score >= 0.8:
                risk_level = RiskLevel.CRITICAL
            elif risk_score >= 0.6:
                risk_level = RiskLevel.HIGH
            elif risk_score >= 0.3:
                risk_level = RiskLevel.MODERATE
            else:
                risk_level = RiskLevel.LOW
            
            recommendations = [
                "定期监测血压和血脂",
                "保持健康饮食，减少饱和脂肪摄入",
                "增加有氧运动，每周至少150分钟",
                "戒烟限酒",
                "控制体重"
            ]
            
            return RiskAssessment(
                risk_factor="心血管疾病",
                risk_level=risk_level,
                probability=min(risk_score, 1.0),
                contributing_factors=risk_factors,
                recommendations=recommendations,
                time_horizon="10年"
            )
        
        return None
    
    async def _assess_diabetes_risk(
        self,
        processed_data: Dict[str, List[HealthMetric]]
    ) -> Optional[RiskAssessment]:
        """评估糖尿病风险"""
        risk_factors = []
        risk_score = 0.0
        
        # 检查血糖
        glucose_metrics = self._get_metrics_by_name(processed_data, ["blood_glucose", "hba1c"])
        if glucose_metrics:
            for metric in glucose_metrics:
                if metric.name == "blood_glucose" and metric.value > 6.1:
                    risk_factors.append("空腹血糖偏高")
                    risk_score += 0.4
                elif metric.name == "hba1c" and metric.value > 6.0:
                    risk_factors.append("糖化血红蛋白偏高")
                    risk_score += 0.5
        
        # 检查BMI
        bmi_metrics = self._get_metrics_by_name(processed_data, ["bmi"])
        if bmi_metrics:
            for metric in bmi_metrics:
                if metric.value > 25:
                    risk_factors.append("超重")
                    risk_score += 0.2
                elif metric.value > 30:
                    risk_factors.append("肥胖")
                    risk_score += 0.3
        
        if risk_score > 0:
            if risk_score >= 0.7:
                risk_level = RiskLevel.HIGH
            elif risk_score >= 0.4:
                risk_level = RiskLevel.MODERATE
            else:
                risk_level = RiskLevel.LOW
            
            recommendations = [
                "定期监测血糖",
                "控制饮食，减少糖分摄入",
                "增加运动量",
                "控制体重",
                "定期体检"
            ]
            
            return RiskAssessment(
                risk_factor="2型糖尿病",
                risk_level=risk_level,
                probability=min(risk_score, 1.0),
                contributing_factors=risk_factors,
                recommendations=recommendations,
                time_horizon="5年"
            )
        
        return None
    
    async def _assess_hypertension_risk(
        self,
        processed_data: Dict[str, List[HealthMetric]]
    ) -> Optional[RiskAssessment]:
        """评估高血压风险"""
        risk_factors = []
        risk_score = 0.0
        
        # 检查血压趋势
        bp_metrics = self._get_metrics_by_name(processed_data, ["blood_pressure_systolic", "blood_pressure_diastolic"])
        if bp_metrics:
            systolic_values = [m.value for m in bp_metrics if m.name == "blood_pressure_systolic"]
            diastolic_values = [m.value for m in bp_metrics if m.name == "blood_pressure_diastolic"]
            
            if systolic_values:
                avg_systolic = statistics.mean(systolic_values)
                if avg_systolic > 130:
                    risk_factors.append("收缩压偏高")
                    risk_score += 0.4
            
            if diastolic_values:
                avg_diastolic = statistics.mean(diastolic_values)
                if avg_diastolic > 85:
                    risk_factors.append("舒张压偏高")
                    risk_score += 0.3
        
        if risk_score > 0:
            if risk_score >= 0.6:
                risk_level = RiskLevel.HIGH
            elif risk_score >= 0.3:
                risk_level = RiskLevel.MODERATE
            else:
                risk_level = RiskLevel.LOW
            
            recommendations = [
                "减少钠盐摄入",
                "增加钾的摄入",
                "规律运动",
                "控制体重",
                "限制酒精摄入",
                "管理压力"
            ]
            
            return RiskAssessment(
                risk_factor="高血压",
                risk_level=risk_level,
                probability=min(risk_score, 1.0),
                contributing_factors=risk_factors,
                recommendations=recommendations,
                time_horizon="3年"
            )
        
        return None
    
    async def _assess_obesity_risk(
        self,
        processed_data: Dict[str, List[HealthMetric]]
    ) -> Optional[RiskAssessment]:
        """评估肥胖风险"""
        risk_factors = []
        risk_score = 0.0
        
        # 检查BMI
        bmi_metrics = self._get_metrics_by_name(processed_data, ["bmi"])
        if bmi_metrics:
            latest_bmi = bmi_metrics[-1].value
            if latest_bmi > 25:
                risk_factors.append("BMI超标")
                risk_score += 0.3
            if latest_bmi > 30:
                risk_factors.append("肥胖")
                risk_score += 0.5
        
        # 检查腰围
        waist_metrics = self._get_metrics_by_name(processed_data, ["waist_circumference"])
        if waist_metrics:
            latest_waist = waist_metrics[-1].value
            # 假设用户性别信息可获得
            if latest_waist > 90:  # 男性标准
                risk_factors.append("腰围超标")
                risk_score += 0.3
        
        if risk_score > 0:
            if risk_score >= 0.7:
                risk_level = RiskLevel.HIGH
            elif risk_score >= 0.4:
                risk_level = RiskLevel.MODERATE
            else:
                risk_level = RiskLevel.LOW
            
            recommendations = [
                "控制饮食热量摄入",
                "增加有氧运动",
                "规律作息",
                "多吃蔬菜水果",
                "减少高热量食物"
            ]
            
            return RiskAssessment(
                risk_factor="肥胖",
                risk_level=risk_level,
                probability=min(risk_score, 1.0),
                contributing_factors=risk_factors,
                recommendations=recommendations,
                time_horizon="1年"
            )
        
        return None
    
    async def _assess_constitution_risk(
        self,
        processed_data: Dict[str, List[HealthMetric]]
    ) -> Optional[RiskAssessment]:
        """评估中医体质风险"""
        # 基于症状分析体质类型
        symptom_metrics = self._get_metrics_by_category(processed_data, "symptoms")
        if not symptom_metrics:
            return None
        
        constitution_scores = {}
        for constitution, symptoms in self.constitution_analyzer["symptom_mapping"].items():
            score = 0
            for metric in symptom_metrics:
                if any(symptom in str(metric.value) for symptom in symptoms):
                    score += 1
            constitution_scores[constitution] = score
        
        # 找出最可能的体质类型
        if constitution_scores:
            dominant_constitution = max(constitution_scores, key=constitution_scores.get)
            max_score = constitution_scores[dominant_constitution]
            
            if max_score > 0:
                # 基于体质类型给出风险评估
                constitution_risks = {
                    "气虚质": ["免疫力低下", "容易感冒", "消化不良"],
                    "阳虚质": ["代谢缓慢", "容易水肿", "性功能减退"],
                    "阴虚质": ["失眠", "皮肤干燥", "更年期综合征"],
                    "痰湿质": ["高血脂", "脂肪肝", "糖尿病"],
                    "湿热质": ["皮肤病", "泌尿系感染", "高血压"],
                    "血瘀质": ["心血管疾病", "血栓", "肿瘤"],
                    "气郁质": ["抑郁症", "焦虑症", "乳腺增生"],
                    "特禀质": ["过敏性疾病", "哮喘", "皮炎"]
                }
                
                risk_factors = constitution_risks.get(dominant_constitution, [])
                
                # 体质调理建议
                constitution_recommendations = {
                    "气虚质": ["补气食物", "适量运动", "充足睡眠", "避免过劳"],
                    "阳虚质": ["温阳食物", "避免寒凉", "适当运动", "保暖"],
                    "阴虚质": ["滋阴食物", "避免熬夜", "减少辛辣", "静心养神"],
                    "痰湿质": ["健脾化湿", "控制体重", "清淡饮食", "增加运动"],
                    "湿热质": ["清热利湿", "避免油腻", "多吃蔬果", "规律作息"],
                    "血瘀质": ["活血化瘀", "适量运动", "保持心情愉快", "避免久坐"],
                    "气郁质": ["疏肝理气", "调节情绪", "适当运动", "社交活动"],
                    "特禀质": ["避免过敏原", "增强体质", "规律作息", "适量运动"]
                }
                
                recommendations = constitution_recommendations.get(dominant_constitution, [])
                
                return RiskAssessment(
                    risk_factor=f"中医体质风险（{dominant_constitution}）",
                    risk_level=RiskLevel.MODERATE,
                    probability=max_score / len(self.constitution_analyzer["symptom_mapping"][dominant_constitution]),
                    contributing_factors=risk_factors,
                    recommendations=recommendations,
                    time_horizon="长期"
                )
        
        return None
    
    async def _analyze_trends(
        self,
        processed_data: Dict[str, List[HealthMetric]]
    ) -> List[HealthTrend]:
        """趋势分析"""
        trends = []
        
        for category, metrics in processed_data.items():
            # 按指标名称分组
            metric_groups = {}
            for metric in metrics:
                if metric.name not in metric_groups:
                    metric_groups[metric.name] = []
                metric_groups[metric.name].append(metric)
            
            # 分析每个指标的趋势
            for metric_name, metric_list in metric_groups.items():
                if len(metric_list) >= 3:  # 至少需要3个数据点
                    trend = await self._calculate_trend(metric_name, metric_list)
                    if trend:
                        trends.append(trend)
        
        return trends
    
    async def _calculate_trend(
        self,
        metric_name: str,
        metrics: List[HealthMetric]
    ) -> Optional[HealthTrend]:
        """计算单个指标的趋势"""
        # 提取数值和时间
        values = []
        timestamps = []
        
        for metric in metrics:
            if isinstance(metric.value, (int, float)):
                values.append(float(metric.value))
                timestamps.append(metric.timestamp)
        
        if len(values) < 3:
            return None
        
        # 计算线性趋势
        time_deltas = [(t - timestamps[0]).total_seconds() for t in timestamps]
        
        # 使用numpy计算线性回归
        coeffs = np.polyfit(time_deltas, values, 1)
        slope = coeffs[0]
        
        # 确定趋势方向
        if abs(slope) < 0.01:  # 阈值可调整
            direction = TrendDirection.STABLE
        elif slope > 0:
            direction = TrendDirection.IMPROVING if self._is_positive_trend(metric_name) else TrendDirection.DECLINING
        else:
            direction = TrendDirection.DECLINING if self._is_positive_trend(metric_name) else TrendDirection.IMPROVING
        
        # 计算变化率
        if len(values) > 1:
            change_rate = (values[-1] - values[0]) / values[0] * 100
        else:
            change_rate = 0.0
        
        # 计算置信度（基于R²）
        y_pred = np.polyval(coeffs, time_deltas)
        ss_res = np.sum((values - y_pred) ** 2)
        ss_tot = np.sum((values - np.mean(values)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        confidence = max(0.0, min(1.0, r_squared))
        
        # 时间周期
        time_period = timestamps[-1] - timestamps[0]
        
        return HealthTrend(
            metric_name=metric_name,
            direction=direction,
            change_rate=change_rate,
            confidence=confidence,
            time_period=time_period
        )
    
    def _is_positive_trend(self, metric_name: str) -> bool:
        """判断指标上升是否为正面趋势"""
        positive_metrics = {
            "exercise_frequency", "sleep_duration", "water_intake",
            "hdl_cholesterol", "muscle_mass", "bone_density"
        }
        negative_metrics = {
            "blood_pressure_systolic", "blood_pressure_diastolic",
            "blood_glucose", "total_cholesterol", "ldl_cholesterol",
            "body_fat_percentage", "stress_level"
        }
        
        if metric_name in positive_metrics:
            return True
        elif metric_name in negative_metrics:
            return False
        else:
            return True  # 默认认为上升是正面的
    
    async def _generate_insights(
        self,
        processed_data: Dict[str, List[HealthMetric]],
        risk_assessments: List[RiskAssessment],
        trends: List[HealthTrend]
    ) -> List[HealthInsight]:
        """生成健康洞察"""
        insights = []
        
        # 基于风险评估的洞察
        for risk in risk_assessments:
            if risk.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                insight = HealthInsight(
                    title=f"高风险警告：{risk.risk_factor}",
                    description=f"您的{risk.risk_factor}风险较高，需要立即关注",
                    category="risk_warning",
                    importance=5,
                    actionable=True,
                    recommendations=risk.recommendations,
                    related_metrics=risk.contributing_factors
                )
                insights.append(insight)
        
        # 基于趋势的洞察
        for trend in trends:
            if trend.confidence > 0.7:  # 高置信度趋势
                if trend.direction == TrendDirection.DECLINING:
                    insight = HealthInsight(
                        title=f"{trend.metric_name}呈下降趋势",
                        description=f"过去{trend.time_period.days}天内，您的{trend.metric_name}下降了{abs(trend.change_rate):.1f}%",
                        category="trend_alert",
                        importance=4,
                        actionable=True,
                        recommendations=[f"关注{trend.metric_name}的变化，考虑调整生活方式"],
                        related_metrics=[trend.metric_name]
                    )
                    insights.append(insight)
                elif trend.direction == TrendDirection.IMPROVING:
                    insight = HealthInsight(
                        title=f"{trend.metric_name}持续改善",
                        description=f"过去{trend.time_period.days}天内，您的{trend.metric_name}改善了{trend.change_rate:.1f}%",
                        category="positive_trend",
                        importance=3,
                        actionable=False,
                        recommendations=["继续保持当前的健康习惯"],
                        related_metrics=[trend.metric_name]
                    )
                    insights.append(insight)
        
        # 数据质量洞察
        total_metrics = sum(len(metrics) for metrics in processed_data.values())
        if total_metrics < 10:
            insight = HealthInsight(
                title="健康数据不足",
                description="您的健康数据较少，建议增加数据记录频率以获得更准确的分析",
                category="data_quality",
                importance=2,
                actionable=True,
                recommendations=["定期记录生命体征", "使用健康监测设备", "定期体检"],
                related_metrics=[]
            )
            insights.append(insight)
        
        return insights
    
    async def _generate_recommendations(
        self,
        processed_data: Dict[str, List[HealthMetric]],
        risk_assessments: List[RiskAssessment],
        insights: List[HealthInsight]
    ) -> List[str]:
        """生成个性化建议"""
        recommendations = set()
        
        # 从风险评估中提取建议
        for risk in risk_assessments:
            recommendations.update(risk.recommendations)
        
        # 从洞察中提取建议
        for insight in insights:
            recommendations.update(insight.recommendations)
        
        # 基于数据分析的通用建议
        general_recommendations = [
            "保持规律的作息时间",
            "均衡饮食，多吃蔬菜水果",
            "每周进行至少150分钟的中等强度运动",
            "定期进行健康检查",
            "保持良好的心理状态"
        ]
        
        # 如果没有特定建议，添加通用建议
        if len(recommendations) < 3:
            recommendations.update(general_recommendations[:3])
        
        return list(recommendations)
    
    async def _predict_next_checkup(
        self,
        risk_assessments: List[RiskAssessment]
    ) -> Optional[datetime]:
        """预测下次检查时间"""
        if not risk_assessments:
            return datetime.now() + timedelta(days=365)  # 默认一年后
        
        # 根据最高风险等级确定检查频率
        max_risk_level = max(risk.risk_level for risk in risk_assessments)
        
        if max_risk_level == RiskLevel.CRITICAL:
            days = 30  # 一个月后
        elif max_risk_level == RiskLevel.HIGH:
            days = 90  # 三个月后
        elif max_risk_level == RiskLevel.MODERATE:
            days = 180  # 六个月后
        else:
            days = 365  # 一年后
        
        return datetime.now() + timedelta(days=days)
    
    async def _generate_summary(
        self,
        overall_score: float,
        risk_assessments: List[RiskAssessment],
        trends: List[HealthTrend],
        insights: List[HealthInsight]
    ) -> str:
        """生成健康报告摘要"""
        summary_parts = []
        
        # 整体评分
        if overall_score >= 80:
            summary_parts.append(f"您的整体健康状况良好（{overall_score:.1f}分）")
        elif overall_score >= 60:
            summary_parts.append(f"您的整体健康状况一般（{overall_score:.1f}分）")
        else:
            summary_parts.append(f"您的健康状况需要关注（{overall_score:.1f}分）")
        
        # 风险评估摘要
        high_risks = [r for r in risk_assessments if r.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]
        if high_risks:
            risk_names = [r.risk_factor for r in high_risks]
            summary_parts.append(f"需要特别关注：{', '.join(risk_names)}")
        
        # 趋势摘要
        improving_trends = [t for t in trends if t.direction == TrendDirection.IMPROVING and t.confidence > 0.7]
        declining_trends = [t for t in trends if t.direction == TrendDirection.DECLINING and t.confidence > 0.7]
        
        if improving_trends:
            summary_parts.append(f"改善指标：{', '.join([t.metric_name for t in improving_trends])}")
        
        if declining_trends:
            summary_parts.append(f"需要关注的指标：{', '.join([t.metric_name for t in declining_trends])}")
        
        # 重要洞察
        important_insights = [i for i in insights if i.importance >= 4]
        if important_insights:
            summary_parts.append(f"重要发现：{important_insights[0].title}")
        
        return "。".join(summary_parts) + "。"
    
    def _get_metrics_by_name(
        self,
        processed_data: Dict[str, List[HealthMetric]],
        names: List[str]
    ) -> List[HealthMetric]:
        """根据名称获取指标"""
        metrics = []
        for category_metrics in processed_data.values():
            for metric in category_metrics:
                if metric.name in names:
                    metrics.append(metric)
        return metrics
    
    def _get_metrics_by_category(
        self,
        processed_data: Dict[str, List[HealthMetric]],
        category: str
    ) -> List[HealthMetric]:
        """根据类别获取指标"""
        return processed_data.get(category, [])
    
    async def export_report(
        self,
        report: HealthReport,
        format_type: str = "json"
    ) -> Dict[str, Any]:
        """导出健康报告"""
        if format_type == "json":
            return {
                "user_id": report.user_id,
                "report_date": report.report_date.isoformat(),
                "overall_score": report.overall_score,
                "summary": report.summary,
                "risk_assessments": [
                    {
                        "risk_factor": r.risk_factor,
                        "risk_level": r.risk_level.value,
                        "probability": r.probability,
                        "contributing_factors": r.contributing_factors,
                        "recommendations": r.recommendations
                    }
                    for r in report.risk_assessments
                ],
                "trends": [
                    {
                        "metric_name": t.metric_name,
                        "direction": t.direction.value,
                        "change_rate": t.change_rate,
                        "confidence": t.confidence
                    }
                    for t in report.trends
                ],
                "insights": [
                    {
                        "title": i.title,
                        "description": i.description,
                        "category": i.category,
                        "importance": i.importance,
                        "recommendations": i.recommendations
                    }
                    for i in report.insights
                ],
                "recommendations": report.recommendations,
                "next_checkup_date": report.next_checkup_date.isoformat() if report.next_checkup_date else None
            }
        
        return {} 