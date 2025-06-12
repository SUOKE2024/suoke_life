"""
中医体质分析器

基于《中医体质分类与判定》标准，分析用户的体质类型
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import logging
from typing import Any, Dict, List, Optional

from .five_diagnosis_coordinator import DiagnosisResult, DiagnosisType

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


@dataclass
class ConstitutionFeature:
    """体质特征"""

    name: str
    weight: float
    description: str
    category: str  # 形体、精神、睡眠、饮食、二便、舌脉等


@dataclass
class ConstitutionScore:
    """体质得分"""

    constitution_type: ConstitutionType
    raw_score: float
    normalized_score: float
    is_dominant: bool
    confidence: float
    supporting_features: List[str] = field(default_factory=list)


@dataclass
class ConstitutionAnalysisResult:
    """体质分析结果"""

    dominant_constitution: Optional[ConstitutionScore]
    constitution_scores: List[ConstitutionScore]
    constitution_tendency: List[ConstitutionType] = field(default_factory=list)
    health_guidance: Dict[str, Any] = field(default_factory=dict)
    analysis_summary: str = ""
    overall_confidence: float = 0.0
    analysis_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ConstitutionAnalyzer:
    """中医体质分析器"""

    def __init__(self):
        self.constitution_features = self._load_constitution_features()
        self.scoring_rules = self._load_scoring_rules()
        self.health_guidance_templates = self._load_health_guidance()

    def _load_constitution_features(self) -> Dict[ConstitutionType, List[ConstitutionFeature]]:
        """加载体质特征库"""
        features = {
            ConstitutionType.BALANCED: [
                ConstitutionFeature("体形匀称健壮", 0.8, "身材不胖不瘦，体形匀称", "形体"),
                ConstitutionFeature("面色润泽", 0.7, "面色红润有光泽", "面色"),
                ConstitutionFeature("精力充沛", 0.8, "精神饱满，活力充沛", "精神"),
                ConstitutionFeature("睡眠良好", 0.7, "入睡容易，睡眠深沉", "睡眠"),
                ConstitutionFeature("食欲正常", 0.6, "食欲良好，不挑食", "饮食"),
                ConstitutionFeature("二便正常", 0.7, "大小便正常", "二便"),
                ConstitutionFeature("舌淡红苔薄白", 0.8, "舌质淡红，苔薄白", "舌象"),
                ConstitutionFeature("脉和缓有力", 0.7, "脉象和缓有力", "脉象"),
            ],
            ConstitutionType.QI_DEFICIENCY: [
                ConstitutionFeature("容易疲乏", 0.9, "平素语音低弱，气短懒言", "精神"),
                ConstitutionFeature("容易出汗", 0.8, "平素易出汗，不耐受风、寒、暑、湿邪", "汗出"),
                ConstitutionFeature("舌淡红", 0.7, "舌淡红，舌边有齿痕", "舌象"),
                ConstitutionFeature("脉弱", 0.8, "脉象虚弱", "脉象"),
                ConstitutionFeature("容易感冒", 0.7, "平素体质虚弱，易感冒", "体质"),
                ConstitutionFeature("声音低微", 0.6, "说话声音低微", "声音"),
                ConstitutionFeature("面色萎黄", 0.7, "面色萎黄或淡白", "面色"),
            ],
            ConstitutionType.YANG_DEFICIENCY: [
                ConstitutionFeature("畏寒怕冷", 0.9, "平素畏冷，手足不温", "寒热"),
                ConstitutionFeature("喜热饮食", 0.7, "喜热饮食，不耐寒邪", "饮食"),
                ConstitutionFeature("精神不振", 0.8, "精神不振，睡眠偏多", "精神"),
                ConstitutionFeature("舌淡胖", 0.8, "舌淡胖嫩，边有齿痕", "舌象"),
                ConstitutionFeature("脉沉迟", 0.8, "脉象沉迟而弱", "脉象"),
                ConstitutionFeature("面色柔白", 0.6, "面色柔白", "面色"),
                ConstitutionFeature("小便清长", 0.7, "小便清长，夜尿多", "二便"),
            ],
            ConstitutionType.YIN_DEFICIENCY: [
                ConstitutionFeature("手足心热", 0.9, "手足心热，平素易上火", "寒热"),
                ConstitutionFeature("口燥咽干", 0.8, "口燥咽干，喜冷饮", "津液"),
                ConstitutionFeature("大便干燥", 0.7, "大便干燥，小便短赤", "二便"),
                ConstitutionFeature("舌红少津", 0.8, "舌红少津，苔少", "舌象"),
                ConstitutionFeature("脉细数", 0.8, "脉象细数", "脉象"),
                ConstitutionFeature("面色潮红", 0.6, "面色潮红，有烘热感", "面色"),
                ConstitutionFeature("眼干涩", 0.6, "眼干涩，视物花", "五官"),
                ConstitutionFeature("皮肤干燥", 0.7, "皮肤干燥，易生皱纹", "皮肤"),
            ],
            ConstitutionType.PHLEGM_DAMPNESS: [
                ConstitutionFeature("形体肥胖", 0.9, "形体肥胖，腹部肥满松软", "形体"),
                ConstitutionFeature("容易困倦", 0.8, "平素多汗，易困倦", "精神"),
                ConstitutionFeature("痰多", 0.8, "痰多，口黏腻或甜", "痰湿"),
                ConstitutionFeature("舌体胖大", 0.8, "舌体胖大，苔白腻", "舌象"),
                ConstitutionFeature("脉滑", 0.7, "脉象滑", "脉象"),
                ConstitutionFeature("面部皮肤油脂多", 0.6, "面部皮肤油脂较多", "皮肤"),
                ConstitutionFeature("胸闷", 0.7, "胸闷，腹胀", "症状"),
            ],
            ConstitutionType.DAMP_HEAT: [
                ConstitutionFeature("面垢油腻", 0.8, "面垢油腻，易生痤疮", "面色"),
                ConstitutionFeature("口苦口干", 0.8, "口苦口干，身重困倦", "津液"),
                ConstitutionFeature("大便黏滞", 0.8, "大便黏滞不爽或燥结", "二便"),
                ConstitutionFeature("小便短赤", 0.7, "小便短赤", "二便"),
                ConstitutionFeature("舌质偏红", 0.8, "舌质偏红，苔黄腻", "舌象"),
                ConstitutionFeature("脉滑数", 0.7, "脉象滑数", "脉象"),
                ConstitutionFeature("易生疮疖", 0.6, "易生疮疖", "皮肤"),
            ],
            ConstitutionType.BLOOD_STASIS: [
                ConstitutionFeature("肤色晦暗", 0.8, "肤色晦黯，色素沉着", "面色"),
                ConstitutionFeature("容易出现瘀斑", 0.9, "容易出现瘀斑，疼痛", "血瘀"),
                ConstitutionFeature("口唇黯淡", 0.7, "口唇黯淡，舌黯或有瘀点", "舌象"),
                ConstitutionFeature("脉涩", 0.8, "脉象涩", "脉象"),
                ConstitutionFeature("眼眶黯黑", 0.6, "眼眶黯黑", "五官"),
                ConstitutionFeature("头发易脱落", 0.5, "头发容易脱落", "毛发"),
                ConstitutionFeature("健忘", 0.6, "健忘，烦躁", "精神"),
            ],
            ConstitutionType.QI_STAGNATION: [
                ConstitutionFeature("情绪不稳定", 0.9, "情绪不稳定，烦闷不乐", "精神"),
                ConstitutionFeature("胸胁胀满", 0.8, "胸胁胀满，或走窜疼痛", "症状"),
                ConstitutionFeature("善太息", 0.8, "善太息，易惊恐", "精神"),
                ConstitutionFeature("舌淡红", 0.6, "舌淡红，苔薄白", "舌象"),
                ConstitutionFeature("脉弦", 0.8, "脉象弦", "脉象"),
                ConstitutionFeature("睡眠不安", 0.7, "睡眠不安，多梦", "睡眠"),
                ConstitutionFeature("咽部异物感", 0.6, "咽部如有异物感", "五官"),
            ],
            ConstitutionType.SPECIAL_DIATHESIS: [
                ConstitutionFeature("过敏体质", 0.9, "易过敏，对外界适应能力差", "过敏"),
                ConstitutionFeature("鼻塞流涕", 0.8, "常鼻塞、打喷嚏、流清涕", "五官"),
                ConstitutionFeature("皮肤过敏", 0.8, "皮肤易起荨麻疹", "皮肤"),
                ConstitutionFeature("哮喘", 0.7, "易患哮喘", "呼吸"),
                ConstitutionFeature("药物过敏", 0.6, "对药物、食物、气味过敏", "过敏"),
                ConstitutionFeature("舌淡", 0.5, "舌淡，苔白", "舌象"),
                ConstitutionFeature("脉濡弱", 0.6, "脉象濡弱", "脉象"),
            ],
        }
        return features

    def _load_scoring_rules(self) -> Dict[str, Any]:
        """加载评分规则"""
        return {
            "feature_threshold": 0.6,  # 特征匹配阈值
            "dominant_threshold": 60,  # 主导体质阈值
            "tendency_threshold": 40,  # 倾向体质阈值
            "max_score": 100,  # 最高分数
            "min_confidence": 0.5,  # 最低置信度
        }

    def _load_health_guidance(self) -> Dict[ConstitutionType, Dict[str, Any]]:
        """加载健康指导模板"""
        return {
            ConstitutionType.BALANCED: {
                "diet": "饮食有节，不要过饥过饱，不要常吃过冷过热或不干净的食物",
                "exercise": "可选择运动量较大的锻炼项目，如跑步、武术、球类等",
                "lifestyle": "起居有常，劳逸结合，保持充足睡眠",
                "emotion": "保持平和心态，避免大喜大悲",
                "season": "顺应四时变化，适时调整作息",
            },
            ConstitutionType.QI_DEFICIENCY: {
                "diet": "宜食性平偏温、健脾益气的食物，如大枣、山药、小米等",
                "exercise": "适合缓和、柔缓的运动，如散步、太极拳等",
                "lifestyle": "起居有常，避免过度劳累，保证充足睡眠",
                "emotion": "保持乐观情绪，避免过度思虑",
                "season": "春夏养阳，注意保暖，避免出汗过多",
            },
            ConstitutionType.YANG_DEFICIENCY: {
                "diet": "宜食温热的食物，如羊肉、韭菜、生姜等，少食生冷",
                "exercise": "适合舒缓柔和的运动，避免大汗淋漓",
                "lifestyle": "注意保暖，尤其是背部和下肢，避免熬夜",
                "emotion": "保持积极乐观的心态，多与人交流",
                "season": "春夏养阳，秋冬注意保暖防寒",
            },
            ConstitutionType.YIN_DEFICIENCY: {
                "diet": "宜食甘凉滋润的食物，如百合、枸杞、银耳等",
                "exercise": "适合中小强度的运动，避免大汗淋漓",
                "lifestyle": "规律作息，避免熬夜，保证充足睡眠",
                "emotion": "保持心境平和，避免情绪激动",
                "season": "秋冬养阴，夏季避免暴晒，注意防暑",
            },
            ConstitutionType.PHLEGM_DAMPNESS: {
                "diet": "宜食清淡、少盐少糖，多食健脾利湿的食物",
                "exercise": "适合较大运动量的锻炼，如跑步、游泳等",
                "lifestyle": "居住环境宜干燥，避免潮湿",
                "emotion": "保持乐观开朗的心情，多参加社交活动",
                "season": "梅雨季节注意除湿，避免贪凉饮冷",
            },
            ConstitutionType.DAMP_HEAT: {
                "diet": "宜食清热利湿的食物，如绿豆、冬瓜、苦瓜等",
                "exercise": "适合大强度、大运动量的锻炼",
                "lifestyle": "居住环境宜干燥通风，避免熬夜",
                "emotion": "保持心境平和，避免急躁易怒",
                "season": "夏季避免暑湿，长夏注意化湿",
            },
            ConstitutionType.BLOOD_STASIS: {
                "diet": "宜食活血化瘀的食物，如山楂、醋、玫瑰花等",
                "exercise": "适合促进气血运行的运动，如太极拳、八段锦",
                "lifestyle": "保持规律作息，避免久坐久立",
                "emotion": "保持心情舒畅，避免情绪郁闷",
                "season": "注意保暖，避免寒凝血瘀",
            },
            ConstitutionType.QI_STAGNATION: {
                "diet": "宜食行气解郁的食物，如柑橘、柚子、佛手等",
                "exercise": "适合户外运动，如慢跑、登山、游泳等",
                "lifestyle": "保持规律作息，创造安静的睡眠环境",
                "emotion": "保持心情愉快，多参加集体活动",
                "season": "春季注意疏肝理气，避免情志不畅",
            },
            ConstitutionType.SPECIAL_DIATHESIS: {
                "diet": "饮食清淡，避免腥膻发物和含致敏物质的食物",
                "exercise": "适合温和的运动，避免剧烈运动",
                "lifestyle": "居住环境避免花粉、粉尘等过敏原",
                "emotion": "保持心境平和，避免情绪波动",
                "season": "春季防风，夏季防暑湿，注意环境卫生",
            },
        }

    async def analyze(self, diagnosis_results: List[DiagnosisResult]) -> Dict[str, Any]:
        """执行体质分析"""
        logger.info("开始中医体质分析...")

        try:
            # 提取体质相关特征
            extracted_features = await self._extract_constitution_features(diagnosis_results)

            # 计算各体质得分
            constitution_scores = await self._calculate_constitution_scores(extracted_features)

            # 确定主导体质
            dominant_constitution = self._determine_dominant_constitution(constitution_scores)

            # 确定体质倾向
            constitution_tendency = self._determine_constitution_tendency(constitution_scores)

            # 生成健康指导
            health_guidance = await self._generate_health_guidance(
                dominant_constitution, constitution_tendency
            )

            # 生成分析总结
            analysis_summary = await self._generate_analysis_summary(
                dominant_constitution, constitution_tendency
            )

            # 计算整体置信度
            overall_confidence = self._calculate_overall_confidence(constitution_scores)

            result = ConstitutionAnalysisResult(
                dominant_constitution=dominant_constitution,
                constitution_scores=constitution_scores,
                constitution_tendency=constitution_tendency,
                health_guidance=health_guidance,
                analysis_summary=analysis_summary,
                overall_confidence=overall_confidence,
            )

            logger.info(
                f"体质分析完成，主导体质：{dominant_constitution.constitution_type.value if dominant_constitution else '未确定'}"
            )

            return {
                "dominant_constitution": (
                    self._constitution_score_to_dict(dominant_constitution)
                    if dominant_constitution
                    else None
                ),
                "constitution_scores": [
                    self._constitution_score_to_dict(score) for score in constitution_scores
                ],
                "constitution_tendency": [ct.value for ct in constitution_tendency],
                "health_guidance": health_guidance,
                "analysis_summary": analysis_summary,
                "overall_confidence": overall_confidence,
                "analysis_timestamp": result.analysis_timestamp.isoformat(),
            }

        except Exception as e:
            logger.error(f"体质分析失败: {e}")
            return {
                "dominant_constitution": None,
                "constitution_scores": [],
                "constitution_tendency": [],
                "health_guidance": {},
                "analysis_summary": "体质分析失败",
                "overall_confidence": 0.0,
                "error": str(e),
            }

    async def _extract_constitution_features(
        self, diagnosis_results: List[DiagnosisResult]
    ) -> Dict[str, Any]:
        """提取体质相关特征"""
        features = {
            "physical_features": {},  # 形体特征
            "mental_features": {},  # 精神特征
            "sleep_features": {},  # 睡眠特征
            "diet_features": {},  # 饮食特征
            "excretion_features": {},  # 二便特征
            "tongue_features": {},  # 舌象特征
            "pulse_features": {},  # 脉象特征
            "skin_features": {},  # 皮肤特征
            "voice_features": {},  # 声音特征
            "symptoms": [],  # 症状列表
        }

        for result in diagnosis_results:
            if result.diagnosis_type == DiagnosisType.LOOKING:
                features.update(self._extract_looking_constitution_features(result))
            elif result.diagnosis_type == DiagnosisType.LISTENING:
                features.update(self._extract_listening_constitution_features(result))
            elif result.diagnosis_type == DiagnosisType.INQUIRY:
                features.update(self._extract_inquiry_constitution_features(result))
            elif result.diagnosis_type == DiagnosisType.PALPATION:
                features.update(self._extract_palpation_constitution_features(result))

        return features

    def _extract_looking_constitution_features(self, result: DiagnosisResult) -> Dict[str, Any]:
        """提取望诊体质特征"""
        features = {}

        # 舌象特征
        if "tongue_analysis" in result.features:
            tongue = result.features["tongue_analysis"]
            features["tongue_features"] = {
                "color": tongue.get("tongue_color", ""),
                "coating": tongue.get("coating_color", ""),
                "shape": tongue.get("tongue_shape", ""),
                "moisture": tongue.get("moisture", ""),
            }

        # 面色特征
        if "face_analysis" in result.features:
            face = result.features["face_analysis"]
            features["physical_features"] = {
                "face_color": face.get("overall_color", ""),
                "complexion": face.get("complexion", ""),
                "luster": face.get("luster", ""),
            }

        # 形体特征
        if "body_analysis" in result.features:
            body = result.features["body_analysis"]
            features["physical_features"].update(
                {
                    "body_type": body.get("body_type", ""),
                    "posture": body.get("posture", ""),
                    "bmi": body.get("bmi", 0),
                }
            )

        return features

    def _extract_listening_constitution_features(self, result: DiagnosisResult) -> Dict[str, Any]:
        """提取闻诊体质特征"""
        features = {}

        if "voice_analysis" in result.features:
            voice = result.features["voice_analysis"]
            features["voice_features"] = {
                "strength": voice.get("voice_strength", ""),
                "quality": voice.get("voice_quality", ""),
                "rhythm": voice.get("speech_rhythm", ""),
            }

        return features

    def _extract_inquiry_constitution_features(self, result: DiagnosisResult) -> Dict[str, Any]:
        """提取问诊体质特征"""
        features = {}

        if "conversation_analysis" in result.features:
            conversation = result.features["conversation_analysis"]

            # 精神状态
            features["mental_features"] = {
                "energy_level": self._extract_energy_level(conversation),
                "mood": self._extract_mood(conversation),
                "stress_level": self._extract_stress_level(conversation),
            }

            # 睡眠特征
            features["sleep_features"] = {
                "sleep_quality": conversation.get("sleep_quality", ""),
                "sleep_duration": conversation.get("sleep_duration", ""),
                "dream_frequency": conversation.get("dream_frequency", ""),
            }

            # 饮食特征
            features["diet_features"] = {
                "appetite": conversation.get("appetite", ""),
                "food_preferences": conversation.get("food_preferences", ""),
                "thirst": conversation.get("thirst", ""),
            }

            # 症状提取
            features["symptoms"] = self._extract_constitution_symptoms(conversation)

        return features

    def _extract_palpation_constitution_features(self, result: DiagnosisResult) -> Dict[str, Any]:
        """提取切诊体质特征"""
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

    def _extract_energy_level(self, conversation: Dict[str, Any]) -> str:
        """提取精力水平"""
        chief_complaint = conversation.get("chief_complaint", "")
        if any(keyword in chief_complaint for keyword in ["疲乏", "乏力", "困倦", "精神不振"]):
            return "低"
        elif any(keyword in chief_complaint for keyword in ["精力充沛", "精神饱满"]):
            return "高"
        return "中等"

    def _extract_mood(self, conversation: Dict[str, Any]) -> str:
        """提取情绪状态"""
        chief_complaint = conversation.get("chief_complaint", "")
        if any(keyword in chief_complaint for keyword in ["抑郁", "烦躁", "易怒", "焦虑"]):
            return "不稳定"
        elif any(keyword in chief_complaint for keyword in ["开朗", "乐观"]):
            return "稳定"
        return "一般"

    def _extract_stress_level(self, conversation: Dict[str, Any]) -> str:
        """提取压力水平"""
        chief_complaint = conversation.get("chief_complaint", "")
        if any(keyword in chief_complaint for keyword in ["压力大", "紧张", "焦虑", "失眠"]):
            return "高"
        return "正常"

    def _extract_constitution_symptoms(self, conversation: Dict[str, Any]) -> List[str]:
        """提取体质相关症状"""
        chief_complaint = conversation.get("chief_complaint", "")

        constitution_symptoms = [
            "畏寒怕冷",
            "手足不温",
            "容易疲乏",
            "容易出汗",
            "手足心热",
            "口燥咽干",
            "形体肥胖",
            "容易困倦",
            "痰多",
            "面垢油腻",
            "口苦口干",
            "肤色晦暗",
            "容易出现瘀斑",
            "情绪不稳定",
            "胸胁胀满",
            "善太息",
            "过敏体质",
            "鼻塞流涕",
        ]

        found_symptoms = []
        for symptom in constitution_symptoms:
            if symptom in chief_complaint:
                found_symptoms.append(symptom)

        return found_symptoms

    async def _calculate_constitution_scores(
        self, features: Dict[str, Any]
    ) -> List[ConstitutionScore]:
        """计算各体质得分"""
        constitution_scores = []

        for constitution_type, constitution_features in self.constitution_features.items():
            raw_score = 0.0
            total_weight = 0.0
            supporting_features = []

            for feature in constitution_features:
                weight = feature.weight
                total_weight += weight

                if self._feature_matches_constitution(feature, features):
                    raw_score += weight
                    supporting_features.append(feature.name)

            # 归一化分数 (0-100)
            normalized_score = (raw_score / total_weight * 100) if total_weight > 0 else 0

            # 判断是否为主导体质
            is_dominant = normalized_score >= self.scoring_rules["dominant_threshold"]

            # 计算置信度
            confidence = min(normalized_score / 100, 1.0)

            constitution_scores.append(
                ConstitutionScore(
                    constitution_type=constitution_type,
                    raw_score=raw_score,
                    normalized_score=normalized_score,
                    is_dominant=is_dominant,
                    confidence=confidence,
                    supporting_features=supporting_features,
                )
            )

        # 按分数排序
        constitution_scores.sort(key=lambda x: x.normalized_score, reverse=True)

        return constitution_scores

    def _feature_matches_constitution(
        self, feature: ConstitutionFeature, extracted_features: Dict[str, Any]
    ) -> bool:
        """检查特征是否匹配体质"""
        feature_name = feature.name

        # 检查症状列表
        if feature_name in extracted_features.get("symptoms", []):
            return True

        # 检查形体特征
        physical = extracted_features.get("physical_features", {})
        if "体形匀称" in feature_name and physical.get("body_type") == "匀称":
            return True
        if "形体肥胖" in feature_name and physical.get("bmi", 0) > 25:
            return True

        # 检查面色特征
        if "面色润泽" in feature_name and physical.get("complexion") == "润泽":
            return True
        if "面色萎黄" in feature_name and "萎黄" in physical.get("face_color", ""):
            return True
        if "面色柔白" in feature_name and "柔白" in physical.get("face_color", ""):
            return True
        if "面色潮红" in feature_name and "潮红" in physical.get("face_color", ""):
            return True
        if "面垢油腻" in feature_name and "油腻" in physical.get("complexion", ""):
            return True
        if "肤色晦暗" in feature_name and "晦暗" in physical.get("face_color", ""):
            return True

        # 检查精神特征
        mental = extracted_features.get("mental_features", {})
        if "精力充沛" in feature_name and mental.get("energy_level") == "高":
            return True
        if "容易疲乏" in feature_name and mental.get("energy_level") == "低":
            return True
        if "精神不振" in feature_name and mental.get("energy_level") == "低":
            return True
        if "情绪不稳定" in feature_name and mental.get("mood") == "不稳定":
            return True

        # 检查睡眠特征
        sleep = extracted_features.get("sleep_features", {})
        if "睡眠良好" in feature_name and sleep.get("sleep_quality") == "良好":
            return True
        if "睡眠不安" in feature_name and sleep.get("sleep_quality") == "不佳":
            return True

        # 检查饮食特征
        diet = extracted_features.get("diet_features", {})
        if "食欲正常" in feature_name and diet.get("appetite") == "正常":
            return True
        if "喜热饮食" in feature_name and "热" in diet.get("food_preferences", ""):
            return True

        # 检查舌象特征
        tongue = extracted_features.get("tongue_features", {})
        if (
            "舌淡红苔薄白" in feature_name
            and tongue.get("color") == "淡红"
            and "薄白" in tongue.get("coating", "")
        ):
            return True
        if "舌淡红" in feature_name and tongue.get("color") == "淡红":
            return True
        if (
            "舌淡胖" in feature_name
            and tongue.get("color") == "淡"
            and "胖" in tongue.get("shape", "")
        ):
            return True
        if (
            "舌红少津" in feature_name
            and tongue.get("color") == "红"
            and "少津" in tongue.get("moisture", "")
        ):
            return True
        if "舌体胖大" in feature_name and "胖大" in tongue.get("shape", ""):
            return True
        if "舌质偏红" in feature_name and "红" in tongue.get("color", ""):
            return True

        # 检查脉象特征
        pulse = extracted_features.get("pulse_features", {})
        if (
            "脉和缓有力" in feature_name
            and "和缓" in pulse.get("rhythm", "")
            and "有力" in pulse.get("strength", "")
        ):
            return True
        if "脉弱" in feature_name and "弱" in pulse.get("strength", ""):
            return True
        if (
            "脉沉迟" in feature_name
            and "沉" in pulse.get("depth", "")
            and "迟" in pulse.get("rate", "")
        ):
            return True
        if (
            "脉细数" in feature_name
            and "细" in pulse.get("strength", "")
            and "数" in pulse.get("rate", "")
        ):
            return True
        if "脉滑" in feature_name and "滑" in pulse.get("rhythm", ""):
            return True
        if (
            "脉滑数" in feature_name
            and "滑" in pulse.get("rhythm", "")
            and "数" in pulse.get("rate", "")
        ):
            return True
        if "脉涩" in feature_name and "涩" in pulse.get("rhythm", ""):
            return True
        if "脉弦" in feature_name and "弦" in pulse.get("strength", ""):
            return True
        if (
            "脉濡弱" in feature_name
            and "濡" in pulse.get("strength", "")
            and "弱" in pulse.get("strength", "")
        ):
            return True

        # 检查声音特征
        voice = extracted_features.get("voice_features", {})
        if "声音低微" in feature_name and voice.get("strength") == "低微":
            return True

        return False

    def _determine_dominant_constitution(
        self, constitution_scores: List[ConstitutionScore]
    ) -> Optional[ConstitutionScore]:
        """确定主导体质"""
        for score in constitution_scores:
            if score.is_dominant and score.confidence >= self.scoring_rules["min_confidence"]:
                return score
        return None

    def _determine_constitution_tendency(
        self, constitution_scores: List[ConstitutionScore]
    ) -> List[ConstitutionType]:
        """确定体质倾向"""
        tendency = []
        for score in constitution_scores:
            if (
                score.normalized_score >= self.scoring_rules["tendency_threshold"]
                and score.confidence >= self.scoring_rules["min_confidence"]
            ):
                tendency.append(score.constitution_type)

        return tendency[:3]  # 最多返回3个倾向体质

    async def _generate_health_guidance(
        self,
        dominant_constitution: Optional[ConstitutionScore],
        constitution_tendency: List[ConstitutionType],
    ) -> Dict[str, Any]:
        """生成健康指导"""
        if not dominant_constitution:
            # 如果没有主导体质，使用倾向体质
            if constitution_tendency:
                constitution_type = constitution_tendency[0]
            else:
                constitution_type = ConstitutionType.BALANCED
        else:
            constitution_type = dominant_constitution.constitution_type

        guidance_template = self.health_guidance_templates.get(constitution_type, {})

        return {
            "constitution_type": constitution_type.value,
            "diet_guidance": guidance_template.get("diet", ""),
            "exercise_guidance": guidance_template.get("exercise", ""),
            "lifestyle_guidance": guidance_template.get("lifestyle", ""),
            "emotion_guidance": guidance_template.get("emotion", ""),
            "seasonal_guidance": guidance_template.get("season", ""),
            "additional_notes": self._generate_additional_notes(
                constitution_type, constitution_tendency
            ),
        }

    def _generate_additional_notes(
        self, main_constitution: ConstitutionType, constitution_tendency: List[ConstitutionType]
    ) -> List[str]:
        """生成额外注意事项"""
        notes = []

        # 根据体质组合给出特殊建议
        if len(constitution_tendency) > 1:
            if (
                ConstitutionType.QI_DEFICIENCY in constitution_tendency
                and ConstitutionType.YANG_DEFICIENCY in constitution_tendency
            ):
                notes.append("气阳两虚，需要温补气阳，避免过度劳累")

            if (
                ConstitutionType.YIN_DEFICIENCY in constitution_tendency
                and ConstitutionType.DAMP_HEAT in constitution_tendency
            ):
                notes.append("阴虚湿热并存，需要滋阴清热，避免辛辣燥热食物")

            if (
                ConstitutionType.QI_STAGNATION in constitution_tendency
                and ConstitutionType.BLOOD_STASIS in constitution_tendency
            ):
                notes.append("气滞血瘀，需要疏肝理气，活血化瘀")

        # 根据主导体质给出重点提醒
        if main_constitution == ConstitutionType.SPECIAL_DIATHESIS:
            notes.append("特禀体质需要特别注意避免过敏原，建议定期体检")

        return notes

    async def _generate_analysis_summary(
        self,
        dominant_constitution: Optional[ConstitutionScore],
        constitution_tendency: List[ConstitutionType],
    ) -> str:
        """生成分析总结"""
        if dominant_constitution:
            summary = f"主导体质为{dominant_constitution.constitution_type.value}，置信度{dominant_constitution.confidence:.2f}"

            if constitution_tendency and len(constitution_tendency) > 1:
                other_tendencies = [ct.value for ct in constitution_tendency[1:]]
                summary += f"，同时具有{', '.join(other_tendencies)}倾向"
        else:
            if constitution_tendency:
                summary = f"体质倾向为{', '.join([ct.value for ct in constitution_tendency])}"
            else:
                summary = "体质特征不明显，建议进一步观察"

        return summary

    def _calculate_overall_confidence(self, constitution_scores: List[ConstitutionScore]) -> float:
        """计算整体置信度"""
        if not constitution_scores:
            return 0.0

        # 使用最高分体质的置信度作为整体置信度
        return constitution_scores[0].confidence

    def _constitution_score_to_dict(self, score: ConstitutionScore) -> Dict[str, Any]:
        """将体质得分对象转换为字典"""
        return {
            "type": score.constitution_type.value,
            "raw_score": score.raw_score,
            "normalized_score": score.normalized_score,
            "is_dominant": score.is_dominant,
            "confidence": score.confidence,
            "supporting_features": score.supporting_features,
        }
