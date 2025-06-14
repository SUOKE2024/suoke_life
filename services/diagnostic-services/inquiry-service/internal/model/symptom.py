"""
symptom - 索克生活项目模块
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

#! / usr / bin / env python

"""
症状模型
定义症状相关的数据结构和操作
"""



class SymptomSeverity(str, Enum):
    """症状严重程度枚举"""

    MILD = "mild"  # 轻度
    MODERATE = "moderate"  # 中度
    SEVERE = "severe"  # 重度
    VERY_SEVERE = "very_severe"  # 极重度
    UNKNOWN = "unknown"  # 未知


class SymptomDuration(str, Enum):
    """症状持续时间枚举"""

    ACUTE = "acute"  # 急性 (<2周)
    SUBACUTE = "subacute"  # 亚急性 (2周 - 3个月)
    CHRONIC = "chronic"  # 慢性 (>3个月)
    RECURRENT = "recurrent"  # 复发性
    INTERMITTENT = "intermittent"  # 间歇性
    UNKNOWN = "unknown"  # 未知


class SymptomTrend(str, Enum):
    """症状变化趋势枚举"""

    IMPROVING = "improving"  # 改善中
    WORSENING = "worsening"  # 恶化中
    STABLE = "stable"  # 稳定
    FLUCTUATING = "fluctuating"  # 波动
    UNKNOWN = "unknown"  # 未知


@dataclass
class Symptom:
    """症状模型"""

    name: str  # 症状名称
    description: str | None = None  # 症状描述
    body_location: str | None = None  # 身体部位
    severity: SymptomSeverity = SymptomSeverity.UNKNOWN  # 严重程度
    duration: SymptomDuration = SymptomDuration.UNKNOWN  # 持续时间
    duration_value: int | None = None  # 持续时间值（天 / 周 / 月）
    onset_time: str | None = None  # 发作时间
    trend: SymptomTrend = SymptomTrend.UNKNOWN  # 变化趋势
    aggravating_factors: list[str] = field(default_factory = list)  # 加重因素
    alleviating_factors: list[str] = field(default_factory = list)  # 缓解因素
    associated_symptoms: list[str] = field(default_factory = list)  # 相关症状
    tcm_symptom_names: list[str] = field(default_factory = list)  # 对应的中医症状名称
    confidence: float = 1.0  # 提取置信度
    source_text: str | None = None  # 原始文本
    negated: bool = False  # 是否为否定症状
    metadata: dict[str, Any] = field(default_factory = dict)  # 元数据

    def to_dict(self)-> dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "body_location": self.body_location,
            "severity": self.severity.value,
            "duration": self.duration.value,
            "duration_value": self.duration_value,
            "onset_time": self.onset_time,
            "trend": self.trend.value,
            "aggravating_factors": self.aggravating_factors,
            "alleviating_factors": self.alleviating_factors,
            "associated_symptoms": self.associated_symptoms,
            "tcm_symptom_names": self.tcm_symptom_names,
            "confidence": self.confidence,
            "source_text": self.source_text,
            "negated": self.negated,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any])-> "Symptom":
        """从字典创建症状对象"""
        return cls(
            name = data["name"],
            description = data.get("description"),
            body_location = data.get("body_location"),
            severity = SymptomSeverity(data.get("severity", "unknown")),
            duration = SymptomDuration(data.get("duration", "unknown")),
            duration_value = data.get("duration_value"),
            onset_time = data.get("onset_time"),
            trend = SymptomTrend(data.get("trend", "unknown")),
            aggravating_factors = data.get("aggravating_factors", []),
            alleviating_factors = data.get("alleviating_factors", []),
            associated_symptoms = data.get("associated_symptoms", []),
            tcm_symptom_names = data.get("tcm_symptom_names", []),
            confidence = data.get("confidence", 1.0),
            source_text = data.get("source_text"),
            negated = data.get("negated", False),
            metadata = data.get("metadata", {}),
        )

    @staticmethod
    def extract_structured_symptoms(llm_response: dict[str, Any])-> list["Symptom"]:
        """
        从LLM响应中提取结构化症状

        Args:
            llm_response: LLM响应的结构化数据

        Returns:
            结构化症状列表
        """
        symptoms = []

        for symptom_data in llm_response.get("symptoms", []):
            try:
                # 创建Symptom对象
                symptom = Symptom.from_dict(symptom_data)
                symptoms.append(symptom)
            except (KeyError, ValueError) as e:
                # 处理错误，跳过无效数据
                print(f"提取症状时出错: {e}, 数据: {symptom_data}")
                continue

        return symptoms
