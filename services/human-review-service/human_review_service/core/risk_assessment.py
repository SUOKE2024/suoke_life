"""
风险评估引擎
Risk Assessment Engine

用于评估医疗建议的风险等级
"""

from typing import Any, Dict, Optional

import structlog

logger = structlog.get_logger(__name__)


class RiskAssessmentEngine:
    """风险评估引擎"""

    def __init__(self):
        """初始化风险评估引擎"""
        self.risk_factors = {
            "high_risk_symptoms": ["胸痛", "呼吸困难", "意识模糊", "严重头痛"],
            "medication_interactions": ["华法林", "胰岛素", "地高辛"],
            "age_thresholds": {"elderly": 65, "pediatric": 18},
            "severity_keywords": ["急性", "严重", "危险", "紧急"],
        }

    def assess_risk(
        self,
        content_data: Dict[str, Any],
        content_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> float:
        """
        评估内容风险等级

        Args:
            content_data: 内容数据
            content_type: 内容类型
            metadata: 元数据

        Returns:
            风险评分 (0.0-1.0)
        """
        try:
            risk_score = 0.0

            # 基于内容类型的基础风险
            base_risk = self._get_base_risk(content_type)
            risk_score += base_risk

            # 症状风险评估
            symptom_risk = self._assess_symptom_risk(content_data)
            risk_score += symptom_risk

            # 药物风险评估
            medication_risk = self._assess_medication_risk(content_data)
            risk_score += medication_risk

            # 年龄风险评估
            age_risk = self._assess_age_risk(content_data, metadata)
            risk_score += age_risk

            # 严重性关键词评估
            severity_risk = self._assess_severity_risk(content_data)
            risk_score += severity_risk

            # 确保风险评分在有效范围内
            risk_score = min(max(risk_score, 0.0), 1.0)

            logger.info(
                "Risk assessment completed",
                content_type=content_type,
                risk_score=risk_score,
                base_risk=base_risk,
                symptom_risk=symptom_risk,
                medication_risk=medication_risk,
                age_risk=age_risk,
                severity_risk=severity_risk,
            )

            return risk_score

        except Exception as e:
            logger.error("Risk assessment failed", error=str(e))
            # 发生错误时返回中等风险
            return 0.5

    def _get_base_risk(self, content_type: str) -> float:
        """获取基于内容类型的基础风险"""
        risk_mapping = {
            "diagnosis": 0.3,
            "treatment": 0.4,
            "medication": 0.5,
            "surgery": 0.7,
            "emergency": 0.8,
            "prescription": 0.4,
            "lifestyle": 0.1,
            "nutrition": 0.1,
        }

        return risk_mapping.get(content_type, 0.3)

    def _assess_symptom_risk(self, content_data: Dict[str, Any]) -> float:
        """评估症状相关风险"""
        risk_score = 0.0

        # 检查症状字段
        symptoms = content_data.get("symptoms", [])
        if isinstance(symptoms, str):
            symptoms = [symptoms]

        # 检查诊断字段
        diagnosis = content_data.get("diagnosis", "")
        if diagnosis:
            symptoms.append(diagnosis)

        # 检查主诉字段
        chief_complaint = content_data.get("chief_complaint", "")
        if chief_complaint:
            symptoms.append(chief_complaint)

        # 评估高风险症状
        for symptom in symptoms:
            if isinstance(symptom, str):
                for high_risk_symptom in self.risk_factors["high_risk_symptoms"]:
                    if high_risk_symptom in symptom:
                        risk_score += 0.2
                        break

        return min(risk_score, 0.4)  # 最大0.4

    def _assess_medication_risk(self, content_data: Dict[str, Any]) -> float:
        """评估药物相关风险"""
        risk_score = 0.0

        # 检查药物字段
        medications = content_data.get("medications", [])
        if isinstance(medications, str):
            medications = [medications]

        # 检查治疗方案
        treatment = content_data.get("treatment", "")
        if treatment:
            medications.append(treatment)

        # 检查处方
        prescription = content_data.get("prescription", "")
        if prescription:
            medications.append(prescription)

        # 评估高风险药物
        for medication in medications:
            if isinstance(medication, str):
                for high_risk_med in self.risk_factors["medication_interactions"]:
                    if high_risk_med in medication:
                        risk_score += 0.15
                        break

        return min(risk_score, 0.3)  # 最大0.3

    def _assess_age_risk(
        self, content_data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None
    ) -> float:
        """评估年龄相关风险"""
        risk_score = 0.0

        # 从内容数据获取年龄
        age = content_data.get("age")

        # 从元数据获取年龄
        if not age and metadata:
            age = metadata.get("patient_age")

        if age:
            try:
                age_num = int(age)
                # 老年人风险
                if age_num >= self.risk_factors["age_thresholds"]["elderly"]:
                    risk_score += 0.1
                # 儿童风险
                elif age_num < self.risk_factors["age_thresholds"]["pediatric"]:
                    risk_score += 0.1
            except (ValueError, TypeError):
                pass

        return risk_score

    def _assess_severity_risk(self, content_data: Dict[str, Any]) -> float:
        """评估严重性关键词风险"""
        risk_score = 0.0

        # 将所有文本内容合并
        text_content = ""
        for key, value in content_data.items():
            if isinstance(value, str):
                text_content += value + " "
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        text_content += item + " "

        text_content = text_content.lower()

        # 检查严重性关键词
        for keyword in self.risk_factors["severity_keywords"]:
            if keyword in text_content:
                risk_score += 0.1

        return min(risk_score, 0.2)  # 最大0.2
