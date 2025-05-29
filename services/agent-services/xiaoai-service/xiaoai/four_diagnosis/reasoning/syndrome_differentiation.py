#!/usr/bin/env python3
"""
高级辨证分析引擎
支持多种辨证方法和知识图谱推理
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

@dataclass
class SyndromeEvidence:
    """证候证据数据类"""
    featurename: str
    modality: str
    confidence: float
    weight: float = 1.0
    category: str = ""
    notes: str = ""

@dataclass
class Constitution:
    """体质数据类"""
    name: str
    score: float
    confidence: float
    traits: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

@dataclass
class Syndrome:
    """证候数据类"""
    name: str
    score: float
    confidence: float
    category: str
    evidences: list[SyndromeEvidence] = field(default_factory=list)
    mechanism: str = ""
    patternmapping: dict[str, float] = field(default_factory=dict)

class SyndromeDifferentiationEngine:
    """
    高级辨证分析引擎
    集成多种辨证方法, 支持知识图谱推理
    """

    # 辨证方法
    METHODEIGHT_PRINCIPLES = "eight_principles"  # 八纲辨证
    METHODZANG_FU = "zang_fu"  # 脏腑辨证
    METHODQI_BLOOD_FLUID = "qi_blood_fluid"  # 气血津液辨证
    METHODMERIDIAN = "meridian"  # 经络辨证
    METHODSIX_MERIDIANS = "six_meridians"  # 六经辨证
    METHODTRIPLE_ENERGIZER = "triple_energizer"  # 三焦辨证
    METHODWEI_QI_YING_BLOOD = "wei_qi_ying_blood"  # 卫气营血辨证

    def __init__(self, config: dict | None = None):
        """
        初始化辨证分析引擎

        Args:
            config: 配置参数
        """
        self.config = config or {}

        # 辨证方法配置
        self.enabledmethods = self.config.get("methods", [
            self.METHODEIGHT_PRINCIPLES,
            self.METHODZANG_FU,
            self.METHOD_QI_BLOOD_FLUID
        ])

        # 置信度阈值
        self.confidencethreshold = self.config.get("confidence_threshold", 0.6)

        # 各模态基础权重
        self.modalityweights = {
            "looking": self.config.get("weights.looking", 1.0),
            "listening": self.config.get("weights.listening", 1.0),
            "inquiry": self.config.get("weights.inquiry", 1.5),
            "palpation": self.config.get("weights.palpation", 1.2)
        }

        # 证候知识库
        self.syndromeknowledge = self._load_syndrome_knowledge()

        # 体质知识库
        self.constitutionknowledge = self._load_constitution_knowledge()

        # 证候关系图谱
        self.syndromegraph = self._load_syndrome_graph()

        logger.info(f"辨证分析引擎初始化完成, 已启用辨证方法: {', '.join(self.enabledmethods)}")

    def _load_syndrome_knowledge(self) -> dict[str, dict]:
        """加载证候知识库"""
        # 实际应用中从数据库或知识库加载
        # 这里使用示例数据
        knowledge = {
            # 八纲辨证
            "寒证": {
                "category": "八纲辨证",
                "features": ["畏寒", "肢冷", "面色苍白", "舌淡", "舌苔白", "脉沉紧"],
                "mechanism": "阳气不足, 或寒邪侵袭",
                "opposing": ["热证"],
                "related": ["虚证", "表证"],
                "treatment_principles": ["温阳散寒"]
            },
            "热证": {
                "category": "八纲辨证",
                "features": ["发热", "口渴", "面红", "舌红", "舌苔黄", "脉数"],
                "mechanism": "阳热亢盛, 或热邪侵袭",
                "opposing": ["寒证"],
                "related": ["实证", "里证"],
                "treatment_principles": ["清热泻火"]
            },
            "虚证": {
                "category": "八纲辨证",
                "features": ["疲乏", "气短", "自汗", "舌淡", "脉弱"],
                "mechanism": "正气不足",
                "opposing": ["实证"],
                "related": ["寒证"],
                "treatment_principles": ["补益扶正"]
            },
            "实证": {
                "category": "八纲辨证",
                "features": ["胀满", "疼痛拒按", "烦躁", "舌苔厚", "脉实"],
                "mechanism": "邪气亢盛",
                "opposing": ["虚证"],
                "related": ["热证"],
                "treatment_principles": ["祛邪"]
            },

            # 脏腑辨证
            "肝气郁结": {
                "category": "脏腑辨证",
                "features": ["胁肋胀痛", "情志不畅", "善太息", "脉弦"],
                "mechanism": "肝失疏泄, 气机郁滞",
                "related": ["实证"],
                "treatment_principles": ["疏肝理气"]
            },
            "肝阳上亢": {
                "category": "脏腑辨证",
                "features": ["头痛", "眩晕", "急躁易怒", "面红", "舌红", "脉弦有力"],
                "mechanism": "肝阴不足, 肝阳上亢",
                "related": ["阴虚", "热证"],
                "treatment_principles": ["平肝潜阳"]
            },
            "脾气虚": {
                "category": "脏腑辨证",
                "features": ["食欲不振", "腹胀", "大便溏薄", "倦怠乏力", "舌淡胖", "脉缓弱"],
                "mechanism": "脾失健运",
                "related": ["虚证", "寒证"],
                "treatment_principles": ["健脾益气"]
            },
            "脾胃湿热": {
                "category": "脏腑辨证",
                "features": ["腹痛", "口苦", "口干", "便秘", "舌苔黄腻", "脉滑数"],
                "mechanism": "湿热内蕴脾胃",
                "related": ["实证", "热证"],
                "treatment_principles": ["清热化湿"]
            },
            "心气虚": {
                "category": "脏腑辨证",
                "features": ["心悸", "气短", "自汗", "面色淡白", "舌淡", "脉细弱"],
                "mechanism": "心气不足",
                "related": ["虚证"],
                "treatment_principles": ["益气养心"]
            },

            # 气血津液辨证
            "气虚": {
                "category": "气血津液辨证",
                "features": ["疲乏", "气短", "自汗", "舌淡", "脉虚弱"],
                "mechanism": "气的生成不足或过度消耗",
                "related": ["虚证"],
                "treatment_principles": ["补气"]
            },
            "气滞": {
                "category": "气血津液辨证",
                "features": ["胀痛", "痛处固定", "情志不畅", "脉弦"],
                "mechanism": "气机不畅",
                "related": ["实证"],
                "treatment_principles": ["理气"]
            },
            "血虚": {
                "category": "气血津液辨证",
                "features": ["面色萎黄", "唇甲色淡", "头晕", "心悸", "舌淡", "脉细"],
                "mechanism": "血的生成不足或过度消耗",
                "related": ["虚证"],
                "treatment_principles": ["养血"]
            },
            "血瘀": {
                "category": "气血津液辨证",
                "features": ["刺痛", "痛处固定", "舌紫暗", "脉涩"],
                "mechanism": "血流不畅",
                "related": ["实证"],
                "treatment_principles": ["活血化瘀"]
            },
            "津液亏虚": {
                "category": "气血津液辨证",
                "features": ["口干", "皮肤干燥", "大便干结", "舌干", "脉细数"],
                "mechanism": "津液不足",
                "related": ["虚证", "热证"],
                "treatment_principles": ["生津润燥"]
            }
        }

        return knowledge

    def _load_constitution_knowledge(self) -> dict[str, dict]:
        """加载体质知识库"""
        # 实际应用中从数据库或知识库加载
        # 这里使用示例数据, 九种体质
        knowledge = {
            "平和质": {
                "traits": ["面色润泽", "精力充沛", "体形匀称", "性格平和", "适应力强"],
                "features": ["舌淡红", "苔薄白", "脉和缓有力"],
                "recommendations": ["保持规律生活", "均衡饮食", "适度运动", "心情舒畅", "注意保健"]
            },
            "气虚质": {
                "traits": ["疲乏无力", "气短自汗", "语声低弱", "易感冒", "舌淡"],
                "features": ["面色淡白", "食欲不振", "大便溏", "舌胖嫩", "脉虚弱"],
                "recommendations": ["健脾益气", "适当休息", "饮食规律", "温和运动", "避免过劳"]
            },
            "阳虚质": {
                "traits": ["畏寒肢冷", "喜热饮", "精神不振", "面色苍白", "小便清长"],
                "features": ["腰膝酸软", "舌淡胖", "苔白", "脉沉迟无力"],
                "recommendations": ["温阳补肾", "避免寒冷", "饮食温热", "适当晒太阳", "保暖"]
            },
            "阴虚质": {
                "traits": ["手足心热", "口干咽燥", "潮热盗汗", "消瘦", "容易失眠"],
                "features": ["舌红少苔", "脉细数", "心烦", "皮肤干燥"],
                "recommendations": ["滋阴润燥", "避免辛辣", "避免劳累", "保持心情舒畅", "充足休息"]
            },
            "痰湿质": {
                "traits": ["体形肥胖", "腹部松软", "胸闷痰多", "口黏腻", "易困倦"],
                "features": ["苔厚腻", "脉滑", "舌胖大", "身重困重"],
                "recommendations": ["健脾化湿", "控制饮食", "积极运动", "避免油腻", "保持通畅"]
            },
            "湿热质": {
                "traits": ["面垢油光", "易生痤疮", "口苦口臭", "大便黏滞", "尿黄"],
                "features": ["舌红", "苔黄腻", "脉滑数", "易怒"],
                "recommendations": ["清热利湿", "少食辛辣", "保持通畅", "心情舒畅", "饮食清淡"]
            },
            "血瘀质": {
                "traits": ["肤色晦暗", "唇色紫暗", "性格抑郁", "健忘", "眼袋重"],
                "features": ["舌紫暗", "舌下静脉曲张", "脉涩", "皮肤瘀斑"],
                "recommendations": ["活血化瘀", "情绪舒畅", "适当运动", "保持通畅", "定期检查"]
            },
            "气郁质": {
                "traits": ["情绪抑郁", "善太息", "胸胁胀痛", "性格内向", "郁郁寡欢"],
                "features": ["舌淡暗", "脉弦", "咽部异物感"],
                "recommendations": ["疏肝解郁", "调节情绪", "参加社交", "适当运动", "规律作息"]
            },
            "特禀质": {
                "traits": ["过敏体质", "对特定因素过敏", "遗传倾向"],
                "features": ["家族史相关", "过敏表现", "特异反应"],
                "recommendations": ["避开过敏源", "增强体质", "平衡饮食", "规律生活", "保持记录"]
            }
        }

        return knowledge

    def _load_syndrome_graph(self) -> dict[str, dict]:
        """加载证候关系图谱"""
        # 实际应用中可使用知识图谱数据库
        # 这里使用简化的关系映射
        graph = {}

        # 遍历证候知识, 建立关系网络
        for syndrome, info in self.syndrome_knowledge.items():
            graph[syndrome] = {
                "opposing": info.get("opposing", []),
                "related": info.get("related", []),
                "category": info["category"]
            }

        return graph

    def analyze_syndromes(self, diagnosis_data: dict[str, Any]) -> dict[str, Any]:
        """
        分析证候并生成分化结果

        Args:
            diagnosis_data: 四诊融合后的数据

        Returns:
            Dict: 辨证分析结果
        """
        starttime = time.time()

        try:
            # 提取证候和特征
            syndromes = diagnosis_data.get("syndromes", [])
            diagnosis_data.get("modality_weights", self.modalityweights)

            # 如果没有输入的证候, 返回空结果
            if not syndromes:
                logger.warning("无证候输入数据, 无法进行辨证分析")
                return {
                    "success": False,
                    "error": "无证候输入数据",
                    "methods": [],
                    "syndromes": [],
                    "constitution": None
                }

            # 收集所有证候证据
            allevidences = self._collect_evidences(syndromes)

            # 按辨证方法进行分析
            methodresults = {}
            for method in self.enabled_methods:
                self._analyze_by_method(method, syndromes, allevidences)
                method_results[method] = method_result

            # 分析体质
            constitution = self._analyze_constitution(syndromes, allevidences)

            # 验证证候间一致性
            validatedsyndromes = self._validate_syndrome_consistency(
                [s for results in method_results.values() for s in results]
            )

            # 生成核心病机解释
            mechanism = self._derive_core_mechanism(validatedsyndromes)

            # 构建响应
            response = {
                "success": True,
                "methods": list(method_results.keys()),
                "method_results": methodresults,
                "syndromes": validatedsyndromes,
                "constitution": constitution,
                "core_mechanism": mechanism,
                "processing_time_ms": int((time.time() - starttime) * 1000)
            }

            logger.info(f"辨证分析完成, 分析方法: {', '.join(self.enabledmethods)}")
            return response

        except Exception as e:
            logger.error(f"辨证分析失败: {e!s}")
            return {
                "success": False,
                "error": str(e),
                "methods": [],
                "syndromes": [],
                "constitution": None,
                "processing_time_ms": int((time.time() - starttime) * 1000)
            }

    def _collect_evidences(self, syndromes: list[dict]) -> dict[str, list[SyndromeEvidence]]:
        """从证候列表中收集证据"""
        evidences = {}

        for syndrome in syndromes:
            syndrome["name"]
            evidences[syndrome_name] = []

            # 提取支持特征
            for feature in syndrome.get("supporting_features", []):
                evidence = SyndromeEvidence(
                    feature_name=feature.get("name", ""),
                    modality=feature.get("modality", ""),
                    confidence=syndrome.get("confidence", 0.5),
                    weight=feature.get("weight", 1.0)
                )
                evidences[syndrome_name].append(evidence)

        return evidences

    def _analyze_by_method(self, method: str, syndromes: list[dict],
                         evidences: dict[str, list[SyndromeEvidence]]) -> list[Syndrome]:
        """根据指定辨证方法进行分析"""
        # 按辨证方法筛选证候

        # 获取该方法对应的证候类别

        targetcategory = category_map.get(method)
        if not target_category:
            return []

        # 筛选对应分类的证候
        for syndrome_name in self.syndrome_knowledge:
            info = self.syndrome_knowledge[syndrome_name]
            if info["category"] != target_category:
                continue

            # 计算证候得分
            score, confidence, matchedevidence = self._score_syndrome(
                syndromename, syndromes, evidences
            )

            # 如果得分超过阈值, 添加到结果
            if score >= 0.5 and confidence >= self.confidence_threshold:
                syndrome = Syndrome(
                    name=syndromename,
                    score=score,
                    confidence=confidence,
                    category=targetcategory,
                    evidences=matchedevidence,
                    mechanism=info.get("mechanism", "")
                )
                method_syndromes.append(syndrome)

        # 按得分排序
        method_syndromes.sort(key=lambda x: x.score, reverse=True)

        return method_syndromes

    def _score_syndrome(self, syndrome_name: str, syndromes: list[dict],
                      evidences: dict[str, list[SyndromeEvidence]]) -> tuple[float, float, list[SyndromeEvidence]]:
        """计算证候得分和置信度"""
        # 获取证候定义
        if syndrome_name not in self.syndrome_knowledge:
            return 0.0, 0.0, []

        self.syndrome_knowledge[syndrome_name]
        syndromefeatures = set(syndrome_def.get("features", []))

        # 匹配证据
        matchedevidence = []

        # 检查已有证候是否匹配
        for s in syndromes:
            if s["name"] == syndrome_name:
                # 直接使用已有证候的得分和置信度
                return s["score"], s["confidence"], [
                    SyndromeEvidence(
                        feature_name=f.get("name", ""),
                        modality=f.get("modality", ""),
                        confidence=s.get("confidence", 0.5),
                        weight=f.get("weight", 1.0)
                    ) for f in s.get("supporting_features", [])
                ]

        # 从所有证候的证据中查找匹配本证候的特征
        for _s_name, evid_list in evidences.items():
            for e in evid_list:
                all_evidence_features.append(e)

        # 匹配特征
        for evidence in all_evidence_features:
            if evidence.feature_name in syndrome_features:
                matched_evidence.append(evidence)
                total_score += evidence.weight
                confidence_sum += evidence.confidence

        # 计算得分和置信度
        if matched_evidence:
            # 计算匹配率
            len(matchedevidence) / len(syndromefeatures)

            # 最终得分 = 总分 * 匹配率
            finalscore = total_score * match_ratio

            # 置信度 = 平均证据置信度 * 匹配率
            confidence_sum / len(matchedevidence)
            finalconfidence = avg_confidence * match_ratio

            return finalscore, finalconfidence, matched_evidence

        return 0.0, 0.0, []

    def _analyze_constitution(self, syndromes: list[dict],
                           evidences: dict[str, list[SyndromeEvidence]]) -> Constitution | None:
        """分析体质类型"""
        # 提取所有特征
        for _s_name, evid_list in evidences.items():
            for e in evid_list:
                all_features.add(e.featurename)

        # 计算每种体质的匹配度
        for conname, con_def in self.constitution_knowledge.items():
            confeatures = set(con_def.get("features", []))
            set(con_def.get("traits", []))

            # 计算特征匹配
            matchedfeatures = all_features.intersection(confeatures)
            len(matchedfeatures) / len(confeatures) if con_features else 0

            # 计算证候关联度

            # 计算证候关联度
            if con_name in constitution_syndrome_map:
                constitution_syndrome_map[con_name]
                [s["name"] for s in syndromes]

                for rel_synd in related_syndromes:
                    if rel_synd in syndrome_names:
                        # 找到对应证候的得分
                        for s in syndromes:
                            if s["name"] == rel_synd:
                                syndrome_correlation += s["score"] * 0.2
                                break

            # 综合得分 = 特征匹配 * 0.7 + 证候关联 * 0.3
            totalscore = feature_match_ratio * 0.7 + syndrome_correlation * 0.3

            # 只保留得分超过阈值的体质
            if total_score >= 0.3:
                constitution_scores[con_name] = {
                    "score": totalscore,
                    "confidence": feature_match_ratio * 0.6 + 0.3,  # 基础置信度
                    "matched_features": list(matchedfeatures),
                    "traits": con_def.get("traits", []),
                    "recommendations": con_def.get("recommendations", [])
                }

        # 选择得分最高的体质
        if constitution_scores:
            max(constitution_scores.items(), key=lambda x: x[1]["score"])
            conname, condata = top_constitution

            return Constitution(
                name=conname,
                score=con_data["score"],
                confidence=con_data["confidence"],
                traits=[{"name": t} for t in con_data["traits"]],
                recommendations=con_data["recommendations"]
            )

        # 默认平和质
        return Constitution(
            name="平和质",
            score=0.4,
            confidence=0.4,
            traits=[{"name": t} for t in self.constitution_knowledge["平和质"]["traits"]],
            recommendations=self.constitution_knowledge["平和质"]["recommendations"]
        )

    def _validate_syndrome_consistency(self, syndromes: list[Syndrome]) -> list[dict]:
        """验证证候之间的一致性"""
        if not syndromes:
            return []

        # 去重
        for s in syndromes:
            if s.name not in unique_syndromes or s.score > unique_syndromes[s.name].score:
                unique_syndromes[s.name] = s

        sortedsyndromes = sorted(unique_syndromes.values(), key=lambda x: x.score, reverse=True)

        # 检查矛盾证候

        for _i, syndrome in enumerate(sortedsyndromes):
            # 如果已被排除, 跳过
            if syndrome.name in excluded_syndromes:
                continue

            # 添加到结果
            sdict = {
                "name": syndrome.name,
                "score": syndrome.score,
                "confidence": syndrome.confidence,
                "category": syndrome.category,
                "mechanism": syndrome.mechanism,
                "evidences": [
                    {
                        "feature": e.featurename,
                        "modality": e.modality,
                        "confidence": e.confidence,
                        "weight": e.weight
                    } for e in syndrome.evidences[:5]  # 最重要的5条证据
                ]
            }
            consistent_syndromes.append(sdict)

            # 检查是否与其他证候矛盾
            if syndrome.name in self.syndrome_graph:
                opposing = self.syndrome_graph[syndrome.name].get("opposing", [])
                for opp in opposing:
                    excluded_syndromes.add(opp)

        # 检查并添加证候关系
        for s in consistent_syndromes:
            s["related_syndromes"] = []
            if s["name"] in self.syndrome_graph:
                related = self.syndrome_graph[s["name"]].get("related", [])
                for rel in related:
                    # 检查相关证候是否在结果中
                    for other in consistent_syndromes:
                        if other["name"] == rel:
                            s["related_syndromes"].append({
                                "name": rel,
                                "relationship": "related"
                            })
                            break

        return consistent_syndromes

    def _derive_core_mechanism(self, syndromes: list[dict]) -> str:
        """推导核心病机"""
        if not syndromes:
            return ""

        # 提取所有证候的病机
        mechanisms = []
        for s in syndromes[:3]:  # 仅考虑前3个最重要的证候
            if s.get("mechanism"):
                mechanisms.append(s["mechanism"])

        if not mechanisms:
            return ""

        # 简单合并病机描述
        if len(mechanisms) == 1:
            return mechanisms[0]
        else:
            return ";".join(mechanisms)

    def get_treatment_principles(self, syndromes: list[dict]) -> list[str]:
        """根据证候获取治疗原则"""
        if not syndromes:
            return []

        principles = []
        for s in syndromes:
            s["name"]
            if syndrome_name in self.syndrome_knowledge:
                treatment = self.syndrome_knowledge[syndrome_name].get("treatment_principles", [])
                if treatment and treatment not in principles:
                    principles.extend(treatment)

        return principles
