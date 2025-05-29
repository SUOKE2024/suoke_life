"""
数据模型包

包含问诊服务的所有数据模型定义。
"""

from inquiry_service.models.base import BaseModel, TimestampMixin
from inquiry_service.models.dialogue import DialogueMessage, DialogueSession
from inquiry_service.models.health import HealthRiskAssessment, RiskFactor
from inquiry_service.models.symptom import Symptom, SymptomExtraction
from inquiry_service.models.tcm import BodyLocation, TCMPattern, TCMSymptom

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
