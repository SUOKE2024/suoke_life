"""
ai_tcm_analyzer - 索克生活项目模块
"""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from typing import Any
import asyncio
import logging

#! / usr / bin / env python3

"""
AI增强的中医证型分析器
结合传统中医理论和现代机器学习技术，提供精准的证型识别和健康评估
"""


logger = logging.getLogger(__name__)

class ConstitutionType(Enum):
    """体质类型枚举"""

    BALANCED = "平和质"  # 平和质
    QI_DEFICIENCY = "气虚质"  # 气虚质
    YANG_DEFICIENCY = "阳虚质"  # 阳虚质
    YIN_DEFICIENCY = "阴虚质"  # 阴虚质
    PHLEGM_DAMPNESS = "痰湿质"  # 痰湿质
    DAMP_HEAT = "湿热质"  # 湿热质
    BLOOD_STASIS = "血瘀质"  # 血瘀质
    QI_STAGNATION = "气郁质"  # 气郁质
    SPECIAL_DIATHESIS = "特禀质"  # 特禀质

class PatternType(Enum):
    """证型枚举"""

    # 气血证型
    QI_DEFICIENCY_PATTERN = "气虚证"
    BLOOD_DEFICIENCY_PATTERN = "血虚证"
    QI_STAGNATION_PATTERN = "气滞证"
    BLOOD_STASIS_PATTERN = "血瘀证"

    # 阴阳证型
    YIN_DEFICIENCY_PATTERN = "阴虚证"
    YANG_DEFICIENCY_PATTERN = "阳虚证"
    YIN_EXCESS_PATTERN = "阴盛证"
    YANG_EXCESS_PATTERN = "阳盛证"

    # 寒热证型
    COLD_PATTERN = "寒证"
    HEAT_PATTERN = "热证"

    # 虚实证型
    DEFICIENCY_PATTERN = "虚证"
    EXCESS_PATTERN = "实证"

    # 脏腑证型
    HEART_PATTERN = "心系证型"
    LIVER_PATTERN = "肝系证型"
    SPLEEN_PATTERN = "脾系证型"
    LUNG_PATTERN = "肺系证型"
    KIDNEY_PATTERN = "肾系证型"

@dataclass
class PulseCharacteristics:
    """脉象特征"""

    rate: float  # 脉率 (次 / 分钟)
    rhythm: str  # 节律 (规整 / 不规整)
    strength: float  # 脉力 (0 - 1)
    depth: str  # 脉位 (浮 / 中 / 沉)
    width: str  # 脉形 (细 / 正常 / 洪)
    tension: str  # 脉势 (缓 / 正常 / 紧)
    smoothness: str  # 脉流 (滑 / 涩)

@dataclass
class TCMPattern:
    """中医证型"""

    pattern_type: PatternType
    confidence: float
    symptoms: list[str]
    pulse_indicators: list[str]
    constitution_tendency: ConstitutionType
    severity: str  # 轻度 / 中度 / 重度
    treatment_principle: str
    lifestyle_advice: list[str]

@dataclass
class HealthAssessment:
    """健康评估结果"""

    overall_score: float  # 总体健康评分 (0 - 100)
    constitution_type: ConstitutionType
    primary_patterns: list[TCMPattern]
    risk_factors: list[str]
    recommendations: list[str]
    follow_up_interval: int  # 建议复查间隔(天)

