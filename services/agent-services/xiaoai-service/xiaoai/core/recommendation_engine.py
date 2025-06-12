"""
建议引擎

基于辨证分析和体质分析结果，生成个性化的健康建议
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
import logging
from typing import Any, Dict, List, Optional

from ..config.settings import get_settings
from .five_diagnosis_coordinator import DiagnosisResult

logger = logging.getLogger(__name__)


class RecommendationType(Enum):
    """建议类型枚举"""

    DIET = "diet"  # 饮食建议
    EXERCISE = "exercise"  # 运动建议
    LIFESTYLE = "lifestyle"  # 生活方式建议
    MEDICATION = "medication"  # 用药建议
    ACUPUNCTURE = "acupuncture"  # 针灸建议
    MASSAGE = "massage"  # 按摩建议
    EMOTIONAL = "emotional"  # 情志调节建议
    SEASONAL = "seasonal"  # 季节养生建议
    PREVENTION = "prevention"  # 预防保健建议
    MONITORING = "monitoring"  # 监测建议


class Priority(Enum):
    """优先级枚举"""

    URGENT = 5  # 紧急
    HIGH = 4  # 高
    MEDIUM = 3  # 中等
    LOW = 2  # 低
    INFO = 1  # 信息性


@dataclass
class Recommendation:
    """建议数据结构"""

    id: str
    type: RecommendationType
    title: str
    description: str
    priority: Priority
    confidence: float
    evidence: List[str] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)
    duration: Optional[str] = None
    frequency: Optional[str] = None
    dosage: Optional[str] = None
    precautions: List[str] = field(default_factory=list)
    related_syndromes: List[str] = field(default_factory=list)
    related_constitution: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None


@dataclass
class RecommendationPlan:
    """建议方案"""

    plan_id: str
    user_id: str
    session_id: str
    recommendations: List[Recommendation]
    overall_strategy: str
    implementation_order: List[str] = field(default_factory=list)
    monitoring_points: List[str] = field(default_factory=list)
    follow_up_schedule: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    valid_until: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=30)
    )


class RecommendationEngine:
    """建议引擎"""

    def __init__(self):
        self.settings = get_settings()
        self.recommendation_templates = self._load_recommendation_templates()
        self.contraindication_rules = self._load_contraindication_rules()
        self.interaction_rules = self._load_interaction_rules()

    def _load_recommendation_templates(self) -> Dict[str, Dict[str, Any]]:
        """加载建议模板"""
        return {
            # 饮食建议模板
            "diet_yang_deficiency": {
                "type": RecommendationType.DIET,
                "title": "温阳补气饮食调理",
                "description": "选择温热性质的食物，避免生冷寒凉",
                "specific_foods": {
                    "recommended": [
                        "羊肉",
                        "韭菜",
                        "生姜",
                        "桂圆",
                        "核桃",
                        "红枣",
                        "小米",
                    ],
                    "avoid": ["西瓜", "梨", "苦瓜", "绿豆", "冰镇饮料", "生菜"],
                },
                "cooking_methods": ["炖煮", "烧烤", "温热食用"],
                "meal_timing": "规律三餐，早餐要吃好",
                "priority": Priority.HIGH,
            },
            "diet_yin_deficiency": {
                "type": RecommendationType.DIET,
                "title": "滋阴润燥饮食调理",
                "description": "选择甘凉滋润的食物，避免辛辣燥热",
                "specific_foods": {
                    "recommended": [
                        "百合",
                        "银耳",
                        "枸杞",
                        "梨",
                        "蜂蜜",
                        "芝麻",
                        "鸭肉",
                    ],
                    "avoid": ["辣椒", "胡椒", "烧烤", "油炸食品", "白酒", "咖啡"],
                },
                "cooking_methods": ["蒸煮", "炖汤", "凉拌"],
                "meal_timing": "少食多餐，避免过饱",
                "priority": Priority.HIGH,
            },
            "diet_qi_deficiency": {
                "type": RecommendationType.DIET,
                "title": "补气健脾饮食调理",
                "description": "选择健脾益气的食物，易消化为主",
                "specific_foods": {
                    "recommended": [
                        "山药",
                        "大枣",
                        "小米",
                        "南瓜",
                        "土豆",
                        "鸡肉",
                        "鲫鱼",
                    ],
                    "avoid": ["生冷食物", "油腻食品", "难消化食物", "过甜食品"],
                },
                "cooking_methods": ["蒸煮", "炖汤", "粥类"],
                "meal_timing": "定时定量，细嚼慢咽",
                "priority": Priority.HIGH,
            },
            "diet_phlegm_dampness": {
                "type": RecommendationType.DIET,
                "title": "化痰除湿饮食调理",
                "description": "选择健脾化湿的食物，控制体重",
                "specific_foods": {
                    "recommended": ["薏米", "冬瓜", "白萝卜", "陈皮", "茯苓", "荷叶"],
                    "avoid": ["肥腻食物", "甜腻食品", "酒类", "奶制品过量"],
                },
                "cooking_methods": ["清蒸", "水煮", "少油烹饪"],
                "meal_timing": "控制食量，避免过饱",
                "priority": Priority.HIGH,
            },
            # 运动建议模板
            "exercise_yang_deficiency": {
                "type": RecommendationType.EXERCISE,
                "title": "温和补阳运动方案",
                "description": "选择温和的运动，避免大汗淋漓",
                "exercises": ["太极拳", "八段锦", "慢走", "瑜伽"],
                "intensity": "低到中等强度",
                "duration": "30-45分钟",
                "frequency": "每周3-4次",
                "best_time": "上午阳气升发时",
                "precautions": ["避免出汗过多", "运动后注意保暖"],
                "priority": Priority.MEDIUM,
            },
            "exercise_qi_deficiency": {
                "type": RecommendationType.EXERCISE,
                "title": "补气强身运动方案",
                "description": "选择缓和的有氧运动，循序渐进",
                "exercises": ["散步", "太极拳", "五禽戏", "气功"],
                "intensity": "低强度",
                "duration": "20-30分钟",
                "frequency": "每天或隔天",
                "best_time": "早晨或傍晚",
                "precautions": ["避免过度疲劳", "运动量循序渐进"],
                "priority": Priority.MEDIUM,
            },
            "exercise_phlegm_dampness": {
                "type": RecommendationType.EXERCISE,
                "title": "化湿减重运动方案",
                "description": "选择有氧运动，促进新陈代谢",
                "exercises": ["快走", "慢跑", "游泳", "骑车", "健身操"],
                "intensity": "中等到高强度",
                "duration": "45-60分钟",
                "frequency": "每周4-5次",
                "best_time": "下午或傍晚",
                "precautions": ["适当出汗", "运动后及时补水"],
                "priority": Priority.HIGH,
            },
            # 生活方式建议模板
            "lifestyle_general": {
                "type": RecommendationType.LIFESTYLE,
                "title": "健康生活方式指导",
                "description": "建立规律的作息和良好的生活习惯",
                "sleep": {
                    "bedtime": "22:00-23:00",
                    "wake_time": "6:00-7:00",
                    "duration": "7-8小时",
                    "environment": "安静、黑暗、适宜温度",
                },
                "work_rest": "劳逸结合，避免过度疲劳",
                "environment": "保持居住环境清洁、通风",
                "stress_management": "学会放松，保持心情愉快",
                "priority": Priority.MEDIUM,
            },
            # 情志调节建议模板
            "emotional_qi_stagnation": {
                "type": RecommendationType.EMOTIONAL,
                "title": "疏肝理气情志调节",
                "description": "调节情绪，疏解肝气郁结",
                "techniques": ["深呼吸", "冥想", "音乐疗法", "芳香疗法"],
                "activities": ["户外活动", "社交聚会", "兴趣爱好", "旅游"],
                "avoid": ["长期压抑情绪", "过度思虑", "熬夜"],
                "professional_help": "必要时寻求心理咨询",
                "priority": Priority.HIGH,
            },
            # 季节养生建议模板
            "seasonal_spring": {
                "type": RecommendationType.SEASONAL,
                "title": "春季养生指导",
                "description": "顺应春季阳气升发，注意疏肝理气",
                "diet": "多食绿色蔬菜，少食酸味",
                "exercise": "适当增加户外运动",
                "emotion": "保持心情舒畅，避免愤怒",
                "clothing": "春捂秋冻，适当保暖",
                "priority": Priority.LOW,
            },
            # 预防保健建议模板
            "prevention_general": {
                "type": RecommendationType.PREVENTION,
                "title": "日常预防保健",
                "description": "预防疾病，维护健康",
                "regular_checkup": "定期体检，早发现早治疗",
                "vaccination": "按时接种疫苗",
                "hygiene": "保持个人卫生，勤洗手",
                "environment": "避免污染环境，注意空气质量",
                "priority": Priority.MEDIUM,
            },
        }

    def _load_contraindication_rules(self) -> Dict[str, List[str]]:
        """加载禁忌规则"""
        return {
            "pregnancy": [
                "避免活血化瘀类药物",
                "避免寒凉性食物",
                "避免剧烈运动",
                "避免针刺某些穴位",
            ],
            "hypertension": [
                "限制钠盐摄入",
                "避免高强度运动",
                "避免情绪激动",
                "避免温热性药物过量",
            ],
            "diabetes": [
                "控制糖分摄入",
                "避免高糖食物",
                "注意运动强度",
                "监测血糖变化",
            ],
            "heart_disease": [
                "避免剧烈运动",
                "限制钠盐摄入",
                "避免情绪波动",
                "注意药物相互作用",
            ],
            "liver_disease": ["避免酒精", "避免肝毒性药物", "避免高脂饮食", "注意休息"],
            "kidney_disease": [
                "限制蛋白质摄入",
                "控制水分摄入",
                "避免肾毒性药物",
                "监测肾功能",
            ],
        }

    def _load_interaction_rules(self) -> Dict[str, Dict[str, str]]:
        """加载相互作用规则"""
        return {
            "food_drug": {
                "grapefruit_statins": "柚子与他汀类药物相互作用，增加副作用风险",
                "green_tea_iron": "绿茶影响铁剂吸收，建议间隔2小时服用",
                "dairy_antibiotics": "乳制品影响某些抗生素吸收",
            },
            "herb_drug": {
                "ginseng_warfarin": "人参可能影响华法林抗凝效果",
                "ginkgo_aspirin": "银杏与阿司匹林同用增加出血风险",
                "st_johns_wort": "圣约翰草影响多种药物代谢",
            },
            "exercise_condition": {
                "high_intensity_heart_disease": "心脏病患者避免高强度运动",
                "weight_bearing_osteoporosis": "骨质疏松患者注意负重运动安全",
            },
        }

    async def generate_recommendations(
        self,
        syndrome_analysis: Dict[str, Any],
        constitution_analysis: Dict[str, Any],
        diagnosis_results: List[DiagnosisResult],
        user_profile: Optional[Dict[str, Any]] = None,
    ) -> List[Recommendation]:
        """生成个性化建议"""
        logger.info("开始生成个性化健康建议...")

        recommendations = []

        try:
            # 基于证型生成建议
            syndrome_recommendations = await self._generate_syndrome_based_recommendations(
                syndrome_analysis
            )
            recommendations.extend(syndrome_recommendations)

            # 基于体质生成建议
            constitution_recommendations = await self._generate_constitution_based_recommendations(
                constitution_analysis
            )
            recommendations.extend(constitution_recommendations)

            # 基于诊断结果生成建议
            diagnosis_recommendations = await self._generate_diagnosis_based_recommendations(
                diagnosis_results
            )
            recommendations.extend(diagnosis_recommendations)

            # 生成季节性建议
            seasonal_recommendations = await self._generate_seasonal_recommendations()
            recommendations.extend(seasonal_recommendations)

            # 生成预防保健建议
            prevention_recommendations = await self._generate_prevention_recommendations(
                user_profile
            )
            recommendations.extend(prevention_recommendations)

            # 应用禁忌规则
            recommendations = await self._apply_contraindication_rules(
                recommendations, user_profile
            )

            # 检查相互作用
            recommendations = await self._check_interactions(recommendations)

            # 排序和优化
            recommendations = await self._prioritize_and_optimize(recommendations)

            logger.info(f"生成建议完成，共{len(recommendations)}条建议")

            return recommendations

        except Exception as e:
            logger.error(f"生成建议失败: {e}")
            return []

    async def _generate_syndrome_based_recommendations(
        self, syndrome_analysis: Dict[str, Any]
    ) -> List[Recommendation]:
        """基于证型生成建议"""
        recommendations = []

        primary_syndromes = syndrome_analysis.get("primary_syndromes", [])

        for syndrome in primary_syndromes:
            syndrome_name = syndrome.get("name", "")
            confidence = syndrome.get("confidence", 0.0)

            # 根据证型选择相应的建议模板
            if "阳虚" in syndrome_name:
                recommendations.extend(
                    self._create_recommendations_from_template(
                        "diet_yang_deficiency", confidence, [syndrome_name]
                    )
                )
                recommendations.extend(
                    self._create_recommendations_from_template(
                        "exercise_yang_deficiency", confidence, [syndrome_name]
                    )
                )

            elif "阴虚" in syndrome_name:
                recommendations.extend(
                    self._create_recommendations_from_template(
                        "diet_yin_deficiency", confidence, [syndrome_name]
                    )
                )

            elif "气虚" in syndrome_name:
                recommendations.extend(
                    self._create_recommendations_from_template(
                        "diet_qi_deficiency", confidence, [syndrome_name]
                    )
                )
                recommendations.extend(
                    self._create_recommendations_from_template(
                        "exercise_qi_deficiency", confidence, [syndrome_name]
                    )
                )

            elif "痰湿" in syndrome_name:
                recommendations.extend(
                    self._create_recommendations_from_template(
                        "diet_phlegm_dampness", confidence, [syndrome_name]
                    )
                )
                recommendations.extend(
                    self._create_recommendations_from_template(
                        "exercise_phlegm_dampness", confidence, [syndrome_name]
                    )
                )

            elif "气郁" in syndrome_name or "肝郁" in syndrome_name:
                recommendations.extend(
                    self._create_recommendations_from_template(
                        "emotional_qi_stagnation", confidence, [syndrome_name]
                    )
                )

        return recommendations

    async def _generate_constitution_based_recommendations(
        self, constitution_analysis: Dict[str, Any]
    ) -> List[Recommendation]:
        """基于体质生成建议"""
        recommendations = []

        dominant_constitution = constitution_analysis.get("dominant_constitution")
        if not dominant_constitution:
            return recommendations

        constitution_type = dominant_constitution.get("type", "")
        confidence = dominant_constitution.get("confidence", 0.0)

        # 根据体质类型生成相应建议
        if constitution_type == "阳虚质":
            recommendations.extend(
                self._create_recommendations_from_template(
                    "diet_yang_deficiency", confidence, [], [constitution_type]
                )
            )
            recommendations.extend(
                self._create_recommendations_from_template(
                    "exercise_yang_deficiency", confidence, [], [constitution_type]
                )
            )

        elif constitution_type == "阴虚质":
            recommendations.extend(
                self._create_recommendations_from_template(
                    "diet_yin_deficiency", confidence, [], [constitution_type]
                )
            )

        elif constitution_type == "气虚质":
            recommendations.extend(
                self._create_recommendations_from_template(
                    "diet_qi_deficiency", confidence, [], [constitution_type]
                )
            )
            recommendations.extend(
                self._create_recommendations_from_template(
                    "exercise_qi_deficiency", confidence, [], [constitution_type]
                )
            )

        elif constitution_type == "痰湿质":
            recommendations.extend(
                self._create_recommendations_from_template(
                    "diet_phlegm_dampness", confidence, [], [constitution_type]
                )
            )
            recommendations.extend(
                self._create_recommendations_from_template(
                    "exercise_phlegm_dampness", confidence, [], [constitution_type]
                )
            )

        elif constitution_type == "气郁质":
            recommendations.extend(
                self._create_recommendations_from_template(
                    "emotional_qi_stagnation", confidence, [], [constitution_type]
                )
            )

        # 为所有体质添加通用生活方式建议
        recommendations.extend(
            self._create_recommendations_from_template(
                "lifestyle_general", confidence, [], [constitution_type]
            )
        )

        return recommendations

    async def _generate_diagnosis_based_recommendations(
        self, diagnosis_results: List[DiagnosisResult]
    ) -> List[Recommendation]:
        """基于诊断结果生成建议"""
        recommendations = []

        for result in diagnosis_results:
            if result.confidence < 0.5:  # 置信度过低的结果不生成建议
                continue

            # 根据诊断类型和特征生成特定建议
            if "sleep_quality" in result.features:
                sleep_quality = result.features["sleep_quality"]
                if sleep_quality == "不佳":
                    recommendations.append(
                        self._create_sleep_improvement_recommendation(result.confidence)
                    )

            if "stress_level" in result.features:
                stress_level = result.features["stress_level"]
                if stress_level == "高":
                    recommendations.append(
                        self._create_stress_management_recommendation(result.confidence)
                    )

            # 基于症状生成监测建议
            if "symptoms" in result.features and result.features["symptoms"]:
                recommendations.append(
                    self._create_symptom_monitoring_recommendation(
                        result.features["symptoms"], result.confidence
                    )
                )

        return recommendations

    async def _generate_seasonal_recommendations(self) -> List[Recommendation]:
        """生成季节性建议"""
        current_month = datetime.now().month

        # 根据当前月份确定季节
        if current_month in [3, 4, 5]:  # 春季
            template_key = "seasonal_spring"
        elif current_month in [6, 7, 8]:  # 夏季
            template_key = "seasonal_spring"  # 暂时使用春季模板
        elif current_month in [9, 10, 11]:  # 秋季
            template_key = "seasonal_spring"  # 暂时使用春季模板
        else:  # 冬季
            template_key = "seasonal_spring"  # 暂时使用春季模板

        return self._create_recommendations_from_template(template_key, 0.8)

    async def _generate_prevention_recommendations(
        self, user_profile: Optional[Dict[str, Any]]
    ) -> List[Recommendation]:
        """生成预防保健建议"""
        recommendations = []

        # 通用预防建议
        recommendations.extend(
            self._create_recommendations_from_template("prevention_general", 0.7)
        )

        # 基于用户年龄的特定建议
        if user_profile and "age" in user_profile:
            age = user_profile["age"]

            if age >= 65:
                recommendations.append(self._create_elderly_care_recommendation())
            elif age >= 40:
                recommendations.append(self._create_middle_age_care_recommendation())

        return recommendations

    def _create_recommendations_from_template(
        self,
        template_key: str,
        confidence: float,
        related_syndromes: List[str] = None,
        related_constitution: List[str] = None,
    ) -> List[Recommendation]:
        """从模板创建建议"""
        template = self.recommendation_templates.get(template_key)
        if not template:
            return []

        recommendation_id = f"{template_key}_{int(datetime.now().timestamp())}"

        recommendation = Recommendation(
            id=recommendation_id,
            type=template["type"],
            title=template["title"],
            description=template["description"],
            priority=template.get("priority", Priority.MEDIUM),
            confidence=confidence,
            related_syndromes=related_syndromes or [],
            related_constitution=related_constitution or [],
        )

        # 添加具体的实施细节
        if "specific_foods" in template:
            foods = template["specific_foods"]
            recommendation.description += f"\n推荐食物：{', '.join(foods['recommended'])}"
            recommendation.description += f"\n避免食物：{', '.join(foods['avoid'])}"

        if "exercises" in template:
            recommendation.description += f"\n推荐运动：{', '.join(template['exercises'])}"
            recommendation.duration = template.get("duration")
            recommendation.frequency = template.get("frequency")

        if "techniques" in template:
            recommendation.description += f"\n调节方法：{', '.join(template['techniques'])}"

        return [recommendation]

    def _create_sleep_improvement_recommendation(self, confidence: float) -> Recommendation:
        """创建睡眠改善建议"""
        return Recommendation(
            id=f"sleep_improvement_{int(datetime.now().timestamp())}",
            type=RecommendationType.LIFESTYLE,
            title="睡眠质量改善建议",
            description="建立规律的睡眠习惯，创造良好的睡眠环境",
            priority=Priority.HIGH,
            confidence=confidence,
            precautions=[
                "睡前避免使用电子设备",
                "保持卧室安静、黑暗",
                "避免睡前饮用咖啡或茶",
                "建立固定的睡前仪式",
            ],
        )

    def _create_stress_management_recommendation(self, confidence: float) -> Recommendation:
        """创建压力管理建议"""
        return Recommendation(
            id=f"stress_management_{int(datetime.now().timestamp())}",
            type=RecommendationType.EMOTIONAL,
            title="压力管理指导",
            description="学习有效的压力管理技巧，保持心理健康",
            priority=Priority.HIGH,
            confidence=confidence,
            precautions=[
                "学习深呼吸和冥想技巧",
                "适当进行体育锻炼",
                "保持社交联系",
                "必要时寻求专业帮助",
            ],
        )

    def _create_symptom_monitoring_recommendation(
        self, symptoms: List[str], confidence: float
    ) -> Recommendation:
        """创建症状监测建议"""
        return Recommendation(
            id=f"symptom_monitoring_{int(datetime.now().timestamp())}",
            type=RecommendationType.MONITORING,
            title="症状监测建议",
            description=f"密切关注以下症状的变化：{', '.join(symptoms)}",
            priority=Priority.MEDIUM,
            confidence=confidence,
            precautions=[
                "记录症状出现的时间和程度",
                "注意症状的变化趋势",
                "症状加重时及时就医",
                "按时复查和随访",
            ],
        )

    def _create_elderly_care_recommendation(self) -> Recommendation:
        """创建老年人保健建议"""
        return Recommendation(
            id=f"elderly_care_{int(datetime.now().timestamp())}",
            type=RecommendationType.PREVENTION,
            title="老年人健康保健",
            description="针对老年人的特殊健康需求制定的保健方案",
            priority=Priority.MEDIUM,
            confidence=0.8,
            precautions=[
                "定期进行骨密度检查",
                "注意跌倒预防",
                "保持适度的社交活动",
                "定期检查视力和听力",
                "注意营养均衡",
            ],
        )

    def _create_middle_age_care_recommendation(self) -> Recommendation:
        """创建中年人保健建议"""
        return Recommendation(
            id=f"middle_age_care_{int(datetime.now().timestamp())}",
            type=RecommendationType.PREVENTION,
            title="中年人健康保健",
            description="针对中年人的健康风险制定的预防方案",
            priority=Priority.MEDIUM,
            confidence=0.8,
            precautions=[
                "定期进行心血管检查",
                "注意体重控制",
                "定期进行癌症筛查",
                "保持工作生活平衡",
                "注意骨关节保护",
            ],
        )

    async def _apply_contraindication_rules(
        self,
        recommendations: List[Recommendation],
        user_profile: Optional[Dict[str, Any]],
    ) -> List[Recommendation]:
        """应用禁忌规则"""
        if not user_profile:
            return recommendations

        medical_conditions = user_profile.get("medical_conditions", [])
        filtered_recommendations = []

        for recommendation in recommendations:
            is_contraindicated = False

            for condition in medical_conditions:
                contraindications = self.contraindication_rules.get(condition, [])

                # 检查是否有禁忌
                for contraindication in contraindications:
                    if any(
                        keyword in recommendation.description.lower()
                        for keyword in contraindication.lower().split()
                    ):
                        recommendation.contraindications.append(contraindication)
                        is_contraindicated = True

            if not is_contraindicated:
                filtered_recommendations.append(recommendation)
            else:
                logger.info(f"建议因禁忌被过滤: {recommendation.title}")

        return filtered_recommendations

    async def _check_interactions(
        self, recommendations: List[Recommendation]
    ) -> List[Recommendation]:
        """检查相互作用"""
        # 简单的相互作用检查
        for i, rec1 in enumerate(recommendations):
            for j, rec2 in enumerate(recommendations[i + 1 :], i + 1):
                # 检查是否有冲突的建议
                if rec1.type == RecommendationType.DIET and rec2.type == RecommendationType.DIET:
                    # 检查饮食建议是否冲突
                    if self._check_diet_conflict(rec1, rec2):
                        # 保留置信度更高的建议
                        if rec1.confidence > rec2.confidence:
                            recommendations[j] = None
                        else:
                            recommendations[i] = None

        # 移除被标记为None的建议
        return [rec for rec in recommendations if rec is not None]

    def _check_diet_conflict(self, rec1: Recommendation, rec2: Recommendation) -> bool:
        """检查饮食建议冲突"""
        # 简单的冲突检查逻辑
        if ("温热" in rec1.description and "寒凉" in rec2.description) or (
            "寒凉" in rec1.description and "温热" in rec2.description
        ):
            return True
        return False

    async def _prioritize_and_optimize(
        self, recommendations: List[Recommendation]
    ) -> List[Recommendation]:
        """排序和优化建议"""
        # 按优先级和置信度排序
        recommendations.sort(key=lambda x: (x.priority.value, x.confidence), reverse=True)

        # 去重和合并相似建议
        optimized_recommendations = []
        seen_types = set()

        for recommendation in recommendations:
            # 避免同类型建议过多
            type_key = (recommendation.type, recommendation.title)
            if type_key not in seen_types:
                optimized_recommendations.append(recommendation)
                seen_types.add(type_key)

        # 限制建议数量
        max_recommendations = self.settings.recommendation_engine.max_recommendations_per_session
        return optimized_recommendations[:max_recommendations]

    async def create_recommendation_plan(
        self, user_id: str, session_id: str, recommendations: List[Recommendation]
    ) -> RecommendationPlan:
        """创建建议方案"""
        plan_id = f"plan_{user_id}_{session_id}_{int(datetime.now().timestamp())}"

        # 确定实施顺序
        implementation_order = self._determine_implementation_order(recommendations)

        # 生成监测要点
        monitoring_points = self._generate_monitoring_points(recommendations)

        # 制定随访计划
        follow_up_schedule = self._create_follow_up_schedule(recommendations)

        # 生成整体策略
        overall_strategy = self._generate_overall_strategy(recommendations)

        return RecommendationPlan(
            plan_id=plan_id,
            user_id=user_id,
            session_id=session_id,
            recommendations=recommendations,
            overall_strategy=overall_strategy,
            implementation_order=implementation_order,
            monitoring_points=monitoring_points,
            follow_up_schedule=follow_up_schedule,
        )

    def _determine_implementation_order(self, recommendations: List[Recommendation]) -> List[str]:
        """确定实施顺序"""
        # 按优先级排序
        sorted_recs = sorted(recommendations, key=lambda x: x.priority.value, reverse=True)
        return [rec.id for rec in sorted_recs]

    def _generate_monitoring_points(self, recommendations: List[Recommendation]) -> List[str]:
        """生成监测要点"""
        monitoring_points = []

        for recommendation in recommendations:
            if recommendation.type == RecommendationType.MONITORING:
                monitoring_points.append(recommendation.description)
            elif recommendation.type == RecommendationType.DIET:
                monitoring_points.append("监测饮食调整后的身体反应")
            elif recommendation.type == RecommendationType.EXERCISE:
                monitoring_points.append("监测运动后的体力和精神状态")

        return list(set(monitoring_points))  # 去重

    def _create_follow_up_schedule(self, recommendations: List[Recommendation]) -> Dict[str, str]:
        """创建随访计划"""
        schedule = {}

        # 根据建议类型确定随访时间
        has_high_priority = any(
            rec.priority == Priority.URGENT or rec.priority == Priority.HIGH
            for rec in recommendations
        )

        if has_high_priority:
            schedule["first_follow_up"] = "1周后"
            schedule["second_follow_up"] = "2周后"
            schedule["monthly_follow_up"] = "每月一次"
        else:
            schedule["first_follow_up"] = "2周后"
            schedule["monthly_follow_up"] = "每月一次"

        return schedule

    def _generate_overall_strategy(self, recommendations: List[Recommendation]) -> str:
        """生成整体策略"""
        strategy_parts = []

        # 统计建议类型
        type_counts = {}
        for rec in recommendations:
            type_counts[rec.type] = type_counts.get(rec.type, 0) + 1

        # 生成策略描述
        if RecommendationType.DIET in type_counts:
            strategy_parts.append("通过饮食调理改善体质")

        if RecommendationType.EXERCISE in type_counts:
            strategy_parts.append("配合适当运动增强体质")

        if RecommendationType.EMOTIONAL in type_counts:
            strategy_parts.append("注重情志调节")

        if RecommendationType.LIFESTYLE in type_counts:
            strategy_parts.append("建立健康的生活方式")

        strategy = "，".join(strategy_parts) if strategy_parts else "综合调理，整体改善"

        return f"采用中医整体观念，{strategy}，循序渐进，持之以恒。"
