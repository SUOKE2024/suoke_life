#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中医模型定义
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Symptom:
    """症状"""
    name: str
    severity: str  # "MILD", "MODERATE", "SEVERE"
    onset_time: Optional[int] = None
    duration: Optional[int] = None
    description: Optional[str] = None
    confidence: float = 0.8

@dataclass
class BodyLocation:
    """身体部位"""
    name: str
    side: str  # "left", "right", "central", "bilateral"
    associated_symptoms: List[str]

@dataclass
class TemporalFactor:
    """时间因素"""
    factor_type: str  # "diurnal", "seasonal", "durational", "frequency", "triggers"
    description: str
    symptoms_affected: List[str]

@dataclass
class TCMPattern:
    """中医证型"""
    id: str
    name: str
    english_name: str
    category: str
    confidence: float
    matched_symptoms: List[str]
    rule_id: Optional[str] = None

@dataclass
class Constitution:
    """体质类型"""
    type_code: str
    type_name: str
    confidence: float
    description: str
    characteristics: List[str]