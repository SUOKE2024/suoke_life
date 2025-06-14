from typing import Any, Dict, List, Optional, Union

"""
__init__ - 索克生活项目模块
"""

from inquiry_service.models.base import BaseModel, TimestampMixin
from inquiry_service.models.dialogue import DialogueMessage, DialogueSession
from inquiry_service.models.health import HealthRiskAssessment, RiskFactor
from inquiry_service.models.symptom import Symptom, SymptomExtraction
from inquiry_service.models.tcm import BodyLocation, TCMPattern, TCMSymptom

"""
数据模型包

包含问诊服务的所有数据模型定义。
"""


__all__ = [
    "BaseModel",
    "BodyLocation",
    "DialogueMessage",
    "DialogueSession",
    "HealthRiskAssessment",
    "RiskFactor",
    "Symptom",
    "SymptomExtraction",
    "TCMPattern",
    "TCMSymptom",
    "TimestampMixin",
]
