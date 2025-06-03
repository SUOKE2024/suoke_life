#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中医辨证分析器 - 实现中医辨证论治的数字化分析
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import jieba
from loguru import logger

from ..service.embedding_service import EmbeddingService
from ..model.tcm_models import (
    Syndrome, SyndromePattern, ConstitutionType, 
    SymptomCategory, TreatmentPrinciple
)

class SyndromeType(Enum):
    """证型分类"""
    QI_XU = "气虚"           # 气虚证
    YANG_XU = "阳虚"         # 阳虚证
    YIN_XU = "阴虚"          # 阴虚证
    XUE_XU = "血虚"          # 血虚证
    QI_ZHI = "气滞"          # 气滞证
    XUE_YU = "血瘀"          # 血瘀证
    TAN_SHI = "痰湿"         # 痰湿证
    SHI_RE = "湿热"          # 湿热证
    FENG_HAN = "风寒"        # 风寒证
    FENG_RE = "风热"         # 风热证

@dataclass
class SymptomAnalysis:
    """症状分析结果"""
    symptom: str
    category: SymptomCategory
    severity: float  # 0-1
    confidence: float  # 0-1
    related_organs: List[str]
    pathological_factors: List[str]

@dataclass
class SyndromeAnalysisResult:
    """辨证分析结果"""
    primary_syndrome: Syndrome
    secondary_syndromes: List[Syndrome]
    confidence_score: float
    symptom_analyses: List[SymptomAnalysis]
    treatment_principles: List[TreatmentPrinciple]
    constitution_tendency: ConstitutionType
    reasoning_chain: List[str]  # 推理链
    recommendations: Dict[str, Any]

