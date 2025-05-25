#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
腹诊分析器
负责分析腹部触诊数据，评估腹部各区域状态
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

from internal.model.palpation_models import (
    AbdominalRegion, AbdominalRegionData, AbdominalFinding,
    TendernessLevel, TensionLevel
)


class AbdominalAnalyzer:
    """腹诊分析器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化腹诊分析器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.regions_config = config.get('regions', [])
        self.assessment_criteria = config.get('assessment_criteria', {})
        self.logger = logging.getLogger(__name__)
        
        # 建立区域与经络的映射关系
        self._init_region_meridian_mapping()
        
    def _init_region_meridian_mapping(self):
        """初始化区域与经络的映射关系"""
        self.region_meridian_map = {}
        for region in self.regions_config:
            self.region_meridian_map[region['id']] = region.get('meridians', [])
    
    def analyze_abdominal_regions(self, regions_data: List[AbdominalRegionData]) -> List[AbdominalFinding]:
        """
        分析腹部各区域数据
        
        Args:
            regions_data: 腹部区域数据列表
            
        Returns:
            腹诊发现列表
        """
        findings = []
        
        for region_data in regions_data:
            # 分析单个区域
            region_findings = self._analyze_single_region(region_data)
            findings.extend(region_findings)
        
        # 综合分析各区域关联
        correlation_findings = self._analyze_region_correlations(regions_data)
        findings.extend(correlation_findings)
        
        return findings
    
    def _analyze_single_region(self, region_data: AbdominalRegionData) -> List[AbdominalFinding]:
        """分析单个腹部区域"""
        findings = []
        
        # 分析压痛
        if region_data.tenderness_level != TendernessLevel.NONE:
            finding = self._analyze_tenderness(region_data)
            if finding:
                findings.append(finding)
        
        # 分析紧张度
        if region_data.tension_level != TensionLevel.NORMAL:
            finding = self._analyze_tension(region_data)
            if finding:
                findings.append(finding)
        
        # 分析肿块
        if region_data.has_mass:
            finding = self._analyze_mass(region_data)
            if finding:
                findings.append(finding)
        
        # 分析搏动
        if region_data.pulsation:
            finding = self._analyze_pulsation(region_data)
            if finding:
                findings.append(finding)
        
        # 分析肠鸣音
        if region_data.gurgling:
            finding = self._analyze_gurgling(region_data)
            if finding:
                findings.append(finding)
        
        return findings
    
    def _analyze_tenderness(self, region_data: AbdominalRegionData) -> Optional[AbdominalFinding]:
        """分析压痛"""
        severity_map = {
            TendernessLevel.MILD: 0.3,
            TendernessLevel.MODERATE: 0.6,
            TendernessLevel.SEVERE: 0.9,
            TendernessLevel.REBOUND: 1.0
        }
        
        severity = severity_map.get(region_data.tenderness_level, 0)
        
        # 根据区域和压痛程度推断可能原因
        potential_causes = self._infer_tenderness_causes(
            region_data.region_type, 
            region_data.tenderness_level
        )
        
        # 获取相关经络
        related_meridians = self.region_meridian_map.get(region_data.region_id, [])
        
        # 中医解释
        tcm_interpretation = self._get_tcm_interpretation_for_tenderness(
            region_data.region_type,
            region_data.tenderness_level
        )
        
        return AbdominalFinding(
            region_id=region_data.region_id,
            region_name=region_data.region_name,
            finding_type="压痛",
            description=f"{region_data.region_name}区域{region_data.tenderness_level.value}",
            severity=severity,
            confidence=0.8,
            potential_causes=potential_causes,
            related_meridians=related_meridians,
            tcm_interpretation=tcm_interpretation
        )
    
    def _analyze_tension(self, region_data: AbdominalRegionData) -> Optional[AbdominalFinding]:
        """分析腹部紧张度"""
        severity_map = {
            TensionLevel.RELAXED: 0.2,
            TensionLevel.TENSE: 0.6,
            TensionLevel.RIGID: 0.9
        }
        
        severity = severity_map.get(region_data.tension_level, 0)
        
        # 推断可能原因
        potential_causes = []
        if region_data.tension_level == TensionLevel.RELAXED:
            potential_causes = ["气虚", "脾虚", "中气下陷"]
        elif region_data.tension_level == TensionLevel.TENSE:
            potential_causes = ["气滞", "寒凝", "情志不畅"]
        elif region_data.tension_level == TensionLevel.RIGID:
            potential_causes = ["实证", "热结", "瘀血"]
        
        # 中医解释
        tcm_interpretation = self._get_tcm_interpretation_for_tension(
            region_data.region_type,
            region_data.tension_level
        )
        
        return AbdominalFinding(
            region_id=region_data.region_id,
            region_name=region_data.region_name,
            finding_type="腹部紧张度异常",
            description=f"{region_data.region_name}区域腹肌{region_data.tension_level.value}",
            severity=severity,
            confidence=0.75,
            potential_causes=potential_causes,
            related_meridians=self.region_meridian_map.get(region_data.region_id, []),
            tcm_interpretation=tcm_interpretation
        )
    
    def _analyze_mass(self, region_data: AbdominalRegionData) -> Optional[AbdominalFinding]:
        """分析腹部肿块"""
        # 根据区域推断可能的肿块性质
        potential_causes = self._infer_mass_causes(region_data.region_type)
        
        description = f"{region_data.region_name}区域触及肿块"
        if region_data.mass_description:
            description += f"，{region_data.mass_description}"
        
        return AbdominalFinding(
            region_id=region_data.region_id,
            region_name=region_data.region_name,
            finding_type="肿块",
            description=description,
            severity=0.8,  # 肿块通常需要重视
            confidence=0.9,
            potential_causes=potential_causes,
            related_meridians=self.region_meridian_map.get(region_data.region_id, []),
            tcm_interpretation="痰湿凝聚或瘀血阻滞，需进一步辨证"
        )
    
    def _analyze_pulsation(self, region_data: AbdominalRegionData) -> Optional[AbdominalFinding]:
        """分析腹部搏动"""
        # 不同区域的搏动有不同意义
        if region_data.region_type == AbdominalRegion.EPIGASTRIC:
            description = "上腹部搏动明显"
            potential_causes = ["胃气上逆", "心下悸", "水饮内停"]
            tcm_interpretation = "可能为水饮凌心或胃气不降"
        elif region_data.region_type == AbdominalRegion.UMBILICAL:
            description = "脐部搏动明显"
            potential_causes = ["肾气不固", "冲脉失调", "气血不足"]
            tcm_interpretation = "可能为肾气虚弱或冲脉失调"
        else:
            description = f"{region_data.region_name}区域搏动"
            potential_causes = ["局部气血不畅"]
            tcm_interpretation = "局部气血运行异常"
        
        return AbdominalFinding(
            region_id=region_data.region_id,
            region_name=region_data.region_name,
            finding_type="搏动",
            description=description,
            severity=0.5,
            confidence=0.7,
            potential_causes=potential_causes,
            related_meridians=self.region_meridian_map.get(region_data.region_id, []),
            tcm_interpretation=tcm_interpretation
        )
    
    def _analyze_gurgling(self, region_data: AbdominalRegionData) -> Optional[AbdominalFinding]:
        """分析肠鸣音"""
        description = f"{region_data.region_name}区域肠鸣音活跃"
        
        # 根据区域判断可能原因
        if region_data.region_type in [AbdominalRegion.UMBILICAL, AbdominalRegion.HYPOGASTRIC]:
            potential_causes = ["脾虚", "寒湿", "食积", "肠道功能紊乱"]
            tcm_interpretation = "脾胃虚寒或食积内停"
        else:
            potential_causes = ["局部气机不畅"]
            tcm_interpretation = "局部气机运行不畅"
        
        return AbdominalFinding(
            region_id=region_data.region_id,
            region_name=region_data.region_name,
            finding_type="肠鸣音异常",
            description=description,
            severity=0.3,
            confidence=0.8,
            potential_causes=potential_causes,
            related_meridians=self.region_meridian_map.get(region_data.region_id, []),
            tcm_interpretation=tcm_interpretation
        )
    
    def _analyze_region_correlations(self, regions_data: List[AbdominalRegionData]) -> List[AbdominalFinding]:
        """分析各区域之间的关联"""
        findings = []
        
        # 检查是否有多个区域都有压痛
        tender_regions = [r for r in regions_data if r.tenderness_level != TendernessLevel.NONE]
        if len(tender_regions) >= 3:
            finding = AbdominalFinding(
                region_id="multiple",
                region_name="多区域",
                finding_type="广泛压痛",
                description="腹部多个区域存在压痛，提示全身性问题",
                severity=0.8,
                confidence=0.85,
                potential_causes=["气滞血瘀", "湿热蕴结", "脏腑功能失调"],
                related_meridians=["脾经", "胃经", "肝经"],
                tcm_interpretation="可能存在全身性的气滞血瘀或湿热蕴结"
            )
            findings.append(finding)
        
        # 检查左右对称性
        left_regions = [r for r in regions_data if "左" in r.region_name]
        right_regions = [r for r in regions_data if "右" in r.region_name]
        
        if self._check_asymmetry(left_regions, right_regions):
            finding = AbdominalFinding(
                region_id="asymmetry",
                region_name="左右不对称",
                finding_type="不对称性发现",
                description="腹部左右两侧触诊发现不对称",
                severity=0.6,
                confidence=0.7,
                potential_causes=["单侧脏腑病变", "经络阻滞"],
                related_meridians=["任脉", "冲脉"],
                tcm_interpretation="可能存在单侧经络阻滞或脏腑偏颇"
            )
            findings.append(finding)
        
        return findings
    
    def _check_asymmetry(self, left_regions: List[AbdominalRegionData], 
                        right_regions: List[AbdominalRegionData]) -> bool:
        """检查左右是否不对称"""
        if not left_regions or not right_regions:
            return False
        
        # 简单比较左右两侧的压痛和紧张度
        left_tenderness = sum(1 for r in left_regions if r.tenderness_level != TendernessLevel.NONE)
        right_tenderness = sum(1 for r in right_regions if r.tenderness_level != TendernessLevel.NONE)
        
        left_tension = sum(1 for r in left_regions if r.tension_level != TensionLevel.NORMAL)
        right_tension = sum(1 for r in right_regions if r.tension_level != TensionLevel.NORMAL)
        
        return abs(left_tenderness - right_tenderness) >= 2 or abs(left_tension - right_tension) >= 2
    
    def _infer_tenderness_causes(self, region: AbdominalRegion, 
                                level: TendernessLevel) -> List[str]:
        """根据区域和压痛程度推断可能原因"""
        causes_map = {
            AbdominalRegion.EPIGASTRIC: {
                TendernessLevel.MILD: ["胃气不和", "食积"],
                TendernessLevel.MODERATE: ["胃热", "肝胃不和"],
                TendernessLevel.SEVERE: ["胃脘痛", "急性胃炎"]
            },
            AbdominalRegion.UMBILICAL: {
                TendernessLevel.MILD: ["脾虚", "寒湿"],
                TendernessLevel.MODERATE: ["脾胃不和", "肠道积滞"],
                TendernessLevel.SEVERE: ["肠痈", "腹部炎症"]
            },
            AbdominalRegion.HYPOGASTRIC: {
                TendernessLevel.MILD: ["膀胱虚寒", "肾气不足"],
                TendernessLevel.MODERATE: ["下焦湿热", "瘀血"],
                TendernessLevel.SEVERE: ["膀胱炎", "盆腔炎症"]
            },
            AbdominalRegion.RIGHT_HYPOCHONDRIUM: {
                TendernessLevel.MILD: ["肝气郁结", "胆气不利"],
                TendernessLevel.MODERATE: ["肝胆湿热", "气滞"],
                TendernessLevel.SEVERE: ["胆囊炎", "肝区病变"]
            },
            AbdominalRegion.LEFT_HYPOCHONDRIUM: {
                TendernessLevel.MILD: ["脾虚", "气滞"],
                TendernessLevel.MODERATE: ["脾胃不和", "痰湿"],
                TendernessLevel.SEVERE: ["脾脏肿大", "胰腺问题"]
            }
        }
        
        region_causes = causes_map.get(region, {})
        return region_causes.get(level, ["需进一步辨证"])
    
    def _infer_mass_causes(self, region: AbdominalRegion) -> List[str]:
        """根据区域推断肿块可能原因"""
        mass_causes_map = {
            AbdominalRegion.EPIGASTRIC: ["胃部肿物", "肝左叶肿大", "胰腺肿物"],
            AbdominalRegion.UMBILICAL: ["肠道肿物", "腹腔肿物", "淋巴结肿大"],
            AbdominalRegion.HYPOGASTRIC: ["膀胱充盈", "子宫肌瘤", "卵巢囊肿"],
            AbdominalRegion.RIGHT_HYPOCHONDRIUM: ["肝脏肿大", "胆囊肿大"],
            AbdominalRegion.LEFT_HYPOCHONDRIUM: ["脾脏肿大", "胰尾肿物"],
            AbdominalRegion.RIGHT_ILIAC: ["阑尾肿物", "盲肠肿物", "卵巢肿物"],
            AbdominalRegion.LEFT_ILIAC: ["乙状结肠肿物", "卵巢肿物"]
        }
        
        return mass_causes_map.get(region, ["不明原因肿块"])
    
    def _get_tcm_interpretation_for_tenderness(self, region: AbdominalRegion, 
                                             level: TendernessLevel) -> str:
        """获取压痛的中医解释"""
        if level == TendernessLevel.MILD:
            return "轻度压痛多为虚证或气滞初起"
        elif level == TendernessLevel.MODERATE:
            return "中度压痛提示气滞血瘀或湿热蕴结"
        elif level == TendernessLevel.SEVERE:
            return "重度压痛多为实证、热证或瘀血重证"
        elif level == TendernessLevel.REBOUND:
            return "反跳痛提示腹腔炎症，属急症范畴"
        
        return "需结合其他症状辨证"
    
    def _get_tcm_interpretation_for_tension(self, region: AbdominalRegion, 
                                          level: TensionLevel) -> str:
        """获取腹部紧张度的中医解释"""
        if level == TensionLevel.RELAXED:
            return "腹部松软多为虚证，提示脾胃虚弱或中气不足"
        elif level == TensionLevel.TENSE:
            return "腹部紧张多为实证，提示气滞、寒凝或情志不畅"
        elif level == TensionLevel.RIGID:
            return "腹部板状多为急症，提示热结、瘀血或腹腔急性炎症"
        
        return "正常腹部张力"
    
    def generate_summary(self, findings: List[AbdominalFinding]) -> str:
        """
        生成腹诊分析总结
        
        Args:
            findings: 腹诊发现列表
            
        Returns:
            分析总结文本
        """
        if not findings:
            return "腹诊检查未发现明显异常"
        
        # 按严重程度排序
        findings.sort(key=lambda x: x.severity, reverse=True)
        
        # 统计各类发现
        finding_types = {}
        for finding in findings:
            finding_type = finding.finding_type
            if finding_type not in finding_types:
                finding_types[finding_type] = []
            finding_types[finding_type].append(finding)
        
        # 生成总结
        summary_parts = []
        
        # 最严重的发现
        most_severe = findings[0]
        summary_parts.append(f"腹诊检查发现最显著的问题是{most_severe.region_name}{most_severe.finding_type}")
        
        # 各类发现统计
        if len(finding_types) > 1:
            summary_parts.append(f"共发现{len(finding_types)}类异常：")
            for ftype, items in finding_types.items():
                regions = [item.region_name for item in items]
                summary_parts.append(f"- {ftype}：{', '.join(regions)}")
        
        # 中医证候归纳
        tcm_patterns = set()
        for finding in findings:
            for cause in finding.potential_causes:
                if any(pattern in cause for pattern in ["气滞", "血瘀", "湿热", "虚", "寒"]):
                    tcm_patterns.add(cause)
        
        if tcm_patterns:
            summary_parts.append(f"中医辨证提示可能存在：{', '.join(tcm_patterns)}")
        
        # 建议
        if most_severe.severity > 0.7:
            summary_parts.append("建议进一步检查明确诊断")
        
        return "。".join(summary_parts) 