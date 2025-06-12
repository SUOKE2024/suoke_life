"""
中医辨证分析器

基于五诊数据进行中医辨证分析，包括八纲辨证、气血津液辨证、脏腑辨证等
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Tuple

from .five_diagnosis_coordinator import DiagnosisResult, DiagnosisType

logger = logging.getLogger(__name__)


class SyndromeCategory(Enum):
    """证型分类"""

    EIGHT_PRINCIPLES = "eight_principles"  # 八纲辨证
    QI_BLOOD = "qi_blood"  # 气血辨证
    ZANG_FU = "zang_fu"  # 脏腑辨证
    SIX_CHANNELS = "six_channels"  # 六经辨证
    WEI_QI_YING_XUE = "wei_qi_ying_xue"  # 卫气营血辨证
    SAN_JIAO = "san_jiao"  # 三焦辨证


@dataclass
class SyndromePattern:
    """证型模式"""

    name: str
    category: SyndromeCategory
    confidence: float
    description: str
    key_features: List[str] = field(default_factory=list)
    related_organs: List[str] = field(default_factory=list)
    pathogenesis: str = ""
    treatment_principle: str = ""


@dataclass
class SyndromeAnalysisResult:
    """辨证分析结果"""

    primary_syndromes: List[SyndromePattern]
    secondary_syndromes: List[SyndromePattern]
    syndrome_combinations: List[Dict[str, Any]] = field(default_factory=list)
    pathogenesis_summary: str = ""
    treatment_principles: List[str] = field(default_factory=list)
    overall_confidence: float = 0.0
    analysis_timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class SyndromeAnalyzer:
    """中医辨证分析器"""

    def __init__(self):
        self.syndrome_patterns = self._load_syndrome_patterns()
        self.feature_weights = self._load_feature_weights()
        self.syndrome_rules = self._load_syndrome_rules()

    def _load_syndrome_patterns(self) -> Dict[str, SyndromePattern]:
        """加载证型模式库"""
        patterns = {
            # 八纲辨证
            "yang_deficiency": SyndromePattern(
                name="阳虚证",
                category=SyndromeCategory.EIGHT_PRINCIPLES,
                confidence=0.0,
                description="阳气不足，温煦功能减退",
                key_features=["畏寒", "四肢不温", "精神萎靡", "舌淡", "脉沉迟"],
                related_organs=["肾", "脾", "心"],
                pathogenesis="阳气虚衰，温煦失职",
                treatment_principle="温阳补气",
            ),
            "yin_deficiency": SyndromePattern(
                name="阴虚证",
                category=SyndromeCategory.EIGHT_PRINCIPLES,
                confidence=0.0,
                description="阴液不足，虚热内生",
                key_features=["五心烦热", "盗汗", "口干", "舌红少苔", "脉细数"],
                related_organs=["肾", "肺", "胃"],
                pathogenesis="阴液亏虚，虚火上炎",
                treatment_principle="滋阴降火",
            ),
            "qi_deficiency": SyndromePattern(
                name="气虚证",
                category=SyndromeCategory.QI_BLOOD,
                confidence=0.0,
                description="元气不足，脏腑功能减退",
                key_features=["神疲乏力", "气短懒言", "自汗", "舌淡", "脉弱"],
                related_organs=["脾", "肺", "肾"],
                pathogenesis="元气不足，脏腑失养",
                treatment_principle="补气健脾",
            ),
            "blood_stasis": SyndromePattern(
                name="血瘀证",
                category=SyndromeCategory.QI_BLOOD,
                confidence=0.0,
                description="血液运行不畅，瘀血内阻",
                key_features=["刺痛", "痛有定处", "舌紫暗", "脉涩"],
                related_organs=["心", "肝"],
                pathogenesis="血行不畅，瘀血阻络",
                treatment_principle="活血化瘀",
            ),
            "phlegm_dampness": SyndromePattern(
                name="痰湿证",
                category=SyndromeCategory.QI_BLOOD,
                confidence=0.0,
                description="痰湿内生，阻滞气机",
                key_features=["胸闷", "痰多", "身重", "舌苔厚腻", "脉滑"],
                related_organs=["脾", "肺"],
                pathogenesis="脾失健运，痰湿内生",
                treatment_principle="化痰除湿",
            ),
            "liver_qi_stagnation": SyndromePattern(
                name="肝气郁结",
                category=SyndromeCategory.ZANG_FU,
                confidence=0.0,
                description="肝气疏泄失常，气机郁滞",
                key_features=["胸胁胀痛", "情志抑郁", "善太息", "脉弦"],
                related_organs=["肝"],
                pathogenesis="情志不遂，肝气郁结",
                treatment_principle="疏肝理气",
            ),
            "spleen_qi_deficiency": SyndromePattern(
                name="脾气虚证",
                category=SyndromeCategory.ZANG_FU,
                confidence=0.0,
                description="脾气不足，运化失职",
                key_features=["食少腹胀", "便溏", "倦怠乏力", "舌淡苔白", "脉缓弱"],
                related_organs=["脾"],
                pathogenesis="脾气虚弱，运化失司",
                treatment_principle="健脾益气",
            ),
            "kidney_yang_deficiency": SyndromePattern(
                name="肾阳虚证",
                category=SyndromeCategory.ZANG_FU,
                confidence=0.0,
                description="肾阳不足，温煦失职",
                key_features=["腰膝酸冷", "阳痿", "小便清长", "舌淡", "脉沉迟"],
                related_organs=["肾"],
                pathogenesis="肾阳亏虚，命门火衰",
                treatment_principle="温补肾阳",
            ),
            "heart_blood_deficiency": SyndromePattern(
                name="心血虚证",
                category=SyndromeCategory.ZANG_FU,
                confidence=0.0,
                description="心血不足，心神失养",
                key_features=["心悸", "失眠", "健忘", "面色淡白", "脉细弱"],
                related_organs=["心"],
                pathogenesis="心血不足，心神失养",
                treatment_principle="养血安神",
            ),
            "lung_qi_deficiency": SyndromePattern(
                name="肺气虚证",
                category=SyndromeCategory.ZANG_FU,
                confidence=0.0,
                description="肺气不足，宣降失职",
                key_features=["咳嗽气短", "声音低微", "易感冒", "舌淡", "脉弱"],
                related_organs=["肺"],
                pathogenesis="肺气虚弱，宣降失司",
                treatment_principle="补肺益气",
            ),
        }
        return patterns

    def _load_feature_weights(self) -> Dict[str, float]:
        """加载特征权重"""
        return {
            # 舌象特征权重
            "tongue_color": 0.8,
            "tongue_coating": 0.7,
            "tongue_shape": 0.6,
            # 脉象特征权重
            "pulse_rate": 0.9,
            "pulse_strength": 0.8,
            "pulse_rhythm": 0.7,
            # 症状特征权重
            "chief_complaint": 1.0,
            "pain_characteristics": 0.9,
            "sleep_quality": 0.7,
            "appetite": 0.6,
            "mood": 0.6,
            # 面色特征权重
            "face_color": 0.7,
            "complexion": 0.6,
            # 声音特征权重
            "voice_strength": 0.6,
            "voice_quality": 0.5,
        }

    def _load_syndrome_rules(self) -> List[Dict[str, Any]]:
        """加载辨证规则"""
        return [
            {
                "syndrome": "yang_deficiency",
                "required_features": ["畏寒", "四肢不温"],
                "supporting_features": ["精神萎靡", "舌淡", "脉沉迟"],
                "min_confidence": 0.6,
            },
            {
                "syndrome": "yin_deficiency",
                "required_features": ["五心烦热"],
                "supporting_features": ["盗汗", "口干", "舌红少苔", "脉细数"],
                "min_confidence": 0.6,
            },
            {
                "syndrome": "qi_deficiency",
                "required_features": ["神疲乏力"],
                "supporting_features": ["气短懒言", "自汗", "舌淡", "脉弱"],
                "min_confidence": 0.6,
            },
            {
                "syndrome": "blood_stasis",
                "required_features": ["刺痛", "痛有定处"],
                "supporting_features": ["舌紫暗", "脉涩"],
                "min_confidence": 0.7,
            },
            {
                "syndrome": "phlegm_dampness",
                "required_features": ["痰多"],
                "supporting_features": ["胸闷", "身重", "舌苔厚腻", "脉滑"],
                "min_confidence": 0.6,
            },
        ]

    async def analyze(self, diagnosis_results: List[DiagnosisResult]) -> Dict[str, Any]:
        """执行辨证分析"""
        logger.info("开始中医辨证分析...")

        try:
            # 提取诊断特征
            extracted_features = await self._extract_features(diagnosis_results)

            # 计算证型匹配度
            syndrome_scores = await self._calculate_syndrome_scores(extracted_features)

            # 识别主要证型和次要证型
            primary_syndromes, secondary_syndromes = await self._identify_syndromes(
                syndrome_scores
            )

            # 分析证型组合
            syndrome_combinations = await self._analyze_syndrome_combinations(
                primary_syndromes, secondary_syndromes
            )

            # 生成病机总结
            pathogenesis_summary = await self._generate_pathogenesis_summary(
                primary_syndromes, syndrome_combinations
            )

            # 确定治疗原则
            treatment_principles = await self._determine_treatment_principles(
                primary_syndromes, secondary_syndromes
            )

            # 计算整体置信度
            overall_confidence = self._calculate_overall_confidence(primary_syndromes)

            result = SyndromeAnalysisResult(
                primary_syndromes=primary_syndromes,
                secondary_syndromes=secondary_syndromes,
                syndrome_combinations=syndrome_combinations,
                pathogenesis_summary=pathogenesis_summary,
                treatment_principles=treatment_principles,
                overall_confidence=overall_confidence,
            )

            logger.info(f"辨证分析完成，识别到 {len(primary_syndromes)} 个主要证型")

            return {
                "primary_syndromes": [
                    self._syndrome_to_dict(s) for s in primary_syndromes
                ],
                "secondary_syndromes": [
                    self._syndrome_to_dict(s) for s in secondary_syndromes
                ],
                "syndrome_combinations": syndrome_combinations,
                "pathogenesis_summary": pathogenesis_summary,
                "treatment_principles": treatment_principles,
                "overall_confidence": overall_confidence,
                "analysis_timestamp": result.analysis_timestamp.isoformat(),
            }

        except Exception as e:
            logger.error(f"辨证分析失败: {e}")
            return {
                "primary_syndromes": [],
                "secondary_syndromes": [],
                "syndrome_combinations": [],
                "pathogenesis_summary": "辨证分析失败",
                "treatment_principles": [],
                "overall_confidence": 0.0,
                "error": str(e),
            }

    async def _extract_features(
        self, diagnosis_results: List[DiagnosisResult]
    ) -> Dict[str, Any]:
        """从诊断结果中提取特征"""
        features = {
            "symptoms": [],
            "tongue_features": {},
            "pulse_features": {},
            "face_features": {},
            "voice_features": {},
            "constitution_indicators": [],
        }

        for result in diagnosis_results:
            if result.diagnosis_type == DiagnosisType.LOOKING:
                # 提取望诊特征
                features.update(self._extract_looking_features(result))
            elif result.diagnosis_type == DiagnosisType.LISTENING:
                # 提取闻诊特征
                features.update(self._extract_listening_features(result))
            elif result.diagnosis_type == DiagnosisType.INQUIRY:
                # 提取问诊特征
                features.update(self._extract_inquiry_features(result))
            elif result.diagnosis_type == DiagnosisType.PALPATION:
                # 提取切诊特征
                features.update(self._extract_palpation_features(result))

        return features

    def _extract_looking_features(self, result: DiagnosisResult) -> Dict[str, Any]:
        """提取望诊特征"""
        features = {}

        if "tongue_analysis" in result.features:
            tongue = result.features["tongue_analysis"]
            features["tongue_features"] = {
                "color": tongue.get("tongue_color", ""),
                "coating": tongue.get("coating_color", ""),
                "shape": tongue.get("tongue_shape", ""),
                "moisture": tongue.get("moisture", ""),
            }

        if "face_analysis" in result.features:
            face = result.features["face_analysis"]
            features["face_features"] = {
                "color": face.get("overall_color", ""),
                "complexion": face.get("complexion", ""),
                "luster": face.get("luster", ""),
            }

        return features

    def _extract_listening_features(self, result: DiagnosisResult) -> Dict[str, Any]:
        """提取闻诊特征"""
        features = {}

        if "voice_analysis" in result.features:
            voice = result.features["voice_analysis"]
            features["voice_features"] = {
                "strength": voice.get("voice_strength", ""),
                "quality": voice.get("voice_quality", ""),
                "rhythm": voice.get("speech_rhythm", ""),
            }

        if "breathing_analysis" in result.features:
            breathing = result.features["breathing_analysis"]
            features["breathing_features"] = {
                "rate": breathing.get("breathing_rate", 0),
                "depth": breathing.get("breathing_depth", ""),
                "sound": breathing.get("breathing_sound", ""),
            }

        return features

    def _extract_inquiry_features(self, result: DiagnosisResult) -> Dict[str, Any]:
        """提取问诊特征"""
        features = {}

        if "conversation_analysis" in result.features:
            conversation = result.features["conversation_analysis"]
            features["symptoms"] = self._parse_symptoms(
                conversation.get("chief_complaint", "")
            )
            features["pain_characteristics"] = conversation.get("pain_description", "")
            features["sleep_quality"] = conversation.get("sleep_quality", "")
            features["appetite"] = conversation.get("appetite", "")

        return features

    def _extract_palpation_features(self, result: DiagnosisResult) -> Dict[str, Any]:
        """提取切诊特征"""
        features = {}

        if "pulse_analysis" in result.features:
            pulse = result.features["pulse_analysis"]
            features["pulse_features"] = {
                "rate": pulse.get("pulse_overall_type", ""),
                "strength": pulse.get("pulse_force", ""),
                "rhythm": pulse.get("pulse_rhythm", ""),
                "depth": pulse.get("pulse_depth", ""),
            }

        return features

    def _parse_symptoms(self, chief_complaint: str) -> List[str]:
        """解析症状"""
        # 简单的症状关键词提取
        symptom_keywords = [
            "畏寒",
            "四肢不温",
            "精神萎靡",
            "五心烦热",
            "盗汗",
            "口干",
            "神疲乏力",
            "气短懒言",
            "自汗",
            "刺痛",
            "痛有定处",
            "胸闷",
            "痰多",
            "身重",
            "胸胁胀痛",
            "情志抑郁",
            "善太息",
            "食少腹胀",
            "便溏",
            "倦怠乏力",
            "腰膝酸冷",
            "阳痿",
            "小便清长",
            "心悸",
            "失眠",
            "健忘",
            "面色淡白",
            "咳嗽气短",
            "声音低微",
            "易感冒",
        ]

        found_symptoms = []
        for symptom in symptom_keywords:
            if symptom in chief_complaint:
                found_symptoms.append(symptom)

        return found_symptoms

    async def _calculate_syndrome_scores(
        self, features: Dict[str, Any]
    ) -> Dict[str, float]:
        """计算证型匹配度"""
        syndrome_scores = {}

        for syndrome_name, pattern in self.syndrome_patterns.items():
            score = 0.0
            total_weight = 0.0

            # 检查关键特征
            for key_feature in pattern.key_features:
                weight = self.feature_weights.get(key_feature, 0.5)
                total_weight += weight

                if self._feature_matches(key_feature, features):
                    score += weight

            # 归一化分数
            syndrome_scores[syndrome_name] = (
                score / total_weight if total_weight > 0 else 0.0
            )

        return syndrome_scores

    def _feature_matches(
        self, feature: str, extracted_features: Dict[str, Any]
    ) -> bool:
        """检查特征是否匹配"""
        # 检查症状列表
        if feature in extracted_features.get("symptoms", []):
            return True

        # 检查舌象特征
        tongue_features = extracted_features.get("tongue_features", {})
        if feature == "舌淡" and tongue_features.get("color") in ["淡红", "淡白"]:
            return True
        if (
            feature == "舌红少苔"
            and tongue_features.get("color") == "红"
            and "少苔" in tongue_features.get("coating", "")
        ):
            return True
        if feature == "舌紫暗" and "紫" in tongue_features.get("color", ""):
            return True
        if feature == "舌苔厚腻" and "厚腻" in tongue_features.get("coating", ""):
            return True

        # 检查脉象特征
        pulse_features = extracted_features.get("pulse_features", {})
        if (
            feature == "脉沉迟"
            and pulse_features.get("depth") == "沉"
            and "迟" in pulse_features.get("rate", "")
        ):
            return True
        if (
            feature == "脉细数"
            and "细" in pulse_features.get("strength", "")
            and "数" in pulse_features.get("rate", "")
        ):
            return True
        if feature == "脉弱" and "弱" in pulse_features.get("strength", ""):
            return True
        if feature == "脉涩" and "涩" in pulse_features.get("rhythm", ""):
            return True
        if feature == "脉滑" and "滑" in pulse_features.get("rhythm", ""):
            return True
        if feature == "脉弦" and "弦" in pulse_features.get("strength", ""):
            return True
        if (
            feature == "脉缓弱"
            and "缓" in pulse_features.get("rate", "")
            and "弱" in pulse_features.get("strength", "")
        ):
            return True

        return False

    async def _identify_syndromes(
        self, syndrome_scores: Dict[str, float]
    ) -> Tuple[List[SyndromePattern], List[SyndromePattern]]:
        """识别主要证型和次要证型"""
        # 按分数排序
        sorted_syndromes = sorted(
            syndrome_scores.items(), key=lambda x: x[1], reverse=True
        )

        primary_syndromes = []
        secondary_syndromes = []

        for syndrome_name, score in sorted_syndromes:
            if score >= 0.7:  # 高置信度阈值
                pattern = self.syndrome_patterns[syndrome_name]
                pattern.confidence = score
                primary_syndromes.append(pattern)
            elif score >= 0.4:  # 中等置信度阈值
                pattern = self.syndrome_patterns[syndrome_name]
                pattern.confidence = score
                secondary_syndromes.append(pattern)

        return primary_syndromes[:3], secondary_syndromes[:5]  # 限制数量

    async def _analyze_syndrome_combinations(
        self,
        primary_syndromes: List[SyndromePattern],
        secondary_syndromes: List[SyndromePattern],
    ) -> List[Dict[str, Any]]:
        """分析证型组合"""
        combinations = []

        # 常见证型组合模式
        combination_patterns = {
            ("qi_deficiency", "blood_stasis"): {
                "name": "气虚血瘀",
                "description": "气虚推动无力，血行瘀滞",
                "treatment": "益气活血",
            },
            ("yin_deficiency", "yang_deficiency"): {
                "name": "阴阳两虚",
                "description": "阴阳俱虚，需要阴阳并补",
                "treatment": "阴阳双补",
            },
            ("liver_qi_stagnation", "spleen_qi_deficiency"): {
                "name": "肝郁脾虚",
                "description": "肝气郁结，脾气虚弱",
                "treatment": "疏肝健脾",
            },
            ("phlegm_dampness", "qi_deficiency"): {
                "name": "痰湿气虚",
                "description": "脾虚生痰，痰湿困脾",
                "treatment": "健脾化痰",
            },
        }

        # 检查证型组合
        primary_names = [s.name for s in primary_syndromes]
        for pattern_key, pattern_info in combination_patterns.items():
            if all(name in primary_names for name in pattern_key):
                combinations.append(
                    {
                        "syndromes": list(pattern_key),
                        "combination_name": pattern_info["name"],
                        "description": pattern_info["description"],
                        "treatment_principle": pattern_info["treatment"],
                    }
                )

        return combinations

    async def _generate_pathogenesis_summary(
        self,
        primary_syndromes: List[SyndromePattern],
        syndrome_combinations: List[Dict[str, Any]],
    ) -> str:
        """生成病机总结"""
        if not primary_syndromes:
            return "病机不明"

        if syndrome_combinations:
            # 有证型组合时，使用组合的病机描述
            combination = syndrome_combinations[0]
            return f"{combination['combination_name']}：{combination['description']}"
        else:
            # 单一证型时，使用主要证型的病机
            main_syndrome = primary_syndromes[0]
            return f"{main_syndrome.name}：{main_syndrome.pathogenesis}"

    async def _determine_treatment_principles(
        self,
        primary_syndromes: List[SyndromePattern],
        secondary_syndromes: List[SyndromePattern],
    ) -> List[str]:
        """确定治疗原则"""
        principles = []

        for syndrome in primary_syndromes:
            if (
                syndrome.treatment_principle
                and syndrome.treatment_principle not in principles
            ):
                principles.append(syndrome.treatment_principle)

        return principles[:3]  # 限制数量

    def _calculate_overall_confidence(
        self, primary_syndromes: List[SyndromePattern]
    ) -> float:
        """计算整体置信度"""
        if not primary_syndromes:
            return 0.0

        # 使用主要证型的平均置信度
        total_confidence = sum(s.confidence for s in primary_syndromes)
        return total_confidence / len(primary_syndromes)

    def _syndrome_to_dict(self, syndrome: SyndromePattern) -> Dict[str, Any]:
        """将证型对象转换为字典"""
        return {
            "name": syndrome.name,
            "category": syndrome.category.value,
            "confidence": syndrome.confidence,
            "description": syndrome.description,
            "key_features": syndrome.key_features,
            "related_organs": syndrome.related_organs,
            "pathogenesis": syndrome.pathogenesis,
            "treatment_principle": syndrome.treatment_principle,
        }
