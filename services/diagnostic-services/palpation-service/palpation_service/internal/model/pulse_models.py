#!/usr/bin/env python

"""
脉诊数据模型定义
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import numpy as np


class PulsePosition(Enum):
    """脉诊位置枚举"""

    CUN_LEFT = "寸左"
    GUAN_LEFT = "关左"
    CHI_LEFT = "尺左"
    CUN_RIGHT = "寸右"
    GUAN_RIGHT = "关右"
    CHI_RIGHT = "尺右"


class PulseWaveType(Enum):
    """脉象类型枚举"""

    FLOATING = "浮脉"
    SUNKEN = "沉脉"
    SLOW = "迟脉"
    RAPID = "数脉"
    SLIPPERY = "滑脉"
    ROUGH = "涩脉"
    WIRY = "弦脉"
    MODERATE = "和脉"
    FAINT = "微脉"
    SURGING = "洪脉"
    TIGHT = "紧脉"
    EMPTY = "虚脉"
    LEATHER = "革脉"
    WEAK = "弱脉"
    SCATTERED = "散脉"
    INTERMITTENT = "代脉"
    BOUND = "结脉"
    HASTY = "促脉"
    HIDDEN = "伏脉"
    LONG = "长脉"
    SHORT = "短脉"
    THREADY = "细脉"
    SOFT = "软脉"
    REGULARLY_INTERMITTENT = "结代脉"
    IRREGULARLY_INTERMITTENT = "促代脉"


@dataclass
class DeviceInfo:
    """设备信息"""

    device_id: str
    model: str
    firmware_version: str
    sensor_types: list[str] = field(default_factory=list)
    sampling_rate: int = 1000
    channels: int = 6
    features: list[str] = field(default_factory=list)
    calibration_date: datetime | None = None


@dataclass
class SensorCalibrationData:
    """传感器校准数据"""

    calibration_values: list[float]
    calibration_timestamp: datetime
    calibration_operator: str
    calibration_result: bool = True
    error_margin: float = 0.05


@dataclass
class PulseSession:
    """脉诊会话"""

    session_id: str
    user_id: str
    device_info: DeviceInfo
    start_time: datetime
    end_time: datetime | None = None
    status: str = "active"
    total_packets: int = 0
    quality_score: float = 0.0
    calibration_data: SensorCalibrationData | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PulseDataPacket:
    """脉搏数据包"""

    session_id: str
    timestamp: datetime
    position: PulsePosition
    pressure_data: np.ndarray
    velocity_data: np.ndarray | None = None
    skin_temperature: float | None = None
    skin_moisture: float | None = None
    quality_indicators: dict[str, float] = field(default_factory=dict)


@dataclass
class PulseFeature:
    """脉象特征"""

    feature_name: str
    feature_value: float
    feature_unit: str
    position: PulsePosition
    description: str = ""
    confidence: float = 1.0

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "name": self.feature_name,
            "value": self.feature_value,
            "unit": self.feature_unit,
            "position": self.position.value,
            "description": self.description,
            "confidence": self.confidence,
        }


@dataclass
class TimedomainFeatures:
    """时域特征"""

    amplitude: float  # 脉搏幅度
    period: float  # 脉搏周期
    rate: int  # 脉率
    rhythm_regularity: float  # 节律规整度
    rise_time: float  # 上升时间
    fall_time: float  # 下降时间
    width: float  # 脉宽
    area: float  # 脉搏面积

    def to_features(self, position: PulsePosition) -> list[PulseFeature]:
        """转换为特征列表"""
        return [
            PulseFeature("幅度", self.amplitude, "mmHg", position, "脉搏波形的最大振幅"),
            PulseFeature("周期", self.period, "s", position, "相邻脉搏的时间间隔"),
            PulseFeature("脉率", float(self.rate), "次/分", position, "每分钟脉搏次数"),
            PulseFeature("节律规整度", self.rhythm_regularity, "%", position, "脉搏节律的规则程度"),
            PulseFeature("上升时间", self.rise_time, "s", position, "脉搏上升支持续时间"),
            PulseFeature("下降时间", self.fall_time, "s", position, "脉搏下降支持续时间"),
            PulseFeature("脉宽", self.width, "s", position, "脉搏持续时间"),
            PulseFeature("面积", self.area, "mmHg·s", position, "脉搏波形下的面积"),
        ]


@dataclass
class FrequencydomainFeatures:
    """频域特征"""

    peak_frequency: float  # 主频
    power_spectrum: np.ndarray  # 功率谱
    harmonic_amplitudes: list[float]  # 谐波幅度
    spectral_entropy: float  # 频谱熵

    def to_features(self, position: PulsePosition) -> list[PulseFeature]:
        """转换为特征列表"""
        features = [
            PulseFeature("主频", self.peak_frequency, "Hz", position, "功率谱的峰值频率"),
            PulseFeature("频谱熵", self.spectral_entropy, "", position, "频谱复杂度指标"),
        ]

        # 添加前3个谐波的幅度
        for i, amp in enumerate(self.harmonic_amplitudes[:3]):
            features.append(
                PulseFeature(f"第{i+1}谐波", amp, "dB", position, f"第{i+1}次谐波分量的幅度")
            )

        return features


@dataclass
class WaveletFeatures:
    """小波域特征"""

    energy_distribution: list[float]  # 各尺度能量分布
    detail_coefficients: list[np.ndarray]  # 细节系数
    approximation_coefficients: np.ndarray  # 逼近系数

    def to_features(self, position: PulsePosition) -> list[PulseFeature]:
        """转换为特征列表"""
        features = []

        # 添加各尺度的能量分布
        for i, energy in enumerate(self.energy_distribution):
            features.append(
                PulseFeature(
                    f"尺度{i+1}能量", energy, "%", position, f"小波分解第{i+1}尺度的能量占比"
                )
            )

        return features


@dataclass
class PulseQualityMetrics:
    """脉搏质量指标"""

    signal_quality: float  # 信号质量 (0-1)
    noise_level: float  # 噪声水平
    is_valid: bool  # 是否有效
    quality_issues: list[str] = field(default_factory=list)
    snr: float = 0.0  # 信噪比
    baseline_drift: float = 0.0  # 基线漂移
    motion_artifact: float = 0.0  # 运动伪影


@dataclass
class TCMPulsePattern:
    """中医脉象模式"""

    pattern_name: str
    pattern_type: PulseWaveType
    confidence: float
    description: str
    related_conditions: list[str] = field(default_factory=list)
    supporting_features: list[str] = field(default_factory=list)


@dataclass
class OrganCondition:
    """脏腑状态"""

    organ_name: str
    tcm_name: str  # 中医名称
    condition: str
    severity: float  # 0-1
    description: str
    related_symptoms: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


@dataclass
class PulseAnalysisResult:
    """脉诊分析结果"""

    session_id: str
    analysis_time: datetime
    pulse_types: list[PulseWaveType]
    tcm_patterns: list[TCMPulsePattern]
    organ_conditions: list[OrganCondition]
    overall_assessment: str
    confidence_score: float
    quality_metrics: PulseQualityMetrics
    recommendations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class PulseTrend:
    """脉象趋势"""

    user_id: str
    start_date: datetime
    end_date: datetime
    sessions_analyzed: int
    dominant_patterns: list[dict[str, Any]]
    improving_aspects: list[str]
    worsening_aspects: list[str]
    stable_aspects: list[str]
    overall_trend: str
    visualization_data: dict[str, Any] | None = None


@dataclass
class PulseComparison:
    """脉诊对比结果"""

    baseline_session_id: str
    comparison_session_id: str
    baseline_date: datetime
    comparison_date: datetime
    changed_features: list[dict[str, Any]]
    new_patterns: list[str]
    resolved_patterns: list[str]
    persisting_patterns: list[str]
    comparison_summary: str
    improvement_score: float  # -1 到 1，负值表示恶化，正值表示改善
