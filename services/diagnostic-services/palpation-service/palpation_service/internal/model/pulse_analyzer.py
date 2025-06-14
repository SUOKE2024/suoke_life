"""
pulse_analyzer - 索克生活项目模块
"""

from dataclasses import dataclass
from typing import Any
import logging

#! / usr / bin / env python

"""
脉象分析器
负责分析脉象特征并识别脉象类型
"""


logger = logging.getLogger(__name__)

@dataclass
class PulseTypeResult:
    """脉象类型识别结果"""

    type: str
    confidence: float
    description: str
    characteristics: list[str]

@dataclass
class TCMPatternResult:
    """中医证型识别结果"""

    pattern_name: str
    confidence: float
    description: str
    related_conditions: list[str]

@dataclass
class OrganConditionResult:
    """脏腑状态评估结果"""

    organ_name: str
    condition: str
    severity: float
    description: str

class PulseAnalyzer:
    """脉象分析器"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化脉象分析器

        Args:
            config: 配置信息
        """
        self.config = config

        # 脉象类型定义
        self.pulse_types = self._init_pulse_types()

        # 中医证型映射
        self.tcm_patterns = self._init_tcm_patterns()

        # 脏腑对应关系
        self.organ_mapping = self._init_organ_mapping()

        logger.info("脉象分析器初始化完成")

    def _init_pulse_types(dict[str, dict[str, Any]]):
        """初始化脉象类型定义"""
        return {
            "FLOATING": {
                "name": "浮脉",
                "description": "轻取即得，重按稍减而不空",
                "characteristics": ["轻取有力", "重按减弱", "脉位表浅"],
                "conditions": ["外感表证", "虚阳外越"],
            },
            "SUNKEN": {
                "name": "沉脉",
                "description": "轻取不应，重按始得",
                "characteristics": ["轻取不明", "重按明显", "脉位深沉"],
                "conditions": ["里证", "寒证", "积聚"],
            },
            "SLOW": {
                "name": "迟脉",
                "description": "脉来迟缓，一息不足四至",
                "characteristics": ["脉率缓慢", "节律规整", "一息三至"],
                "conditions": ["寒证", "阳虚", "气血不足"],
            },
            "RAPID": {
                "name": "数脉",
                "description": "脉来急速，一息五至以上",
                "characteristics": ["脉率快速", "节律规整", "一息五至以上"],
                "conditions": ["热证", "阴虚", "气血亢盛"],
            },
            "SLIPPERY": {
                "name": "滑脉",
                "description": "往来流利，如珠走盘",
                "characteristics": ["流利圆滑", "来去自如", "如珠滚动"],
                "conditions": ["痰湿", "食积", "妊娠", "实热"],
            },
            "ROUGH": {
                "name": "涩脉",
                "description": "往来艰涩，如轻刀刮竹",
                "characteristics": ["往来不畅", "细而迟缓", "如刀刮竹"],
                "conditions": ["血虚", "津亏", "血瘀", "精伤"],
            },
            "WIRY": {
                "name": "弦脉",
                "description": "端直以长，如按琴弦",
                "characteristics": ["挺直有力", "如按琴弦", "脉体较硬"],
                "conditions": ["肝胆病", "痛证", "痰饮", "疟疾"],
            },
            "MODERATE": {
                "name": "和脉",
                "description": "不浮不沉，不快不慢，从容和缓",
                "characteristics": ["节律均匀", "力度适中", "从容和缓"],
                "conditions": ["正常脉象", "气血调和"],
            },
            "FAINT": {
                "name": "微脉",
                "description": "极细极软，若有若无",
                "characteristics": ["极其细弱", "若有若无", "按之欲绝"],
                "conditions": ["阳气衰微", "气血大虚"],
            },
            "SURGING": {
                "name": "洪脉",
                "description": "脉来盛大，如波涛汹涌",
                "characteristics": ["脉体宽大", "来盛去衰", "如波涛状"],
                "conditions": ["热盛", "阳明实热", "暑热"],
            },
            "TIGHT": {
                "name": "紧脉",
                "description": "脉来绷急，如转绳索",
                "characteristics": ["绷紧有力", "如转绳索", "左右弹指"],
                "conditions": ["寒邪", "疼痛", "宿食"],
            },
            "EMPTY": {
                "name": "虚脉",
                "description": "三部脉举之无力，按之空虚",
                "characteristics": ["举按无力", "脉体空虚", "似有似无"],
                "conditions": ["气血两虚", "脏腑虚损"],
            },
            "THREADY": {
                "name": "细脉",
                "description": "脉细如线，但应指明显",
                "characteristics": ["脉体细小", "如丝如线", "应指明显"],
                "conditions": ["气血两虚", "湿证", "劳损"],
            },
            "WEAK": {
                "name": "弱脉",
                "description": "极软而沉细",
                "characteristics": ["沉细无力", "极其软弱", "须重按"],
                "conditions": ["阳气虚衰", "气血俱虚"],
            },
            "SCATTERED": {
                "name": "散脉",
                "description": "浮散无根，至数不齐",
                "characteristics": ["浮而散漫", "无根无力", "至数不齐"],
                "conditions": ["元气离散", "脏腑衰败"],
            },
            "INTERMITTENT": {
                "name": "代脉",
                "description": "脉来缓慢，时有歇止",
                "characteristics": ["缓而有止", "止有定数", "良久复来"],
                "conditions": ["脏气衰微", "跌打损伤", "情志失调"],
            },
            "BOUND": {
                "name": "结脉",
                "description": "脉来缓慢，时有歇止，止无定数",
                "characteristics": ["缓而有止", "止无定数", "歇止不规则"],
                "conditions": ["阴盛气结", "寒痰血瘀"],
            },
            "HASTY": {
                "name": "促脉",
                "description": "脉来急数，时有歇止",
                "characteristics": ["数而有止", "止无定数", "急促不整"],
                "conditions": ["阳盛实热", "气血痰食郁滞"],
            },
        }

    def _init_tcm_patterns(dict[str, dict[str, Any]]):
        """初始化中医证型"""
        return {
            "wind_cold": {
                "name": "风寒表证",
                "description": "外感风寒，表卫不固",
                "pulse_types": ["FLOATING", "TIGHT"],
                "symptoms": ["恶寒", "发热", "无汗", "头身疼痛"],
            },
            "wind_heat": {
                "name": "风热表证",
                "description": "外感风热，卫表不和",
                "pulse_types": ["FLOATING", "RAPID"],
                "symptoms": ["发热", "微恶风寒", "咽痛", "口渴"],
            },
            "qi_deficiency": {
                "name": "气虚证",
                "description": "元气不足，脏腑功能减退",
                "pulse_types": ["WEAK", "EMPTY", "SLOW"],
                "symptoms": ["神疲乏力", "气短懒言", "自汗", "面色㿠白"],
            },
            "blood_deficiency": {
                "name": "血虚证",
                "description": "血液亏虚，不能濡养脏腑",
                "pulse_types": ["THREADY", "WEAK", "ROUGH"],
                "symptoms": ["面色萎黄", "头晕眼花", "心悸失眠", "手足麻木"],
            },
            "yin_deficiency": {
                "name": "阴虚证",
                "description": "阴液亏损，虚热内生",
                "pulse_types": ["THREADY", "RAPID"],
                "symptoms": ["潮热盗汗", "五心烦热", "口燥咽干", "舌红少苔"],
            },
            "yang_deficiency": {
                "name": "阳虚证",
                "description": "阳气不足，温煦失职",
                "pulse_types": ["SUNKEN", "SLOW", "WEAK"],
                "symptoms": ["畏寒肢冷", "神疲乏力", "腰膝酸软", "小便清长"],
            },
            "phlegm_dampness": {
                "name": "痰湿证",
                "description": "水湿内停，聚而成痰",
                "pulse_types": ["SLIPPERY", "MODERATE"],
                "symptoms": ["身重困倦", "胸闷", "痰多", "纳呆"],
            },
            "blood_stasis": {
                "name": "血瘀证",
                "description": "血行不畅，瘀血内阻",
                "pulse_types": ["ROUGH", "BOUND", "INTERMITTENT"],
                "symptoms": ["刺痛固定", "肌肤甲错", "面色黧黑", "舌有瘀斑"],
            },
            "liver_qi_stagnation": {
                "name": "肝气郁结",
                "description": "情志不遂，肝失疏泄",
                "pulse_types": ["WIRY"],
                "symptoms": ["胸胁胀痛", "情志抑郁", "善太息", "月经不调"],
            },
            "spleen_stomach_weakness": {
                "name": "脾胃虚弱",
                "description": "中焦虚弱，运化失常",
                "pulse_types": ["WEAK", "SLOW", "MODERATE"],
                "symptoms": ["纳差", "腹胀", "便溏", "倦怠乏力"],
            },
        }

    def _init_organ_mapping(dict[str, dict[str, str]]):
        """初始化脏腑对应关系"""
        return {
            "CUN_LEFT": {"organ": "心", "function": "主血脉，主神志"},
            "GUAN_LEFT": {"organ": "肝胆", "function": "主疏泄，主筋"},
            "CHI_LEFT": {"organ": "肾（左）", "function": "主水，主纳气"},
            "CUN_RIGHT": {"organ": "肺", "function": "主气，司呼吸"},
            "GUAN_RIGHT": {"organ": "脾胃", "function": "主运化，主统血"},
            "CHI_RIGHT": {"organ": "肾（右） / 命门", "function": "主生殖，主骨"},
        }

    def analyze_pulse(
        self, features: dict[str, Any], user_info: dict[str, Any], options: dict[str, Any]
    ) - > dict[str, Any]:
        """
        分析脉象

        Args:
            features: 脉象特征
            user_info: 用户信息
            options: 分析选项

        Returns:
            分析结果
        """
        try:
            # 识别脉象类型
            pulse_types = self._identify_pulse_types(features)

            # 识别中医证型
            tcm_patterns = []
            if options.get("use_tcm_model", True):
                tcm_patterns = self._identify_tcm_patterns(pulse_types, user_info)

            # 评估脏腑状态
            organ_conditions = self._assess_organ_conditions(features, pulse_types)

            # 生成分析总结
            analysis_summary = self._generate_analysis_summary(
                pulse_types, tcm_patterns, organ_conditions, user_info
            )

            # 计算置信度
            confidence_score = self._calculate_confidence_score(features, pulse_types)

            return {
                "pulse_types": pulse_types,
                "tcm_patterns": tcm_patterns,
                "organ_conditions": organ_conditions,
                "analysis_summary": analysis_summary,
                "confidence_score": confidence_score,
            }

        except Exception as e:
            logger.exception(f"脉象分析失败: {e!s}")
            raise

    def _identify_pulse_types(list[dict[str, Any]]):
        """识别脉象类型"""
        identified_types = []

        # 获取特征数据
        feature_list = features.get("features", [])

        # 按位置分组特征
        position_features = {}
        for feature in feature_list:
            position = feature.get("position", "UNKNOWN")
            if position not in position_features:
                position_features[position] = {}
            position_features[position][feature.get("name")] = feature.get("value")

        # 分析每个位置的脉象
        for position, pos_features in position_features.items():
            # 基于规则的脉象识别

            # 浮沉脉判断
            main_peak_amplitude = pos_features.get("main_peak_amplitude", 0)
            if main_peak_amplitude > 0.8:  # 高幅度
                if pos_features.get("rising_time", 0) < 0.1:  # 快速上升
                    identified_types.append(
                        {"type": "FLOATING", "confidence": 0.8, "position": position}
                    )
            elif main_peak_amplitude < 0.3:  # 低幅度
                identified_types.append({"type": "SUNKEN", "confidence": 0.7, "position": position})

            # 迟数脉判断
            pulse_rate = pos_features.get("pulse_rate", 70)
            if pulse_rate < 60:
                identified_types.append({"type": "SLOW", "confidence": 0.9, "position": position})
            elif pulse_rate > 90:
                identified_types.append({"type": "RAPID", "confidence": 0.9, "position": position})

            # 滑涩脉判断
            spectral_entropy = pos_features.get("spectral_entropy", 0)
            if spectral_entropy < 0.3:  # 低熵值，规则
                identified_types.append(
                    {"type": "SLIPPERY", "confidence": 0.7, "position": position}
                )
            elif spectral_entropy > 0.7:  # 高熵值，不规则
                identified_types.append({"type": "ROUGH", "confidence": 0.7, "position": position})

            # 弦脉判断
            dicrotic_ratio = pos_features.get("dicrotic_ratio", 0)
            if dicrotic_ratio < 0.2 and main_peak_amplitude > 0.6:
                identified_types.append({"type": "WIRY", "confidence": 0.75, "position": position})

        # 合并相同类型的脉象，取最高置信度
        merged_types = {}
        for pulse_type in identified_types:
            type_name = pulse_type["type"]
            if (
                type_name not in merged_types
                or pulse_type["confidence"] > merged_types[type_name]["confidence"]
            ):
                merged_types[type_name] = pulse_type

        # 转换为结果格式
        result = []
        for type_name, type_info in merged_types.items():
            if type_name in self.pulse_types:
                pulse_def = self.pulse_types[type_name]
                result.append(
                    {
                        "type": type_name,
                        "name": pulse_def["name"],
                        "confidence": type_info["confidence"],
                        "description": pulse_def["description"],
                        "characteristics": pulse_def["characteristics"],
                    }
                )

        return result

    def _identify_tcm_patterns(
        self, pulse_types: list[dict[str, Any]], user_info: dict[str, Any]
    ) - > list[dict[str, Any]]:
        """识别中医证型"""
        identified_patterns = []

        # 获取识别到的脉象类型
        identified_pulse_types = [pt["type"] for pt in pulse_types]

        # 匹配证型
        for pattern_key, pattern_def in self.tcm_patterns.items():
            # 计算匹配度
            required_pulses = pattern_def.get("pulse_types", [])
            matched_pulses = [p for p in required_pulses if p in identified_pulse_types]

            if len(matched_pulses) > 0:
                # 计算置信度
                confidence = len(matched_pulses) / len(required_pulses)

                # 考虑用户信息调整置信度
                age = user_info.get("age", 0)
                if pattern_key == "yang_deficiency" and age > 60:
                    confidence * = 1.2  # 老年人阳虚可能性增加
                elif pattern_key == "yin_deficiency" and age > 40:
                    confidence * = 1.1  # 中年后阴虚可能性增加

                # 限制置信度范围
                confidence = min(confidence, 0.95)

                if confidence > 0.5:  # 置信度阈值
                    identified_patterns.append(
                        {
                            "pattern_name": pattern_def["name"],
                            "confidence": confidence,
                            "description": pattern_def["description"],
                            "related_conditions": pattern_def.get("symptoms", []),
                        }
                    )

        # 按置信度排序
        identified_patterns.sort(key = lambda x: x["confidence"], reverse = True)

        # 返回前3个最可能的证型
        return identified_patterns[:3]

    def _assess_organ_conditions(
        self, features: dict[str, Any], pulse_types: list[dict[str, Any]]
    ) - > list[dict[str, Any]]:
        """评估脏腑状态"""
        organ_conditions = []

        # 获取特征数据
        feature_list = features.get("features", [])

        # 按位置评估脏腑
        position_assessments = {}

        for feature in feature_list:
            position = feature.get("position", "UNKNOWN")
            if position in self.organ_mapping:
                if position not in position_assessments:
                    position_assessments[position] = {
                        "organ_info": self.organ_mapping[position],
                        "features": {},
                    }
                position_assessments[position]["features"][feature.get("name")] = feature.get(
                    "value"
                )

        # 评估每个位置的脏腑状态
        for position, assessment in position_assessments.items():
            organ_info = assessment["organ_info"]
            pos_features = assessment["features"]

            # 基于特征评估状态
            condition = "正常"
            severity = 0.0
            description = f"{organ_info['organ']}功能正常"

            # 评估逻辑
            main_peak_amplitude = pos_features.get("main_peak_amplitude", 0.5)
            pulse_rate = pos_features.get("pulse_rate", 70)

            if main_peak_amplitude < 0.3:
                condition = "虚弱"
                severity = 0.6
                description = f"{organ_info['organ']}气血不足，功能减退"
            elif main_peak_amplitude > 0.8:
                if pulse_rate > 90:
                    condition = "亢进"
                    severity = 0.7
                    description = f"{organ_info['organ']}功能亢进，可能有热证"
                else:
                    condition = "实证"
                    severity = 0.5
                    description = f"{organ_info['organ']}气血充盛"

            # 特殊位置的特殊评估
            if position == "GUAN_LEFT" and any(pt["type"] == "WIRY" for pt in pulse_types):
                condition = "肝气郁结"
                severity = 0.7
                description = "肝失疏泄，气机不畅"

            if condition ! = "正常":
                organ_conditions.append(
                    {
                        "organ_name": organ_info["organ"],
                        "condition": condition,
                        "severity": severity,
                        "description": description,
                    }
                )

        return organ_conditions

    def _generate_analysis_summary(
        self,
        pulse_types: list[dict[str, Any]],
        tcm_patterns: list[dict[str, Any]],
        organ_conditions: list[dict[str, Any]],
        user_info: dict[str, Any],
    ) - > str:
        """生成分析总结"""
        summary_parts = []

        # 脉象总结
        if pulse_types:
            pulse_names = [pt["name"] for pt in pulse_types[:3]]  # 取前3个主要脉象
            summary_parts.append(f"脉象特征：主要表现为{'、'.join(pulse_names)}")

        # 证型总结
        if tcm_patterns:
            main_pattern = tcm_patterns[0]
            summary_parts.append(
                f"中医辨证：倾向于{main_pattern['pattern_name']}（置信度：{main_pattern['confidence']:.1%}）"
            )

        # 脏腑状态总结
        if organ_conditions:
            abnormal_organs = [oc for oc in organ_conditions if oc["severity"] > 0.5]
            if abnormal_organs:
                organ_desc = []
                for oc in abnormal_organs[:2]:  # 取前2个主要问题
                    organ_desc.append(f"{oc['organ_name']}{oc['condition']}")
                summary_parts.append(f"脏腑评估：{'，'.join(organ_desc)}")

        # 健康建议
        if tcm_patterns:
            main_pattern_key = None
            for key, pattern in self.tcm_patterns.items():
                if pattern["name"] == tcm_patterns[0]["pattern_name"]:
                    main_pattern_key = key
                    break

            if main_pattern_key:
                if main_pattern_key in ["qi_deficiency", "blood_deficiency"]:
                    summary_parts.append("建议：注意休息，加强营养，适当运动以补益气血")
                elif main_pattern_key in ["yin_deficiency"]:
                    summary_parts.append("建议：滋阴降火，避免熬夜，多食滋阴食物")
                elif main_pattern_key in ["yang_deficiency"]:
                    summary_parts.append("建议：温阳散寒，注意保暖，可适当食用温补食物")
                elif main_pattern_key == "liver_qi_stagnation":
                    summary_parts.append("建议：疏肝理气，调节情志，保持心情舒畅")

        return "。".join(summary_parts) + "。"

    def _calculate_confidence_score(
        self, features: dict[str, Any], pulse_types: list[dict[str, Any]]
    ) - > float:
        """计算分析置信度"""
        confidence_factors = []

        # 信号质量因素
        quality = features.get("quality", {})
        signal_quality = quality.get("signal_quality", 0)
        confidence_factors.append(signal_quality)

        # 脉象识别置信度
        if pulse_types:
            avg_pulse_confidence = np.mean([pt["confidence"] for pt in pulse_types])
            confidence_factors.append(avg_pulse_confidence)

        # 特征完整性
        feature_list = features.get("features", [])
        feature_completeness = min(len(feature_list) / 100.0, 1.0)  # 假设100个特征为完整
        confidence_factors.append(feature_completeness)

        # 计算总体置信度
        if confidence_factors:
            overall_confidence = np.mean(confidence_factors)
            return float(overall_confidence)

        return 0.5  # 默认置信度

    def check_model_loaded(None):
        """检查模型是否已加载"""
        # 这里是简化实现，实际应该检查机器学习模型的加载状态
        return True
