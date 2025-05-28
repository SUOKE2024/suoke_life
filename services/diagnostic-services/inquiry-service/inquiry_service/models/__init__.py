"""
数据模型包

包含问诊服务的所有数据模型定义。
"""

from inquiry_service.models.base import BaseModel, TimestampMixin
from inquiry_service.models.dialogue import DialogueSession, DialogueMessage
from inquiry_service.models.symptom import Symptom, SymptomExtraction
from inquiry_service.models.tcm import TCMPattern, TCMSymptom, BodyLocation
from inquiry_service.models.health import HealthRiskAssessment, RiskFactor

__all__ = [
    "BaseModel",
    "TimestampMixin",
    "DialogueSession",
    "DialogueMessage",
    "Symptom",
    "SymptomExtraction",
    "TCMPattern",
    "TCMSymptom",
    "BodyLocation",
    "HealthRiskAssessment",
    "RiskFactor",
] 