class AITCMAnalyzer:
    """AI增强的中医证型分析器"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化AI中医分析器

        Args:
            config: 配置字典
        """
        self.config = config

        # 模型配置
        self.model_config = config.get("ai_model", {})
        self.confidence_threshold = self.model_config.get("confidence_threshold", 0.7)
        self.use_ensemble = self.model_config.get("use_ensemble", True)

        # 中医知识库
        self.tcm_knowledge = self._load_tcm_knowledge()
        self.pulse_pattern_mapping = self._load_pulse_pattern_mapping()
        self.constitution_rules = self._load_constitution_rules()

        # AI模型
        self.pattern_classifier = None
        self.constitution_classifier = None
        self.severity_estimator = None

        # 特征权重
        self.feature_weights = self._initialize_feature_weights()

        # 线程池
        self.executor = ThreadPoolExecutor(max_workers = 2)

        # 初始化模型
        self._initialize_models()

        logger.info("AI中医证型分析器初始化完成")

    def _load_tcm_knowledge(dict[str, Any]):
        """加载中医知识库"""
        knowledge = {
            # 脉象与证型的对应关系
            "pulse_patterns": {
                "浮脉": ["表证", "阳证", "虚证"],
                "沉脉": ["里证", "阴证", "实证"],
                "迟脉": ["寒证", "阳虚证"],
                "数脉": ["热证", "阴虚证"],
                "虚脉": ["气虚证", "血虚证"],
                "实脉": ["实证", "邪盛证"],
                "滑脉": ["痰湿证", "食积证", "实热证"],
                "涩脉": ["血瘀证", "精血不足证"],
                "弦脉": ["肝胆病证", "痰饮证"],
                "紧脉": ["寒证", "痛证"],
                "缓脉": ["脾胃虚弱", "湿证"],
                "洪脉": ["热盛证", "阳明证"],
                "细脉": ["气血两虚", "阴虚证"],
                "微脉": ["阳气衰微", "气血大虚"],
            },
            # 五脏与脉象的关系
            "organ_pulse_mapping": {
                "心": ["数脉", "结脉", "代脉", "促脉"],
                "肝": ["弦脉", "急脉"],
                "脾": ["缓脉", "弱脉"],
                "肺": ["浮脉", "短脉"],
                "肾": ["沉脉", "迟脉", "微脉"],
            },
            # 体质特征
            "constitution_features": {
                ConstitutionType.QI_DEFICIENCY: {
                    "pulse": ["虚脉", "弱脉", "缓脉"],
                    "symptoms": ["气短", "乏力", "声低", "自汗"],
                    "tongue": ["淡红", "苔薄白"],
                },
                ConstitutionType.YANG_DEFICIENCY: {
                    "pulse": ["沉脉", "迟脉", "弱脉"],
                    "symptoms": ["畏寒", "肢冷", "精神不振", "小便清长"],
                    "tongue": ["淡胖", "苔白"],
                },
                ConstitutionType.YIN_DEFICIENCY: {
                    "pulse": ["细脉", "数脉"],
                    "symptoms": ["潮热", "盗汗", "五心烦热", "口干"],
                    "tongue": ["红", "苔少"],
                },
            },
        }

        return knowledge

    def _load_pulse_pattern_mapping(dict[str, dict]):
        """加载脉象模式映射"""
        return {
            # 基于脉率的分类
            "rate_patterns": {
                "bradycardia": {
                    "rate_range": (0, 60),
                    "tcm_type": "迟脉",
                    "patterns": ["寒证", "阳虚"],
                },
                "normal": {"rate_range": (60, 100), "tcm_type": "平脉", "patterns": ["正常"]},
                "tachycardia": {
                    "rate_range": (100, 200),
                    "tcm_type": "数脉",
                    "patterns": ["热证", "阴虚"],
                },
            },
            # 基于脉力的分类
            "strength_patterns": {
                "weak": {
                    "strength_range": (0, 0.3),
                    "tcm_type": "虚脉",
                    "patterns": ["气虚", "血虚"],
                },
                "normal": {"strength_range": (0.3, 0.7), "tcm_type": "平脉", "patterns": ["正常"]},
                "strong": {
                    "strength_range": (0.7, 1.0),
                    "tcm_type": "实脉",
                    "patterns": ["实证", "邪盛"],
                },
            },
            # 基于节律的分类
            "rhythm_patterns": {
                "regular": {
                    "regularity_range": (0.8, 1.0),
                    "tcm_type": "平脉",
                    "patterns": ["正常"],
                },
                "irregular": {
                    "regularity_range": (0, 0.8),
                    "tcm_type": "结脉",
                    "patterns": ["心气虚", "血瘀"],
                },
            },
        }

    def _load_constitution_rules(dict[str, Any]):
        """加载体质判定规则"""
        return {
            "scoring_weights": {
                "pulse_features": 0.4,
                "symptom_features": 0.3,
                "lifestyle_features": 0.2,
                "environmental_features": 0.1,
            },
            "constitution_thresholds": {
                ConstitutionType.BALANCED: 0.8,
                ConstitutionType.QI_DEFICIENCY: 0.6,
                ConstitutionType.YANG_DEFICIENCY: 0.6,
                ConstitutionType.YIN_DEFICIENCY: 0.6,
                ConstitutionType.PHLEGM_DAMPNESS: 0.6,
                ConstitutionType.DAMP_HEAT: 0.6,
                ConstitutionType.BLOOD_STASIS: 0.6,
                ConstitutionType.QI_STAGNATION: 0.6,
                ConstitutionType.SPECIAL_DIATHESIS: 0.5,
            },
        }

    def _initialize_feature_weights(dict[str, float]):
        """初始化特征权重"""
        return {
            # 脉象特征权重
            "heart_rate": 0.15,
            "heart_rate_variability": 0.12,
            "pulse_strength": 0.18,
            "rhythm_regularity": 0.15,
            "waveform_complexity": 0.10,
            # 频域特征权重
            "dominant_frequency": 0.08,
            "spectral_centroid": 0.06,
            "spectral_bandwidth": 0.05,
            # 小波特征权重
            "wavelet_energy": 0.06,
            "wavelet_entropy": 0.05,
        }

    def _initialize_models(None):
        """初始化AI模型"""
        try:
            # 这里应该加载实际的机器学习模型
            # 例如：scikit - learn、TensorFlow、PyTorch模型

            # 模拟模型初始化
            self.pattern_classifier = self._create_pattern_classifier()
            self.constitution_classifier = self._create_constitution_classifier()
            self.severity_estimator = self._create_severity_estimator()

            logger.info("AI模型初始化完成")

        except Exception as e:
            logger.warning(f"AI模型初始化失败，将使用传统规则: {e}")
            self.pattern_classifier = None
            self.constitution_classifier = None
            self.severity_estimator = None

    def _create_pattern_classifier(None):
        """创建证型分类器"""
        # 这里应该返回实际的分类器模型
        # 例如：RandomForestClassifier, XGBoostClassifier等
        return None

    def _create_constitution_classifier(None):
        """创建体质分类器"""
        # 这里应该返回实际的分类器模型
        return None

    def _create_severity_estimator(None):
        """创建严重程度评估器"""
        # 这里应该返回实际的回归模型
        return None

    async def analyze_pulse_pattern(
        self, pulse_features: dict[str, float], user_profile: dict[str, Any] | None = None
    ) - > list[TCMPattern]:
        """
        分析脉象证型

        Args:
            pulse_features: 脉象特征
            user_profile: 用户档案信息

        Returns:
            识别的证型列表
        """
        try:
            # 提取脉象特征
            pulse_chars = self._extract_pulse_characteristics(pulse_features)

            # 传统规则分析
            traditional_patterns = await self._traditional_pattern_analysis(pulse_chars)

            # AI模型分析（如果可用）
            ai_patterns = []
            if self.pattern_classifier:
                ai_patterns = await self._ai_pattern_analysis(pulse_features, user_profile)

            # 融合分析结果
            final_patterns = self._merge_pattern_results(traditional_patterns, ai_patterns)

            # 排序和筛选
            final_patterns = self._rank_and_filter_patterns(final_patterns)

            return final_patterns

        except Exception as e:
            logger.error(f"脉象证型分析失败: {e}")
            return []

    def _extract_pulse_characteristics(PulseCharacteristics):
        """提取脉象特征"""
        # 脉率
        rate = features.get("heart_rate", 70)

        # 节律
        regularity = features.get("rhythm_regularity", 0.8)
        rhythm = "规整" if regularity > 0.8 else "不规整"

        # 脉力
        strength = features.get("main_peak_amplitude", 0.5)

        # 脉位（基于信号特征推断）
        depth = self._infer_pulse_depth(features)

        # 脉形
        width = self._infer_pulse_width(features)

        # 脉势
        tension = self._infer_pulse_tension(features)

        # 脉流
        smoothness = self._infer_pulse_smoothness(features)

        return PulseCharacteristics(
            rate = rate,
            rhythm = rhythm,
            strength = strength,
            depth = depth,
            width = width,
            tension = tension,
            smoothness = smoothness,
        )

    def _infer_pulse_depth(str):
        """推断脉位"""
        # 基于信号强度和复杂度推断
        strength = features.get("main_peak_amplitude", 0.5)
        complexity = features.get("waveform_complexity", 0.5)

        if strength > 0.7 and complexity > 0.6:
            return "浮"
        elif strength < 0.3 or complexity < 0.3:
            return "沉"
        else:
            return "中"

    def _infer_pulse_width(str):
        """推断脉形"""
        # 基于波形宽度特征
        width_ratio = features.get("rise_time_ratio", 0.3)
        amplitude = features.get("main_peak_amplitude", 0.5)

        if width_ratio < 0.2 and amplitude > 0.8:
            return "洪"
        elif width_ratio > 0.4 or amplitude < 0.3:
            return "细"
        else:
            return "正常"

    def _infer_pulse_tension(str):
        """推断脉势"""
        # 基于频域特征
        dominant_freq = features.get("dominant_frequency", 1.0)
        spectral_bandwidth = features.get("spectral_bandwidth", 0.5)

        if dominant_freq > 2.0 and spectral_bandwidth > 0.8:
            return "紧"
        elif dominant_freq < 0.8 or spectral_bandwidth < 0.3:
            return "缓"
        else:
            return "正常"

    def _infer_pulse_smoothness(str):
        """推断脉流"""
        # 基于波形复杂度和规律性
        complexity = features.get("waveform_complexity", 0.5)
        regularity = features.get("rhythm_regularity", 0.8)

        if complexity > 0.7 and regularity > 0.8:
            return "滑"
        elif complexity < 0.3 or regularity < 0.6:
            return "涩"
        else:
            return "正常"

    async def _traditional_pattern_analysis(
        self, pulse_chars: PulseCharacteristics
    ) - > list[TCMPattern]:
        """传统中医规则分析"""
        patterns = []

        # 基于脉率分析
        if pulse_chars.rate < 60:
            patterns.append(
                self._create_pattern(
                    PatternType.COLD_PATTERN,
                    0.8,
                    ["迟脉", "寒证"],
                    ["畏寒", "肢冷", "精神不振"],
                    ConstitutionType.YANG_DEFICIENCY,
                )
            )
        elif pulse_chars.rate > 100:
            patterns.append(
                self._create_pattern(
                    PatternType.HEAT_PATTERN,
                    0.8,
                    ["数脉", "热证"],
                    ["潮热", "口干", "心烦"],
                    ConstitutionType.YIN_DEFICIENCY,
                )
            )

        # 基于脉力分析
        if pulse_chars.strength < 0.3:
            patterns.append(
                self._create_pattern(
                    PatternType.QI_DEFICIENCY_PATTERN,
                    0.7,
                    ["虚脉", "气虚"],
                    ["气短", "乏力", "声低"],
                    ConstitutionType.QI_DEFICIENCY,
                )
            )
        elif pulse_chars.strength > 0.8:
            patterns.append(
                self._create_pattern(
                    PatternType.EXCESS_PATTERN,
                    0.7,
                    ["实脉", "实证"],
                    ["精神亢奋", "声高气粗"],
                    ConstitutionType.BALANCED,
                )
            )

        # 基于脉位分析
        if pulse_chars.depth == "浮":
            patterns.append(
                self._create_pattern(
                    PatternType.YANG_EXCESS_PATTERN,
                    0.6,
                    ["浮脉", "表证"],
                    ["发热", "恶寒", "头痛"],
                    ConstitutionType.BALANCED,
                )
            )
        elif pulse_chars.depth == "沉":
            patterns.append(
                self._create_pattern(
                    PatternType.YIN_EXCESS_PATTERN,
                    0.6,
                    ["沉脉", "里证"],
                    ["腹痛", "便秘", "口苦"],
                    ConstitutionType.BALANCED,
                )
            )

        # 基于脉流分析
        if pulse_chars.smoothness == "滑":
            patterns.append(
                self._create_pattern(
                    PatternType.EXCESS_PATTERN,
                    0.6,
                    ["滑脉", "痰湿"],
                    ["胸闷", "痰多", "身重"],
                    ConstitutionType.PHLEGM_DAMPNESS,
                )
            )
        elif pulse_chars.smoothness == "涩":
            patterns.append(
                self._create_pattern(
                    PatternType.BLOOD_STASIS_PATTERN,
                    0.6,
                    ["涩脉", "血瘀"],
                    ["胸痛", "舌暗", "肌肤甲错"],
                    ConstitutionType.BLOOD_STASIS,
                )
            )

        return patterns

    async def _ai_pattern_analysis(
        self, features: dict[str, float], user_profile: dict[str, Any] | None
    ) - > list[TCMPattern]:
        """AI模型证型分析"""
        if not self.pattern_classifier:
            return []

        try:
            # 准备特征向量
            feature_vector = self._prepare_feature_vector(features, user_profile)

            # 在线程池中执行预测
            loop = asyncio.get_event_loop()
            predictions = await loop.run_in_executor(
                self.executor, self._predict_patterns, feature_vector
            )

            # 转换预测结果为TCMPattern对象
            patterns = self._convert_predictions_to_patterns(predictions)

            return patterns

        except Exception as e:
            logger.error(f"AI证型分析失败: {e}")
            return []

    def _prepare_feature_vector(
        self, features: dict[str, float], user_profile: dict[str, Any] | None
    ) - > np.ndarray:
        """准备特征向量"""
        # 基础脉象特征
        base_features = []
        for feature_name, weight in self.feature_weights.items():
            value = features.get(feature_name, 0.0)
            base_features.append(value * weight)

        # 用户档案特征（如果有）
        profile_features = []
        if user_profile:
            age = user_profile.get("age", 30) / 100.0  # 归一化
            gender = 1.0 if user_profile.get("gender") == "male" else 0.0
            bmi = user_profile.get("bmi", 22) / 40.0  # 归一化

            profile_features.extend([age, gender, bmi])
        else:
            profile_features.extend([0.3, 0.5, 0.55])  # 默认值

        # 合并特征
        all_features = base_features + profile_features

        return np.array(all_features).reshape(1, - 1)

    def _predict_patterns(dict[str, float]):
        """使用AI模型预测证型"""
        # 这里应该调用实际的模型预测
        # 模拟预测结果
        predictions = {
            PatternType.QI_DEFICIENCY_PATTERN.value: 0.3,
            PatternType.YIN_DEFICIENCY_PATTERN.value: 0.2,
            PatternType.YANG_DEFICIENCY_PATTERN.value: 0.1,
            PatternType.BLOOD_STASIS_PATTERN.value: 0.15,
            PatternType.HEAT_PATTERN.value: 0.25,
        }

        return predictions

    def _convert_predictions_to_patterns(list[TCMPattern]):
        """将预测结果转换为TCMPattern对象"""
        patterns = []

        for pattern_name, confidence in predictions.items():
            if confidence > self.confidence_threshold:
                try:
                    pattern_type = PatternType(pattern_name)
                    pattern = self._create_ai_pattern(pattern_type, confidence)
                    patterns.append(pattern)
                except ValueError:
                    logger.warning(f"未知证型: {pattern_name}")

        return patterns

    def _create_pattern(
        self,
        pattern_type: PatternType,
        confidence: float,
        pulse_indicators: list[str],
        symptoms: list[str],
        constitution: ConstitutionType,
    ) - > TCMPattern:
        """创建证型对象"""
        # 根据证型确定治疗原则
        treatment_principle = self._get_treatment_principle(pattern_type)

        # 生成生活建议
        lifestyle_advice = self._get_lifestyle_advice(pattern_type, constitution)

        # 确定严重程度
        severity = self._assess_severity(confidence, pattern_type)

        return TCMPattern(
            pattern_type = pattern_type,
            confidence = confidence,
            symptoms = symptoms,
            pulse_indicators = pulse_indicators,
            constitution_tendency = constitution,
            severity = severity,
            treatment_principle = treatment_principle,
            lifestyle_advice = lifestyle_advice,
        )

    def _create_ai_pattern(TCMPattern):
        """基于AI预测创建证型对象"""
        # 从知识库获取相关信息
        symptoms = self._get_pattern_symptoms(pattern_type)
        pulse_indicators = self._get_pattern_pulse_indicators(pattern_type)
        constitution = self._get_pattern_constitution(pattern_type)

        return self._create_pattern(
            pattern_type, confidence, pulse_indicators, symptoms, constitution
        )

    def _get_treatment_principle(str):
        """获取治疗原则"""
        principles = {
            PatternType.QI_DEFICIENCY_PATTERN: "补气健脾",
            PatternType.BLOOD_DEFICIENCY_PATTERN: "补血养血",
            PatternType.YIN_DEFICIENCY_PATTERN: "滋阴降火",
            PatternType.YANG_DEFICIENCY_PATTERN: "温阳补肾",
            PatternType.QI_STAGNATION_PATTERN: "疏肝理气",
            PatternType.BLOOD_STASIS_PATTERN: "活血化瘀",
            PatternType.COLD_PATTERN: "温中散寒",
            PatternType.HEAT_PATTERN: "清热泻火",
            PatternType.EXCESS_PATTERN: "泻实攻邪",
            PatternType.DEFICIENCY_PATTERN: "扶正补虚",
        }

        return principles.get(pattern_type, "辨证施治")

    def _get_lifestyle_advice(
        self, pattern_type: PatternType, constitution: ConstitutionType
    ) - > list[str]:
        """获取生活建议"""
        advice_map = {
            PatternType.QI_DEFICIENCY_PATTERN: [
                "适当运动，避免过度劳累",
                "规律作息，保证充足睡眠",
                "饮食清淡，多食健脾益气食物",
                "保持心情愉悦，避免过度思虑",
            ],
            PatternType.YIN_DEFICIENCY_PATTERN: [
                "避免熬夜，保证充足睡眠",
                "饮食滋润，多食养阴食物",
                "避免辛辣燥热食物",
                "适当静养，避免过度运动",
            ],
            PatternType.YANG_DEFICIENCY_PATTERN: [
                "注意保暖，避免受寒",
                "适当运动，增强体质",
                "饮食温热，多食温阳食物",
                "规律作息，避免过度疲劳",
            ],
        }

        return advice_map.get(pattern_type, ["注意休息", "饮食调理", "适当运动"])

    def _assess_severity(str):
        """评估严重程度"""
        if confidence > = 0.8:
            return "重度"
        elif confidence > = 0.6:
            return "中度"
        else:
            return "轻度"

    def _get_pattern_symptoms(list[str]):
        """获取证型相关症状"""
        symptom_map = {
            PatternType.QI_DEFICIENCY_PATTERN: ["气短", "乏力", "声低", "自汗"],
            PatternType.YIN_DEFICIENCY_PATTERN: ["潮热", "盗汗", "五心烦热", "口干"],
            PatternType.YANG_DEFICIENCY_PATTERN: ["畏寒", "肢冷", "精神不振", "小便清长"],
            PatternType.BLOOD_STASIS_PATTERN: ["胸痛", "舌暗", "肌肤甲错", "痛有定处"],
        }

        return symptom_map.get(pattern_type, [])

    def _get_pattern_pulse_indicators(list[str]):
        """获取证型脉象指标"""
        pulse_map = {
            PatternType.QI_DEFICIENCY_PATTERN: ["虚脉", "弱脉"],
            PatternType.YIN_DEFICIENCY_PATTERN: ["细脉", "数脉"],
            PatternType.YANG_DEFICIENCY_PATTERN: ["沉脉", "迟脉"],
            PatternType.BLOOD_STASIS_PATTERN: ["涩脉", "结脉"],
        }

        return pulse_map.get(pattern_type, [])

    def _get_pattern_constitution(ConstitutionType):
        """获取证型对应体质"""
        constitution_map = {
            PatternType.QI_DEFICIENCY_PATTERN: ConstitutionType.QI_DEFICIENCY,
            PatternType.YIN_DEFICIENCY_PATTERN: ConstitutionType.YIN_DEFICIENCY,
            PatternType.YANG_DEFICIENCY_PATTERN: ConstitutionType.YANG_DEFICIENCY,
            PatternType.BLOOD_STASIS_PATTERN: ConstitutionType.BLOOD_STASIS,
        }

        return constitution_map.get(pattern_type, ConstitutionType.BALANCED)

    def _merge_pattern_results(
        self, traditional_patterns: list[TCMPattern], ai_patterns: list[TCMPattern]
    ) - > list[TCMPattern]:
        """融合传统和AI分析结果"""
        # 创建证型字典
        pattern_dict = {}

        # 添加传统分析结果
        for pattern in traditional_patterns:
            key = pattern.pattern_type
            if key not in pattern_dict:
                pattern_dict[key] = pattern
            else:
                # 取置信度更高的
                if pattern.confidence > pattern_dict[key].confidence:
                    pattern_dict[key] = pattern

        # 融合AI分析结果
        for pattern in ai_patterns:
            key = pattern.pattern_type
            if key not in pattern_dict:
                pattern_dict[key] = pattern
            else:
                # 加权平均置信度
                existing = pattern_dict[key]
                merged_confidence = existing.confidence * 0.6 + pattern.confidence * 0.4
                existing.confidence = merged_confidence

        return list(pattern_dict.values())

    def _rank_and_filter_patterns(list[TCMPattern]):
        """排序和筛选证型"""
        # 按置信度排序
        patterns.sort(key = lambda p: p.confidence, reverse = True)

        # 筛选置信度高的证型
        filtered_patterns = [p for p in patterns if p.confidence > = self.confidence_threshold]

        # 最多返回前5个证型
        return filtered_patterns[:5]

    async def assess_constitution(
        self,
        pulse_features: dict[str, float],
        user_profile: dict[str, Any] | None = None,
        lifestyle_data: dict[str, Any] | None = None,
    ) - > ConstitutionType:
        """
        评估体质类型

        Args:
            pulse_features: 脉象特征
            user_profile: 用户档案
            lifestyle_data: 生活方式数据

        Returns:
            体质类型
        """
        try:
            # 基于脉象特征评估
            pulse_constitution = self._assess_constitution_from_pulse(pulse_features)

            # 基于用户档案评估
            profile_constitution = self._assess_constitution_from_profile(user_profile)

            # 基于生活方式评估
            lifestyle_constitution = self._assess_constitution_from_lifestyle(lifestyle_data)

            # 综合评估
            final_constitution = self._merge_constitution_assessments(
                pulse_constitution, profile_constitution, lifestyle_constitution
            )

            return final_constitution

        except Exception as e:
            logger.error(f"体质评估失败: {e}")
            return ConstitutionType.BALANCED

    def _assess_constitution_from_pulse(
        self, features: dict[str, float]
    ) - > dict[ConstitutionType, float]:
        """基于脉象评估体质"""
        scores = dict.fromkeys(ConstitutionType, 0.0)

        # 脉率评估
        heart_rate = features.get("heart_rate", 70)
        if heart_rate < 60:
            scores[ConstitutionType.YANG_DEFICIENCY] + = 0.3
        elif heart_rate > 90:
            scores[ConstitutionType.YIN_DEFICIENCY] + = 0.3
        else:
            scores[ConstitutionType.BALANCED] + = 0.2

        # 脉力评估
        strength = features.get("main_peak_amplitude", 0.5)
        if strength < 0.3:
            scores[ConstitutionType.QI_DEFICIENCY] + = 0.3
        elif strength > 0.8:
            scores[ConstitutionType.BALANCED] + = 0.2

        # 节律评估
        regularity = features.get("rhythm_regularity", 0.8)
        if regularity < 0.7:
            scores[ConstitutionType.QI_STAGNATION] + = 0.2
            scores[ConstitutionType.BLOOD_STASIS] + = 0.2

        return scores

    def _assess_constitution_from_profile(
        self, profile: dict[str, Any] | None
    ) - > dict[ConstitutionType, float]:
        """基于用户档案评估体质"""
        scores = dict.fromkeys(ConstitutionType, 0.0)

        if not profile:
            return scores

        # 年龄因素
        age = profile.get("age", 30)
        if age > 50:
            scores[ConstitutionType.YANG_DEFICIENCY] + = 0.1
            scores[ConstitutionType.QI_DEFICIENCY] + = 0.1
        elif age < 30:
            scores[ConstitutionType.BALANCED] + = 0.1

        # 性别因素
        gender = profile.get("gender", "unknown")
        if gender == "female":
            scores[ConstitutionType.YIN_DEFICIENCY] + = 0.05
            scores[ConstitutionType.BLOOD_STASIS] + = 0.05

        # BMI因素
        bmi = profile.get("bmi", 22)
        if bmi > 25:
            scores[ConstitutionType.PHLEGM_DAMPNESS] + = 0.2
        elif bmi < 18.5:
            scores[ConstitutionType.QI_DEFICIENCY] + = 0.1
            scores[ConstitutionType.YIN_DEFICIENCY] + = 0.1

        return scores

    def _assess_constitution_from_lifestyle(
        self, lifestyle: dict[str, Any] | None
    ) - > dict[ConstitutionType, float]:
        """基于生活方式评估体质"""
        scores = dict.fromkeys(ConstitutionType, 0.0)

        if not lifestyle:
            return scores

        # 睡眠质量
        sleep_quality = lifestyle.get("sleep_quality", "good")
        if sleep_quality == "poor":
            scores[ConstitutionType.YIN_DEFICIENCY] + = 0.1
            scores[ConstitutionType.QI_DEFICIENCY] + = 0.1

        # 运动习惯
        exercise_frequency = lifestyle.get("exercise_frequency", "moderate")
        if exercise_frequency == "low":
            scores[ConstitutionType.QI_DEFICIENCY] + = 0.1
            scores[ConstitutionType.PHLEGM_DAMPNESS] + = 0.1
        elif exercise_frequency == "high":
            scores[ConstitutionType.BALANCED] + = 0.1

        # 饮食习惯
        diet_preference = lifestyle.get("diet_preference", "balanced")
        if diet_preference == "spicy":
            scores[ConstitutionType.DAMP_HEAT] + = 0.1
        elif diet_preference == "cold":
            scores[ConstitutionType.YANG_DEFICIENCY] + = 0.1

        return scores

    def _merge_constitution_assessments(
        self,
        pulse_scores: dict[ConstitutionType, float],
        profile_scores: dict[ConstitutionType, float],
        lifestyle_scores: dict[ConstitutionType, float],
    ) - > ConstitutionType:
        """合并体质评估结果"""
        # 权重设置
        weights = self.constitution_rules["scoring_weights"]

        # 计算综合得分
        final_scores = {}
        for const in ConstitutionType:
            score = (
                pulse_scores.get(const, 0) * weights["pulse_features"]
                + profile_scores.get(const, 0) * weights["symptom_features"]
                + lifestyle_scores.get(const, 0) * weights["lifestyle_features"]
            )
            final_scores[const] = score

        # 选择得分最高的体质
        best_constitution = max(final_scores, key = final_scores.get)

        # 检查是否达到阈值
        threshold = self.constitution_rules["constitution_thresholds"][best_constitution]
        if final_scores[best_constitution] > = threshold:
            return best_constitution
        else:
            return ConstitutionType.BALANCED

    async def generate_health_assessment(
        self,
        patterns: list[TCMPattern],
        constitution: ConstitutionType,
        user_profile: dict[str, Any] | None = None,
    ) - > HealthAssessment:
        """
        生成健康评估报告

        Args:
            patterns: 识别的证型列表
            constitution: 体质类型
            user_profile: 用户档案

        Returns:
            健康评估结果
        """
        try:
            # 计算总体健康评分
            overall_score = self._calculate_health_score(patterns, constitution)

            # 识别风险因素
            risk_factors = self._identify_risk_factors(patterns, constitution)

            # 生成建议
            recommendations = self._generate_recommendations(patterns, constitution)

            # 确定复查间隔
            follow_up_interval = self._determine_follow_up_interval(patterns)

            return HealthAssessment(
                overall_score = overall_score,
                constitution_type = constitution,
                primary_patterns = patterns[:3],  # 前3个主要证型
                risk_factors = risk_factors,
                recommendations = recommendations,
                follow_up_interval = follow_up_interval,
            )

        except Exception as e:
            logger.error(f"健康评估生成失败: {e}")
            return HealthAssessment(
                overall_score = 70.0,
                constitution_type = ConstitutionType.BALANCED,
                primary_patterns = [],
                risk_factors = [],
                recommendations = ["建议咨询专业医师"],
                follow_up_interval = 30,
            )

    def _calculate_health_score(
        self, patterns: list[TCMPattern], constitution: ConstitutionType
    ) - > float:
        """计算健康评分"""
        base_score = 100.0

        # 根据证型扣分
        for pattern in patterns:
            if pattern.severity == "重度":
                base_score - = 20 * pattern.confidence
            elif pattern.severity == "中度":
                base_score - = 10 * pattern.confidence
            else:
                base_score - = 5 * pattern.confidence

        # 根据体质调整
        if constitution == ConstitutionType.BALANCED:
            base_score + = 5
        elif constitution in [ConstitutionType.QI_DEFICIENCY, ConstitutionType.YANG_DEFICIENCY]:
            base_score - = 10

        return max(0, min(100, base_score))

    def _identify_risk_factors(
        self, patterns: list[TCMPattern], constitution: ConstitutionType
    ) - > list[str]:
        """识别风险因素"""
        risk_factors = []

        # 基于证型识别风险
        for pattern in patterns:
            if pattern.pattern_type == PatternType.BLOOD_STASIS_PATTERN:
                risk_factors.append("心血管疾病风险")
            elif pattern.pattern_type == PatternType.YIN_DEFICIENCY_PATTERN:
                risk_factors.append("代谢紊乱风险")
            elif pattern.pattern_type == PatternType.QI_DEFICIENCY_PATTERN:
                risk_factors.append("免疫力下降风险")

        # 基于体质识别风险
        if constitution == ConstitutionType.PHLEGM_DAMPNESS:
            risk_factors.append("肥胖及相关疾病风险")
        elif constitution == ConstitutionType.DAMP_HEAT:
            risk_factors.append("炎症性疾病风险")

        return list(set(risk_factors))  # 去重

    def _generate_recommendations(
        self, patterns: list[TCMPattern], constitution: ConstitutionType
    ) - > list[str]:
        """生成健康建议"""
        recommendations = []

        # 基于主要证型生成建议
        if patterns:
            primary_pattern = patterns[0]
            recommendations.extend(primary_pattern.lifestyle_advice)

        # 基于体质生成建议
        constitution_advice = {
            ConstitutionType.QI_DEFICIENCY: ["加强营养，适当运动", "保证充足睡眠"],
            ConstitutionType.YIN_DEFICIENCY: ["避免熬夜，滋阴润燥", "减少辛辣食物"],
            ConstitutionType.YANG_DEFICIENCY: ["注意保暖，温阳补肾", "适当进补"],
            ConstitutionType.PHLEGM_DAMPNESS: ["控制体重，清淡饮食", "增加运动量"],
        }

        if constitution in constitution_advice:
            recommendations.extend(constitution_advice[constitution])

        # 通用建议
        recommendations.extend(
            ["定期体检，监测健康状况", "保持良好的生活习惯", "如有不适，及时就医"]
        )

        return list(set(recommendations))  # 去重

    def _determine_follow_up_interval(int):
        """确定复查间隔"""
        if not patterns:
            return 90  # 3个月

        # 根据最严重的证型确定间隔
        max_severity = max(patterns, key = lambda p: p.confidence)

        if max_severity.severity == "重度":
            return 14  # 2周
        elif max_severity.severity == "中度":
            return 30  # 1个月
        else:
            return 60  # 2个月
