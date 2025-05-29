#!/usr/bin/env python

"""
皮肤触诊分析器
负责分析皮肤触诊数据，评估皮肤各项指标
"""

import logging
from typing import Any

from internal.model.palpation_models import (
    SkinElasticityLevel,
    SkinFinding,
    SkinMoistureLevel,
    SkinRegionData,
    SkinTemperatureLevel,
    SkinTexture,
)


class SkinAnalyzer:
    """皮肤触诊分析器"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化皮肤分析器

        Args:
            config: 配置字典
        """
        self.config = config
        self.parameters = config.get("parameters", {})
        self.texture_mapping = config.get("texture_mapping", {})
        self.logger = logging.getLogger(__name__)

    def analyze_skin_regions(self, regions_data: list[SkinRegionData]) -> list[SkinFinding]:
        """
        分析皮肤各区域数据

        Args:
            regions_data: 皮肤区域数据列表

        Returns:
            皮肤触诊发现列表
        """
        findings = []

        for region_data in regions_data:
            # 分析单个区域
            region_findings = self._analyze_single_region(region_data)
            findings.extend(region_findings)

        # 综合分析各区域模式
        pattern_findings = self._analyze_skin_patterns(regions_data)
        findings.extend(pattern_findings)

        return findings

    def _analyze_single_region(self, region_data: SkinRegionData) -> list[SkinFinding]:
        """分析单个皮肤区域"""
        findings = []

        # 分析湿度
        moisture_finding = self._analyze_moisture(region_data)
        if moisture_finding:
            findings.append(moisture_finding)

        # 分析弹性
        elasticity_finding = self._analyze_elasticity(region_data)
        if elasticity_finding:
            findings.append(elasticity_finding)

        # 分析温度
        temperature_finding = self._analyze_temperature(region_data)
        if temperature_finding:
            findings.append(temperature_finding)

        # 分析质地
        texture_finding = self._analyze_texture(region_data)
        if texture_finding:
            findings.append(texture_finding)

        # 分析颜色
        color_finding = self._analyze_color(region_data)
        if color_finding:
            findings.append(color_finding)

        # 分析特殊标记
        if region_data.special_markings:
            marking_finding = self._analyze_special_markings(region_data)
            if marking_finding:
                findings.append(marking_finding)

        return findings

    def _analyze_moisture(self, region_data: SkinRegionData) -> SkinFinding | None:
        """分析皮肤湿度"""
        if region_data.moisture_level == SkinMoistureLevel.NORMAL:
            return None

        # 根据湿度级别确定严重程度
        severity_map = {
            SkinMoistureLevel.VERY_DRY: 0.8,
            SkinMoistureLevel.DRY: 0.5,
            SkinMoistureLevel.MOIST: 0.3,
            SkinMoistureLevel.VERY_MOIST: 0.6,
        }

        severity = severity_map.get(region_data.moisture_level, 0.3)

        # 推断相关病症
        if region_data.moisture_level in [SkinMoistureLevel.VERY_DRY, SkinMoistureLevel.DRY]:
            related_conditions = ["阴虚", "血虚", "津液不足", "燥证"]
            tcm_interpretation = "皮肤干燥提示阴津亏虚或血虚失养"
        else:  # MOIST or VERY_MOIST
            related_conditions = ["湿热", "水湿内停", "阳虚水泛"]
            tcm_interpretation = "皮肤湿润过度提示湿邪内盛或阳虚不能化湿"

        description = f"{region_data.region_name}皮肤{region_data.moisture_level.value}"
        if region_data.moisture_value is not None:
            description += f"（湿度值：{region_data.moisture_value}%）"

        return SkinFinding(
            region_id=region_data.region_id,
            region_name=region_data.region_name,
            finding_type="湿度异常",
            description=description,
            related_conditions=related_conditions,
            tcm_interpretation=tcm_interpretation,
            severity=severity,
            requires_attention=severity > 0.6,
        )

    def _analyze_elasticity(self, region_data: SkinRegionData) -> SkinFinding | None:
        """分析皮肤弹性"""
        if region_data.elasticity in [
            SkinElasticityLevel.GOOD,
            SkinElasticityLevel.VERY_GOOD,
            SkinElasticityLevel.EXCELLENT,
        ]:
            return None

        # 根据弹性级别确定严重程度
        severity_map = {SkinElasticityLevel.POOR: 0.8, SkinElasticityLevel.FAIR: 0.5}

        severity = severity_map.get(region_data.elasticity, 0.3)

        # 推断相关病症
        related_conditions = ["气虚", "血虚", "肾精不足", "脾虚", "衰老"]
        tcm_interpretation = "皮肤弹性差提示气血不足或肾精亏虚"

        description = f"{region_data.region_name}皮肤弹性{region_data.elasticity.value}"

        return SkinFinding(
            region_id=region_data.region_id,
            region_name=region_data.region_name,
            finding_type="弹性降低",
            description=description,
            related_conditions=related_conditions,
            tcm_interpretation=tcm_interpretation,
            severity=severity,
            requires_attention=severity > 0.6,
        )

    def _analyze_temperature(self, region_data: SkinRegionData) -> SkinFinding | None:
        """分析皮肤温度"""
        if region_data.temperature == SkinTemperatureLevel.NORMAL:
            return None

        # 根据温度级别确定严重程度和相关病症
        if region_data.temperature in [SkinTemperatureLevel.COLD, SkinTemperatureLevel.COOL]:
            severity = 0.7 if region_data.temperature == SkinTemperatureLevel.COLD else 0.4
            related_conditions = ["阳虚", "寒证", "气血不足", "经络不通"]
            tcm_interpretation = "皮肤发凉提示阳气不足或寒邪内盛"
        else:  # WARM or HOT
            severity = 0.7 if region_data.temperature == SkinTemperatureLevel.HOT else 0.4
            related_conditions = ["热证", "阴虚发热", "实热", "炎症"]
            tcm_interpretation = "皮肤发热提示热邪内盛或阴虚发热"

        description = f"{region_data.region_name}皮肤温度{region_data.temperature.value}"
        if region_data.temperature_value is not None:
            description += f"（{region_data.temperature_value}°C）"

        return SkinFinding(
            region_id=region_data.region_id,
            region_name=region_data.region_name,
            finding_type="温度异常",
            description=description,
            related_conditions=related_conditions,
            tcm_interpretation=tcm_interpretation,
            severity=severity,
            requires_attention=severity > 0.6,
        )

    def _analyze_texture(self, region_data: SkinRegionData) -> SkinFinding | None:
        """分析皮肤质地"""
        if region_data.texture == SkinTexture.NORMAL:
            return None

        # 根据质地类型确定相关病症
        texture_conditions_map = {
            SkinTexture.SMOOTH: {
                "conditions": ["气血充足", "津液充沛"],
                "interpretation": "皮肤光滑通常为正常表现",
                "severity": 0.1,
            },
            SkinTexture.ROUGH: {
                "conditions": ["血虚", "风燥", "瘀血"],
                "interpretation": "皮肤粗糙提示血虚失养或风燥伤津",
                "severity": 0.5,
            },
            SkinTexture.DRY: {
                "conditions": ["阴虚", "血虚", "燥证"],
                "interpretation": "皮肤干燥提示阴血不足",
                "severity": 0.6,
            },
            SkinTexture.OILY: {
                "conditions": ["湿热", "痰湿", "脾虚湿盛"],
                "interpretation": "皮肤油腻提示湿热内蕴或脾虚生湿",
                "severity": 0.4,
            },
            SkinTexture.SCALY: {
                "conditions": ["血虚风燥", "血热", "皮肤病"],
                "interpretation": "皮肤鳞状提示血虚风燥或血热生风",
                "severity": 0.7,
            },
        }

        texture_info = texture_conditions_map.get(
            region_data.texture,
            {"conditions": ["需进一步辨证"], "interpretation": "皮肤质地异常", "severity": 0.5},
        )

        description = f"{region_data.region_name}皮肤{self.texture_mapping.get(region_data.texture.name, region_data.texture.value)}"

        return SkinFinding(
            region_id=region_data.region_id,
            region_name=region_data.region_name,
            finding_type="质地异常",
            description=description,
            related_conditions=texture_info["conditions"],
            tcm_interpretation=texture_info["interpretation"],
            severity=texture_info["severity"],
            requires_attention=texture_info["severity"] > 0.6,
        )

    def _analyze_color(self, region_data: SkinRegionData) -> SkinFinding | None:
        """分析皮肤颜色"""
        if not region_data.color or region_data.color.lower() in ["正常", "normal"]:
            return None

        # 根据颜色描述推断病症
        color_patterns = {
            "苍白": {
                "conditions": ["气血不足", "阳虚", "失血"],
                "interpretation": "面色苍白提示气血亏虚或阳气不足",
                "severity": 0.7,
            },
            "萎黄": {
                "conditions": ["脾虚", "营养不良", "慢性病"],
                "interpretation": "面色萎黄提示脾胃虚弱或气血生化不足",
                "severity": 0.6,
            },
            "潮红": {
                "conditions": ["阴虚", "实热", "血热"],
                "interpretation": "皮肤潮红提示阴虚火旺或实热内盛",
                "severity": 0.6,
            },
            "紫暗": {
                "conditions": ["瘀血", "寒凝", "缺氧"],
                "interpretation": "皮肤紫暗提示血瘀或寒凝血脉",
                "severity": 0.8,
            },
            "青紫": {
                "conditions": ["寒证", "瘀血", "气滞"],
                "interpretation": "皮肤青紫提示寒邪内盛或气血瘀滞",
                "severity": 0.8,
            },
        }

        # 查找匹配的颜色模式
        color_info = None
        for pattern, info in color_patterns.items():
            if pattern in region_data.color:
                color_info = info
                break

        if not color_info:
            color_info = {
                "conditions": ["需进一步辨证"],
                "interpretation": "皮肤颜色异常",
                "severity": 0.5,
            }

        description = f"{region_data.region_name}皮肤呈{region_data.color}"

        return SkinFinding(
            region_id=region_data.region_id,
            region_name=region_data.region_name,
            finding_type="颜色异常",
            description=description,
            related_conditions=color_info["conditions"],
            tcm_interpretation=color_info["interpretation"],
            severity=color_info["severity"],
            requires_attention=color_info["severity"] > 0.6,
        )

    def _analyze_special_markings(self, region_data: SkinRegionData) -> SkinFinding | None:
        """分析特殊标记"""
        if not region_data.special_markings:
            return None

        # 分析各种特殊标记
        marking_interpretations = {
            "痣": "多数为正常，但需注意观察变化",
            "斑": "可能与肝郁、血瘀、肾虚有关",
            "疹": "可能与风热、湿热、血热有关",
            "疮": "多与热毒、湿毒有关",
            "瘀点": "提示血瘀或出血倾向",
            "瘀斑": "提示严重血瘀或凝血功能异常",
        }

        conditions = []
        interpretations = []
        severity = 0.3

        for marking in region_data.special_markings:
            for key, interpretation in marking_interpretations.items():
                if key in marking:
                    interpretations.append(interpretation)
                    if key in ["疮", "瘀斑"]:
                        severity = max(severity, 0.8)
                    elif key in ["斑", "疹", "瘀点"]:
                        severity = max(severity, 0.6)

                    # 添加相关病症
                    if key == "斑":
                        conditions.extend(["肝郁", "血瘀", "肾虚"])
                    elif key in ["疹", "疮"]:
                        conditions.extend(["风热", "湿热", "血热"])
                    elif key in ["瘀点", "瘀斑"]:
                        conditions.extend(["血瘀", "出血证"])

        description = f"{region_data.region_name}发现{', '.join(region_data.special_markings)}"
        tcm_interpretation = (
            "；".join(set(interpretations)) if interpretations else "特殊皮肤标记需结合其他症状辨证"
        )

        return SkinFinding(
            region_id=region_data.region_id,
            region_name=region_data.region_name,
            finding_type="特殊标记",
            description=description,
            related_conditions=list(set(conditions)),
            tcm_interpretation=tcm_interpretation,
            severity=severity,
            requires_attention=severity > 0.6,
        )

    def _analyze_skin_patterns(self, regions_data: list[SkinRegionData]) -> list[SkinFinding]:
        """分析皮肤的整体模式"""
        findings = []

        # 统计各项指标
        moisture_levels = [r.moisture_level for r in regions_data]
        temperature_levels = [r.temperature for r in regions_data]
        elasticity_levels = [r.elasticity for r in regions_data]
        textures = [r.texture for r in regions_data]

        # 检查全身性干燥
        dry_count = sum(
            1 for m in moisture_levels if m in [SkinMoistureLevel.DRY, SkinMoistureLevel.VERY_DRY]
        )
        if dry_count >= len(regions_data) * 0.6:  # 60%以上区域干燥
            finding = SkinFinding(
                region_id="whole_body",
                region_name="全身",
                finding_type="广泛性干燥",
                description="全身多处皮肤干燥",
                related_conditions=["阴虚", "血虚", "津液大伤"],
                tcm_interpretation="全身皮肤干燥提示阴血亏虚或津液大伤",
                severity=0.8,
                requires_attention=True,
            )
            findings.append(finding)

        # 检查全身性发冷
        cold_count = sum(
            1
            for t in temperature_levels
            if t in [SkinTemperatureLevel.COLD, SkinTemperatureLevel.COOL]
        )
        if cold_count >= len(regions_data) * 0.6:
            finding = SkinFinding(
                region_id="whole_body",
                region_name="全身",
                finding_type="广泛性发冷",
                description="全身多处皮肤发冷",
                related_conditions=["阳虚", "寒证", "气血不足"],
                tcm_interpretation="全身皮肤发冷提示阳虚或寒邪内盛",
                severity=0.8,
                requires_attention=True,
            )
            findings.append(finding)

        # 检查皮肤弹性普遍降低
        poor_elasticity_count = sum(
            1
            for e in elasticity_levels
            if e in [SkinElasticityLevel.POOR, SkinElasticityLevel.FAIR]
        )
        if poor_elasticity_count >= len(regions_data) * 0.5:
            finding = SkinFinding(
                region_id="whole_body",
                region_name="全身",
                finding_type="弹性普遍降低",
                description="全身皮肤弹性普遍较差",
                related_conditions=["气血不足", "肾精亏虚", "脾虚"],
                tcm_interpretation="皮肤弹性普遍降低提示气血不足或肾精亏虚",
                severity=0.7,
                requires_attention=True,
            )
            findings.append(finding)

        return findings

    def generate_summary(self, findings: list[SkinFinding]) -> str:
        """
        生成皮肤触诊分析总结

        Args:
            findings: 皮肤触诊发现列表

        Returns:
            分析总结文本
        """
        if not findings:
            return "皮肤触诊检查未发现明显异常"

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
        summary_parts.append(f"皮肤触诊发现最显著的问题是{most_severe.description}")

        # 各类发现统计
        if len(finding_types) > 1:
            type_summary = []
            for ftype, items in finding_types.items():
                type_summary.append(f"{ftype}（{len(items)}处）")
            summary_parts.append(f"共发现{len(finding_types)}类异常：{', '.join(type_summary)}")

        # 中医证候归纳
        all_conditions = set()
        for finding in findings:
            all_conditions.update(finding.related_conditions)

        # 统计高频证候
        condition_counts = {}
        for finding in findings:
            for condition in finding.related_conditions:
                condition_counts[condition] = condition_counts.get(condition, 0) + 1

        # 找出出现3次以上的证候
        frequent_conditions = [c for c, count in condition_counts.items() if count >= 3]
        if frequent_conditions:
            summary_parts.append(f"中医辨证提示主要存在：{', '.join(frequent_conditions)}")

        # 需要注意的发现
        attention_needed = [f for f in findings if f.requires_attention]
        if attention_needed:
            summary_parts.append(f"有{len(attention_needed)}项发现需要特别关注")

        return "。".join(summary_parts)
