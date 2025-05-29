#!/usr/bin/env python

"""
中医模型定义
"""

from dataclasses import dataclass


@dataclass
class Symptom:
    """症状"""

    name: str
    severity: str  # "MILD", "MODERATE", "SEVERE"
    onset_time: int | None = None
    duration: int | None = None
    description: str | None = None
    confidence: float = 0.8


@dataclass
class BodyLocation:
    """身体部位"""

    name: str
    side: str  # "left", "right", "central", "bilateral"
    associated_symptoms: list[str]


@dataclass
class TemporalFactor:
    """时间因素"""

    factor_type: str  # "diurnal", "seasonal", "durational", "frequency", "triggers"
    description: str
    symptoms_affected: list[str]


@dataclass
class TCMPattern:
    """中医证型"""

    id: str
    name: str
    english_name: str
    category: str
    confidence: float
    matched_symptoms: list[str]
    rule_id: str | None = None


@dataclass
class Constitution:
    """体质类型"""

    type_code: str
    type_name: str
    confidence: float
    description: str
    characteristics: list[str]