class SyndromeAnalyzer:
    """中医辨证分析器"""
    
    def __init__(self, config: Dict[str, Any], embedding_service: EmbeddingService):
        """
        初始化辨证分析器
        
        Args:
            config: 配置信息
            embedding_service: 嵌入服务
        """
        self.config = config
        self.embedding_service = embedding_service
        
        # 中医术语词典
        self.tcm_terms = {}
        self.syndrome_patterns = {}
        self.symptom_mappings = {}
        
        # 加载中医知识库
        self._load_tcm_knowledge()
        
        # 初始化jieba分词
        self._init_jieba()
    
    def _load_tcm_knowledge(self) -> None:
        """加载中医知识库"""
        # 这里应该从数据库或文件加载中医知识
        # 暂时使用硬编码的示例数据
        
        # 症状-证型映射
        self.symptom_mappings = {
            "乏力": ["气虚", "阳虚"],
            "怕冷": ["阳虚", "气虚"],
            "手脚冰凉": ["阳虚"],
            "口干": ["阴虚", "燥热"],
            "盗汗": ["阴虚"],
            "失眠": ["心火旺", "阴虚", "气郁"],
            "头晕": ["气虚", "血虚", "痰湿"],
            "胸闷": ["气滞", "痰湿"],
            "腹胀": ["气滞", "脾虚"],
            "便秘": ["燥热", "气滞", "阴虚"],
            "腹泻": ["脾虚", "湿热"],
            "月经不调": ["气滞血瘀", "肾虚"],
            "面色苍白": ["气虚", "血虚"],
            "舌苔厚腻": ["痰湿", "湿热"],
            "脉细弱": ["气虚", "血虚"]
        }
        
        # 证型特征模式
        self.syndrome_patterns = {
            SyndromeType.QI_XU: {
                "primary_symptoms": ["乏力", "气短", "懒言", "自汗"],
                "secondary_symptoms": ["头晕", "面色萎黄", "食欲不振"],
                "tongue": ["舌淡", "苔薄白"],
                "pulse": ["脉细弱"],
                "severity_weights": {"乏力": 0.3, "气短": 0.25, "懒言": 0.2}
            },
            SyndromeType.YANG_XU: {
                "primary_symptoms": ["怕冷", "手脚冰凉", "腰膝酸软", "夜尿频"],
                "secondary_symptoms": ["乏力", "面色苍白", "舌淡胖"],
                "tongue": ["舌淡胖", "苔白"],
                "pulse": ["脉沉迟"],
                "severity_weights": {"怕冷": 0.3, "手脚冰凉": 0.25, "腰膝酸软": 0.2}
            },
            SyndromeType.YIN_XU: {
                "primary_symptoms": ["口干", "盗汗", "五心烦热", "失眠"],
                "secondary_symptoms": ["头晕", "耳鸣", "腰膝酸软"],
                "tongue": ["舌红", "苔少"],
                "pulse": ["脉细数"],
                "severity_weights": {"口干": 0.25, "盗汗": 0.25, "五心烦热": 0.25}
            }
        }
    
    def _init_jieba(self) -> None:
        """初始化jieba分词器"""
        # 添加中医术语到jieba词典
        tcm_terms = [
            "气虚", "阳虚", "阴虚", "血虚", "气滞", "血瘀", "痰湿", "湿热",
            "脾胃虚弱", "肝郁气滞", "心火旺盛", "肾阳虚", "肾阴虚",
            "五心烦热", "腰膝酸软", "夜尿频", "盗汗", "自汗"
        ]
        
        for term in tcm_terms:
            jieba.add_word(term, freq=1000, tag='tcm')
    
    async def analyze_syndrome(
        self,
        symptoms: List[str],
        patient_info: Optional[Dict[str, Any]] = None,
        context: Optional[str] = None
    ) -> SyndromeAnalysisResult:
        """
        进行中医辨证分析
        
        Args:
            symptoms: 症状列表
            patient_info: 患者信息（年龄、性别、体质等）
            context: 额外上下文信息
            
        Returns:
            辨证分析结果
        """
        logger.info(f"开始辨证分析，症状: {symptoms}")
        
        # 1. 症状预处理和标准化
        normalized_symptoms = await self._normalize_symptoms(symptoms)
        
        # 2. 症状分析
        symptom_analyses = await self._analyze_symptoms(normalized_symptoms)
        
        # 3. 证型识别
        syndrome_scores = await self._calculate_syndrome_scores(symptom_analyses)
        
        # 4. 确定主次证型
        primary_syndrome, secondary_syndromes = self._determine_syndromes(syndrome_scores)
        
        # 5. 生成推理链
        reasoning_chain = self._generate_reasoning_chain(
            symptom_analyses, primary_syndrome, secondary_syndromes
        )
        
        # 6. 确定治疗原则
        treatment_principles = self._determine_treatment_principles(
            primary_syndrome, secondary_syndromes
        )
        
        # 7. 体质倾向分析
        constitution_tendency = self._analyze_constitution_tendency(
            symptom_analyses, patient_info
        )
        
        # 8. 生成建议
        recommendations = await self._generate_recommendations(
            primary_syndrome, secondary_syndromes, patient_info
        )
        
        # 9. 计算整体置信度
        confidence_score = self._calculate_overall_confidence(
            syndrome_scores, symptom_analyses
        )
        
        result = SyndromeAnalysisResult(
            primary_syndrome=primary_syndrome,
            secondary_syndromes=secondary_syndromes,
            confidence_score=confidence_score,
            symptom_analyses=symptom_analyses,
            treatment_principles=treatment_principles,
            constitution_tendency=constitution_tendency,
            reasoning_chain=reasoning_chain,
            recommendations=recommendations
        )
        
        logger.info(f"辨证分析完成，主证: {primary_syndrome.name}, 置信度: {confidence_score:.2f}")
        return result
    
    async def _normalize_symptoms(self, symptoms: List[str]) -> List[str]:
        """标准化症状描述"""
        normalized = []
        
        for symptom in symptoms:
            # 分词处理
            words = jieba.lcut(symptom)
            
            # 提取中医相关词汇
            tcm_words = []
            for word in words:
                if word in self.symptom_mappings or len(word) >= 2:
                    tcm_words.append(word)
            
            if tcm_words:
                normalized.extend(tcm_words)
            else:
                normalized.append(symptom)
        
        return list(set(normalized))  # 去重
    
    async def _analyze_symptoms(self, symptoms: List[str]) -> List[SymptomAnalysis]:
        """分析症状"""
        analyses = []
        
        for symptom in symptoms:
            # 确定症状类别
            category = self._categorize_symptom(symptom)
            
            # 计算严重程度（基于症状描述的语义强度）
            severity = await self._calculate_symptom_severity(symptom)
            
            # 计算置信度
            confidence = self._calculate_symptom_confidence(symptom)
            
            # 确定相关脏腑
            related_organs = self._get_related_organs(symptom)
            
            # 确定病理因素
            pathological_factors = self._get_pathological_factors(symptom)
            
            analysis = SymptomAnalysis(
                symptom=symptom,
                category=category,
                severity=severity,
                confidence=confidence,
                related_organs=related_organs,
                pathological_factors=pathological_factors
            )
            analyses.append(analysis)
        
        return analyses
    
    def _categorize_symptom(self, symptom: str) -> SymptomCategory:
        """症状分类"""
        # 基于症状内容进行分类
        if any(word in symptom for word in ["头", "眩", "晕"]):
            return SymptomCategory.HEAD_NECK
        elif any(word in symptom for word in ["胸", "心", "悸"]):
            return SymptomCategory.CHEST_HEART
        elif any(word in symptom for word in ["腹", "胃", "肠", "便", "泻"]):
            return SymptomCategory.DIGESTIVE
        elif any(word in symptom for word in ["腰", "膝", "关节", "肢"]):
            return SymptomCategory.MUSCULOSKELETAL
        elif any(word in symptom for word in ["汗", "热", "寒", "冷"]):
            return SymptomCategory.CONSTITUTIONAL
        else:
            return SymptomCategory.GENERAL
    
    async def _calculate_symptom_severity(self, symptom: str) -> float:
        """计算症状严重程度"""
        # 基于症状描述中的程度词汇
        severity_keywords = {
            "剧烈": 0.9, "严重": 0.8, "明显": 0.7, "较重": 0.6,
            "中等": 0.5, "轻微": 0.3, "偶尔": 0.2, "轻度": 0.3
        }
        
        for keyword, score in severity_keywords.items():
            if keyword in symptom:
                return score
        
        return 0.5  # 默认中等程度
    
    def _calculate_symptom_confidence(self, symptom: str) -> float:
        """计算症状识别置信度"""
        if symptom in self.symptom_mappings:
            return 0.9
        elif len(symptom) >= 2:
            return 0.7
        else:
            return 0.5
    
    def _get_related_organs(self, symptom: str) -> List[str]:
        """获取症状相关的脏腑"""
        organ_mappings = {
            "心": ["失眠", "心悸", "胸闷", "健忘"],
            "肝": ["胁痛", "易怒", "目赤", "头痛"],
            "脾": ["腹胀", "便溏", "乏力", "食欲不振"],
            "肺": ["咳嗽", "气短", "胸闷", "自汗"],
            "肾": ["腰酸", "耳鸣", "夜尿", "怕冷"]
        }
        
        related = []
        for organ, symptoms in organ_mappings.items():
            if any(s in symptom for s in symptoms):
                related.append(organ)
        
        return related
    
    def _get_pathological_factors(self, symptom: str) -> List[str]:
        """获取病理因素"""
        factor_mappings = {
            "气虚": ["乏力", "气短", "懒言"],
            "血虚": ["面色苍白", "头晕", "心悸"],
            "阴虚": ["口干", "盗汗", "五心烦热"],
            "阳虚": ["怕冷", "手脚冰凉", "腰膝酸软"],
            "气滞": ["胸闷", "腹胀", "情志不畅"],
            "血瘀": ["刺痛", "固定痛", "面色晦暗"],
            "痰湿": ["胸闷", "头重", "舌苔厚腻"],
            "湿热": ["口苦", "小便黄", "舌苔黄腻"]
        }
        
        factors = []
        for factor, symptoms in factor_mappings.items():
            if any(s in symptom for s in symptoms):
                factors.append(factor)
        
        return factors
    
    async def _calculate_syndrome_scores(
        self, 
        symptom_analyses: List[SymptomAnalysis]
    ) -> Dict[SyndromeType, float]:
        """计算各证型得分"""
        scores = {syndrome: 0.0 for syndrome in SyndromeType}
        
        for analysis in symptom_analyses:
            symptom = analysis.symptom
            
            # 基于症状映射计算得分
            if symptom in self.symptom_mappings:
                for syndrome_name in self.symptom_mappings[symptom]:
                    # 找到对应的证型枚举
                    for syndrome_type in SyndromeType:
                        if syndrome_type.value == syndrome_name:
                            # 得分 = 症状严重程度 × 置信度 × 权重
                            weight = 1.0
                            if syndrome_type in self.syndrome_patterns:
                                pattern = self.syndrome_patterns[syndrome_type]
                                weight = pattern.get("severity_weights", {}).get(symptom, 1.0)
                            
                            score = analysis.severity * analysis.confidence * weight
                            scores[syndrome_type] += score
                            break
        
        return scores
    
    def _determine_syndromes(
        self, 
        syndrome_scores: Dict[SyndromeType, float]
    ) -> Tuple[Syndrome, List[Syndrome]]:
        """确定主次证型"""
        # 按得分排序
        sorted_syndromes = sorted(
            syndrome_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # 主证（得分最高）
        primary_type, primary_score = sorted_syndromes[0]
        primary_syndrome = Syndrome(
            name=primary_type.value,
            type=primary_type,
            confidence=min(primary_score, 1.0),
            description=f"{primary_type.value}证候"
        )
        
        # 次证（得分超过阈值的其他证型）
        secondary_syndromes = []
        threshold = primary_score * 0.6  # 次证阈值为主证得分的60%
        
        for syndrome_type, score in sorted_syndromes[1:]:
            if score >= threshold:
                secondary_syndrome = Syndrome(
                    name=syndrome_type.value,
                    type=syndrome_type,
                    confidence=min(score, 1.0),
                    description=f"{syndrome_type.value}证候"
                )
                secondary_syndromes.append(secondary_syndrome)
        
        return primary_syndrome, secondary_syndromes
    
    def _generate_reasoning_chain(
        self,
        symptom_analyses: List[SymptomAnalysis],
        primary_syndrome: Syndrome,
        secondary_syndromes: List[Syndrome]
    ) -> List[str]:
        """生成推理链"""
        reasoning = []
        
        # 症状总结
        symptoms_summary = [analysis.symptom for analysis in symptom_analyses]
        reasoning.append(f"患者主要症状：{', '.join(symptoms_summary)}")
        
        # 症状分析
        for analysis in symptom_analyses:
            if analysis.confidence > 0.7:
                reasoning.append(
                    f"症状'{analysis.symptom}'提示{', '.join(analysis.pathological_factors)}，"
                    f"涉及{', '.join(analysis.related_organs)}脏腑"
                )
        
        # 证型推断
        reasoning.append(f"综合分析，患者主要证型为{primary_syndrome.name}")
        
        if secondary_syndromes:
            secondary_names = [s.name for s in secondary_syndromes]
            reasoning.append(f"兼有{', '.join(secondary_names)}证候")
        
        return reasoning
    
    def _determine_treatment_principles(
        self,
        primary_syndrome: Syndrome,
        secondary_syndromes: List[Syndrome]
    ) -> List[TreatmentPrinciple]:
        """确定治疗原则"""
        principles = []
        
        # 基于主证确定主要治疗原则
        principle_mappings = {
            SyndromeType.QI_XU: TreatmentPrinciple(
                name="补气健脾",
                description="补益元气，健运脾胃",
                priority=1
            ),
            SyndromeType.YANG_XU: TreatmentPrinciple(
                name="温阳补肾",
                description="温补肾阳，固本培元",
                priority=1
            ),
            SyndromeType.YIN_XU: TreatmentPrinciple(
                name="滋阴润燥",
                description="滋养阴液，润燥生津",
                priority=1
            )
        }
        
        if primary_syndrome.type in principle_mappings:
            principles.append(principle_mappings[primary_syndrome.type])
        
        # 基于次证添加辅助治疗原则
        for secondary in secondary_syndromes:
            if secondary.type in principle_mappings:
                principle = principle_mappings[secondary.type]
                principle.priority = 2  # 次要优先级
                principles.append(principle)
        
        return principles
    
    def _analyze_constitution_tendency(
        self,
        symptom_analyses: List[SymptomAnalysis],
        patient_info: Optional[Dict[str, Any]]
    ) -> ConstitutionType:
        """分析体质倾向"""
        # 基于症状和患者信息分析体质
        # 这里简化处理，实际应该有更复杂的体质分析算法
        
        constitution_scores = {
            ConstitutionType.PEACEFUL: 0.0,
            ConstitutionType.QI_DEFICIENCY: 0.0,
            ConstitutionType.YANG_DEFICIENCY: 0.0,
            ConstitutionType.YIN_DEFICIENCY: 0.0,
            ConstitutionType.PHLEGM_DAMPNESS: 0.0,
            ConstitutionType.DAMP_HEAT: 0.0,
            ConstitutionType.BLOOD_STASIS: 0.0,
            ConstitutionType.QI_STAGNATION: 0.0,
            ConstitutionType.SPECIAL_DIATHESIS: 0.0
        }
        
        # 基于症状计算体质得分
        for analysis in symptom_analyses:
            for factor in analysis.pathological_factors:
                if "气虚" in factor:
                    constitution_scores[ConstitutionType.QI_DEFICIENCY] += 1
                elif "阳虚" in factor:
                    constitution_scores[ConstitutionType.YANG_DEFICIENCY] += 1
                elif "阴虚" in factor:
                    constitution_scores[ConstitutionType.YIN_DEFICIENCY] += 1
                elif "痰湿" in factor:
                    constitution_scores[ConstitutionType.PHLEGM_DAMPNESS] += 1
        
        # 返回得分最高的体质类型
        return max(constitution_scores.items(), key=lambda x: x[1])[0]
    
    async def _generate_recommendations(
        self,
        primary_syndrome: Syndrome,
        secondary_syndromes: List[Syndrome],
        patient_info: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """生成个性化建议"""
        recommendations = {
            "lifestyle": [],
            "diet": [],
            "exercise": [],
            "emotional": [],
            "prevention": []
        }
        
        # 基于证型生成建议
        if primary_syndrome.type == SyndromeType.QI_XU:
            recommendations["lifestyle"].extend([
                "规律作息，避免过度劳累",
                "适当午休，保证充足睡眠"
            ])
            recommendations["diet"].extend([
                "多食用健脾益气的食物，如山药、大枣、小米",
                "避免生冷寒凉食物"
            ])
            recommendations["exercise"].extend([
                "选择温和的运动，如太极拳、八段锦",
                "避免剧烈运动"
            ])
        
        elif primary_syndrome.type == SyndromeType.YIN_XU:
            recommendations["lifestyle"].extend([
                "避免熬夜，保持心情平静",
                "居住环境保持湿润"
            ])
            recommendations["diet"].extend([
                "多食用滋阴润燥的食物，如银耳、百合、梨",
                "少食辛辣燥热食物"
            ])
        
        return recommendations
    
    def _calculate_overall_confidence(
        self,
        syndrome_scores: Dict[SyndromeType, float],
        symptom_analyses: List[SymptomAnalysis]
    ) -> float:
        """计算整体置信度"""
        # 基于症状置信度和证型得分计算
        symptom_confidence = sum(a.confidence for a in symptom_analyses) / len(symptom_analyses)
        
        # 主证得分
        max_syndrome_score = max(syndrome_scores.values()) if syndrome_scores else 0
        
        # 综合置信度
        overall_confidence = (symptom_confidence + min(max_syndrome_score, 1.0)) / 2
        
        return overall_confidence 