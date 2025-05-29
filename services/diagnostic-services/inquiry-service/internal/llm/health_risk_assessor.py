#!/usr/bin/env python

"""
健康风险评估模块，基于症状、病史和体质类型进行风险评估
"""

from datetime import datetime
import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class HealthRiskAssessor:
    """健康风险评估器"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化健康风险评估器

        Args:
            config: 配置信息
        """
        self.config = config
        self.risk_config = config.get("health_risk_assessment", {})

        # 风险阈值配置
        self.risk_thresholds = self.risk_config.get(
            "risk_thresholds",
            {"low": 0.3, "moderate": 0.5, "high": 0.7, "critical": 0.9},
        )

        # 最小置信度
        self.min_confidence = self.risk_config.get("min_confidence", 0.6)

        # 加载风险评估规则
        self.risk_rules = self._load_risk_rules()

        # 加载体质与疾病关联数据
        self.constitution_disease_mapping = self._load_constitution_disease_mapping()

        logger.info("健康风险评估器初始化完成")

    def _load_risk_rules(self) -> dict[str, Any]:
        """加载风险评估规则"""
        default_rules = {
            # 症状组合规则
            "symptom_combinations": [
                {
                    "symptoms": ["胸痛", "气短", "心悸"],
                    "risk_name": "心血管疾病",
                    "base_risk": 0.7,
                    "severity_multiplier": 1.2,
                },
                {
                    "symptoms": ["头痛", "眩晕", "耳鸣"],
                    "risk_name": "高血压",
                    "base_risk": 0.6,
                    "severity_multiplier": 1.1,
                },
                {
                    "symptoms": ["口渴", "多饮", "多尿", "疲劳"],
                    "risk_name": "糖尿病",
                    "base_risk": 0.65,
                    "severity_multiplier": 1.15,
                },
                {
                    "symptoms": ["腹痛", "腹泻", "便血"],
                    "risk_name": "消化系统疾病",
                    "base_risk": 0.6,
                    "severity_multiplier": 1.1,
                },
                {
                    "symptoms": ["咳嗽", "痰多", "胸闷", "气喘"],
                    "risk_name": "呼吸系统疾病",
                    "base_risk": 0.55,
                    "severity_multiplier": 1.1,
                },
            ],
            # 单症状风险规则
            "single_symptom_risks": {
                "持续性胸痛": {"risk_name": "心脏疾病", "base_risk": 0.7},
                "便血": {"risk_name": "消化道出血", "base_risk": 0.75},
                "黄疸": {"risk_name": "肝胆疾病", "base_risk": 0.7},
                "持续高热": {"risk_name": "感染性疾病", "base_risk": 0.65},
                "意识障碍": {"risk_name": "神经系统疾病", "base_risk": 0.8},
            },
            # 时间因素规则
            "temporal_rules": {
                "急性": {"risk_multiplier": 1.3, "timeframe": "immediate"},
                "慢性": {"risk_multiplier": 0.9, "timeframe": "long_term"},
                "持续恶化": {"risk_multiplier": 1.4, "timeframe": "immediate"},
            },
        }

        # 尝试从文件加载自定义规则
        rules_file = os.path.join(
            self.config.get("data", {}).get("base_dir", "./data"), "risk_rules.json"
        )
        if os.path.exists(rules_file):
            try:
                with open(rules_file, encoding="utf-8") as f:
                    custom_rules = json.load(f)
                    default_rules.update(custom_rules)
                    logger.info("加载自定义风险评估规则成功")
            except Exception as e:
                logger.error(f"加载自定义风险评估规则失败: {e!s}")

        return default_rules

    def _load_constitution_disease_mapping(self) -> dict[str, list[dict]]:
        """加载体质与疾病关联数据"""
        return {
            "QI_DEFICIENCY": [
                {"disease": "慢性疲劳综合征", "risk_factor": 1.3},
                {"disease": "消化系统疾病", "risk_factor": 1.2},
                {"disease": "呼吸系统疾病", "risk_factor": 1.15},
            ],
            "YANG_DEFICIENCY": [
                {"disease": "寒性疾病", "risk_factor": 1.4},
                {"disease": "关节疾病", "risk_factor": 1.25},
                {"disease": "消化系统疾病", "risk_factor": 1.2},
            ],
            "YIN_DEFICIENCY": [
                {"disease": "高血压", "risk_factor": 1.3},
                {"disease": "糖尿病", "risk_factor": 1.25},
                {"disease": "失眠症", "risk_factor": 1.35},
            ],
            "PHLEGM_DAMPNESS": [
                {"disease": "肥胖相关疾病", "risk_factor": 1.5},
                {"disease": "代谢综合征", "risk_factor": 1.4},
                {"disease": "心血管疾病", "risk_factor": 1.3},
            ],
            "DAMP_HEAT": [
                {"disease": "皮肤疾病", "risk_factor": 1.35},
                {"disease": "消化系统疾病", "risk_factor": 1.3},
                {"disease": "泌尿系统疾病", "risk_factor": 1.25},
            ],
            "BLOOD_STASIS": [
                {"disease": "心血管疾病", "risk_factor": 1.45},
                {"disease": "血栓性疾病", "risk_factor": 1.5},
                {"disease": "妇科疾病", "risk_factor": 1.3},
            ],
            "QI_STAGNATION": [
                {"disease": "抑郁症", "risk_factor": 1.4},
                {"disease": "焦虑症", "risk_factor": 1.35},
                {"disease": "消化系统疾病", "risk_factor": 1.2},
            ],
        }

    async def assess_health_risks(
        self,
        user_id: str,
        current_symptoms: list[dict],
        medical_history: dict,
        health_profile: dict,
    ) -> dict[str, Any]:
        """
        评估健康风险

        Args:
            user_id: 用户ID
            current_symptoms: 当前症状列表
            medical_history: 病史信息
            health_profile: 健康档案

        Returns:
            包含即时风险、长期风险和预防策略的评估结果
        """
        try:
            # 1. 分析症状风险
            symptom_risks = self._analyze_symptom_risks(current_symptoms)

            # 2. 分析病史风险
            history_risks = self._analyze_history_risks(medical_history)

            # 3. 分析体质相关风险
            constitution_risks = self._analyze_constitution_risks(
                health_profile.get("constitution_type", "BALANCED"), current_symptoms
            )

            # 4. 综合风险评估
            immediate_risks, long_term_risks = self._combine_risks(
                symptom_risks, history_risks, constitution_risks
            )

            # 5. 生成预防策略
            prevention_strategies = self._generate_prevention_strategies(
                immediate_risks + long_term_risks, health_profile
            )

            # 6. 计算总体风险评分
            overall_risk_score = self._calculate_overall_risk_score(
                immediate_risks, long_term_risks
            )

            return {
                "immediate_risks": immediate_risks,
                "long_term_risks": long_term_risks,
                "prevention_strategies": prevention_strategies,
                "overall_risk_score": overall_risk_score,
                "assessment_timestamp": int(datetime.now().timestamp()),
                "confidence_score": self._calculate_confidence_score(current_symptoms),
            }

        except Exception as e:
            logger.error(f"健康风险评估失败: {e!s}")
            return {
                "immediate_risks": [],
                "long_term_risks": [],
                "prevention_strategies": [],
                "overall_risk_score": 0.0,
                "error": str(e),
            }

    def _analyze_symptom_risks(self, symptoms: list[dict]) -> list[dict]:
        """分析症状相关风险"""
        risks = []

        # 提取症状名称和严重程度
        symptom_names = [s.get("symptom_name", "") for s in symptoms]
        symptom_severities = {
            s.get("symptom_name", ""): s.get("severity", "MODERATE") for s in symptoms
        }

        # 检查症状组合规则
        for rule in self.risk_rules.get("symptom_combinations", []):
            matched_symptoms = [s for s in rule["symptoms"] if s in symptom_names]

            if len(matched_symptoms) >= len(rule["symptoms"]) * 0.6:  # 60%匹配度
                # 计算风险概率
                base_risk = rule["base_risk"]

                # 根据严重程度调整风险
                severity_factor = 1.0
                for symptom in matched_symptoms:
                    severity = symptom_severities.get(symptom, "MODERATE")
                    if severity == "SEVERE":
                        severity_factor *= 1.2
                    elif severity == "EXTREME":
                        severity_factor *= 1.4

                probability = min(base_risk * severity_factor, 0.95)

                risks.append(
                    {
                        "risk_name": rule["risk_name"],
                        "probability": probability,
                        "severity": self._get_severity_level(probability),
                        "timeframe": "immediate" if probability > 0.7 else "short_term",
                        "contributing_factors": matched_symptoms,
                    }
                )

        # 检查单症状风险
        for symptom_name in symptom_names:
            if symptom_name in self.risk_rules.get("single_symptom_risks", {}):
                risk_info = self.risk_rules["single_symptom_risks"][symptom_name]
                risks.append(
                    {
                        "risk_name": risk_info["risk_name"],
                        "probability": risk_info["base_risk"],
                        "severity": self._get_severity_level(risk_info["base_risk"]),
                        "timeframe": "immediate",
                        "contributing_factors": [symptom_name],
                    }
                )

        return risks

    def _analyze_history_risks(self, medical_history: dict) -> list[dict]:
        """分析病史相关风险"""
        risks = []

        # 慢性病风险
        chronic_conditions = medical_history.get("chronic_conditions", [])
        for condition in chronic_conditions:
            condition_name = condition.get("condition_name", "")

            # 根据慢性病类型评估相关风险
            if "糖尿病" in condition_name:
                risks.append(
                    {
                        "risk_name": "糖尿病并发症",
                        "probability": 0.6,
                        "severity": "moderate",
                        "timeframe": "long_term",
                        "contributing_factors": ["糖尿病病史"],
                    }
                )
            elif "高血压" in condition_name:
                risks.append(
                    {
                        "risk_name": "心脑血管疾病",
                        "probability": 0.65,
                        "severity": "high",
                        "timeframe": "long_term",
                        "contributing_factors": ["高血压病史"],
                    }
                )

        # 家族史风险
        risk_factors = medical_history.get("risk_factors", [])
        for factor in risk_factors:
            if factor.get("risk_score", 0) > 0.5:
                risks.append(
                    {
                        "risk_name": factor.get("factor_name", ""),
                        "probability": factor.get("risk_score", 0),
                        "severity": self._get_severity_level(
                            factor.get("risk_score", 0)
                        ),
                        "timeframe": "long_term",
                        "contributing_factors": ["家族史"],
                    }
                )

        return risks

    def _analyze_constitution_risks(
        self, constitution_type: str, current_symptoms: list[dict]
    ) -> list[dict]:
        """分析体质相关风险"""
        risks = []

        # 获取体质相关疾病风险
        constitution_risks = self.constitution_disease_mapping.get(
            constitution_type, []
        )

        for risk_info in constitution_risks:
            # 基础风险
            base_probability = 0.3

            # 如果有相关症状，增加风险
            symptom_names = [s.get("symptom_name", "") for s in current_symptoms]
            if self._has_related_symptoms(risk_info["disease"], symptom_names):
                base_probability *= risk_info["risk_factor"]

            if base_probability > self.risk_thresholds["low"]:
                risks.append(
                    {
                        "risk_name": risk_info["disease"],
                        "probability": min(base_probability, 0.85),
                        "severity": self._get_severity_level(base_probability),
                        "timeframe": "long_term",
                        "contributing_factors": [f"{constitution_type}体质"],
                    }
                )

        return risks

    def _has_related_symptoms(self, disease: str, symptoms: list[str]) -> bool:
        """检查是否有疾病相关症状"""
        disease_symptom_mapping = {
            "心血管疾病": ["胸痛", "心悸", "气短", "胸闷"],
            "糖尿病": ["口渴", "多饮", "多尿", "疲劳", "体重下降"],
            "高血压": ["头痛", "眩晕", "耳鸣", "心悸"],
            "消化系统疾病": ["腹痛", "腹泻", "便秘", "恶心", "呕吐"],
            "呼吸系统疾病": ["咳嗽", "痰多", "气喘", "胸闷"],
            "抑郁症": ["情绪低落", "失眠", "疲劳", "食欲不振"],
            "焦虑症": ["心悸", "出汗", "紧张", "失眠"],
        }

        related_symptoms = disease_symptom_mapping.get(disease, [])
        return any(symptom in symptoms for symptom in related_symptoms)

    def _combine_risks(
        self,
        symptom_risks: list[dict],
        history_risks: list[dict],
        constitution_risks: list[dict],
    ) -> tuple:
        """综合各类风险"""
        all_risks = symptom_risks + history_risks + constitution_risks

        # 合并相同风险
        merged_risks = {}
        for risk in all_risks:
            risk_name = risk["risk_name"]
            if risk_name in merged_risks:
                # 取最高概率
                merged_risks[risk_name]["probability"] = max(
                    merged_risks[risk_name]["probability"], risk["probability"]
                )
                # 合并贡献因素
                merged_risks[risk_name]["contributing_factors"].extend(
                    risk["contributing_factors"]
                )
            else:
                merged_risks[risk_name] = risk.copy()

        # 分类为即时风险和长期风险
        immediate_risks = []
        long_term_risks = []

        for risk in merged_risks.values():
            # 去重贡献因素
            risk["contributing_factors"] = list(set(risk["contributing_factors"]))

            if risk["timeframe"] in ["immediate", "short_term"]:
                immediate_risks.append(risk)
            else:
                long_term_risks.append(risk)

        # 按概率排序
        immediate_risks.sort(key=lambda x: x["probability"], reverse=True)
        long_term_risks.sort(key=lambda x: x["probability"], reverse=True)

        return immediate_risks[:5], long_term_risks[:5]  # 返回前5个风险

    def _generate_prevention_strategies(
        self, risks: list[dict], health_profile: dict
    ) -> list[dict]:
        """生成预防策略"""
        strategies = []

        # 基于风险生成策略
        for risk in risks:
            risk_name = risk["risk_name"]

            if "心血管" in risk_name:
                strategies.append(
                    {
                        "strategy_name": "心血管疾病预防",
                        "description": "通过生活方式调整降低心血管疾病风险",
                        "action_items": [
                            "每周至少150分钟中等强度有氧运动",
                            "低盐低脂饮食，多吃蔬菜水果",
                            "戒烟限酒",
                            "定期监测血压血脂",
                            "保持健康体重",
                        ],
                        "targets": [risk_name],
                        "effectiveness_score": 0.8,
                    }
                )
            elif "糖尿病" in risk_name:
                strategies.append(
                    {
                        "strategy_name": "糖尿病预防",
                        "description": "通过饮食控制和运动预防糖尿病",
                        "action_items": [
                            "控制碳水化合物摄入",
                            "规律运动，每天至少30分钟",
                            "保持健康体重",
                            "定期检测血糖",
                            "避免高糖饮食",
                        ],
                        "targets": [risk_name],
                        "effectiveness_score": 0.75,
                    }
                )
            elif "高血压" in risk_name:
                strategies.append(
                    {
                        "strategy_name": "高血压预防",
                        "description": "通过生活方式管理预防高血压",
                        "action_items": [
                            "限制钠盐摄入，每日少于6克",
                            "增加钾摄入，多吃香蕉、橙子",
                            "规律运动",
                            "减轻精神压力",
                            "定期监测血压",
                        ],
                        "targets": [risk_name],
                        "effectiveness_score": 0.7,
                    }
                )

        # 基于体质的通用预防策略
        constitution_type = health_profile.get("constitution_type", "BALANCED")
        if constitution_type != "BALANCED":
            strategies.append(
                self._get_constitution_prevention_strategy(constitution_type)
            )

        # 去重并按有效性排序
        unique_strategies = {s["strategy_name"]: s for s in strategies}.values()
        return sorted(
            unique_strategies, key=lambda x: x["effectiveness_score"], reverse=True
        )

    def _get_constitution_prevention_strategy(self, constitution_type: str) -> dict:
        """获取体质相关预防策略"""
        strategies = {
            "QI_DEFICIENCY": {
                "strategy_name": "气虚质调理",
                "description": "通过补气养生改善气虚体质",
                "action_items": [
                    "适量运动，避免过度劳累",
                    "多吃补气食物：山药、大枣、黄芪",
                    "保证充足睡眠",
                    "练习八段锦或太极拳",
                    "避免生冷食物",
                ],
                "targets": ["气虚相关疾病"],
                "effectiveness_score": 0.7,
            },
            "YANG_DEFICIENCY": {
                "strategy_name": "阳虚质调理",
                "description": "通过温阳养生改善阳虚体质",
                "action_items": [
                    "注意保暖，特别是腰部和腹部",
                    "多吃温性食物：羊肉、生姜、韭菜",
                    "适当晒太阳",
                    "艾灸关元、命门等穴位",
                    "避免寒凉食物和环境",
                ],
                "targets": ["阳虚相关疾病"],
                "effectiveness_score": 0.7,
            },
            "YIN_DEFICIENCY": {
                "strategy_name": "阴虚质调理",
                "description": "通过滋阴养生改善阴虚体质",
                "action_items": [
                    "保证充足睡眠，避免熬夜",
                    "多吃滋阴食物：银耳、百合、枸杞",
                    "保持情绪平和",
                    "适量饮水",
                    "避免辛辣刺激食物",
                ],
                "targets": ["阴虚相关疾病"],
                "effectiveness_score": 0.7,
            },
        }

        return strategies.get(
            constitution_type,
            {
                "strategy_name": "体质调理",
                "description": "通过生活方式调理改善体质",
                "action_items": ["均衡饮食", "规律作息", "适量运动", "情志调养"],
                "targets": ["体质相关疾病"],
                "effectiveness_score": 0.6,
            },
        )

    def _calculate_overall_risk_score(
        self, immediate_risks: list[dict], long_term_risks: list[dict]
    ) -> float:
        """计算总体风险评分"""
        if not immediate_risks and not long_term_risks:
            return 0.0

        # 即时风险权重更高
        immediate_weight = 0.7
        long_term_weight = 0.3

        # 计算平均风险
        immediate_avg = 0.0
        if immediate_risks:
            immediate_avg = sum(r["probability"] for r in immediate_risks) / len(
                immediate_risks
            )

        long_term_avg = 0.0
        if long_term_risks:
            long_term_avg = sum(r["probability"] for r in long_term_risks) / len(
                long_term_risks
            )

        overall_score = (
            immediate_avg * immediate_weight + long_term_avg * long_term_weight
        )

        return round(overall_score, 2)

    def _get_severity_level(self, probability: float) -> str:
        """根据概率获取严重程度级别"""
        if probability >= self.risk_thresholds["critical"]:
            return "critical"
        elif probability >= self.risk_thresholds["high"]:
            return "high"
        elif probability >= self.risk_thresholds["moderate"]:
            return "moderate"
        else:
            return "low"

    def _calculate_confidence_score(self, symptoms: list[dict]) -> float:
        """计算评估置信度"""
        if not symptoms:
            return 0.5

        # 基于症状数量和置信度计算
        symptom_confidences = [s.get("confidence", 0.8) for s in symptoms]
        avg_confidence = sum(symptom_confidences) / len(symptom_confidences)

        # 症状越多，置信度越高
        quantity_factor = min(len(symptoms) / 10, 1.0)

        confidence = avg_confidence * 0.7 + quantity_factor * 0.3

        return round(confidence, 2)

    async def check_health(self) -> bool:
        """健康检查"""
        try:
            # 检查规则是否加载
            return bool(self.risk_rules) and bool(self.constitution_disease_mapping)
        except Exception:
            return False
