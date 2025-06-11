"""
算诊服务准确率优化器
Calculation Service Accuracy Optimizer

提升综合诊断准确率的核心模块
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class DiagnosisConfidenceLevel(Enum):
    """诊断置信度等级"""
    VERY_LOW = 0.2
    LOW = 0.4
    MEDIUM = 0.6
    HIGH = 0.8
    VERY_HIGH = 0.95


@dataclass
class DiagnosisFeature:
    """诊断特征"""
    name: str
    value: float
    weight: float
    confidence: float
    source: str  # 来源：八字、五运六气、子午流注等


@dataclass
class OptimizedDiagnosisResult:
    """优化后的诊断结果"""
    primary_constitution: str
    constitution_confidence: float
    secondary_constitutions: List[Tuple[str, float]]
    
    # 优化指标
    accuracy_score: float
    consistency_score: float
    feature_importance: Dict[str, float]
    
    # 诊断建议
    recommendations: List[str]
    risk_factors: List[str]
    
    # 元数据
    optimization_version: str = "2.0.0"
    processing_time: float = 0.0
    timestamp: datetime = None


class AccuracyOptimizer:
    """准确率优化器"""
    
    def __init__(self):
        self.feature_weights = self._initialize_feature_weights()
        self.consistency_threshold = 0.7
        self.confidence_boost_factor = 0.15
        self.multi_source_bonus = 0.1
        
    def _initialize_feature_weights(self) -> Dict[str, float]:
        """初始化特征权重"""
        return {
            # 八字体质特征权重
            "birth_year_stem": 0.15,
            "birth_year_branch": 0.15,
            "birth_month_stem": 0.12,
            "birth_month_branch": 0.12,
            "birth_day_stem": 0.10,
            "birth_day_branch": 0.10,
            "birth_hour_stem": 0.08,
            "birth_hour_branch": 0.08,
            
            # 五运六气特征权重
            "main_qi": 0.20,
            "guest_qi": 0.18,
            "central_qi": 0.15,
            "seasonal_factor": 0.12,
            
            # 子午流注特征权重
            "current_hour_qi": 0.10,
            "meridian_flow": 0.08,
            "organ_activity": 0.06,
            
            # 八卦配属特征权重
            "bagua_position": 0.08,
            "five_element": 0.12,
            "yin_yang_balance": 0.10
        }
    
    def optimize_diagnosis(self, 
                          raw_features: Dict[str, Any],
                          algorithm_results: Dict[str, Any]) -> OptimizedDiagnosisResult:
        """
        优化诊断结果
        
        Args:
            raw_features: 原始特征数据
            algorithm_results: 各算法的原始结果
            
        Returns:
            OptimizedDiagnosisResult: 优化后的诊断结果
        """
        start_time = datetime.now()
        
        # 1. 特征提取和标准化
        normalized_features = self._extract_and_normalize_features(raw_features)
        
        # 2. 多算法结果融合
        fused_results = self._fuse_algorithm_results(algorithm_results)
        
        # 3. 一致性检查和置信度调整
        consistency_score = self._calculate_consistency(fused_results)
        adjusted_confidence = self._adjust_confidence(fused_results, consistency_score)
        
        # 4. 特征重要性分析
        feature_importance = self._analyze_feature_importance(normalized_features, fused_results)
        
        # 5. 生成优化建议
        recommendations = self._generate_recommendations(fused_results, feature_importance)
        risk_factors = self._identify_risk_factors(fused_results, normalized_features)
        
        # 6. 计算准确率分数
        accuracy_score = self._calculate_accuracy_score(
            adjusted_confidence, consistency_score, feature_importance
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return OptimizedDiagnosisResult(
            primary_constitution=fused_results["primary_constitution"],
            constitution_confidence=adjusted_confidence,
            secondary_constitutions=fused_results["secondary_constitutions"],
            accuracy_score=accuracy_score,
            consistency_score=consistency_score,
            feature_importance=feature_importance,
            recommendations=recommendations,
            risk_factors=risk_factors,
            processing_time=processing_time,
            timestamp=datetime.now()
        )
    
    def _extract_and_normalize_features(self, raw_features: Dict[str, Any]) -> List[DiagnosisFeature]:
        """提取和标准化特征"""
        features = []
        
        for feature_name, feature_value in raw_features.items():
            if feature_name in self.feature_weights:
                # 标准化特征值
                normalized_value = self._normalize_feature_value(feature_value, feature_name)
                
                # 计算特征置信度
                confidence = self._calculate_feature_confidence(feature_value, feature_name)
                
                features.append(DiagnosisFeature(
                    name=feature_name,
                    value=normalized_value,
                    weight=self.feature_weights[feature_name],
                    confidence=confidence,
                    source=self._get_feature_source(feature_name)
                ))
        
        return features
    
    def _normalize_feature_value(self, value: Any, feature_name: str) -> float:
        """标准化特征值到0-1范围"""
        if isinstance(value, (int, float)):
            # 数值型特征：使用min-max标准化
            return max(0.0, min(1.0, float(value)))
        elif isinstance(value, str):
            # 字符串型特征：转换为数值
            return self._string_to_numeric(value, feature_name)
        else:
            return 0.5  # 默认值
    
    def _string_to_numeric(self, value: str, feature_name: str) -> float:
        """将字符串特征转换为数值"""
        # 天干地支映射
        heavenly_stems = {"甲": 0.1, "乙": 0.2, "丙": 0.3, "丁": 0.4, "戊": 0.5,
                         "己": 0.6, "庚": 0.7, "辛": 0.8, "壬": 0.9, "癸": 1.0}
        earthly_branches = {"子": 0.083, "丑": 0.167, "寅": 0.25, "卯": 0.333,
                           "辰": 0.417, "巳": 0.5, "午": 0.583, "未": 0.667,
                           "申": 0.75, "酉": 0.833, "戌": 0.917, "亥": 1.0}
        
        # 五行映射
        five_elements = {"木": 0.2, "火": 0.4, "土": 0.6, "金": 0.8, "水": 1.0}
        
        # 体质类型映射
        constitution_types = {
            "平和质": 1.0, "气虚质": 0.8, "阳虚质": 0.7, "阴虚质": 0.6,
            "痰湿质": 0.5, "湿热质": 0.4, "血瘀质": 0.3, "气郁质": 0.2, "特禀质": 0.1
        }
        
        if value in heavenly_stems:
            return heavenly_stems[value]
        elif value in earthly_branches:
            return earthly_branches[value]
        elif value in five_elements:
            return five_elements[value]
        elif value in constitution_types:
            return constitution_types[value]
        else:
            return 0.5  # 未知值默认为中等
    
    def _calculate_feature_confidence(self, value: Any, feature_name: str) -> float:
        """计算特征置信度"""
        base_confidence = 0.7
        
        # 根据特征类型调整置信度
        if "birth" in feature_name:
            # 出生信息置信度较高
            return min(0.95, base_confidence + 0.2)
        elif "current" in feature_name:
            # 当前时间相关信息置信度中等
            return base_confidence
        else:
            # 其他特征
            return max(0.3, base_confidence - 0.1)
    
    def _get_feature_source(self, feature_name: str) -> str:
        """获取特征来源"""
        if "birth" in feature_name:
            return "八字体质"
        elif any(x in feature_name for x in ["qi", "seasonal"]):
            return "五运六气"
        elif any(x in feature_name for x in ["hour", "meridian", "organ"]):
            return "子午流注"
        elif any(x in feature_name for x in ["bagua", "element", "yin_yang"]):
            return "八卦配属"
        else:
            return "综合"
    
    def _fuse_algorithm_results(self, algorithm_results: Dict[str, Any]) -> Dict[str, Any]:
        """融合多算法结果"""
        constitution_scores = {}
        
        # 收集各算法的体质判断结果
        for algorithm_name, result in algorithm_results.items():
            if "constitution" in result:
                constitution = result["constitution"]
                confidence = result.get("confidence", 0.5)
                
                if constitution not in constitution_scores:
                    constitution_scores[constitution] = []
                constitution_scores[constitution].append(confidence)
        
        # 计算加权平均分数
        final_scores = {}
        for constitution, scores in constitution_scores.items():
            # 使用加权平均，给予一致性更高的结果更大权重
            weights = [score for score in scores]  # 置信度作为权重
            weighted_score = np.average(scores, weights=weights)
            final_scores[constitution] = weighted_score
        
        # 排序获取主要和次要体质
        sorted_constitutions = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
        
        primary_constitution = sorted_constitutions[0][0] if sorted_constitutions else "平和质"
        secondary_constitutions = sorted_constitutions[1:4]  # 取前3个次要体质
        
        return {
            "primary_constitution": primary_constitution,
            "secondary_constitutions": secondary_constitutions,
            "all_scores": final_scores
        }
    
    def _calculate_consistency(self, fused_results: Dict[str, Any]) -> float:
        """计算结果一致性"""
        all_scores = fused_results["all_scores"]
        if len(all_scores) < 2:
            return 1.0
        
        scores = list(all_scores.values())
        primary_score = max(scores)
        secondary_scores = [s for s in scores if s != primary_score]
        
        if not secondary_scores:
            return 1.0
        
        # 计算主要结果与次要结果的差距
        max_secondary = max(secondary_scores)
        consistency = (primary_score - max_secondary) / primary_score
        
        return max(0.0, min(1.0, consistency))
    
    def _adjust_confidence(self, fused_results: Dict[str, Any], consistency_score: float) -> float:
        """调整置信度"""
        all_scores = fused_results["all_scores"]
        primary_constitution = fused_results["primary_constitution"]
        
        base_confidence = all_scores.get(primary_constitution, 0.5)
        
        # 一致性加成
        consistency_bonus = consistency_score * self.confidence_boost_factor
        
        # 多源验证加成
        source_count = len([s for s in all_scores.values() if s > 0.3])
        multi_source_bonus = min(0.2, source_count * self.multi_source_bonus)
        
        adjusted_confidence = base_confidence + consistency_bonus + multi_source_bonus
        
        return max(0.1, min(0.98, adjusted_confidence))
    
    def _analyze_feature_importance(self, 
                                  features: List[DiagnosisFeature], 
                                  fused_results: Dict[str, Any]) -> Dict[str, float]:
        """分析特征重要性"""
        importance_scores = {}
        
        for feature in features:
            # 基础重要性 = 特征权重 × 特征置信度
            base_importance = feature.weight * feature.confidence
            
            # 根据特征值调整重要性
            value_factor = abs(feature.value - 0.5) * 2  # 偏离中值越远越重要
            
            # 最终重要性分数
            final_importance = base_importance * (1 + value_factor)
            importance_scores[feature.name] = final_importance
        
        # 归一化重要性分数
        total_importance = sum(importance_scores.values())
        if total_importance > 0:
            importance_scores = {k: v/total_importance for k, v in importance_scores.items()}
        
        return importance_scores
    
    def _generate_recommendations(self, 
                                fused_results: Dict[str, Any], 
                                feature_importance: Dict[str, float]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        primary_constitution = fused_results["primary_constitution"]
        
        # 基于主要体质的建议
        constitution_recommendations = {
            "平和质": ["保持规律作息", "适度运动", "均衡饮食"],
            "气虚质": ["补气养血", "避免过度劳累", "多食健脾益气食物"],
            "阳虚质": ["温阳补肾", "避免寒凉", "适当进补"],
            "阴虚质": ["滋阴润燥", "避免熬夜", "多食滋阴食物"],
            "痰湿质": ["化痰除湿", "控制体重", "清淡饮食"],
            "湿热质": ["清热利湿", "避免辛辣", "多食清热食物"],
            "血瘀质": ["活血化瘀", "适度运动", "避免久坐"],
            "气郁质": ["疏肝理气", "调节情志", "适当放松"],
            "特禀质": ["避免过敏原", "增强体质", "个性化调理"]
        }
        
        recommendations.extend(constitution_recommendations.get(primary_constitution, []))
        
        # 基于重要特征的建议
        top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]
        for feature_name, importance in top_features:
            if importance > 0.1:  # 重要性阈值
                if "qi" in feature_name:
                    recommendations.append("注意季节性调养")
                elif "hour" in feature_name:
                    recommendations.append("按时作息，顺应生物钟")
                elif "element" in feature_name:
                    recommendations.append("根据五行属性调整生活方式")
        
        return list(set(recommendations))  # 去重
    
    def _identify_risk_factors(self, 
                             fused_results: Dict[str, Any], 
                             features: List[DiagnosisFeature]) -> List[str]:
        """识别风险因素"""
        risk_factors = []
        primary_constitution = fused_results["primary_constitution"]
        
        # 基于体质的风险因素
        constitution_risks = {
            "气虚质": ["易感冒", "消化不良", "疲劳乏力"],
            "阳虚质": ["畏寒怕冷", "腰膝酸软", "性功能减退"],
            "阴虚质": ["口干舌燥", "失眠多梦", "潮热盗汗"],
            "痰湿质": ["肥胖", "高血脂", "糖尿病风险"],
            "湿热质": ["皮肤问题", "口苦口臭", "情绪烦躁"],
            "血瘀质": ["心血管疾病", "月经不调", "疼痛症状"],
            "气郁质": ["抑郁焦虑", "乳腺增生", "消化系统问题"],
            "特禀质": ["过敏反应", "免疫系统异常", "遗传性疾病"]
        }
        
        risk_factors.extend(constitution_risks.get(primary_constitution, []))
        
        # 基于特征异常的风险因素
        for feature in features:
            if feature.value < 0.3 or feature.value > 0.7:  # 异常值
                if "yin_yang" in feature.name:
                    risk_factors.append("阴阳失衡")
                elif "qi" in feature.name:
                    risk_factors.append("气机不调")
        
        return list(set(risk_factors))  # 去重
    
    def _calculate_accuracy_score(self, 
                                confidence: float, 
                                consistency: float, 
                                feature_importance: Dict[str, float]) -> float:
        """计算准确率分数"""
        # 基础准确率 = 置信度 × 一致性
        base_accuracy = confidence * consistency
        
        # 特征覆盖度加成
        feature_coverage = len([f for f in feature_importance.values() if f > 0.05]) / len(feature_importance)
        coverage_bonus = feature_coverage * 0.1
        
        # 最终准确率分数
        accuracy_score = base_accuracy + coverage_bonus
        
        return max(0.1, min(0.99, accuracy_score))


# 使用示例
def optimize_calculation_diagnosis(raw_data: Dict[str, Any]) -> OptimizedDiagnosisResult:
    """
    优化算诊结果的主要接口
    
    Args:
        raw_data: 包含原始特征和算法结果的数据
        
    Returns:
        OptimizedDiagnosisResult: 优化后的诊断结果
    """
    optimizer = AccuracyOptimizer()
    
    # 分离特征和算法结果
    raw_features = raw_data.get("features", {})
    algorithm_results = raw_data.get("algorithm_results", {})
    
    # 执行优化
    result = optimizer.optimize_diagnosis(raw_features, algorithm_results)
    
    logger.info(f"诊断优化完成，准确率分数: {result.accuracy_score:.3f}")
    
    return result 