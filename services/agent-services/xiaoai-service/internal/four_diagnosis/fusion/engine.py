#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""多模态融合引擎实现"""

import logging
import time
import uuid
from typing import Dict, List, Optional, Tuple, Any, Set, Union
from dataclasses import dataclass, field

# 导入Proto定义
from xiaoai_service.protos import four_diagnosis_pb2 as diagnosis_pb

logger = logging.getLogger(__name__)


@dataclass
class Feature:
    """特征"""
    name: str
    value: str
    confidence: float
    source: str
    category: str


@dataclass
class ConflictInfo:
    """冲突信息"""
    feature_name: str
    values: List[Dict[str, Any]]  # [{value, source, confidence}]
    resolved_value: str
    resolution_method: str


@dataclass
class FusionContext:
    """融合上下文"""
    user_id: str
    session_id: str
    diagnosis_results: List[diagnosis_pb.SingleDiagnosisResult]
    features: Dict[str, List[Feature]] = field(default_factory=dict)
    conflicts: List[ConflictInfo] = field(default_factory=list)
    creation_time: int = field(default_factory=lambda: int(time.time()))


class MultimodalFusionEngine:
    """多模态融合引擎"""
    
    def __init__(self, min_confidence_threshold: float = 0.5, use_early_fusion: bool = True):
        """
        初始化多模态融合引擎
        
        Args:
            min_confidence_threshold: 最低置信度阈值，低于此值的特征将被忽略
            use_early_fusion: 是否使用早期融合策略
        """
        self.min_confidence_threshold = min_confidence_threshold
        self.use_early_fusion = use_early_fusion
        
        # 特征权重配置
        self.feature_weights = {
            # 面色特征权重
            "face_color": 0.8,
            "face_region": 0.7,
            
            # 舌象特征权重
            "tongue_color": 0.9,
            "tongue_shape": 0.8,
            "coating_color": 0.85,
            "coating_distribution": 0.8,
            
            # 语音特征权重
            "voice_quality": 0.75,
            "voice_strength": 0.7,
            
            # 脉象特征权重
            "pulse_pattern": 0.9,
            "pulse_strength": 0.85,
            "pulse_rhythm": 0.8,
            
            # 症状特征权重
            "symptom": 0.95,
            "chief_complaint": 1.0,
        }
    
    async def fuse_diagnostic_data(self, 
                                  user_id: str, 
                                  session_id: str, 
                                  diagnosis_results: List[diagnosis_pb.SingleDiagnosisResult]) -> diagnosis_pb.FusionResult:
        """
        融合诊断数据
        
        Args:
            user_id: 用户ID
            session_id: 会话ID
            diagnosis_results: 诊断结果列表
            
        Returns:
            融合结果
        """
        # 创建融合上下文
        fusion_context = FusionContext(
            user_id=user_id,
            session_id=session_id,
            diagnosis_results=diagnosis_results
        )
        
        # 提取所有特征
        self._extract_features(fusion_context)
        
        # 处理特征冲突
        self._resolve_conflicts(fusion_context)
        
        # 执行特征级融合
        fused_features = self._fuse_features(fusion_context)
        
        # 创建融合结果
        fusion_result = diagnosis_pb.FusionResult(
            fusion_id=str(uuid.uuid4()),
            user_id=user_id,
            session_id=session_id,
            created_at=int(time.time()),
        )
        
        # 添加融合特征
        fusion_result.fused_features.CopyFrom(fused_features)
        
        # 计算融合置信度
        fusion_result.fusion_confidence = self._calculate_fusion_confidence(fusion_context)
        
        return fusion_result
    
    def _extract_features(self, context: FusionContext) -> None:
        """
        从诊断结果中提取特征
        
        Args:
            context: 融合上下文
        """
        # 遍历所有诊断结果
        for result in context.diagnosis_results:
            # 遍历所有特征
            for feature_pb in result.features:
                # 跳过低置信度特征
                if feature_pb.confidence < self.min_confidence_threshold:
                    continue
                
                # 创建特征对象
                feature = Feature(
                    name=feature_pb.feature_name,
                    value=feature_pb.feature_value,
                    confidence=feature_pb.confidence,
                    source=feature_pb.source,
                    category=feature_pb.category
                )
                
                # 添加到特征字典中
                if feature.name not in context.features:
                    context.features[feature.name] = []
                
                context.features[feature.name].append(feature)
    
    def _resolve_conflicts(self, context: FusionContext) -> None:
        """
        解决特征冲突
        
        Args:
            context: 融合上下文
        """
        # 遍历所有特征
        for feature_name, features in context.features.items():
            # 如果只有一个特征值，则没有冲突
            if len(features) <= 1:
                continue
            
            # 收集所有不同的特征值
            values = set(feature.value for feature in features)
            
            # 如果有多个不同的特征值，则存在冲突
            if len(values) > 1:
                # 收集所有冲突值的信息
                conflicting_values = []
                for feature in features:
                    conflicting_values.append({
                        "value": feature.value,
                        "source": feature.source,
                        "confidence": feature.confidence
                    })
                
                # 解决冲突
                resolved_value, resolution_method = self._resolve_feature_conflict(feature_name, features)
                
                # 添加到冲突列表
                conflict = ConflictInfo(
                    feature_name=feature_name,
                    values=conflicting_values,
                    resolved_value=resolved_value,
                    resolution_method=resolution_method
                )
                
                context.conflicts.append(conflict)
    
    def _resolve_feature_conflict(self, feature_name: str, features: List[Feature]) -> Tuple[str, str]:
        """
        解决单个特征的冲突
        
        Args:
            feature_name: 特征名称
            features: 冲突的特征列表
            
        Returns:
            解决后的特征值和解决方法
        """
        # 首先尝试通过置信度解决冲突
        if self._can_resolve_by_confidence(features):
            # 选择置信度最高的特征
            best_feature = max(features, key=lambda f: f.confidence)
            return best_feature.value, "confidence_based"
        
        # 尝试通过多数投票解决冲突
        if self._can_resolve_by_majority(features):
            # 统计各个值的出现次数
            value_counts = {}
            for feature in features:
                if feature.value not in value_counts:
                    value_counts[feature.value] = 0
                value_counts[feature.value] += 1
            
            # 选择出现次数最多的值
            majority_value = max(value_counts.keys(), key=lambda k: value_counts[k])
            return majority_value, "majority_vote"
        
        # 尝试通过源优先级解决冲突
        if self._can_resolve_by_source_priority(features):
            # 源优先级: 问诊 > 切诊 > 望诊 > 闻诊
            priority_map = {
                "inquiry_service": 4,
                "palpation_service": 3,
                "look_service": 2,
                "listen_service": 1
            }
            
            # 选择优先级最高的源
            best_feature = max(features, key=lambda f: priority_map.get(f.source, 0))
            return best_feature.value, "source_priority"
        
        # 如果都无法解决，使用加权投票
        return self._resolve_by_weighted_vote(feature_name, features), "weighted_vote"
    
    def _can_resolve_by_confidence(self, features: List[Feature]) -> bool:
        """
        判断是否可以通过置信度解决冲突
        
        Args:
            features: 特征列表
            
        Returns:
            是否可以通过置信度解决
        """
        # 获取最高置信度
        max_confidence = max(feature.confidence for feature in features)
        
        # 获取具有最高置信度的特征数量
        max_confidence_count = sum(1 for feature in features if feature.confidence == max_confidence)
        
        # 如果只有一个特征具有最高置信度，则可以解决
        return max_confidence_count == 1
    
    def _can_resolve_by_majority(self, features: List[Feature]) -> bool:
        """
        判断是否可以通过多数投票解决冲突
        
        Args:
            features: 特征列表
            
        Returns:
            是否可以通过多数投票解决
        """
        # 统计各个值的出现次数
        value_counts = {}
        for feature in features:
            if feature.value not in value_counts:
                value_counts[feature.value] = 0
            value_counts[feature.value] += 1
        
        # 获取最高出现次数
        max_count = max(value_counts.values())
        
        # 获取具有最高出现次数的值的数量
        max_count_values = sum(1 for count in value_counts.values() if count == max_count)
        
        # 如果只有一个值具有最高出现次数，则可以解决
        return max_count_values == 1
    
    def _can_resolve_by_source_priority(self, features: List[Feature]) -> bool:
        """
        判断是否可以通过源优先级解决冲突
        
        Args:
            features: 特征列表
            
        Returns:
            是否可以通过源优先级解决
        """
        # 源优先级: 问诊 > 切诊 > 望诊 > 闻诊
        priority_map = {
            "inquiry_service": 4,
            "palpation_service": 3,
            "look_service": 2,
            "listen_service": 1
        }
        
        # 获取最高优先级
        max_priority = max(priority_map.get(feature.source, 0) for feature in features)
        
        # 获取具有最高优先级的源的数量
        max_priority_count = sum(1 for feature in features if priority_map.get(feature.source, 0) == max_priority)
        
        # 如果只有一个源具有最高优先级，则可以解决
        return max_priority_count == 1
    
    def _resolve_by_weighted_vote(self, feature_name: str, features: List[Feature]) -> str:
        """
        通过加权投票解决冲突
        
        Args:
            feature_name: 特征名称
            features: 特征列表
            
        Returns:
            解决后的特征值
        """
        # 获取特征类别
        category = features[0].category if features else ""
        
        # 获取特征权重
        weight_key = category if category in self.feature_weights else feature_name
        weight = self.feature_weights.get(weight_key, 0.5)
        
        # 加权投票
        value_scores = {}
        for feature in features:
            if feature.value not in value_scores:
                value_scores[feature.value] = 0
            
            # 计算加权分数：源权重 * 特征权重 * 置信度
            source_weight = 1.0
            if feature.source == "inquiry_service":
                source_weight = 1.2
            elif feature.source == "palpation_service":
                source_weight = 1.1
            elif feature.source == "look_service":
                source_weight = 1.0
            elif feature.source == "listen_service":
                source_weight = 0.9
            
            score = source_weight * weight * feature.confidence
            value_scores[feature.value] += score
        
        # 选择得分最高的值
        best_value = max(value_scores.keys(), key=lambda k: value_scores[k])
        return best_value
    
    def _fuse_features(self, context: FusionContext) -> diagnosis_pb.FusedFeatures:
        """
        执行特征级融合
        
        Args:
            context: 融合上下文
            
        Returns:
            融合的特征
        """
        fused_features = diagnosis_pb.FusedFeatures()
        
        # 遍历所有特征
        for feature_name, features in context.features.items():
            # 如果没有特征，则跳过
            if not features:
                continue
            
            # 获取特征值，如果有冲突，则使用冲突解决结果
            value = features[0].value
            for conflict in context.conflicts:
                if conflict.feature_name == feature_name:
                    value = conflict.resolved_value
                    break
            
            # 计算特征的置信度
            confidence = self._calculate_feature_confidence(features)
            
            # 创建诊断特征
            diag_feature = diagnosis_pb.DiagnosticFeature(
                feature_name=feature_name,
                feature_value=value,
                confidence=confidence,
                source=",".join(set(feature.source for feature in features)),
                category=features[0].category
            )
            
            # 添加到融合特征中
            fused_features.features.append(diag_feature)
        
        # 添加冲突解决信息
        for conflict in context.conflicts:
            conflict_resolution = diagnosis_pb.ConflictResolution(
                feature_name=conflict.feature_name,
                resolved_value=conflict.resolved_value,
                resolution_method=conflict.resolution_method
            )
            
            for value_info in conflict.values:
                conflict_resolution.values.append(diagnosis_pb.ConflictingValue(
                    value=value_info["value"],
                    source=value_info["source"],
                    confidence=value_info["confidence"]
                ))
            
            fused_features.conflicts.append(conflict_resolution)
        
        return fused_features
    
    def _calculate_feature_confidence(self, features: List[Feature]) -> float:
        """
        计算特征置信度
        
        Args:
            features: 特征列表
            
        Returns:
            计算后的置信度
        """
        # 如果没有特征，返回0
        if not features:
            return 0.0
        
        # 如果只有一个特征，直接返回其置信度
        if len(features) == 1:
            return features[0].confidence
        
        # 如果有多个相同的特征，使用特殊计算方法
        # 基本假设：如果多个源都发现了相同的特征，则置信度应该更高
        total_confidence = sum(feature.confidence for feature in features)
        max_confidence = max(feature.confidence for feature in features)
        
        # 计算加权平均值，偏向于最高置信度
        alpha = 0.7  # 权衡因子
        weighted_confidence = alpha * max_confidence + (1 - alpha) * (total_confidence / len(features))
        
        # 如果所有源都检测到相同的特征，给予额外奖励
        unique_sources = set(feature.source for feature in features)
        source_diversity_factor = min(1.0, len(unique_sources) / 4.0)  # 最多考虑4种不同的源
        
        # 融合置信度 = 加权平均值 * (1 + 源多样性因子 * 0.3)
        # 这样，如果有更多不同的源检测到相同的特征，置信度会更高
        fusion_confidence = weighted_confidence * (1 + source_diversity_factor * 0.3)
        
        # 确保置信度不超过1.0
        return min(fusion_confidence, 1.0)
    
    def _calculate_fusion_confidence(self, context: FusionContext) -> float:
        """
        计算整体融合置信度
        
        Args:
            context: 融合上下文
            
        Returns:
            融合置信度
        """
        # 获取所有特征置信度
        feature_confidences = []
        for features in context.features.values():
            confidence = self._calculate_feature_confidence(features)
            feature_confidences.append(confidence)
        
        # 如果没有特征，返回0
        if not feature_confidences:
            return 0.0
        
        # 计算平均置信度
        avg_confidence = sum(feature_confidences) / len(feature_confidences)
        
        # 计算冲突率
        conflict_rate = len(context.conflicts) / len(context.features) if context.features else 0
        
        # 冲突率越高，置信度越低
        fusion_confidence = avg_confidence * (1 - conflict_rate * 0.5)
        
        return fusion_confidence
    
    async def apply_early_fusion(self, fusion_context: FusionContext) -> diagnosis_pb.FusionResult:
        """
        应用早期融合策略
        
        Args:
            fusion_context: 融合上下文
            
        Returns:
            融合结果
        """
        # 基于原始特征进行早期融合
        # 将不同模态的特征投影到共同的特征空间
        # 然后基于这些特征进行分类或回归
        
        # 注意：这个方法需要结合具体的特征投影和分类/回归模型实现
        # 这里只是一个架构占位符
        
        pass
    
    async def apply_late_fusion(self, fusion_context: FusionContext) -> diagnosis_pb.FusionResult:
        """
        应用晚期融合策略
        
        Args:
            fusion_context: 融合上下文
            
        Returns:
            融合结果
        """
        # 基于各个模态的决策进行晚期融合
        # 将不同模态的决策结果进行加权组合
        
        # 注意：这个方法需要结合具体的决策融合模型实现
        # 这里只是一个架构占位符
        
        pass