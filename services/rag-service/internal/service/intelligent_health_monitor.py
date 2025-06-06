"""
intelligent_health_monitor - 索克生活项目模块
"""

from ..observability.metrics import MetricsCollector
from ..observability.tracing import trace_operation, SpanKind
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from loguru import logger
from scipy import stats
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from typing import Dict, List, Any, Optional, Tuple, Union, Set, Callable
import asyncio
import time
import warnings

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能健康监测引擎 - 提供实时健康数据监测、异常检测、预警系统、趋势分析
"""

warnings.filterwarnings('ignore')


class HealthMetricType(str, Enum):
    """健康指标类型"""
    VITAL_SIGNS = "vital_signs"                     # 生命体征
    BLOOD_PRESSURE = "blood_pressure"               # 血压
    HEART_RATE = "heart_rate"                       # 心率
    BODY_TEMPERATURE = "body_temperature"           # 体温
    BLOOD_GLUCOSE = "blood_glucose"                 # 血糖
    BLOOD_OXYGEN = "blood_oxygen"                   # 血氧
    WEIGHT = "weight"                               # 体重
    BMI = "bmi"                                     # BMI
    SLEEP_QUALITY = "sleep_quality"                 # 睡眠质量
    ACTIVITY_LEVEL = "activity_level"               # 活动水平
    STRESS_LEVEL = "stress_level"                   # 压力水平
    MOOD = "mood"                                   # 情绪
    PAIN_LEVEL = "pain_level"                       # 疼痛程度
    MEDICATION_ADHERENCE = "medication_adherence"   # 用药依从性
    SYMPTOM_SEVERITY = "symptom_severity"           # 症状严重程度

class AlertLevel(str, Enum):
    """预警级别"""
    INFO = "info"           # 信息
    LOW = "low"             # 低级
    MEDIUM = "medium"       # 中级
    HIGH = "high"           # 高级
    CRITICAL = "critical"   # 危急
    EMERGENCY = "emergency" # 紧急

class MonitoringFrequency(str, Enum):
    """监测频率"""
    REAL_TIME = "real_time"     # 实时
    MINUTE = "minute"           # 每分钟
    HOURLY = "hourly"           # 每小时
    DAILY = "daily"             # 每日
    WEEKLY = "weekly"           # 每周
    MONTHLY = "monthly"         # 每月

class TrendDirection(str, Enum):
    """趋势方向"""
    IMPROVING = "improving"     # 改善
    STABLE = "stable"           # 稳定
    DECLINING = "declining"     # 恶化
    FLUCTUATING = "fluctuating" # 波动

class AnomalyType(str, Enum):
    """异常类型"""
    OUTLIER = "outlier"                 # 离群值
    TREND_CHANGE = "trend_change"       # 趋势变化
    PATTERN_BREAK = "pattern_break"     # 模式中断
    THRESHOLD_BREACH = "threshold_breach" # 阈值突破
    MISSING_DATA = "missing_data"       # 数据缺失
    SENSOR_ERROR = "sensor_error"       # 传感器错误

@dataclass
class HealthMetric:
    """健康指标"""
    id: str
    user_id: str
    metric_type: HealthMetricType
    value: float
    unit: str
    timestamp: datetime
    source: str                                     # 数据来源
    device_id: Optional[str] = None
    confidence: float = 1.0                         # 数据置信度
    quality_score: float = 1.0                      # 数据质量分数
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HealthThreshold:
    """健康阈值"""
    metric_type: HealthMetricType
    user_id: str
    min_normal: Optional[float] = None
    max_normal: Optional[float] = None
    min_warning: Optional[float] = None
    max_warning: Optional[float] = None
    min_critical: Optional[float] = None
    max_critical: Optional[float] = None
    age_group: Optional[str] = None
    gender: Optional[str] = None
    condition_specific: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class HealthAlert:
    """健康预警"""
    id: str
    user_id: str
    metric_type: HealthMetricType
    alert_level: AlertLevel
    title: str
    description: str
    current_value: float
    threshold_value: Optional[float] = None
    trend_info: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)
    urgency_score: float = 0.0                      # 紧急程度分数
    auto_resolved: bool = False
    acknowledged: bool = False
    resolved: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HealthTrend:
    """健康趋势"""
    user_id: str
    metric_type: HealthMetricType
    direction: TrendDirection
    slope: float                                    # 趋势斜率
    confidence: float                               # 趋势置信度
    duration_days: int                              # 趋势持续天数
    start_value: float
    end_value: float
    change_percentage: float
    statistical_significance: float                 # 统计显著性
    prediction_next_week: Optional[float] = None
    prediction_next_month: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class AnomalyDetection:
    """异常检测结果"""
    id: str
    user_id: str
    metric_type: HealthMetricType
    anomaly_type: AnomalyType
    severity: float                                 # 异常严重程度
    description: str
    detected_value: float
    expected_range: Tuple[float, float]
    timestamp: datetime
    confidence: float = 0.0
    context: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False

@dataclass
class MonitoringProfile:
    """监测配置文件"""
    user_id: str
    enabled_metrics: List[HealthMetricType]
    monitoring_frequencies: Dict[HealthMetricType, MonitoringFrequency]
    custom_thresholds: Dict[HealthMetricType, HealthThreshold]
    alert_preferences: Dict[str, Any]
    notification_settings: Dict[str, Any]
    data_retention_days: int = 365
    privacy_settings: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

class HealthDataProcessor:
    """健康数据处理器"""
    
    def __init__(self):
        self.scalers = {}
        self.baseline_models = {}
        self.quality_thresholds = {
            "completeness": 0.8,
            "consistency": 0.9,
            "accuracy": 0.85,
            "timeliness": 0.9
        }
    
    async def process_raw_data(
        self, 
        raw_data: Dict[str, Any], 
        user_id: str
    ) -> List[HealthMetric]:
        """处理原始健康数据"""
        try:
            processed_metrics = []
            
            for metric_type_str, value_data in raw_data.items():
                try:
                    metric_type = HealthMetricType(metric_type_str)
                    
                    # 数据验证和清洗
                    cleaned_value = await self._clean_data_value(value_data, metric_type)
                    if cleaned_value is None:
                        continue
                    
                    # 计算数据质量分数
                    quality_score = await self._calculate_quality_score(
                        value_data, metric_type
                    )
                    
                    # 创建健康指标
                    metric = HealthMetric(
                        id=f"{user_id}_{metric_type.value}_{int(time.time())}",
                        user_id=user_id,
                        metric_type=metric_type,
                        value=cleaned_value,
                        unit=self._get_metric_unit(metric_type),
                        timestamp=datetime.now(),
                        source=value_data.get("source", "unknown"),
                        device_id=value_data.get("device_id"),
                        confidence=value_data.get("confidence", 1.0),
                        quality_score=quality_score,
                        metadata=value_data.get("metadata", {})
                    )
                    
                    processed_metrics.append(metric)
                    
                except ValueError:
                    logger.warning(f"未知的健康指标类型: {metric_type_str}")
                    continue
                except Exception as e:
                    logger.error(f"处理健康指标失败 {metric_type_str}: {e}")
                    continue
            
            return processed_metrics
            
        except Exception as e:
            logger.error(f"处理原始健康数据失败: {e}")
            return []
    
    async def _clean_data_value(
        self, 
        value_data: Dict[str, Any], 
        metric_type: HealthMetricType
    ) -> Optional[float]:
        """清洗数据值"""
        try:
            raw_value = value_data.get("value")
            if raw_value is None:
                return None
            
            # 转换为浮点数
            if isinstance(raw_value, str):
                # 处理特殊字符串值
                if raw_value.lower() in ["n/a", "null", "none", ""]:
                    return None
                raw_value = float(raw_value.replace(",", ""))
            
            value = float(raw_value)
            
            # 范围检查
            valid_ranges = {
                HealthMetricType.HEART_RATE: (30, 220),
                HealthMetricType.BLOOD_PRESSURE: (50, 250),  # 收缩压或舒张压
                HealthMetricType.BODY_TEMPERATURE: (35.0, 42.0),
                HealthMetricType.BLOOD_GLUCOSE: (2.0, 30.0),
                HealthMetricType.BLOOD_OXYGEN: (70, 100),
                HealthMetricType.WEIGHT: (20, 300),
                HealthMetricType.BMI: (10, 50),
                HealthMetricType.SLEEP_QUALITY: (0, 10),
                HealthMetricType.ACTIVITY_LEVEL: (0, 10),
                HealthMetricType.STRESS_LEVEL: (0, 10),
                HealthMetricType.MOOD: (0, 10),
                HealthMetricType.PAIN_LEVEL: (0, 10)
            }
            
            if metric_type in valid_ranges:
                min_val, max_val = valid_ranges[metric_type]
                if not (min_val <= value <= max_val):
                    logger.warning(f"数值超出有效范围 {metric_type}: {value}")
                    return None
            
            return value
            
        except (ValueError, TypeError) as e:
            logger.warning(f"数据清洗失败 {metric_type}: {e}")
            return None
    
    async def _calculate_quality_score(
        self, 
        value_data: Dict[str, Any], 
        metric_type: HealthMetricType
    ) -> float:
        """计算数据质量分数"""
        try:
            quality_factors = []
            
            # 完整性检查
            required_fields = ["value", "timestamp"]
            completeness = sum(
                1 for field in required_fields 
                if value_data.get(field) is not None
            ) / len(required_fields)
            quality_factors.append(completeness)
            
            # 时效性检查
            timestamp = value_data.get("timestamp")
            if timestamp:
                try:
                    if isinstance(timestamp, str):
                        timestamp = datetime.fromisoformat(timestamp)
                    time_diff = (datetime.now() - timestamp).total_seconds()
                    timeliness = max(0, 1 - time_diff / 3600)  # 1小时内为满分
                    quality_factors.append(timeliness)
                except:
                    quality_factors.append(0.5)
            else:
                quality_factors.append(0.5)
            
            # 置信度
            confidence = value_data.get("confidence", 0.8)
            quality_factors.append(confidence)
            
            # 设备可靠性
            device_reliability = value_data.get("device_reliability", 0.9)
            quality_factors.append(device_reliability)
            
            return sum(quality_factors) / len(quality_factors)
            
        except Exception as e:
            logger.error(f"计算数据质量分数失败: {e}")
            return 0.5
    
    def _get_metric_unit(self, metric_type: HealthMetricType) -> str:
        """获取指标单位"""
        units = {
            HealthMetricType.HEART_RATE: "bpm",
            HealthMetricType.BLOOD_PRESSURE: "mmHg",
            HealthMetricType.BODY_TEMPERATURE: "°C",
            HealthMetricType.BLOOD_GLUCOSE: "mmol/L",
            HealthMetricType.BLOOD_OXYGEN: "%",
            HealthMetricType.WEIGHT: "kg",
            HealthMetricType.BMI: "kg/m²",
            HealthMetricType.SLEEP_QUALITY: "score",
            HealthMetricType.ACTIVITY_LEVEL: "score",
            HealthMetricType.STRESS_LEVEL: "score",
            HealthMetricType.MOOD: "score",
            HealthMetricType.PAIN_LEVEL: "score",
            HealthMetricType.MEDICATION_ADHERENCE: "%",
            HealthMetricType.SYMPTOM_SEVERITY: "score"
        }
        return units.get(metric_type, "unit")

class AnomalyDetector:
    """异常检测器"""
    
    def __init__(self):
        self.isolation_forests = {}
        self.statistical_models = {}
        self.pattern_models = {}
        self.trained_users = set()
    
    async def detect_anomalies(
        self,
        metrics: List[HealthMetric],
        user_id: str,
        historical_data: Optional[List[HealthMetric]] = None
    ) -> List[AnomalyDetection]:
        """检测异常"""
        try:
            anomalies = []
            
            # 按指标类型分组
            metrics_by_type = {}
            for metric in metrics:
                if metric.metric_type not in metrics_by_type:
                    metrics_by_type[metric.metric_type] = []
                metrics_by_type[metric.metric_type].append(metric)
            
            for metric_type, type_metrics in metrics_by_type.items():
                # 统计异常检测
                stat_anomalies = await self._detect_statistical_anomalies(
                    type_metrics, user_id, metric_type, historical_data
                )
                anomalies.extend(stat_anomalies)
                
                # 机器学习异常检测
                ml_anomalies = await self._detect_ml_anomalies(
                    type_metrics, user_id, metric_type, historical_data
                )
                anomalies.extend(ml_anomalies)
                
                # 模式异常检测
                pattern_anomalies = await self._detect_pattern_anomalies(
                    type_metrics, user_id, metric_type, historical_data
                )
                anomalies.extend(pattern_anomalies)
            
            return anomalies
            
        except Exception as e:
            logger.error(f"异常检测失败: {e}")
            return []
    
    async def _detect_statistical_anomalies(
        self,
        metrics: List[HealthMetric],
        user_id: str,
        metric_type: HealthMetricType,
        historical_data: Optional[List[HealthMetric]] = None
    ) -> List[AnomalyDetection]:
        """统计异常检测"""
        anomalies = []
        
        try:
            if not metrics:
                return anomalies
            
            # 获取历史数据用于建立基线
            if historical_data:
                baseline_values = [m.value for m in historical_data if m.metric_type == metric_type]
            else:
                baseline_values = [m.value for m in metrics]
            
            if len(baseline_values) < 10:  # 数据不足
                return anomalies
            
            # 计算统计参数
            mean_val = np.mean(baseline_values)
            std_val = np.std(baseline_values)
            median_val = np.median(baseline_values)
            q1, q3 = np.percentile(baseline_values, [25, 75])
            iqr = q3 - q1
            
            for metric in metrics:
                # Z-score异常检测
                if std_val > 0:
                    z_score = abs(metric.value - mean_val) / std_val
                    if z_score > 3:  # 3-sigma规则
                        anomaly = AnomalyDetection(
                            id=f"stat_anomaly_{metric.id}",
                            user_id=user_id,
                            metric_type=metric_type,
                            anomaly_type=AnomalyType.OUTLIER,
                            severity=min(z_score / 3, 1.0),
                            description=f"{metric_type.value}值异常偏离正常范围",
                            detected_value=metric.value,
                            expected_range=(mean_val - 2*std_val, mean_val + 2*std_val),
                            timestamp=metric.timestamp,
                            confidence=min(z_score / 5, 1.0),
                            context={"z_score": z_score, "method": "statistical"}
                        )
                        anomalies.append(anomaly)
                
                # IQR异常检测
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                if metric.value < lower_bound or metric.value > upper_bound:
                    severity = max(
                        abs(metric.value - lower_bound) / iqr if metric.value < lower_bound else 0,
                        abs(metric.value - upper_bound) / iqr if metric.value > upper_bound else 0
                    )
                    
                    anomaly = AnomalyDetection(
                        id=f"iqr_anomaly_{metric.id}",
                        user_id=user_id,
                        metric_type=metric_type,
                        anomaly_type=AnomalyType.OUTLIER,
                        severity=min(severity / 2, 1.0),
                        description=f"{metric_type.value}值超出四分位数范围",
                        detected_value=metric.value,
                        expected_range=(lower_bound, upper_bound),
                        timestamp=metric.timestamp,
                        confidence=0.8,
                        context={"method": "iqr", "iqr": iqr}
                    )
                    anomalies.append(anomaly)
            
        except Exception as e:
            logger.error(f"统计异常检测失败: {e}")
        
        return anomalies
    
    async def _detect_ml_anomalies(
        self,
        metrics: List[HealthMetric],
        user_id: str,
        metric_type: HealthMetricType,
        historical_data: Optional[List[HealthMetric]] = None
    ) -> List[AnomalyDetection]:
        """机器学习异常检测"""
        anomalies = []
        
        try:
            if not metrics:
                return anomalies
            
            # 准备训练数据
            if historical_data:
                train_data = [m.value for m in historical_data if m.metric_type == metric_type]
            else:
                train_data = [m.value for m in metrics[:-len(metrics)//4]]  # 使用前75%作为训练
            
            if len(train_data) < 20:  # 数据不足
                return anomalies
            
            # 训练Isolation Forest模型
            model_key = f"{user_id}_{metric_type.value}"
            if model_key not in self.isolation_forests:
                X_train = np.array(train_data).reshape(-1, 1)
                model = IsolationForest(contamination=0.1, random_state=42)
                model.fit(X_train)
                self.isolation_forests[model_key] = model
            
            model = self.isolation_forests[model_key]
            
            # 检测异常
            for metric in metrics:
                X_test = np.array([[metric.value]])
                anomaly_score = model.decision_function(X_test)[0]
                is_anomaly = model.predict(X_test)[0] == -1
                
                if is_anomaly:
                    severity = max(0, -anomaly_score)  # 负值表示异常
                    
                    anomaly = AnomalyDetection(
                        id=f"ml_anomaly_{metric.id}",
                        user_id=user_id,
                        metric_type=metric_type,
                        anomaly_type=AnomalyType.OUTLIER,
                        severity=min(severity, 1.0),
                        description=f"机器学习模型检测到{metric_type.value}异常",
                        detected_value=metric.value,
                        expected_range=(min(train_data), max(train_data)),
                        timestamp=metric.timestamp,
                        confidence=min(severity * 2, 1.0),
                        context={"anomaly_score": anomaly_score, "method": "isolation_forest"}
                    )
                    anomalies.append(anomaly)
            
        except Exception as e:
            logger.error(f"机器学习异常检测失败: {e}")
        
        return anomalies
    
    async def _detect_pattern_anomalies(
        self,
        metrics: List[HealthMetric],
        user_id: str,
        metric_type: HealthMetricType,
        historical_data: Optional[List[HealthMetric]] = None
    ) -> List[AnomalyDetection]:
        """模式异常检测"""
        anomalies = []
        
        try:
            if len(metrics) < 5:  # 数据不足进行模式分析
                return anomalies
            
            # 按时间排序
            sorted_metrics = sorted(metrics, key=lambda x: x.timestamp)
            values = [m.value for m in sorted_metrics]
            timestamps = [m.timestamp for m in sorted_metrics]
            
            # 检测趋势变化
            if len(values) >= 10:
                # 计算滑动窗口的趋势
                window_size = min(5, len(values) // 2)
                trends = []
                
                for i in range(len(values) - window_size + 1):
                    window_values = values[i:i + window_size]
                    window_indices = list(range(len(window_values)))
                    
                    # 线性回归计算趋势
                    slope, intercept, r_value, p_value, std_err = stats.linregress(
                        window_indices, window_values
                    )
                    trends.append(slope)
                
                # 检测趋势突变
                if len(trends) >= 3:
                    for i in range(1, len(trends) - 1):
                        prev_trend = trends[i-1]
                        curr_trend = trends[i]
                        next_trend = trends[i+1]
                        
                        # 趋势方向突然改变
                        if (prev_trend > 0 and curr_trend < -abs(prev_trend) * 0.5) or \
                           (prev_trend < 0 and curr_trend > abs(prev_trend) * 0.5):
                            
                            metric_idx = i + window_size - 1
                            if metric_idx < len(sorted_metrics):
                                metric = sorted_metrics[metric_idx]
                                
                                anomaly = AnomalyDetection(
                                    id=f"trend_anomaly_{metric.id}",
                                    user_id=user_id,
                                    metric_type=metric_type,
                                    anomaly_type=AnomalyType.TREND_CHANGE,
                                    severity=min(abs(curr_trend - prev_trend) / max(abs(prev_trend), 1), 1.0),
                                    description=f"{metric_type.value}趋势发生突变",
                                    detected_value=metric.value,
                                    expected_range=(min(values), max(values)),
                                    timestamp=metric.timestamp,
                                    confidence=0.7,
                                    context={
                                        "prev_trend": prev_trend,
                                        "curr_trend": curr_trend,
                                        "method": "trend_change"
                                    }
                                )
                                anomalies.append(anomaly)
            
            # 检测周期性模式中断
            if len(values) >= 24:  # 至少需要一天的数据（假设每小时一个数据点）
                # 使用FFT检测周期性
                fft_values = np.fft.fft(values)
                frequencies = np.fft.fftfreq(len(values))
                
                # 找到主要频率
                dominant_freq_idx = np.argmax(np.abs(fft_values[1:len(fft_values)//2])) + 1
                dominant_period = int(1 / abs(frequencies[dominant_freq_idx])) if frequencies[dominant_freq_idx] != 0 else len(values)
                
                if 6 <= dominant_period <= len(values) // 3:  # 合理的周期长度
                    # 检测最近的数据是否偏离周期性模式
                    recent_values = values[-dominant_period:]
                    expected_pattern = values[-2*dominant_period:-dominant_period]
                    
                    if len(recent_values) == len(expected_pattern):
                        pattern_deviation = np.mean(np.abs(np.array(recent_values) - np.array(expected_pattern)))
                        pattern_std = np.std(expected_pattern)
                        
                        if pattern_std > 0 and pattern_deviation > 2 * pattern_std:
                            # 模式中断
                            latest_metric = sorted_metrics[-1]
                            
                            anomaly = AnomalyDetection(
                                id=f"pattern_anomaly_{latest_metric.id}",
                                user_id=user_id,
                                metric_type=metric_type,
                                anomaly_type=AnomalyType.PATTERN_BREAK,
                                severity=min(pattern_deviation / (3 * pattern_std), 1.0),
                                description=f"{metric_type.value}偏离正常周期性模式",
                                detected_value=latest_metric.value,
                                expected_range=(min(expected_pattern), max(expected_pattern)),
                                timestamp=latest_metric.timestamp,
                                confidence=0.6,
                                context={
                                    "dominant_period": dominant_period,
                                    "pattern_deviation": pattern_deviation,
                                    "method": "pattern_break"
                                }
                            )
                            anomalies.append(anomaly)
            
        except Exception as e:
            logger.error(f"模式异常检测失败: {e}")
        
        return anomalies

class TrendAnalyzer:
    """趋势分析器"""
    
    def __init__(self):
        self.trend_models = {}
    
    async def analyze_trends(
        self,
        metrics: List[HealthMetric],
        user_id: str,
        time_window_days: int = 30
    ) -> List[HealthTrend]:
        """分析健康趋势"""
        try:
            trends = []
            
            # 按指标类型分组
            metrics_by_type = {}
            for metric in metrics:
                if metric.metric_type not in metrics_by_type:
                    metrics_by_type[metric.metric_type] = []
                metrics_by_type[metric.metric_type].append(metric)
            
            for metric_type, type_metrics in metrics_by_type.items():
                # 过滤时间窗口内的数据
                cutoff_time = datetime.now() - timedelta(days=time_window_days)
                recent_metrics = [
                    m for m in type_metrics 
                    if m.timestamp >= cutoff_time
                ]
                
                if len(recent_metrics) < 5:  # 数据不足
                    continue
                
                # 按时间排序
                recent_metrics.sort(key=lambda x: x.timestamp)
                
                # 计算趋势
                trend = await self._calculate_trend(recent_metrics, user_id, metric_type)
                if trend:
                    trends.append(trend)
            
            return trends
            
        except Exception as e:
            logger.error(f"趋势分析失败: {e}")
            return []
    
    async def _calculate_trend(
        self,
        metrics: List[HealthMetric],
        user_id: str,
        metric_type: HealthMetricType
    ) -> Optional[HealthTrend]:
        """计算单个指标的趋势"""
        try:
            if len(metrics) < 3:
                return None
            
            # 提取数值和时间
            values = [m.value for m in metrics]
            timestamps = [m.timestamp for m in metrics]
            
            # 转换时间为数值（天数）
            start_time = timestamps[0]
            time_days = [(t - start_time).total_seconds() / 86400 for t in timestamps]
            
            # 线性回归分析趋势
            slope, intercept, r_value, p_value, std_err = stats.linregress(time_days, values)
            
            # 确定趋势方向
            if abs(slope) < std_err:  # 趋势不显著
                direction = TrendDirection.STABLE
            elif slope > 0:
                direction = TrendDirection.IMPROVING if self._is_positive_trend(metric_type) else TrendDirection.DECLINING
            else:
                direction = TrendDirection.DECLINING if self._is_positive_trend(metric_type) else TrendDirection.IMPROVING
            
            # 计算变化百分比
            start_value = values[0]
            end_value = values[-1]
            change_percentage = ((end_value - start_value) / start_value * 100) if start_value != 0 else 0
            
            # 预测未来值
            duration_days = (timestamps[-1] - timestamps[0]).days
            prediction_next_week = intercept + slope * (duration_days + 7)
            prediction_next_month = intercept + slope * (duration_days + 30)
            
            # 检查趋势的统计显著性
            statistical_significance = 1 - p_value if p_value < 0.05 else 0
            
            trend = HealthTrend(
                user_id=user_id,
                metric_type=metric_type,
                direction=direction,
                slope=slope,
                confidence=abs(r_value),  # 相关系数的绝对值作为置信度
                duration_days=duration_days,
                start_value=start_value,
                end_value=end_value,
                change_percentage=change_percentage,
                statistical_significance=statistical_significance,
                prediction_next_week=prediction_next_week,
                prediction_next_month=prediction_next_month
            )
            
            return trend
            
        except Exception as e:
            logger.error(f"计算趋势失败: {e}")
            return None
    
    def _is_positive_trend(self, metric_type: HealthMetricType) -> bool:
        """判断指标上升是否为正面趋势"""
        positive_trends = {
            HealthMetricType.BLOOD_OXYGEN,
            HealthMetricType.SLEEP_QUALITY,
            HealthMetricType.ACTIVITY_LEVEL,
            HealthMetricType.MOOD,
            HealthMetricType.MEDICATION_ADHERENCE
        }
        
        negative_trends = {
            HealthMetricType.STRESS_LEVEL,
            HealthMetricType.PAIN_LEVEL,
            HealthMetricType.SYMPTOM_SEVERITY
        }
        
        if metric_type in positive_trends:
            return True
        elif metric_type in negative_trends:
            return False
        else:
            # 对于血压、心率等，需要在正常范围内
            return False  # 保守处理

class AlertEngine:
    """预警引擎"""
    
    def __init__(self):
        self.alert_rules = {}
        self.notification_handlers = []
    
    async def evaluate_alerts(
        self,
        metrics: List[HealthMetric],
        thresholds: Dict[HealthMetricType, HealthThreshold],
        trends: List[HealthTrend],
        anomalies: List[AnomalyDetection],
        user_id: str
    ) -> List[HealthAlert]:
        """评估预警"""
        try:
            alerts = []
            
            # 阈值预警
            threshold_alerts = await self._evaluate_threshold_alerts(metrics, thresholds, user_id)
            alerts.extend(threshold_alerts)
            
            # 趋势预警
            trend_alerts = await self._evaluate_trend_alerts(trends, user_id)
            alerts.extend(trend_alerts)
            
            # 异常预警
            anomaly_alerts = await self._evaluate_anomaly_alerts(anomalies, user_id)
            alerts.extend(anomaly_alerts)
            
            # 组合预警（多个指标异常）
            combination_alerts = await self._evaluate_combination_alerts(metrics, user_id)
            alerts.extend(combination_alerts)
            
            # 按紧急程度排序
            alerts.sort(key=lambda x: x.urgency_score, reverse=True)
            
            return alerts
            
        except Exception as e:
            logger.error(f"预警评估失败: {e}")
            return []
    
    async def _evaluate_threshold_alerts(
        self,
        metrics: List[HealthMetric],
        thresholds: Dict[HealthMetricType, HealthThreshold],
        user_id: str
    ) -> List[HealthAlert]:
        """评估阈值预警"""
        alerts = []
        
        try:
            for metric in metrics:
                threshold = thresholds.get(metric.metric_type)
                if not threshold:
                    continue
                
                alert_level = None
                threshold_value = None
                description = ""
                recommendations = []
                
                # 检查危急阈值
                if threshold.min_critical is not None and metric.value < threshold.min_critical:
                    alert_level = AlertLevel.CRITICAL
                    threshold_value = threshold.min_critical
                    description = f"{metric.metric_type.value}过低，已达到危急水平"
                    recommendations = self._get_critical_recommendations(metric.metric_type, "low")
                elif threshold.max_critical is not None and metric.value > threshold.max_critical:
                    alert_level = AlertLevel.CRITICAL
                    threshold_value = threshold.max_critical
                    description = f"{metric.metric_type.value}过高，已达到危急水平"
                    recommendations = self._get_critical_recommendations(metric.metric_type, "high")
                
                # 检查警告阈值
                elif threshold.min_warning is not None and metric.value < threshold.min_warning:
                    alert_level = AlertLevel.HIGH
                    threshold_value = threshold.min_warning
                    description = f"{metric.metric_type.value}偏低，需要关注"
                    recommendations = self._get_warning_recommendations(metric.metric_type, "low")
                elif threshold.max_warning is not None and metric.value > threshold.max_warning:
                    alert_level = AlertLevel.HIGH
                    threshold_value = threshold.max_warning
                    description = f"{metric.metric_type.value}偏高，需要关注"
                    recommendations = self._get_warning_recommendations(metric.metric_type, "high")
                
                if alert_level:
                    urgency_score = self._calculate_urgency_score(
                        metric, threshold_value, alert_level
                    )
                    
                    alert = HealthAlert(
                        id=f"threshold_alert_{metric.id}",
                        user_id=user_id,
                        metric_type=metric.metric_type,
                        alert_level=alert_level,
                        title=f"{metric.metric_type.value}异常",
                        description=description,
                        current_value=metric.value,
                        threshold_value=threshold_value,
                        recommendations=recommendations,
                        urgency_score=urgency_score
                    )
                    alerts.append(alert)
            
        except Exception as e:
            logger.error(f"阈值预警评估失败: {e}")
        
        return alerts
    
    async def _evaluate_trend_alerts(
        self,
        trends: List[HealthTrend],
        user_id: str
    ) -> List[HealthAlert]:
        """评估趋势预警"""
        alerts = []
        
        try:
            for trend in trends:
                if trend.direction == TrendDirection.DECLINING and trend.confidence > 0.7:
                    # 恶化趋势预警
                    alert_level = AlertLevel.MEDIUM
                    if abs(trend.change_percentage) > 20:
                        alert_level = AlertLevel.HIGH
                    elif abs(trend.change_percentage) > 50:
                        alert_level = AlertLevel.CRITICAL
                    
                    urgency_score = min(abs(trend.change_percentage) / 50, 1.0) * trend.confidence
                    
                    alert = HealthAlert(
                        id=f"trend_alert_{trend.user_id}_{trend.metric_type.value}",
                        user_id=user_id,
                        metric_type=trend.metric_type,
                        alert_level=alert_level,
                        title=f"{trend.metric_type.value}趋势恶化",
                        description=f"过去{trend.duration_days}天{trend.metric_type.value}呈恶化趋势，变化{trend.change_percentage:.1f}%",
                        current_value=trend.end_value,
                        trend_info=f"趋势方向: {trend.direction.value}, 置信度: {trend.confidence:.2f}",
                        recommendations=self._get_trend_recommendations(trend),
                        urgency_score=urgency_score
                    )
                    alerts.append(alert)
            
        except Exception as e:
            logger.error(f"趋势预警评估失败: {e}")
        
        return alerts
    
    async def _evaluate_anomaly_alerts(
        self,
        anomalies: List[AnomalyDetection],
        user_id: str
    ) -> List[HealthAlert]:
        """评估异常预警"""
        alerts = []
        
        try:
            for anomaly in anomalies:
                if anomaly.severity > 0.5:  # 只对严重异常发出预警
                    alert_level = AlertLevel.LOW
                    if anomaly.severity > 0.7:
                        alert_level = AlertLevel.MEDIUM
                    elif anomaly.severity > 0.9:
                        alert_level = AlertLevel.HIGH
                    
                    alert = HealthAlert(
                        id=f"anomaly_alert_{anomaly.id}",
                        user_id=user_id,
                        metric_type=anomaly.metric_type,
                        alert_level=alert_level,
                        title=f"{anomaly.metric_type.value}异常检测",
                        description=anomaly.description,
                        current_value=anomaly.detected_value,
                        recommendations=self._get_anomaly_recommendations(anomaly),
                        urgency_score=anomaly.severity * anomaly.confidence
                    )
                    alerts.append(alert)
            
        except Exception as e:
            logger.error(f"异常预警评估失败: {e}")
        
        return alerts
    
    async def _evaluate_combination_alerts(
        self,
        metrics: List[HealthMetric],
        user_id: str
    ) -> List[HealthAlert]:
        """评估组合预警"""
        alerts = []
        
        try:
            # 检查心血管风险组合
            recent_metrics = [m for m in metrics if (datetime.now() - m.timestamp).hours < 24]
            
            # 按类型分组
            metrics_by_type = {}
            for metric in recent_metrics:
                metrics_by_type[metric.metric_type] = metric
            
            # 心血管风险组合
            bp_metric = metrics_by_type.get(HealthMetricType.BLOOD_PRESSURE)
            hr_metric = metrics_by_type.get(HealthMetricType.HEART_RATE)
            
            if bp_metric and hr_metric:
                if bp_metric.value > 140 and hr_metric.value > 100:  # 高血压 + 心动过速
                    alert = HealthAlert(
                        id=f"combo_alert_cardiovascular_{user_id}",
                        user_id=user_id,
                        metric_type=HealthMetricType.VITAL_SIGNS,
                        alert_level=AlertLevel.HIGH,
                        title="心血管风险预警",
                        description="血压和心率同时偏高，存在心血管风险",
                        current_value=0,  # 组合预警没有单一数值
                        recommendations=[
                            "立即休息，避免剧烈活动",
                            "监测血压和心率变化",
                            "如症状持续，请及时就医",
                            "检查是否有胸痛、气短等症状"
                        ],
                        urgency_score=0.8
                    )
                    alerts.append(alert)
            
            # 糖尿病风险组合
            glucose_metric = metrics_by_type.get(HealthMetricType.BLOOD_GLUCOSE)
            weight_metric = metrics_by_type.get(HealthMetricType.WEIGHT)
            
            if glucose_metric and glucose_metric.value > 11.1:  # 高血糖
                alert = HealthAlert(
                    id=f"combo_alert_diabetes_{user_id}",
                    user_id=user_id,
                    metric_type=HealthMetricType.BLOOD_GLUCOSE,
                    alert_level=AlertLevel.HIGH,
                    title="血糖异常预警",
                    description="血糖水平显著升高，需要紧急关注",
                    current_value=glucose_metric.value,
                    recommendations=[
                        "立即检查血糖仪是否正常",
                        "回顾最近的饮食和用药情况",
                        "如确认血糖过高，立即就医",
                        "监测是否有多饮、多尿等症状"
                    ],
                    urgency_score=0.9
                )
                alerts.append(alert)
            
        except Exception as e:
            logger.error(f"组合预警评估失败: {e}")
        
        return alerts
    
    def _calculate_urgency_score(
        self,
        metric: HealthMetric,
        threshold_value: float,
        alert_level: AlertLevel
    ) -> float:
        """计算紧急程度分数"""
        try:
            # 基础紧急程度
            base_scores = {
                AlertLevel.INFO: 0.1,
                AlertLevel.LOW: 0.3,
                AlertLevel.MEDIUM: 0.5,
                AlertLevel.HIGH: 0.7,
                AlertLevel.CRITICAL: 0.9,
                AlertLevel.EMERGENCY: 1.0
            }
            
            base_score = base_scores.get(alert_level, 0.5)
            
            # 根据偏离程度调整
            if threshold_value != 0:
                deviation_ratio = abs(metric.value - threshold_value) / abs(threshold_value)
                deviation_factor = min(deviation_ratio, 2.0) / 2.0  # 最大2倍偏离
                base_score = min(base_score + deviation_factor * 0.3, 1.0)
            
            # 根据数据质量调整
            quality_factor = metric.quality_score * metric.confidence
            base_score *= quality_factor
            
            return base_score
            
        except Exception as e:
            logger.error(f"计算紧急程度分数失败: {e}")
            return 0.5
    
    def _get_critical_recommendations(self, metric_type: HealthMetricType, direction: str) -> List[str]:
        """获取危急情况建议"""
        recommendations = {
            HealthMetricType.BLOOD_PRESSURE: {
                "high": ["立即就医", "停止所有活动", "监测症状变化", "准备急救药物"],
                "low": ["立即平躺", "抬高双腿", "补充水分", "如症状持续立即就医"]
            },
            HealthMetricType.HEART_RATE: {
                "high": ["立即休息", "深呼吸", "监测心率变化", "如持续过快立即就医"],
                "low": ["避免剧烈活动", "监测意识状态", "立即就医"]
            },
            HealthMetricType.BLOOD_GLUCOSE: {
                "high": ["立即就医", "检查血糖仪", "回顾用药情况", "监测症状"],
                "low": ["立即补充糖分", "监测血糖变化", "如症状严重立即就医"]
            }
        }
        
        return recommendations.get(metric_type, {}).get(direction, ["立即就医", "监测症状变化"])
    
    def _get_warning_recommendations(self, metric_type: HealthMetricType, direction: str) -> List[str]:
        """获取警告情况建议"""
        recommendations = {
            HealthMetricType.BLOOD_PRESSURE: {
                "high": ["减少盐分摄入", "适度运动", "减轻压力", "定期监测"],
                "low": ["增加水分摄入", "避免突然站立", "适当增加盐分"]
            },
            HealthMetricType.HEART_RATE: {
                "high": ["减少咖啡因摄入", "进行放松训练", "检查药物副作用"],
                "low": ["增加有氧运动", "检查甲状腺功能", "咨询医生"]
            }
        }
        
        return recommendations.get(metric_type, {}).get(direction, ["咨询医生", "定期监测"])
    
    def _get_trend_recommendations(self, trend: HealthTrend) -> List[str]:
        """获取趋势建议"""
        if trend.direction == TrendDirection.DECLINING:
            return [
                f"关注{trend.metric_type.value}的持续变化",
                "分析可能的影响因素",
                "考虑调整生活方式或治疗方案",
                "增加监测频率"
            ]
        return ["继续保持当前状态", "定期监测"]
    
    def _get_anomaly_recommendations(self, anomaly: AnomalyDetection) -> List[str]:
        """获取异常建议"""
        return [
            f"检查{anomaly.metric_type.value}测量设备是否正常",
            "回顾最近的活动和环境变化",
            "如异常持续，请咨询医生",
            "增加监测频率以确认趋势"
        ]

class IntelligentHealthMonitor:
    """智能健康监测引擎"""
    
    def __init__(self, config: Dict[str, Any], metrics_collector: Optional[MetricsCollector] = None):
        self.config = config
        self.metrics_collector = metrics_collector
        
        # 核心组件
        self.data_processor = HealthDataProcessor()
        self.anomaly_detector = AnomalyDetector()
        self.trend_analyzer = TrendAnalyzer()
        self.alert_engine = AlertEngine()
        
        # 数据存储
        self.health_metrics: List[HealthMetric] = []
        self.monitoring_profiles: Dict[str, MonitoringProfile] = {}
        self.health_thresholds: Dict[str, Dict[HealthMetricType, HealthThreshold]] = {}
        self.active_alerts: List[HealthAlert] = []
        
        # 监测状态
        self.monitoring_active = False
        self.monitoring_tasks = {}
        
        logger.info("智能健康监测引擎初始化完成")
    
    async def initialize(self):
        """初始化监测引擎"""
        try:
            await self._load_default_thresholds()
            await self._load_monitoring_profiles()
            
            logger.info("健康监测引擎初始化成功")
            
        except Exception as e:
            logger.error(f"健康监测引擎初始化失败: {e}")
    
    async def _load_default_thresholds(self):
        """加载默认健康阈值"""
        default_thresholds = {
            HealthMetricType.HEART_RATE: HealthThreshold(
                metric_type=HealthMetricType.HEART_RATE,
                user_id="default",
                min_normal=60, max_normal=100,
                min_warning=50, max_warning=120,
                min_critical=40, max_critical=150
            ),
            HealthMetricType.BLOOD_PRESSURE: HealthThreshold(
                metric_type=HealthMetricType.BLOOD_PRESSURE,
                user_id="default",
                min_normal=90, max_normal=140,
                min_warning=80, max_warning=160,
                min_critical=70, max_critical=180
            ),
            HealthMetricType.BODY_TEMPERATURE: HealthThreshold(
                metric_type=HealthMetricType.BODY_TEMPERATURE,
                user_id="default",
                min_normal=36.1, max_normal=37.2,
                min_warning=35.5, max_warning=38.0,
                min_critical=35.0, max_critical=39.0
            ),
            HealthMetricType.BLOOD_GLUCOSE: HealthThreshold(
                metric_type=HealthMetricType.BLOOD_GLUCOSE,
                user_id="default",
                min_normal=3.9, max_normal=7.8,
                min_warning=3.5, max_warning=10.0,
                min_critical=2.8, max_critical=15.0
            ),
            HealthMetricType.BLOOD_OXYGEN: HealthThreshold(
                metric_type=HealthMetricType.BLOOD_OXYGEN,
                user_id="default",
                min_normal=95, max_normal=100,
                min_warning=90, max_warning=100,
                min_critical=85, max_critical=100
            )
        }
        
        self.health_thresholds["default"] = default_thresholds
    
    async def _load_monitoring_profiles(self):
        """加载监测配置文件"""
        # 这里应该从数据库加载用户的监测配置
        # 现在创建一个默认配置
        pass
    
    @trace_operation("health_monitor.process_data", SpanKind.INTERNAL)
    async def process_health_data(
        self,
        user_id: str,
        raw_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """处理健康数据"""
        start_time = time.time()
        
        try:
            # 处理原始数据
            processed_metrics = await self.data_processor.process_raw_data(raw_data, user_id)
            
            if not processed_metrics:
                return {"status": "no_valid_data", "processed_metrics": 0}
            
            # 存储数据
            self.health_metrics.extend(processed_metrics)
            
            # 获取历史数据用于分析
            historical_data = await self._get_historical_data(user_id, days=30)
            
            # 异常检测
            anomalies = await self.anomaly_detector.detect_anomalies(
                processed_metrics, user_id, historical_data
            )
            
            # 趋势分析
            trends = await self.trend_analyzer.analyze_trends(
                historical_data + processed_metrics, user_id
            )
            
            # 获取用户阈值
            user_thresholds = self.health_thresholds.get(
                user_id, self.health_thresholds.get("default", {})
            )
            
            # 预警评估
            alerts = await self.alert_engine.evaluate_alerts(
                processed_metrics, user_thresholds, trends, anomalies, user_id
            )
            
            # 更新活跃预警
            self.active_alerts.extend(alerts)
            
            # 发送通知
            if alerts:
                await self._send_notifications(alerts, user_id)
            
            processing_time = time.time() - start_time
            
            # 记录指标
            if self.metrics_collector:
                self.metrics_collector.increment_counter(
                    "health_data_processed",
                    {"user_id": user_id}
                )
                self.metrics_collector.record_histogram(
                    "health_processing_time",
                    processing_time,
                    {"user_id": user_id}
                )
            
            result = {
                "status": "success",
                "processed_metrics": len(processed_metrics),
                "anomalies_detected": len(anomalies),
                "trends_analyzed": len(trends),
                "alerts_generated": len(alerts),
                "processing_time": processing_time,
                "alerts": [
                    {
                        "id": alert.id,
                        "level": alert.alert_level.value,
                        "title": alert.title,
                        "description": alert.description
                    }
                    for alert in alerts
                ]
            }
            
            logger.info(f"健康数据处理完成: {user_id}, 处理{len(processed_metrics)}个指标")
            return result
            
        except Exception as e:
            logger.error(f"健康数据处理失败: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _get_historical_data(self, user_id: str, days: int = 30) -> List[HealthMetric]:
        """获取历史健康数据"""
        cutoff_time = datetime.now() - timedelta(days=days)
        return [
            metric for metric in self.health_metrics
            if metric.user_id == user_id and metric.timestamp >= cutoff_time
        ]
    
    async def _send_notifications(self, alerts: List[HealthAlert], user_id: str):
        """发送通知"""
        try:
            for alert in alerts:
                if alert.alert_level in [AlertLevel.HIGH, AlertLevel.CRITICAL, AlertLevel.EMERGENCY]:
                    # 发送紧急通知
                    logger.warning(f"紧急健康预警: {user_id} - {alert.title}")
                    
                    # 这里应该集成实际的通知系统
                    # 例如：短信、邮件、推送通知等
                    
        except Exception as e:
            logger.error(f"发送通知失败: {e}")
    
    async def get_user_health_summary(self, user_id: str) -> Dict[str, Any]:
        """获取用户健康摘要"""
        try:
            # 获取最近的健康数据
            recent_data = await self._get_historical_data(user_id, days=7)
            
            if not recent_data:
                return {"status": "no_data"}
            
            # 按指标类型分组
            metrics_by_type = {}
            for metric in recent_data:
                if metric.metric_type not in metrics_by_type:
                    metrics_by_type[metric.metric_type] = []
                metrics_by_type[metric.metric_type].append(metric)
            
            # 计算每个指标的统计信息
            summary = {}
            for metric_type, metrics in metrics_by_type.items():
                values = [m.value for m in metrics]
                latest_metric = max(metrics, key=lambda x: x.timestamp)
                
                summary[metric_type.value] = {
                    "latest_value": latest_metric.value,
                    "latest_timestamp": latest_metric.timestamp.isoformat(),
                    "average": np.mean(values),
                    "min": np.min(values),
                    "max": np.max(values),
                    "trend": "stable",  # 简化处理
                    "data_points": len(values)
                }
            
            # 获取活跃预警
            user_alerts = [
                alert for alert in self.active_alerts
                if alert.user_id == user_id and not alert.resolved
            ]
            
            return {
                "status": "success",
                "user_id": user_id,
                "summary_period": "7_days",
                "metrics_summary": summary,
                "active_alerts": len(user_alerts),
                "health_score": await self._calculate_health_score(user_id),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取健康摘要失败: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _calculate_health_score(self, user_id: str) -> float:
        """计算健康分数"""
        try:
            # 简化的健康分数计算
            recent_data = await self._get_historical_data(user_id, days=7)
            
            if not recent_data:
                return 0.0
            
            # 基于数据质量和异常程度计算分数
            quality_scores = [m.quality_score for m in recent_data]
            avg_quality = np.mean(quality_scores)
            
            # 检查是否有高级别预警
            user_alerts = [
                alert for alert in self.active_alerts
                if alert.user_id == user_id and not alert.resolved
            ]
            
            alert_penalty = 0
            for alert in user_alerts:
                if alert.alert_level == AlertLevel.CRITICAL:
                    alert_penalty += 0.3
                elif alert.alert_level == AlertLevel.HIGH:
                    alert_penalty += 0.2
                elif alert.alert_level == AlertLevel.MEDIUM:
                    alert_penalty += 0.1
            
            health_score = max(0, avg_quality - alert_penalty)
            return min(health_score, 1.0)
            
        except Exception as e:
            logger.error(f"计算健康分数失败: {e}")
            return 0.5
    
    async def start_monitoring(self, user_id: str):
        """开始监测"""
        try:
            if user_id in self.monitoring_tasks:
                logger.info(f"用户 {user_id} 已在监测中")
                return
            
            # 创建监测任务
            task = asyncio.create_task(self._monitoring_loop(user_id))
            self.monitoring_tasks[user_id] = task
            
            logger.info(f"开始监测用户: {user_id}")
            
        except Exception as e:
            logger.error(f"开始监测失败: {e}")
    
    async def stop_monitoring(self, user_id: str):
        """停止监测"""
        try:
            if user_id in self.monitoring_tasks:
                task = self.monitoring_tasks[user_id]
                task.cancel()
                del self.monitoring_tasks[user_id]
                
                logger.info(f"停止监测用户: {user_id}")
            
        except Exception as e:
            logger.error(f"停止监测失败: {e}")
    
    async def _monitoring_loop(self, user_id: str):
        """监测循环"""
        try:
            while True:
                # 检查是否有新的健康数据需要处理
                # 这里应该从数据源获取新数据
                
                # 定期清理过期数据
                await self._cleanup_old_data()
                
                # 定期重新评估预警
                await self._reevaluate_alerts(user_id)
                
                # 等待下一次检查
                await asyncio.sleep(60)  # 每分钟检查一次
                
        except asyncio.CancelledError:
            logger.info(f"监测任务已取消: {user_id}")
        except Exception as e:
            logger.error(f"监测循环错误: {e}")
    
    async def _cleanup_old_data(self):
        """清理过期数据"""
        try:
            cutoff_time = datetime.now() - timedelta(days=365)  # 保留一年数据
            
            # 清理过期的健康指标
            self.health_metrics = [
                metric for metric in self.health_metrics
                if metric.timestamp >= cutoff_time
            ]
            
            # 清理已解决的预警
            self.active_alerts = [
                alert for alert in self.active_alerts
                if not alert.resolved or (datetime.now() - alert.created_at).days < 30
            ]
            
        except Exception as e:
            logger.error(f"清理过期数据失败: {e}")
    
    async def _reevaluate_alerts(self, user_id: str):
        """重新评估预警"""
        try:
            # 检查是否有预警可以自动解决
            user_alerts = [
                alert for alert in self.active_alerts
                if alert.user_id == user_id and not alert.resolved
            ]
            
            for alert in user_alerts:
                # 检查预警条件是否仍然满足
                if await self._should_auto_resolve_alert(alert):
                    alert.auto_resolved = True
                    alert.resolved = True
                    alert.resolved_at = datetime.now()
                    
                    logger.info(f"自动解决预警: {alert.id}")
            
        except Exception as e:
            logger.error(f"重新评估预警失败: {e}")
    
    async def _should_auto_resolve_alert(self, alert: HealthAlert) -> bool:
        """判断预警是否应该自动解决"""
        try:
            # 获取最近的相关数据
            recent_metrics = [
                metric for metric in self.health_metrics
                if (metric.user_id == alert.user_id and 
                    metric.metric_type == alert.metric_type and
                    (datetime.now() - metric.timestamp).hours < 2)
            ]
            
            if not recent_metrics:
                return False
            
            # 检查最近的数值是否回到正常范围
            latest_metric = max(recent_metrics, key=lambda x: x.timestamp)
            
            # 简化的自动解决逻辑
            if alert.threshold_value:
                if alert.alert_level == AlertLevel.HIGH:
                    # 如果数值回到阈值范围内，可以自动解决
                    return abs(latest_metric.value - alert.threshold_value) < abs(alert.current_value - alert.threshold_value) * 0.5
            
            return False
            
        except Exception as e:
            logger.error(f"判断自动解决预警失败: {e}")
            return False
    
    async def get_monitoring_statistics(self) -> Dict[str, Any]:
        """获取监测统计信息"""
        try:
            total_metrics = len(self.health_metrics)
            active_users = len(set(metric.user_id for metric in self.health_metrics))
            active_alerts = len([alert for alert in self.active_alerts if not alert.resolved])
            
            # 按指标类型统计
            metrics_by_type = {}
            for metric in self.health_metrics:
                metric_type = metric.metric_type.value
                if metric_type not in metrics_by_type:
                    metrics_by_type[metric_type] = 0
                metrics_by_type[metric_type] += 1
            
            # 按预警级别统计
            alerts_by_level = {}
            for alert in self.active_alerts:
                if not alert.resolved:
                    level = alert.alert_level.value
                    if level not in alerts_by_level:
                        alerts_by_level[level] = 0
                    alerts_by_level[level] += 1
            
            return {
                "total_metrics": total_metrics,
                "active_users": active_users,
                "active_alerts": active_alerts,
                "monitoring_tasks": len(self.monitoring_tasks),
                "metrics_by_type": metrics_by_type,
                "alerts_by_level": alerts_by_level,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"获取监测统计失败: {e}")
            return {}

def initialize_health_monitor(
    config: Dict[str, Any],
    metrics_collector: Optional[MetricsCollector] = None
) -> IntelligentHealthMonitor:
    """初始化智能健康监测引擎"""
    return IntelligentHealthMonitor(config, metrics_collector)

# 全局实例
_health_monitor_instance: Optional[IntelligentHealthMonitor] = None

def get_health_monitor() -> Optional[IntelligentHealthMonitor]:
    """获取健康监测引擎实例"""
    return _health_monitor_instance 