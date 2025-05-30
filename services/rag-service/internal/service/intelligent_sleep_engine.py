#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能睡眠管理引擎 - 提供睡眠质量监测和改善建议
结合中医睡眠养生理念和现代睡眠科学，为用户提供个性化睡眠健康管理
"""

import asyncio
import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta, time
from loguru import logger
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

from ..observability.metrics import MetricsCollector
from ..observability.tracing import trace_operation, SpanKind


class SleepStage(str, Enum):
    """睡眠阶段"""
    AWAKE = "awake"                 # 清醒
    LIGHT_SLEEP = "light_sleep"     # 浅睡眠
    DEEP_SLEEP = "deep_sleep"       # 深睡眠
    REM_SLEEP = "rem_sleep"         # 快速眼动睡眠
    UNKNOWN = "unknown"             # 未知


class SleepQuality(str, Enum):
    """睡眠质量"""
    EXCELLENT = "excellent"         # 优秀 (90-100分)
    GOOD = "good"                   # 良好 (80-89分)
    FAIR = "fair"                   # 一般 (70-79分)
    POOR = "poor"                   # 较差 (60-69分)
    VERY_POOR = "very_poor"         # 很差 (0-59分)


class SleepDisorder(str, Enum):
    """睡眠障碍类型"""
    INSOMNIA = "insomnia"                   # 失眠
    SLEEP_APNEA = "sleep_apnea"             # 睡眠呼吸暂停
    RESTLESS_LEG = "restless_leg"           # 不宁腿综合征
    NARCOLEPSY = "narcolepsy"               # 嗜睡症
    CIRCADIAN_RHYTHM = "circadian_rhythm"   # 昼夜节律紊乱
    NIGHT_TERRORS = "night_terrors"         # 夜惊
    SLEEPWALKING = "sleepwalking"           # 梦游
    SNORING = "snoring"                     # 打鼾
    NONE = "none"                           # 无


class TCMSleepPattern(str, Enum):
    """中医睡眠证型"""
    HEART_KIDNEY_DISHARMONY = "heart_kidney_disharmony"     # 心肾不交
    LIVER_QI_STAGNATION = "liver_qi_stagnation"             # 肝气郁结
    SPLEEN_DEFICIENCY = "spleen_deficiency"                 # 脾虚
    HEART_BLOOD_DEFICIENCY = "heart_blood_deficiency"       # 心血不足
    KIDNEY_YIN_DEFICIENCY = "kidney_yin_deficiency"         # 肾阴虚
    PHLEGM_HEAT = "phlegm_heat"                             # 痰热
    NORMAL = "normal"                                       # 正常


@dataclass
class SleepData:
    """睡眠数据"""
    user_id: str
    date: datetime
    bedtime: time                           # 上床时间
    sleep_onset_time: time                  # 入睡时间
    wake_time: time                         # 起床时间
    total_sleep_time: int                   # 总睡眠时间(分钟)
    sleep_efficiency: float                 # 睡眠效率(%)
    sleep_latency: int                      # 入睡潜伏期(分钟)
    wake_after_sleep_onset: int             # 睡后觉醒时间(分钟)
    number_of_awakenings: int               # 觉醒次数
    # 睡眠阶段分布
    light_sleep_duration: int = 0           # 浅睡眠时长(分钟)
    deep_sleep_duration: int = 0            # 深睡眠时长(分钟)
    rem_sleep_duration: int = 0             # REM睡眠时长(分钟)
    # 生理指标
    average_heart_rate: Optional[float] = None      # 平均心率
    heart_rate_variability: Optional[float] = None  # 心率变异性
    respiratory_rate: Optional[float] = None        # 呼吸频率
    body_temperature: Optional[float] = None        # 体温
    # 环境因素
    room_temperature: Optional[float] = None        # 室温
    humidity: Optional[float] = None                # 湿度
    noise_level: Optional[float] = None             # 噪音水平
    light_exposure: Optional[float] = None          # 光照强度
    # 主观评估
    sleep_quality_rating: Optional[int] = None      # 睡眠质量评分(1-10)
    morning_alertness: Optional[int] = None         # 晨起清醒度(1-10)
    daytime_fatigue: Optional[int] = None           # 日间疲劳度(1-10)
    mood_rating: Optional[int] = None               # 情绪评分(1-10)
    # 生活方式因素
    caffeine_intake: Optional[int] = None           # 咖啡因摄入量(mg)
    alcohol_intake: Optional[int] = None            # 酒精摄入量(ml)
    exercise_duration: Optional[int] = None         # 运动时长(分钟)
    screen_time_before_bed: Optional[int] = None    # 睡前屏幕时间(分钟)
    stress_level: Optional[int] = None              # 压力水平(1-10)
    # 中医相关
    tcm_sleep_pattern: Optional[TCMSleepPattern] = None
    tongue_coating: Optional[str] = None            # 舌苔
    pulse_condition: Optional[str] = None           # 脉象
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SleepAnalysis:
    """睡眠分析结果"""
    user_id: str
    analysis_date: datetime
    period_start: datetime
    period_end: datetime
    # 睡眠质量评估
    overall_sleep_quality: SleepQuality
    sleep_score: float                      # 综合睡眠评分(0-100)
    # 睡眠模式分析
    average_bedtime: time
    average_wake_time: time
    average_sleep_duration: float           # 平均睡眠时长(小时)
    sleep_consistency_score: float          # 睡眠一致性评分(0-100)
    # 睡眠阶段分析
    sleep_stage_distribution: Dict[SleepStage, float] = field(default_factory=dict)
    sleep_architecture_score: float = 0.0   # 睡眠结构评分(0-100)
    # 睡眠效率分析
    average_sleep_efficiency: float
    average_sleep_latency: float
    average_wake_episodes: float
    # 趋势分析
    sleep_quality_trend: str               # improving, stable, declining
    sleep_duration_trend: str              # increasing, stable, decreasing
    # 影响因素分析
    primary_sleep_disruptors: List[str] = field(default_factory=list)
    beneficial_factors: List[str] = field(default_factory=list)
    # 中医分析
    tcm_pattern_analysis: Optional[TCMSleepPattern] = None
    tcm_recommendations: List[str] = field(default_factory=list)
    # 建议
    recommendations: List[str] = field(default_factory=list)
    priority_actions: List[str] = field(default_factory=list)


@dataclass
class SleepGoal:
    """睡眠目标"""
    user_id: str
    goal_type: str                          # duration, quality, consistency, bedtime
    target_value: float
    current_value: float
    target_date: datetime
    progress_percentage: float = 0.0
    is_achieved: bool = False
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SleepIntervention:
    """睡眠干预措施"""
    id: str
    name: str
    description: str
    category: str                           # behavioral, environmental, medical, tcm
    intervention_type: str                  # sleep_hygiene, relaxation, medication, etc.
    instructions: List[str] = field(default_factory=list)
    duration_weeks: int = 4
    expected_benefits: List[str] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)
    evidence_level: str = "moderate"        # high, moderate, low
    # 中医相关
    tcm_principles: List[str] = field(default_factory=list)
    suitable_constitutions: List[str] = field(default_factory=list)


class SleepDataProcessor:
    """睡眠数据处理器"""
    
    def __init__(self):
        self.sleep_data: Dict[str, List[SleepData]] = {}
        self.sleep_norms = self._load_sleep_norms()
    
    def _load_sleep_norms(self) -> Dict[str, Any]:
        """加载睡眠标准"""
        return {
            "total_sleep_time": {
                "18-25": {"min": 420, "max": 540},      # 7-9小时
                "26-64": {"min": 420, "max": 540},      # 7-9小时
                "65+": {"min": 420, "max": 480}         # 7-8小时
            },
            "sleep_efficiency": {"optimal": 85, "good": 80, "fair": 75},
            "sleep_latency": {"optimal": 15, "good": 20, "fair": 30},
            "deep_sleep_percentage": {"optimal": 20, "good": 15, "fair": 10},
            "rem_sleep_percentage": {"optimal": 25, "good": 20, "fair": 15}
        }
    
    async def process_sleep_data(self, sleep_data: SleepData) -> Dict[str, Any]:
        """处理睡眠数据"""
        try:
            # 存储数据
            if sleep_data.user_id not in self.sleep_data:
                self.sleep_data[sleep_data.user_id] = []
            self.sleep_data[sleep_data.user_id].append(sleep_data)
            
            # 计算睡眠质量评分
            quality_score = await self._calculate_sleep_quality_score(sleep_data)
            
            # 检测睡眠异常
            anomalies = await self._detect_sleep_anomalies(sleep_data)
            
            # 分析睡眠模式
            patterns = await self._analyze_sleep_patterns(sleep_data.user_id)
            
            return {
                "quality_score": quality_score,
                "anomalies": anomalies,
                "patterns": patterns,
                "processed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"处理睡眠数据失败: {e}")
            raise
    
    async def _calculate_sleep_quality_score(self, sleep_data: SleepData) -> float:
        """计算睡眠质量评分"""
        score = 0.0
        max_score = 100.0
        
        # 睡眠时长评分 (30分)
        duration_hours = sleep_data.total_sleep_time / 60
        if 7 <= duration_hours <= 9:
            score += 30
        elif 6 <= duration_hours < 7 or 9 < duration_hours <= 10:
            score += 20
        elif 5 <= duration_hours < 6 or 10 < duration_hours <= 11:
            score += 10
        
        # 睡眠效率评分 (25分)
        if sleep_data.sleep_efficiency >= 85:
            score += 25
        elif sleep_data.sleep_efficiency >= 80:
            score += 20
        elif sleep_data.sleep_efficiency >= 75:
            score += 15
        elif sleep_data.sleep_efficiency >= 70:
            score += 10
        
        # 入睡潜伏期评分 (20分)
        if sleep_data.sleep_latency <= 15:
            score += 20
        elif sleep_data.sleep_latency <= 20:
            score += 15
        elif sleep_data.sleep_latency <= 30:
            score += 10
        elif sleep_data.sleep_latency <= 45:
            score += 5
        
        # 觉醒次数评分 (15分)
        if sleep_data.number_of_awakenings <= 1:
            score += 15
        elif sleep_data.number_of_awakenings <= 2:
            score += 10
        elif sleep_data.number_of_awakenings <= 3:
            score += 5
        
        # 主观评分 (10分)
        if sleep_data.sleep_quality_rating:
            subjective_score = (sleep_data.sleep_quality_rating / 10) * 10
            score += subjective_score
        
        return min(score, max_score)
    
    async def _detect_sleep_anomalies(self, sleep_data: SleepData) -> List[str]:
        """检测睡眠异常"""
        anomalies = []
        
        # 睡眠时长异常
        duration_hours = sleep_data.total_sleep_time / 60
        if duration_hours < 5:
            anomalies.append("睡眠时间严重不足")
        elif duration_hours > 11:
            anomalies.append("睡眠时间过长")
        
        # 入睡困难
        if sleep_data.sleep_latency > 60:
            anomalies.append("入睡困难")
        
        # 睡眠效率低
        if sleep_data.sleep_efficiency < 70:
            anomalies.append("睡眠效率低")
        
        # 频繁觉醒
        if sleep_data.number_of_awakenings > 5:
            anomalies.append("频繁觉醒")
        
        # 深睡眠不足
        if sleep_data.deep_sleep_duration < 60:  # 少于1小时
            anomalies.append("深睡眠不足")
        
        # 心率异常
        if sleep_data.average_heart_rate:
            if sleep_data.average_heart_rate > 80:
                anomalies.append("睡眠心率偏高")
            elif sleep_data.average_heart_rate < 45:
                anomalies.append("睡眠心率偏低")
        
        return anomalies
    
    async def _analyze_sleep_patterns(self, user_id: str) -> Dict[str, Any]:
        """分析睡眠模式"""
        user_data = self.sleep_data.get(user_id, [])
        if len(user_data) < 7:  # 至少需要一周数据
            return {"status": "insufficient_data"}
        
        recent_data = sorted(user_data, key=lambda x: x.date)[-30:]  # 最近30天
        
        # 计算平均值
        avg_bedtime = self._calculate_average_time([d.bedtime for d in recent_data])
        avg_wake_time = self._calculate_average_time([d.wake_time for d in recent_data])
        avg_duration = np.mean([d.total_sleep_time for d in recent_data])
        avg_efficiency = np.mean([d.sleep_efficiency for d in recent_data])
        
        # 计算一致性
        bedtime_consistency = self._calculate_time_consistency([d.bedtime for d in recent_data])
        wake_consistency = self._calculate_time_consistency([d.wake_time for d in recent_data])
        
        # 趋势分析
        quality_trend = self._analyze_trend([d.sleep_quality_rating or 5 for d in recent_data])
        duration_trend = self._analyze_trend([d.total_sleep_time for d in recent_data])
        
        return {
            "average_bedtime": avg_bedtime.strftime("%H:%M"),
            "average_wake_time": avg_wake_time.strftime("%H:%M"),
            "average_duration_hours": avg_duration / 60,
            "average_efficiency": avg_efficiency,
            "bedtime_consistency": bedtime_consistency,
            "wake_consistency": wake_consistency,
            "quality_trend": quality_trend,
            "duration_trend": duration_trend
        }
    
    def _calculate_average_time(self, times: List[time]) -> time:
        """计算平均时间"""
        total_minutes = sum(t.hour * 60 + t.minute for t in times)
        avg_minutes = total_minutes / len(times)
        hours = int(avg_minutes // 60)
        minutes = int(avg_minutes % 60)
        return time(hours % 24, minutes)
    
    def _calculate_time_consistency(self, times: List[time]) -> float:
        """计算时间一致性评分"""
        if len(times) < 2:
            return 100.0
        
        # 转换为分钟数
        minutes = [t.hour * 60 + t.minute for t in times]
        
        # 处理跨午夜的情况
        for i in range(len(minutes)):
            if minutes[i] < 12 * 60:  # 假设小于12点的是第二天
                minutes[i] += 24 * 60
        
        # 计算标准差
        std_dev = np.std(minutes)
        
        # 转换为一致性评分 (标准差越小，一致性越高)
        consistency = max(0, 100 - std_dev / 2)
        return consistency
    
    def _analyze_trend(self, values: List[float]) -> str:
        """分析趋势"""
        if len(values) < 3:
            return "stable"
        
        # 使用线性回归分析趋势
        x = np.arange(len(values))
        slope, _ = np.polyfit(x, values, 1)
        
        if slope > 0.1:
            return "improving"
        elif slope < -0.1:
            return "declining"
        else:
            return "stable"


class SleepAnalyzer:
    """睡眠分析器"""
    
    def __init__(self):
        self.tcm_patterns = self._load_tcm_patterns()
    
    def _load_tcm_patterns(self) -> Dict[str, Any]:
        """加载中医睡眠证型"""
        return {
            TCMSleepPattern.HEART_KIDNEY_DISHARMONY: {
                "symptoms": ["入睡困难", "多梦", "心悸", "腰酸", "头晕"],
                "tongue": "舌红少苔",
                "pulse": "细数",
                "treatment_principle": "滋阴降火，交通心肾"
            },
            TCMSleepPattern.LIVER_QI_STAGNATION: {
                "symptoms": ["入睡困难", "易醒", "烦躁", "胸闷", "叹息"],
                "tongue": "舌苔薄白",
                "pulse": "弦",
                "treatment_principle": "疏肝解郁，宁心安神"
            },
            TCMSleepPattern.SPLEEN_DEFICIENCY: {
                "symptoms": ["嗜睡", "疲倦", "食欲不振", "腹胀", "便溏"],
                "tongue": "舌淡苔白",
                "pulse": "缓弱",
                "treatment_principle": "健脾益气，化湿安神"
            },
            TCMSleepPattern.HEART_BLOOD_DEFICIENCY: {
                "symptoms": ["多梦", "易醒", "心悸", "健忘", "面色苍白"],
                "tongue": "舌淡",
                "pulse": "细弱",
                "treatment_principle": "补血养心，宁神定志"
            }
        }
    
    async def analyze_sleep_comprehensive(
        self, 
        user_id: str, 
        sleep_data: List[SleepData],
        period_days: int = 30
    ) -> SleepAnalysis:
        """综合睡眠分析"""
        try:
            if not sleep_data:
                raise ValueError("睡眠数据为空")
            
            # 筛选分析期间的数据
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            period_data = [
                d for d in sleep_data 
                if start_date <= d.date <= end_date
            ]
            
            if not period_data:
                raise ValueError("分析期间无睡眠数据")
            
            # 基础分析
            overall_quality = await self._assess_overall_quality(period_data)
            sleep_score = await self._calculate_comprehensive_score(period_data)
            
            # 睡眠模式分析
            avg_bedtime, avg_wake_time = self._calculate_average_times(period_data)
            avg_duration = np.mean([d.total_sleep_time for d in period_data]) / 60
            consistency_score = self._calculate_consistency_score(period_data)
            
            # 睡眠阶段分析
            stage_distribution = self._analyze_sleep_stages(period_data)
            architecture_score = self._calculate_architecture_score(stage_distribution)
            
            # 睡眠效率分析
            avg_efficiency = np.mean([d.sleep_efficiency for d in period_data])
            avg_latency = np.mean([d.sleep_latency for d in period_data])
            avg_awakenings = np.mean([d.number_of_awakenings for d in period_data])
            
            # 趋势分析
            quality_trend = self._analyze_quality_trend(period_data)
            duration_trend = self._analyze_duration_trend(period_data)
            
            # 影响因素分析
            disruptors, beneficial = await self._analyze_influencing_factors(period_data)
            
            # 中医分析
            tcm_pattern = await self._analyze_tcm_pattern(period_data)
            tcm_recommendations = self._generate_tcm_recommendations(tcm_pattern)
            
            # 生成建议
            recommendations = await self._generate_recommendations(period_data, overall_quality)
            priority_actions = self._identify_priority_actions(period_data)
            
            analysis = SleepAnalysis(
                user_id=user_id,
                analysis_date=datetime.now(),
                period_start=start_date,
                period_end=end_date,
                overall_sleep_quality=overall_quality,
                sleep_score=sleep_score,
                average_bedtime=avg_bedtime,
                average_wake_time=avg_wake_time,
                average_sleep_duration=avg_duration,
                sleep_consistency_score=consistency_score,
                sleep_stage_distribution=stage_distribution,
                sleep_architecture_score=architecture_score,
                average_sleep_efficiency=avg_efficiency,
                average_sleep_latency=avg_latency,
                average_wake_episodes=avg_awakenings,
                sleep_quality_trend=quality_trend,
                sleep_duration_trend=duration_trend,
                primary_sleep_disruptors=disruptors,
                beneficial_factors=beneficial,
                tcm_pattern_analysis=tcm_pattern,
                tcm_recommendations=tcm_recommendations,
                recommendations=recommendations,
                priority_actions=priority_actions
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"综合睡眠分析失败: {e}")
            raise
    
    async def _assess_overall_quality(self, sleep_data: List[SleepData]) -> SleepQuality:
        """评估整体睡眠质量"""
        scores = []
        for data in sleep_data:
            score = 0
            
            # 睡眠时长评分
            duration_hours = data.total_sleep_time / 60
            if 7 <= duration_hours <= 9:
                score += 25
            elif 6 <= duration_hours < 7 or 9 < duration_hours <= 10:
                score += 15
            
            # 睡眠效率评分
            if data.sleep_efficiency >= 85:
                score += 25
            elif data.sleep_efficiency >= 80:
                score += 15
            
            # 入睡潜伏期评分
            if data.sleep_latency <= 15:
                score += 25
            elif data.sleep_latency <= 30:
                score += 15
            
            # 主观评分
            if data.sleep_quality_rating:
                score += (data.sleep_quality_rating / 10) * 25
            
            scores.append(score)
        
        avg_score = np.mean(scores)
        
        if avg_score >= 90:
            return SleepQuality.EXCELLENT
        elif avg_score >= 80:
            return SleepQuality.GOOD
        elif avg_score >= 70:
            return SleepQuality.FAIR
        elif avg_score >= 60:
            return SleepQuality.POOR
        else:
            return SleepQuality.VERY_POOR
    
    async def _calculate_comprehensive_score(self, sleep_data: List[SleepData]) -> float:
        """计算综合睡眠评分"""
        total_score = 0
        count = 0
        
        for data in sleep_data:
            # 使用之前定义的评分方法
            processor = SleepDataProcessor()
            score = await processor._calculate_sleep_quality_score(data)
            total_score += score
            count += 1
        
        return total_score / count if count > 0 else 0
    
    def _calculate_average_times(self, sleep_data: List[SleepData]) -> Tuple[time, time]:
        """计算平均就寝和起床时间"""
        processor = SleepDataProcessor()
        avg_bedtime = processor._calculate_average_time([d.bedtime for d in sleep_data])
        avg_wake_time = processor._calculate_average_time([d.wake_time for d in sleep_data])
        return avg_bedtime, avg_wake_time
    
    def _calculate_consistency_score(self, sleep_data: List[SleepData]) -> float:
        """计算睡眠一致性评分"""
        processor = SleepDataProcessor()
        bedtime_consistency = processor._calculate_time_consistency([d.bedtime for d in sleep_data])
        wake_consistency = processor._calculate_time_consistency([d.wake_time for d in sleep_data])
        return (bedtime_consistency + wake_consistency) / 2
    
    def _analyze_sleep_stages(self, sleep_data: List[SleepData]) -> Dict[SleepStage, float]:
        """分析睡眠阶段分布"""
        total_sleep = sum(d.total_sleep_time for d in sleep_data)
        
        if total_sleep == 0:
            return {}
        
        total_light = sum(d.light_sleep_duration for d in sleep_data)
        total_deep = sum(d.deep_sleep_duration for d in sleep_data)
        total_rem = sum(d.rem_sleep_duration for d in sleep_data)
        
        return {
            SleepStage.LIGHT_SLEEP: (total_light / total_sleep) * 100,
            SleepStage.DEEP_SLEEP: (total_deep / total_sleep) * 100,
            SleepStage.REM_SLEEP: (total_rem / total_sleep) * 100
        }
    
    def _calculate_architecture_score(self, stage_distribution: Dict[SleepStage, float]) -> float:
        """计算睡眠结构评分"""
        score = 0
        
        # 深睡眠比例评分 (40分)
        deep_sleep_pct = stage_distribution.get(SleepStage.DEEP_SLEEP, 0)
        if deep_sleep_pct >= 20:
            score += 40
        elif deep_sleep_pct >= 15:
            score += 30
        elif deep_sleep_pct >= 10:
            score += 20
        
        # REM睡眠比例评分 (40分)
        rem_sleep_pct = stage_distribution.get(SleepStage.REM_SLEEP, 0)
        if rem_sleep_pct >= 20:
            score += 40
        elif rem_sleep_pct >= 15:
            score += 30
        elif rem_sleep_pct >= 10:
            score += 20
        
        # 浅睡眠比例评分 (20分)
        light_sleep_pct = stage_distribution.get(SleepStage.LIGHT_SLEEP, 0)
        if 40 <= light_sleep_pct <= 60:
            score += 20
        elif 30 <= light_sleep_pct < 40 or 60 < light_sleep_pct <= 70:
            score += 15
        
        return score
    
    def _analyze_quality_trend(self, sleep_data: List[SleepData]) -> str:
        """分析睡眠质量趋势"""
        if len(sleep_data) < 7:
            return "stable"
        
        # 按日期排序
        sorted_data = sorted(sleep_data, key=lambda x: x.date)
        
        # 计算每日质量评分
        quality_scores = []
        for data in sorted_data:
            score = (data.sleep_quality_rating or 5) * 10  # 转换为0-100分
            quality_scores.append(score)
        
        # 分析趋势
        processor = SleepDataProcessor()
        return processor._analyze_trend(quality_scores)
    
    def _analyze_duration_trend(self, sleep_data: List[SleepData]) -> str:
        """分析睡眠时长趋势"""
        if len(sleep_data) < 7:
            return "stable"
        
        sorted_data = sorted(sleep_data, key=lambda x: x.date)
        durations = [d.total_sleep_time for d in sorted_data]
        
        processor = SleepDataProcessor()
        return processor._analyze_trend(durations)
    
    async def _analyze_influencing_factors(
        self, 
        sleep_data: List[SleepData]
    ) -> Tuple[List[str], List[str]]:
        """分析影响因素"""
        disruptors = []
        beneficial = []
        
        # 分析各种因素与睡眠质量的关系
        for data in sleep_data:
            quality_score = data.sleep_quality_rating or 5
            
            # 咖啡因影响
            if data.caffeine_intake and data.caffeine_intake > 200:
                if quality_score < 6:
                    disruptors.append("咖啡因摄入过多")
            
            # 酒精影响
            if data.alcohol_intake and data.alcohol_intake > 50:
                if quality_score < 6:
                    disruptors.append("酒精摄入")
            
            # 屏幕时间影响
            if data.screen_time_before_bed and data.screen_time_before_bed > 60:
                if quality_score < 6:
                    disruptors.append("睡前屏幕时间过长")
            
            # 压力水平影响
            if data.stress_level and data.stress_level > 7:
                if quality_score < 6:
                    disruptors.append("压力水平过高")
            
            # 运动的积极影响
            if data.exercise_duration and data.exercise_duration > 30:
                if quality_score >= 7:
                    beneficial.append("适量运动")
            
            # 环境因素
            if data.room_temperature:
                if data.room_temperature < 16 or data.room_temperature > 24:
                    if quality_score < 6:
                        disruptors.append("室温不适宜")
                else:
                    if quality_score >= 7:
                        beneficial.append("适宜的室温")
        
        # 去重并统计频率
        disruptor_counts = {}
        beneficial_counts = {}
        
        for item in disruptors:
            disruptor_counts[item] = disruptor_counts.get(item, 0) + 1
        
        for item in beneficial:
            beneficial_counts[item] = beneficial_counts.get(item, 0) + 1
        
        # 返回出现频率最高的因素
        top_disruptors = sorted(disruptor_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_beneficial = sorted(beneficial_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return [item[0] for item in top_disruptors], [item[0] for item in top_beneficial]
    
    async def _analyze_tcm_pattern(self, sleep_data: List[SleepData]) -> Optional[TCMSleepPattern]:
        """分析中医睡眠证型"""
        # 统计症状模式
        pattern_scores = {}
        
        for pattern in TCMSleepPattern:
            if pattern == TCMSleepPattern.NORMAL:
                continue
            pattern_scores[pattern] = 0
        
        for data in sleep_data:
            # 根据睡眠特征判断证型
            
            # 心肾不交：入睡困难 + 多梦
            if data.sleep_latency > 30 and data.number_of_awakenings > 3:
                pattern_scores[TCMSleepPattern.HEART_KIDNEY_DISHARMONY] += 1
            
            # 肝气郁结：入睡困难 + 易醒
            if data.sleep_latency > 30 and data.wake_after_sleep_onset > 60:
                pattern_scores[TCMSleepPattern.LIVER_QI_STAGNATION] += 1
            
            # 脾虚：嗜睡（睡眠时间过长）
            if data.total_sleep_time > 600:  # 超过10小时
                pattern_scores[TCMSleepPattern.SPLEEN_DEFICIENCY] += 1
            
            # 心血不足：多梦 + 易醒
            if data.number_of_awakenings > 4 and data.rem_sleep_duration > 150:
                pattern_scores[TCMSleepPattern.HEART_BLOOD_DEFICIENCY] += 1
        
        # 找出得分最高的证型
        if pattern_scores:
            max_pattern = max(pattern_scores, key=pattern_scores.get)
            if pattern_scores[max_pattern] > len(sleep_data) * 0.3:  # 至少30%的数据支持
                return max_pattern
        
        return TCMSleepPattern.NORMAL
    
    def _generate_tcm_recommendations(self, tcm_pattern: Optional[TCMSleepPattern]) -> List[str]:
        """生成中医建议"""
        if not tcm_pattern or tcm_pattern == TCMSleepPattern.NORMAL:
            return ["睡眠模式正常，继续保持良好的睡眠习惯"]
        
        pattern_info = self.tcm_patterns.get(tcm_pattern, {})
        recommendations = []
        
        if tcm_pattern == TCMSleepPattern.HEART_KIDNEY_DISHARMONY:
            recommendations.extend([
                "建议滋阴降火，可服用知柏地黄丸",
                "睡前泡脚，按摩涌泉穴",
                "避免辛辣刺激食物",
                "保持心情平静，减少思虑"
            ])
        elif tcm_pattern == TCMSleepPattern.LIVER_QI_STAGNATION:
            recommendations.extend([
                "建议疏肝解郁，可服用逍遥散",
                "睡前按摩太冲穴、三阴交穴",
                "适当运动，如散步、太极",
                "保持情绪稳定，避免生气"
            ])
        elif tcm_pattern == TCMSleepPattern.SPLEEN_DEFICIENCY:
            recommendations.extend([
                "建议健脾益气，可服用参苓白术散",
                "规律作息，避免过度睡眠",
                "饮食清淡，避免生冷食物",
                "适当运动，增强体质"
            ])
        elif tcm_pattern == TCMSleepPattern.HEART_BLOOD_DEFICIENCY:
            recommendations.extend([
                "建议补血养心，可服用归脾汤",
                "睡前按摩神门穴、心俞穴",
                "多食红枣、桂圆等补血食物",
                "避免过度用脑，注意休息"
            ])
        
        return recommendations
    
    async def _generate_recommendations(
        self, 
        sleep_data: List[SleepData], 
        overall_quality: SleepQuality
    ) -> List[str]:
        """生成睡眠改善建议"""
        recommendations = []
        
        # 基于整体质量的建议
        if overall_quality in [SleepQuality.POOR, SleepQuality.VERY_POOR]:
            recommendations.append("建议咨询睡眠专科医生，进行专业评估")
        
        # 分析具体问题并给出建议
        avg_latency = np.mean([d.sleep_latency for d in sleep_data])
        avg_efficiency = np.mean([d.sleep_efficiency for d in sleep_data])
        avg_duration = np.mean([d.total_sleep_time for d in sleep_data]) / 60
        
        # 入睡困难
        if avg_latency > 30:
            recommendations.extend([
                "建立固定的睡前例行程序",
                "睡前1小时避免使用电子设备",
                "尝试放松技巧，如深呼吸或冥想",
                "确保卧室环境安静、黑暗、凉爽"
            ])
        
        # 睡眠效率低
        if avg_efficiency < 80:
            recommendations.extend([
                "限制在床上的时间，只在困倦时上床",
                "如果20分钟内无法入睡，起床进行安静活动",
                "避免在床上进行睡眠以外的活动"
            ])
        
        # 睡眠时间不足
        if avg_duration < 7:
            recommendations.extend([
                "逐步提前就寝时间",
                "评估并减少晚间活动",
                "确保有足够的睡眠机会"
            ])
        
        # 睡眠时间过长
        if avg_duration > 9:
            recommendations.extend([
                "设定固定的起床时间",
                "避免白天长时间午睡",
                "增加日间活动量"
            ])
        
        # 生活方式建议
        recommendations.extend([
            "保持规律的作息时间",
            "白天适量运动，但避免睡前3小时剧烈运动",
            "限制咖啡因摄入，特别是下午和晚上",
            "创造舒适的睡眠环境"
        ])
        
        return recommendations
    
    def _identify_priority_actions(self, sleep_data: List[SleepData]) -> List[str]:
        """识别优先改善行动"""
        priority_actions = []
        
        # 计算平均值
        avg_latency = np.mean([d.sleep_latency for d in sleep_data])
        avg_efficiency = np.mean([d.sleep_efficiency for d in sleep_data])
        avg_awakenings = np.mean([d.number_of_awakenings for d in sleep_data])
        
        # 按严重程度排序
        issues = []
        
        if avg_latency > 45:
            issues.append(("严重入睡困难", "立即建立睡前放松程序"))
        elif avg_latency > 30:
            issues.append(("入睡困难", "改善睡前习惯"))
        
        if avg_efficiency < 70:
            issues.append(("睡眠效率极低", "限制在床时间，提高睡眠效率"))
        elif avg_efficiency < 80:
            issues.append(("睡眠效率偏低", "优化睡眠环境"))
        
        if avg_awakenings > 5:
            issues.append(("频繁觉醒", "检查睡眠环境和健康状况"))
        
        # 返回前3个优先问题
        priority_actions = [action for _, action in issues[:3]]
        
        if not priority_actions:
            priority_actions.append("继续保持良好的睡眠习惯")
        
        return priority_actions


class IntelligentSleepEngine:
    """智能睡眠管理引擎主类"""
    
    def __init__(self, config: Dict[str, Any], metrics_collector: Optional[MetricsCollector] = None):
        self.config = config
        self.metrics_collector = metrics_collector
        
        # 核心组件
        self.data_processor = SleepDataProcessor()
        self.analyzer = SleepAnalyzer()
        
        # 数据存储
        self.sleep_analyses: Dict[str, List[SleepAnalysis]] = {}
        self.sleep_goals: Dict[str, List[SleepGoal]] = {}
        self.interventions = self._load_interventions()
        
        # 运行状态
        self.initialized = False
    
    def _load_interventions(self) -> Dict[str, SleepIntervention]:
        """加载睡眠干预措施"""
        interventions = {}
        
        # 睡眠卫生干预
        interventions["sleep_hygiene"] = SleepIntervention(
            id="sleep_hygiene",
            name="睡眠卫生改善",
            description="建立良好的睡眠习惯和环境",
            category="behavioral",
            intervention_type="sleep_hygiene",
            instructions=[
                "保持规律的作息时间",
                "创造舒适的睡眠环境",
                "避免睡前使用电子设备",
                "限制咖啡因和酒精摄入"
            ],
            expected_benefits=["改善睡眠质量", "缩短入睡时间", "减少夜间觉醒"],
            evidence_level="high"
        )
        
        # 放松训练
        interventions["relaxation"] = SleepIntervention(
            id="relaxation",
            name="放松训练",
            description="通过放松技巧改善睡眠",
            category="behavioral",
            intervention_type="relaxation",
            instructions=[
                "深呼吸练习",
                "渐进性肌肉放松",
                "冥想或正念练习",
                "听舒缓音乐"
            ],
            expected_benefits=["减少入睡焦虑", "改善睡眠质量", "增强放松感"],
            evidence_level="high"
        )
        
        # 中医调理
        interventions["tcm_regulation"] = SleepIntervention(
            id="tcm_regulation",
            name="中医调理",
            description="运用中医理论调理睡眠",
            category="tcm",
            intervention_type="tcm_therapy",
            instructions=[
                "根据体质选择合适的中药方剂",
                "进行穴位按摩和针灸",
                "调整饮食结构",
                "练习太极或气功"
            ],
            expected_benefits=["调和阴阳", "安神定志", "改善整体健康"],
            tcm_principles=["调和阴阳", "宁心安神", "补虚泻实"],
            evidence_level="moderate"
        )
        
        return interventions
    
    async def initialize(self):
        """初始化睡眠管理引擎"""
        try:
            self.initialized = True
            logger.info("智能睡眠管理引擎初始化完成")
        except Exception as e:
            logger.error(f"睡眠管理引擎初始化失败: {e}")
            raise
    
    @trace_operation("sleep_engine.process_data", SpanKind.INTERNAL)
    async def process_sleep_data(self, sleep_data: SleepData) -> Dict[str, Any]:
        """处理睡眠数据"""
        try:
            if not self.initialized:
                await self.initialize()
            
            result = await self.data_processor.process_sleep_data(sleep_data)
            
            # 记录指标
            if self.metrics_collector:
                await self.metrics_collector.increment_counter(
                    "sleep_data_processed",
                    {"user_id": sleep_data.user_id}
                )
            
            return result
            
        except Exception as e:
            logger.error(f"处理睡眠数据失败: {e}")
            raise
    
    @trace_operation("sleep_engine.analyze_sleep", SpanKind.INTERNAL)
    async def analyze_sleep_comprehensive(
        self, 
        user_id: str, 
        period_days: int = 30
    ) -> SleepAnalysis:
        """综合睡眠分析"""
        try:
            if not self.initialized:
                await self.initialize()
            
            # 获取用户睡眠数据
            user_sleep_data = self.data_processor.sleep_data.get(user_id, [])
            
            if not user_sleep_data:
                raise ValueError(f"用户 {user_id} 无睡眠数据")
            
            # 进行综合分析
            analysis = await self.analyzer.analyze_sleep_comprehensive(
                user_id, user_sleep_data, period_days
            )
            
            # 存储分析结果
            if user_id not in self.sleep_analyses:
                self.sleep_analyses[user_id] = []
            self.sleep_analyses[user_id].append(analysis)
            
            # 记录指标
            if self.metrics_collector:
                await self.metrics_collector.increment_counter(
                    "sleep_analyses_completed",
                    {
                        "user_id": user_id,
                        "quality": analysis.overall_sleep_quality.value
                    }
                )
            
            return analysis
            
        except Exception as e:
            logger.error(f"综合睡眠分析失败: {e}")
            raise
    
    async def get_sleep_recommendations(
        self, 
        user_id: str,
        focus_area: str = "general"
    ) -> List[str]:
        """获取睡眠改善建议"""
        try:
            # 获取最新分析结果
            user_analyses = self.sleep_analyses.get(user_id, [])
            if not user_analyses:
                return ["请先进行睡眠分析以获取个性化建议"]
            
            latest_analysis = max(user_analyses, key=lambda x: x.analysis_date)
            
            recommendations = []
            
            if focus_area == "tcm":
                recommendations.extend(latest_analysis.tcm_recommendations)
            elif focus_area == "priority":
                recommendations.extend(latest_analysis.priority_actions)
            else:
                recommendations.extend(latest_analysis.recommendations)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"获取睡眠建议失败: {e}")
            return ["获取建议时出现错误，请稍后重试"]
    
    async def create_sleep_goal(
        self, 
        user_id: str, 
        goal_data: Dict[str, Any]
    ) -> SleepGoal:
        """创建睡眠目标"""
        try:
            goal = SleepGoal(
                user_id=user_id,
                goal_type=goal_data["goal_type"],
                target_value=goal_data["target_value"],
                current_value=goal_data["current_value"],
                target_date=datetime.fromisoformat(goal_data["target_date"])
            )
            
            if user_id not in self.sleep_goals:
                self.sleep_goals[user_id] = []
            self.sleep_goals[user_id].append(goal)
            
            return goal
            
        except Exception as e:
            logger.error(f"创建睡眠目标失败: {e}")
            raise
    
    async def get_sleep_statistics(self, user_id: str) -> Dict[str, Any]:
        """获取睡眠统计"""
        try:
            user_data = self.data_processor.sleep_data.get(user_id, [])
            if not user_data:
                return {"error": "无睡眠数据"}
            
            recent_data = sorted(user_data, key=lambda x: x.date)[-30:]  # 最近30天
            
            stats = {
                "total_records": len(user_data),
                "recent_records": len(recent_data),
                "average_sleep_duration": np.mean([d.total_sleep_time for d in recent_data]) / 60,
                "average_sleep_efficiency": np.mean([d.sleep_efficiency for d in recent_data]),
                "average_sleep_latency": np.mean([d.sleep_latency for d in recent_data]),
                "sleep_quality_distribution": {},
                "latest_analysis": None
            }
            
            # 睡眠质量分布
            quality_ratings = [d.sleep_quality_rating for d in recent_data if d.sleep_quality_rating]
            if quality_ratings:
                for rating in range(1, 11):
                    count = quality_ratings.count(rating)
                    stats["sleep_quality_distribution"][str(rating)] = count
            
            # 最新分析结果
            user_analyses = self.sleep_analyses.get(user_id, [])
            if user_analyses:
                latest = max(user_analyses, key=lambda x: x.analysis_date)
                stats["latest_analysis"] = {
                    "date": latest.analysis_date.isoformat(),
                    "overall_quality": latest.overall_sleep_quality.value,
                    "sleep_score": latest.sleep_score,
                    "quality_trend": latest.sleep_quality_trend
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"获取睡眠统计失败: {e}")
            return {"error": str(e)}


# 全局睡眠管理引擎实例
_sleep_engine: Optional[IntelligentSleepEngine] = None


def initialize_sleep_engine(
    config: Dict[str, Any],
    metrics_collector: Optional[MetricsCollector] = None
) -> IntelligentSleepEngine:
    """初始化睡眠管理引擎"""
    global _sleep_engine
    _sleep_engine = IntelligentSleepEngine(config, metrics_collector)
    return _sleep_engine


def get_sleep_engine() -> Optional[IntelligentSleepEngine]:
    """获取睡眠管理引擎实例"""
    return _sleep_engine 