#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多模态融合引擎 - 高级实现
负责融合望、闻、问、切四诊数据，实现注意力机制和特征融合
"""

import logging
import time
import json
import numpy as np
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ModalityFeature:
    """表示单个模态特征的数据类"""
    name: str
    value: float
    confidence: float
    category: str
    modality: str
    weight: float = 1.0
    correlations: Dict[str, float] = None

@dataclass
class SyndromeScore:
    """证候评分数据类"""
    name: str
    score: float
    features: List[ModalityFeature]
    confidence: float
    modality_weights: Dict[str, float]

class MultimodalFusionEngine:
    """
    多模态融合引擎 - 高级实现
    支持多种融合算法和注意力机制
    """
    
    # 融合算法类型
    FUSION_WEIGHTED = "weighted"  # 加权融合
    FUSION_ATTENTION = "attention"  # 注意力机制融合
    FUSION_ENSEMBLE = "ensemble"  # 集成融合
    FUSION_CROSS_MODAL = "cross_modal"  # 跨模态融合
    
    def __init__(self, config: Dict = None):
        """
        初始化多模态融合引擎
        
        Args:
            config: 融合引擎配置
        """
        self.config = config or {}
        
        # 融合算法类型
        self.fusion_algorithm = self.config.get("algorithm", self.FUSION_WEIGHTED)
        
        # 置信度阈值
        self.confidence_threshold = self.config.get("confidence_threshold", 0.6)
        
        # 各模态基础权重
        self.modality_weights = {
            "looking": self.config.get("weights.looking", 1.0),
            "listening": self.config.get("weights.listening", 1.0),
            "inquiry": self.config.get("weights.inquiry", 1.5),  # 问诊通常更重要
            "palpation": self.config.get("weights.palpation", 1.2)
        }
        
        # 证候-特征映射表
        self.syndrome_feature_map = self._load_syndrome_feature_map()
        
        # 特征权重学习率
        self.feature_weight_lr = self.config.get("feature_weight_lr", 0.01)
        
        # 历史特征权重缓存
        self.feature_weights_cache = {}
        
        # 跨模态相关性矩阵
        self.cross_modal_correlation = self._init_cross_modal_correlation()
        
        logger.info(f"多模态融合引擎初始化完成，使用{self.fusion_algorithm}融合算法")
    
    def _load_syndrome_feature_map(self) -> Dict[str, List[Dict]]:
        """加载证候-特征映射表"""
        # 实际应用中应从知识库加载
        # 这里使用示例数据
        syndromes = {
            "脾胃湿热": [
                {"name": "舌苔黄腻", "modality": "looking", "weight": 1.5},
                {"name": "口干口苦", "modality": "inquiry", "weight": 1.2},
                {"name": "脉滑数", "modality": "palpation", "weight": 1.0}
            ],
            "肝郁气滞": [
                {"name": "胁肋胀痛", "modality": "inquiry", "weight": 1.5},
                {"name": "舌边红", "modality": "looking", "weight": 1.0},
                {"name": "脉弦", "modality": "palpation", "weight": 1.3}
            ],
            "心脾两虚": [
                {"name": "心悸", "modality": "inquiry", "weight": 1.2},
                {"name": "舌淡", "modality": "looking", "weight": 1.0},
                {"name": "乏力", "modality": "inquiry", "weight": 1.1},
                {"name": "脉细弱", "modality": "palpation", "weight": 1.0}
            ],
            "肺阴虚": [
                {"name": "干咳", "modality": "inquiry", "weight": 1.4},
                {"name": "声音嘶哑", "modality": "listening", "weight": 1.3},
                {"name": "舌红少苔", "modality": "looking", "weight": 1.2},
                {"name": "脉细数", "modality": "palpation", "weight": 1.0}
            ],
            "肾阳虚": [
                {"name": "腰膝酸软", "modality": "inquiry", "weight": 1.5},
                {"name": "畏寒肢冷", "modality": "inquiry", "weight": 1.3},
                {"name": "舌淡胖", "modality": "looking", "weight": 1.2},
                {"name": "脉沉细", "modality": "palpation", "weight": 1.4}
            ],
            "气血两虚": [
                {"name": "面色苍白", "modality": "looking", "weight": 1.4},
                {"name": "乏力", "modality": "inquiry", "weight": 1.3},
                {"name": "心悸", "modality": "inquiry", "weight": 1.0},
                {"name": "脉细弱", "modality": "palpation", "weight": 1.2}
            ]
        }
        
        return syndromes
    
    def _init_cross_modal_correlation(self) -> Dict[str, Dict[str, float]]:
        """初始化跨模态相关性矩阵"""
        modalities = ["looking", "listening", "inquiry", "palpation"]
        correlation = {}
        
        for m1 in modalities:
            correlation[m1] = {}
            for m2 in modalities:
                if m1 == m2:
                    correlation[m1][m2] = 1.0
                else:
                    # 默认相关性，实际应从历史数据学习
                    correlation[m1][m2] = 0.5
        
        # 特定模态间相关性调整
        correlation["looking"]["palpation"] = 0.7  # 望诊与切诊相关性较高
        correlation["inquiry"]["listening"] = 0.8  # 问诊与闻诊相关性较高
        
        return correlation
    
    def fuse_diagnosis_data(self, diagnosis_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        融合四诊数据，生成综合分析结果
        
        Args:
            diagnosis_results: 四诊数据结果列表
            
        Returns:
            Dict: 融合结果
        """
        if not diagnosis_results:
            logger.warning("无四诊数据输入，无法进行融合")
            return {
                "success": False,
                "error": "无输入数据",
                "syndromes": [],
                "confidence": 0.0
            }
        
        start_time = time.time()
        try:
            # 预处理四诊数据，提取特征
            features = self._extract_features(diagnosis_results)
            
            # 动态调整模态权重
            adjusted_weights = self._adjust_modality_weights(diagnosis_results, features)
            
            # 根据配置的算法进行融合
            if self.fusion_algorithm == self.FUSION_ATTENTION:
                fusion_result = self._attention_based_fusion(features, adjusted_weights)
            elif self.fusion_algorithm == self.FUSION_ENSEMBLE:
                fusion_result = self._ensemble_fusion(features, adjusted_weights)
            elif self.fusion_algorithm == self.FUSION_CROSS_MODAL:
                fusion_result = self._cross_modal_fusion(features, adjusted_weights)
            else:  # 默认加权融合
                fusion_result = self._weighted_fusion(features, adjusted_weights)
            
            # 构建融合结果
            result = {
                "success": True,
                "fusion_algorithm": self.fusion_algorithm,
                "syndromes": fusion_result["syndromes"],
                "constitution_types": fusion_result.get("constitution_types", []),
                "confidence": fusion_result["confidence"],
                "modality_weights": adjusted_weights,
                "processing_time_ms": int((time.time() - start_time) * 1000)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"融合四诊数据失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "syndromes": [],
                "confidence": 0.0,
                "processing_time_ms": int((time.time() - start_time) * 1000)
            }
    
    def _extract_features(self, diagnosis_results: List[Dict[str, Any]]) -> List[ModalityFeature]:
        """从诊断结果中提取特征"""
        extracted_features = []
        
        for diagnosis in diagnosis_results:
            modality = diagnosis.get("type", "").lower()
            if not modality:
                continue
                
            # 特征数据
            features_data = diagnosis.get("features", [])
            base_weight = self.modality_weights.get(modality, 1.0)
            
            for feature in features_data:
                # 创建特征对象
                feature_obj = ModalityFeature(
                    name=feature.get("name", ""),
                    value=feature.get("value", 0.0),
                    confidence=feature.get("confidence", 0.0),
                    category=feature.get("category", ""),
                    modality=modality,
                    weight=base_weight
                )
                
                # 过滤低置信度特征
                if feature_obj.confidence >= self.confidence_threshold:
                    extracted_features.append(feature_obj)
        
        logger.info(f"从四诊数据中提取了{len(extracted_features)}个有效特征")
        return extracted_features
    
    def _adjust_modality_weights(self, diagnosis_results: List[Dict[str, Any]], 
                                features: List[ModalityFeature]) -> Dict[str, float]:
        """动态调整各模态权重"""
        weights = self.modality_weights.copy()
        
        # 根据诊断结果质量调整权重
        for diagnosis in diagnosis_results:
            modality = diagnosis.get("type", "").lower()
            confidence = diagnosis.get("confidence", 0.0)
            
            if modality in weights:
                # 高置信度提高权重，低置信度降低权重
                if confidence > 0.8:
                    weights[modality] *= 1.2
                elif confidence < 0.5:
                    weights[modality] *= 0.8
        
        # 确保有足够的特征用于分析
        modality_feature_counts = {}
        for feature in features:
            modality = feature.modality
            modality_feature_counts[modality] = modality_feature_counts.get(modality, 0) + 1
        
        # 缺少特征的模态降低权重
        for modality, count in modality_feature_counts.items():
            if count < 2 and modality in weights:
                weights[modality] *= 0.7
        
        # 规范化权重
        total_weight = sum(weights.values())
        if total_weight > 0:
            for modality in weights:
                weights[modality] /= total_weight
        
        return weights
    
    def _weighted_fusion(self, features: List[ModalityFeature], 
                        modality_weights: Dict[str, float]) -> Dict[str, Any]:
        """基础加权融合算法"""
        # 为每个证候计算得分
        syndrome_scores = self._compute_syndrome_scores(features, modality_weights)
        
        # 过滤低置信度证候
        filtered_syndromes = []
        total_confidence = 0.0
        
        for syndrome in syndrome_scores:
            if syndrome.score >= 0.5:  # 得分阈值
                filtered_syndromes.append({
                    "name": syndrome.name,
                    "score": syndrome.score,
                    "confidence": syndrome.confidence,
                    "supporting_features": [
                        {"name": f.name, "modality": f.modality, "weight": f.weight}
                        for f in syndrome.features[:5]  # 最重要的5个支持特征
                    ]
                })
                total_confidence += syndrome.confidence
        
        # 规范化置信度
        if filtered_syndromes and total_confidence > 0:
            for syndrome in filtered_syndromes:
                syndrome["confidence"] /= total_confidence
        
        # 按得分排序
        filtered_syndromes.sort(key=lambda x: x["score"], reverse=True)
        
        # 计算整体置信度
        overall_confidence = sum(s["confidence"] for s in filtered_syndromes[:3]) / min(3, len(filtered_syndromes)) if filtered_syndromes else 0.0
        
        return {
            "syndromes": filtered_syndromes,
            "confidence": overall_confidence
        }
    
    def _attention_based_fusion(self, features: List[ModalityFeature], 
                               modality_weights: Dict[str, float]) -> Dict[str, Any]:
        """基于注意力机制的融合算法"""
        # 计算每个特征的注意力权重
        feature_attention = self._compute_feature_attention(features)
        
        # 应用注意力权重
        for feature in features:
            feature.weight *= feature_attention.get(feature.name, 1.0)
        
        # 使用加权后的特征进行融合
        weighted_result = self._weighted_fusion(features, modality_weights)
        
        # 增强置信度计算
        if weighted_result["syndromes"]:
            coherence_score = self._compute_syndrome_coherence(weighted_result["syndromes"])
            weighted_result["confidence"] = (weighted_result["confidence"] + coherence_score) / 2
        
        return weighted_result
    
    def _compute_feature_attention(self, features: List[ModalityFeature]) -> Dict[str, float]:
        """计算特征的注意力权重"""
        attention_weights = {}
        
        # 基于特征重要性和稀有性计算注意力
        feature_counts = {}
        for feature in features:
            feature_counts[feature.name] = feature_counts.get(feature.name, 0) + 1
        
        # 特征稀有性
        max_count = max(feature_counts.values()) if feature_counts else 1
        
        for feature in features:
            # 基础注意力 = 置信度 * (1 + 稀有度)
            rarity = 1.0 - (feature_counts[feature.name] / max_count) * 0.5
            attention = feature.confidence * (1.0 + rarity)
            
            # 关键特征加权
            if self._is_key_feature(feature.name):
                attention *= 1.5
            
            attention_weights[feature.name] = attention
        
        # 规范化
        total_attention = sum(attention_weights.values())
        if total_attention > 0:
            for name in attention_weights:
                attention_weights[name] /= total_attention
                attention_weights[name] = 0.5 + attention_weights[name]  # 权重范围调整到0.5-1.5
        
        return attention_weights
    
    def _is_key_feature(self, feature_name: str) -> bool:
        """判断是否为关键特征"""
        # 这里可以接入知识库判断
        # 临时解决方案，关键特征列表
        key_features = [
            "舌淡红", "舌红", "舌淡白", "舌苔黄腻", "舌苔白腻", 
            "脉浮", "脉沉", "脉弦", "脉细", "脉数",
            "胸闷", "心悸", "失眠", "乏力", "腰膝酸软"
        ]
        return feature_name in key_features
    
    def _compute_syndrome_coherence(self, syndromes: List[Dict]) -> float:
        """计算证候间的一致性"""
        if len(syndromes) < 2:
            return 1.0  # 只有一个证候，一致性最高
        
        # 计算前两个证候的相关性
        top1 = syndromes[0]["name"]
        top2 = syndromes[1]["name"]
        
        # 证候相关性对照表（实际应从知识库加载）
        coherent_pairs = [
            ("脾胃湿热", "肝郁气滞"),
            ("心脾两虚", "气血两虚"),
            ("肺阴虚", "肾阳虚")
        ]
        
        # 检查前两个证候是否具有相关性
        for pair in coherent_pairs:
            if (top1 in pair and top2 in pair):
                return 0.9  # 高度相关
        
        # 计算得分差距
        score_ratio = syndromes[1]["score"] / syndromes[0]["score"] if syndromes[0]["score"] > 0 else 0
        
        # 一致性评分：若第二高证候得分远低于第一高，则一致性高
        if score_ratio < 0.5:  # 得分差距大
            return 0.95
        elif score_ratio < 0.8:  # 得分差距中等
            return 0.8
        else:  # 得分接近，可能存在不确定性
            return 0.7
    
    def _ensemble_fusion(self, features: List[ModalityFeature], 
                        modality_weights: Dict[str, float]) -> Dict[str, Any]:
        """集成融合算法，结合多种融合方法"""
        # 基础加权融合
        weighted_result = self._weighted_fusion(features, modality_weights)
        
        # 按模态独立分析
        modality_results = self._analyze_by_modality(features)
        
        # 集成多个融合结果
        ensemble_syndromes = self._ensemble_syndrome_results(
            weighted_result["syndromes"], 
            modality_results
        )
        
        # 计算整体置信度
        if ensemble_syndromes:
            overall_confidence = sum(s["confidence"] for s in ensemble_syndromes[:3]) / min(3, len(ensemble_syndromes))
        else:
            overall_confidence = 0.0
        
        return {
            "syndromes": ensemble_syndromes,
            "confidence": overall_confidence
        }
    
    def _analyze_by_modality(self, features: List[ModalityFeature]) -> Dict[str, List[Dict]]:
        """按模态独立分析"""
        modality_features = {}
        
        # 按模态分组特征
        for feature in features:
            if feature.modality not in modality_features:
                modality_features[feature.modality] = []
            modality_features[feature.modality].append(feature)
        
        # 每个模态独立计算证候得分
        modality_results = {}
        for modality, mod_features in modality_features.items():
            mod_weights = {m: 1.0 if m == modality else 0.1 for m in self.modality_weights}
            result = self._weighted_fusion(mod_features, mod_weights)
            modality_results[modality] = result["syndromes"]
        
        return modality_results
    
    def _ensemble_syndrome_results(self, weighted_syndromes: List[Dict], 
                                 modality_results: Dict[str, List[Dict]]) -> List[Dict]:
        """集成多个结果中的证候"""
        # 所有出现的证候
        all_syndromes = {}
        
        # 添加加权融合结果
        for syndrome in weighted_syndromes:
            all_syndromes[syndrome["name"]] = {
                "name": syndrome["name"],
                "score": syndrome["score"] * 2,  # 加权融合结果权重更高
                "confidence": syndrome["confidence"],
                "votes": 1,
                "supporting_features": syndrome.get("supporting_features", [])
            }
        
        # 添加各模态结果
        for modality, syndromes in modality_results.items():
            for syndrome in syndromes:
                if syndrome["name"] in all_syndromes:
                    # 更新已有证候
                    s = all_syndromes[syndrome["name"]]
                    s["score"] += syndrome["score"]
                    s["confidence"] = max(s["confidence"], syndrome["confidence"])
                    s["votes"] += 1
                else:
                    # 添加新证候
                    all_syndromes[syndrome["name"]] = {
                        "name": syndrome["name"],
                        "score": syndrome["score"],
                        "confidence": syndrome["confidence"],
                        "votes": 1,
                        "supporting_features": syndrome.get("supporting_features", [])
                    }
        
        # 规范化得分和置信度
        ensemble_syndromes = list(all_syndromes.values())
        
        # 根据得票数和得分排序
        for s in ensemble_syndromes:
            s["score"] = s["score"] * (1 + 0.2 * min(s["votes"], 3))
            del s["votes"]  # 移除中间字段
        
        # 排序
        ensemble_syndromes.sort(key=lambda x: x["score"], reverse=True)
        
        return ensemble_syndromes
    
    def _cross_modal_fusion(self, features: List[ModalityFeature], 
                           modality_weights: Dict[str, float]) -> Dict[str, Any]:
        """跨模态融合算法，考虑模态间相关性"""
        # 应用跨模态相关性
        enhanced_features = self._apply_cross_modal_correlation(features)
        
        # 使用增强后的特征进行加权融合
        enhanced_result = self._weighted_fusion(enhanced_features, modality_weights)
        
        # 检测并解决模态冲突
        if enhanced_result["syndromes"]:
            conflict_free_result = self._resolve_modal_conflicts(
                enhanced_result["syndromes"], 
                features
            )
            return conflict_free_result
        
        return enhanced_result
    
    def _apply_cross_modal_correlation(self, features: List[ModalityFeature]) -> List[ModalityFeature]:
        """应用跨模态相关性增强特征权重"""
        enhanced_features = []
        
        # 复制特征列表
        for feature in features:
            enhanced_feature = ModalityFeature(
                name=feature.name,
                value=feature.value,
                confidence=feature.confidence,
                category=feature.category,
                modality=feature.modality,
                weight=feature.weight
            )
            
            # 查找互相支持的跨模态特征
            supporting_features = []
            for other in features:
                if other.modality != feature.modality:
                    # 获取模态间相关性
                    correlation = self.cross_modal_correlation.get(
                        feature.modality, {}).get(other.modality, 0.5)
                    
                    # 检查特征是否支持同一证候
                    if self._features_support_same_syndrome(feature.name, other.name):
                        supporting_features.append((other, correlation))
            
            # 根据支持特征增强权重
            if supporting_features:
                # 跨模态支持的权重调整
                support_weight = sum(corr for _, corr in supporting_features) / len(supporting_features)
                enhanced_feature.weight *= (1.0 + support_weight * 0.5)
            
            enhanced_features.append(enhanced_feature)
        
        return enhanced_features
    
    def _features_support_same_syndrome(self, feature1: str, feature2: str) -> bool:
        """检查两个特征是否支持同一证候"""
        # 遍历证候-特征映射表
        for syndrome, features in self.syndrome_feature_map.items():
            feature_names = [f["name"] for f in features]
            if feature1 in feature_names and feature2 in feature_names:
                return True
        
        return False
    
    def _resolve_modal_conflicts(self, syndromes: List[Dict], 
                               features: List[ModalityFeature]) -> Dict[str, Any]:
        """检测并解决模态冲突"""
        # 检查是否存在模态冲突
        if len(syndromes) < 2:
            return {"syndromes": syndromes, "confidence": syndromes[0]["confidence"] if syndromes else 0.0}
        
        # 获取各模态支持的主要证候
        modality_preferred = {}
        for feature in features:
            for syndrome in syndromes:
                for sup_feature in syndrome.get("supporting_features", []):
                    if sup_feature["name"] == feature.name:
                        if feature.modality not in modality_preferred:
                            modality_preferred[feature.modality] = {}
                        
                        syndrome_name = syndrome["name"]
                        if syndrome_name not in modality_preferred[feature.modality]:
                            modality_preferred[feature.modality][syndrome_name] = 0
                        
                        modality_preferred[feature.modality][syndrome_name] += feature.weight
        
        # 检查是否存在明显冲突
        conflicts = False
        for modality, preferred in modality_preferred.items():
            if preferred and len(preferred) > 0:
                top_syndrome = max(preferred.items(), key=lambda x: x[1])[0]
                if top_syndrome != syndromes[0]["name"]:
                    conflicts = True
                    break
        
        # 处理冲突
        if conflicts:
            # 调整证候顺序和置信度
            resolved_syndromes = syndromes.copy()
            
            # 降低整体置信度
            confidence_penalty = 0.2
            overall_confidence = max(0.0, syndromes[0]["confidence"] - confidence_penalty)
            
            # 标记冲突
            for syndrome in resolved_syndromes:
                syndrome["has_modal_conflicts"] = conflicts
            
            return {
                "syndromes": resolved_syndromes,
                "confidence": overall_confidence,
                "modal_conflicts_detected": True
            }
        
        return {"syndromes": syndromes, "confidence": syndromes[0]["confidence"] if syndromes else 0.0}
    
    def _compute_syndrome_scores(self, features: List[ModalityFeature], 
                               modality_weights: Dict[str, float]) -> List[SyndromeScore]:
        """计算每个证候的得分"""
        syndrome_scores = []
        
        # 为每个证候计算得分
        for syndrome_name, syndrome_features in self.syndrome_feature_map.items():
            matched_features = []
            total_score = 0.0
            confidence_sum = 0.0
            
            # 匹配特征
            for feature in features:
                # 检查该特征是否支持当前证候
                for s_feature in syndrome_features:
                    if feature.name == s_feature["name"]:
                        # 应用模态权重
                        modality_weight = modality_weights.get(feature.modality, 1.0)
                        feature_weight = s_feature.get("weight", 1.0)
                        
                        # 综合权重 = 特征权重 * 模态权重 * 置信度
                        weight = feature_weight * modality_weight * feature.confidence
                        
                        # 保存匹配结果
                        weighted_feature = ModalityFeature(
                            name=feature.name,
                            value=feature.value,
                            confidence=feature.confidence,
                            category=feature.category,
                            modality=feature.modality,
                            weight=weight
                        )
                        
                        matched_features.append(weighted_feature)
                        total_score += weight
                        confidence_sum += feature.confidence
                        break
            
            # 计算证候得分和置信度
            if matched_features:
                # 根据匹配特征数量和证候定义特征数量计算得分
                required_features = len(syndrome_features)
                matched_count = len(matched_features)
                
                # 匹配率影响
                match_ratio = matched_count / required_features
                
                # 最终得分 = 基础得分 * 匹配率
                final_score = total_score * match_ratio
                
                # 置信度 = 平均特征置信度 * 匹配率
                confidence = (confidence_sum / matched_count) * match_ratio if matched_count > 0 else 0.0
                
                # 创建证候得分对象
                syndrome_score = SyndromeScore(
                    name=syndrome_name,
                    score=final_score,
                    features=sorted(matched_features, key=lambda x: x.weight, reverse=True),
                    confidence=confidence,
                    modality_weights=modality_weights.copy()
                )
                
                syndrome_scores.append(syndrome_score)
        
        # 按得分排序
        syndrome_scores.sort(key=lambda x: x.score, reverse=True)
        
        return syndrome_scores 