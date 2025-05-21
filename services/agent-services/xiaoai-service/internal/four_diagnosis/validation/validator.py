#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""诊断结果验证器实现"""

import logging
from typing import Dict, List, Optional, Tuple, Any, Set

# 导入Proto定义
from xiaoai_service.protos import four_diagnosis_pb2 as diagnosis_pb

logger = logging.getLogger(__name__)


class DiagnosticValidator:
    """诊断结果验证器"""
    
    def __init__(self, 
                min_confidence_threshold: float = 0.5,
                min_features_count: int = 3,
                min_diagnostic_services: int = 2):
        """
        初始化诊断结果验证器
        
        Args:
            min_confidence_threshold: 最低置信度阈值
            min_features_count: 最少特征数量
            min_diagnostic_services: 最少诊断服务数量
        """
        self.min_confidence_threshold = min_confidence_threshold
        self.min_features_count = min_features_count
        self.min_diagnostic_services = min_diagnostic_services
        
        # 不兼容辨证关系字典
        self.incompatible_syndromes = {
            "肝阳上亢": ["肝血不足", "肝郁气滞"],
            "肝郁气滞": ["肝阳上亢"],
            "肝血不足": ["肝阳上亢"],
            "脾气虚弱": ["脾阳不足"],
            "脾阳不足": ["脾气虚弱"],
            "肾阳不足": ["肾阴不足"],
            "肾阴不足": ["肾阳不足"],
            "心血不足": ["心阴不足"],
            "心阴不足": ["心血不足"]
        }
        
        # 不兼容体质关系字典
        self.incompatible_constitutions = {
            "平和质": ["气虚质", "阳虚质", "阴虚质", "痰湿质", "湿热质", "血瘀质", "气郁质", "特禀质"],
            "阳虚质": ["阴虚质", "湿热质"],
            "阴虚质": ["阳虚质", "痰湿质"],
            "气虚质": ["气郁质"]
        }
    
    def validate_diagnostic_report(self, report: diagnosis_pb.DiagnosisReport) -> Tuple[bool, str, List[str]]:
        """
        验证诊断报告
        
        Args:
            report: 诊断报告
            
        Returns:
            验证结果、验证消息、问题列表
        """
        problems = []
        
        # 检查诊断服务覆盖度
        diagnostic_services_count = sum([
            1 if report.HasField('look_result') else 0,
            1 if report.HasField('listen_result') else 0,
            1 if report.HasField('inquiry_result') else 0,
            1 if report.HasField('palpation_result') else 0
        ])
        
        if diagnostic_services_count < self.min_diagnostic_services:
            problems.append(f"诊断服务覆盖不足，当前：{diagnostic_services_count}，要求至少：{self.min_diagnostic_services}")
        
        # 检查整体置信度
        if report.overall_confidence < self.min_confidence_threshold:
            problems.append(f"整体置信度不足，当前：{report.overall_confidence}，要求至少：{self.min_confidence_threshold}")
        
        # 检查辨证结果
        if report.HasField('syndrome_analysis'):
            syndrome_valid, syndrome_problems = self._validate_syndrome_analysis(report.syndrome_analysis)
            problems.extend(syndrome_problems)
        
        # 检查体质结果
        if report.HasField('constitution_analysis'):
            constitution_valid, constitution_problems = self._validate_constitution_analysis(report.constitution_analysis)
            problems.extend(constitution_problems)
        
        # 检查治疗建议
        if len(report.recommendations) > 0:
            recommendations_valid, recommendations_problems = self._validate_recommendations(report.recommendations)
            problems.extend(recommendations_problems)
        
        # 返回验证结果
        valid = len(problems) == 0
        message = "诊断报告验证通过" if valid else "诊断报告存在问题"
        
        return valid, message, problems
    
    def _validate_syndrome_analysis(self, syndrome_analysis: diagnosis_pb.SyndromeAnalysisResult) -> Tuple[bool, List[str]]:
        """
        验证辨证分析结果
        
        Args:
            syndrome_analysis: 辨证分析结果
            
        Returns:
            验证结果、问题列表
        """
        problems = []
        
        # 检查辨证数量
        if not syndrome_analysis.syndromes:
            problems.append("辨证结果为空")
            return False, problems
        
        # 检查辨证置信度
        if syndrome_analysis.overall_confidence < self.min_confidence_threshold:
            problems.append(f"辨证置信度不足，当前：{syndrome_analysis.overall_confidence}，要求至少：{self.min_confidence_threshold}")
        
        # 检查辨证兼容性
        syndromes = [s.syndrome_name for s in syndrome_analysis.syndromes]
        incompatible_pairs = self._check_incompatible_items(syndromes, self.incompatible_syndromes)
        
        for pair in incompatible_pairs:
            problems.append(f"不兼容的辨证组合：{pair[0]}和{pair[1]}")
        
        # 返回验证结果
        valid = len(problems) == 0
        
        return valid, problems
    
    def _validate_constitution_analysis(self, constitution_analysis: diagnosis_pb.ConstitutionAnalysisResult) -> Tuple[bool, List[str]]:
        """
        验证体质分析结果
        
        Args:
            constitution_analysis: 体质分析结果
            
        Returns:
            验证结果、问题列表
        """
        problems = []
        
        # 检查体质数量
        if not constitution_analysis.constitutions:
            problems.append("体质结果为空")
            return False, problems
        
        # 检查体质置信度
        if constitution_analysis.overall_confidence < self.min_confidence_threshold:
            problems.append(f"体质置信度不足，当前：{constitution_analysis.overall_confidence}，要求至少：{self.min_confidence_threshold}")
        
        # 检查体质兼容性
        constitutions = [c.constitution_name for c in constitution_analysis.constitutions]
        incompatible_pairs = self._check_incompatible_items(constitutions, self.incompatible_constitutions)
        
        for pair in incompatible_pairs:
            problems.append(f"不兼容的体质组合：{pair[0]}和{pair[1]}")
        
        # 如果是平和质，不应该有其他体质
        if "平和质" in constitutions and len(constitutions) > 1:
            problems.append("平和质不应与其他体质并存")
        
        # 返回验证结果
        valid = len(problems) == 0
        
        return valid, problems
    
    def _validate_recommendations(self, recommendations: List[diagnosis_pb.RecommendationItem]) -> Tuple[bool, List[str]]:
        """
        验证治疗建议
        
        Args:
            recommendations: 治疗建议列表
            
        Returns:
            验证结果、问题列表
        """
        problems = []
        
        # 检查建议数量
        if not recommendations:
            problems.append("治疗建议为空")
            return False, problems
        
        # 检查建议类型覆盖
        recommendation_types = set(r.type for r in recommendations)
        expected_types = {
            diagnosis_pb.RecommendationItem.RecommendationType.DIET, 
            diagnosis_pb.RecommendationItem.RecommendationType.EXERCISE,
            diagnosis_pb.RecommendationItem.RecommendationType.LIFESTYLE
        }
        
        missing_types = expected_types - recommendation_types
        if missing_types:
            missing_type_names = [str(t) for t in missing_types]
            problems.append(f"缺少建议类型：{', '.join(missing_type_names)}")
        
        # 检查建议内容
        for rec in recommendations:
            if not rec.content:
                problems.append(f"建议内容为空：{rec.type}")
            
            if not rec.rationale:
                problems.append(f"建议依据为空：{rec.type}")
            
            if not rec.target_issue:
                problems.append(f"建议目标问题为空：{rec.type}")
        
        # 返回验证结果
        valid = len(problems) == 0
        
        return valid, problems
    
    def _check_incompatible_items(self, items: List[str], incompatible_dict: Dict[str, List[str]]) -> List[Tuple[str, str]]:
        """
        检查不兼容项
        
        Args:
            items: 项目列表
            incompatible_dict: 不兼容关系字典
            
        Returns:
            不兼容对列表
        """
        incompatible_pairs = []
        
        for i, item1 in enumerate(items):
            if item1 in incompatible_dict:
                for item2 in items[i+1:]:
                    if item2 in incompatible_dict[item1]:
                        incompatible_pairs.append((item1, item2))
        
        return incompatible_pairs 