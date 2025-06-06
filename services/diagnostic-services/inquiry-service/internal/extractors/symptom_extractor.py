"""
symptom_extractor - 索克生活项目模块
"""

from ..common.base import BaseExtractor, SymptomInfo
from ..common.exceptions import ProcessingError
from ..common.metrics import counter, timer
from ..common.utils import calculate_confidence, sanitize_text
from .context_analyzer import SymptomContextAnalyzer
from .duration_extractor import DurationExtractor
from .negation_detector import NegationDetector
from .severity_analyzer import SeverityAnalyzer
from dataclasses import asdict
from typing import Any
import asyncio

#!/usr/bin/env python

"""
优化后的症状提取器
"""




class OptimizedSymptomExtractor(BaseExtractor):
    """优化后的症状提取器"""

    async def _do_initialize(self) -> None:
        """初始化提取器"""
        # 初始化子组件
        self.negation_detector = NegationDetector(self.config)
        self.severity_analyzer = SeverityAnalyzer(self.config)
        self.duration_extractor = DurationExtractor(self.config)
        self.context_analyzer = SymptomContextAnalyzer(self.config)

        # 加载症状关键词
        self.symptom_keywords = self._load_symptom_keywords()

        # 配置参数
        extraction_config = self.config.get("symptom_extraction", {})
        self.min_confidence = extraction_config.get("min_confidence", 0.6)
        self.max_symptoms_per_text = extraction_config.get("max_symptoms_per_text", 30)
        self.enable_caching = extraction_config.get("enable_caching", True)

        self.logger.info("优化症状提取器初始化完成")

    async def _do_health_check(self) -> bool:
        """健康检查"""
        try:
            # 测试基本功能
            test_text = "我头痛"
            result = await self.extract(test_text)
            return len(result.get("symptoms", [])) > 0
        except Exception:
            return False

    @timer(None, "symptom_extraction")
    @counter(None, "symptom_extractions")
    async def extract(self, text: str, **kwargs) -> dict[str, Any]:
        """提取症状信息"""
        self._validate_initialized()
        self._validate_text_input(text)

        try:
            # 文本预处理
            cleaned_text = sanitize_text(
                text, self.config.get("max_text_length", 10000)
            )

            # 并行执行各种提取任务
            tasks = [
                self._extract_symptoms_from_text(cleaned_text),
                self._extract_body_locations(cleaned_text),
                self._extract_temporal_factors(cleaned_text),
            ]

            symptoms, body_locations, temporal_factors = await asyncio.gather(*tasks)

            # 过滤低置信度症状
            filtered_symptoms = [
                symptom
                for symptom in symptoms
                if symptom.confidence >= self.min_confidence
            ]

            # 限制症状数量
            if len(filtered_symptoms) > self.max_symptoms_per_text:
                filtered_symptoms.sort(key=lambda x: x.confidence, reverse=True)
                filtered_symptoms = filtered_symptoms[: self.max_symptoms_per_text]

            # 计算整体置信度
            overall_confidence = self._calculate_overall_confidence(
                filtered_symptoms, body_locations, temporal_factors
            )

            result = {
                "symptoms": [asdict(symptom) for symptom in filtered_symptoms],
                "body_locations": body_locations,
                "temporal_factors": temporal_factors,
                "confidence_score": overall_confidence,
                "extraction_metadata": {
                    "original_text_length": len(text),
                    "cleaned_text_length": len(cleaned_text),
                    "total_symptoms_found": len(symptoms),
                    "filtered_symptoms_count": len(filtered_symptoms),
                },
            }

            self.logger.info(
                "症状提取完成",
                symptoms_count=len(filtered_symptoms),
                confidence=overall_confidence,
            )

            return result

        except Exception as e:
            self.logger.error("症状提取失败", error=str(e))
            raise ProcessingError(f"症状提取失败: {e!s}", "extract_symptoms", e)

    async def _extract_symptoms_from_text(self, text: str) -> list[SymptomInfo]:
        """从文本中提取症状"""
        symptoms = []

        # 使用关键词匹配
        for keyword in self.symptom_keywords:
            if keyword in text:
                # 检查否定
                is_negated = await self.negation_detector.is_negated(text, keyword)
                if is_negated:
                    continue

                # 分析严重程度
                severity = await self.severity_analyzer.analyze_severity(text, keyword)

                # 提取持续时间
                duration = await self.duration_extractor.extract_duration(text, keyword)

                # 分析上下文
                context = await self.context_analyzer.analyze_context(text, keyword)

                # 计算置信度
                confidence = self._calculate_symptom_confidence(
                    keyword, text, severity, duration, context
                )

                symptom = SymptomInfo(
                    name=keyword,
                    confidence=confidence,
                    severity=severity,
                    duration=duration,
                    context=context,
                )

                symptoms.append(symptom)

        return symptoms

    async def _extract_body_locations(self, text: str) -> list[dict[str, Any]]:
        """提取身体部位信息"""
        body_locations = []

        # 身体部位关键词
        location_keywords = [
            "头部",
            "头",
            "颈部",
            "脖子",
            "胸部",
            "胸",
            "腹部",
            "肚子",
            "腰部",
            "腰",
            "背部",
            "背",
            "手",
            "手臂",
            "腿",
            "脚",
            "眼睛",
            "耳朵",
            "鼻子",
            "嘴",
        ]

        for location in location_keywords:
            if location in text:
                # 计算位置在文本中的重要性
                count = text.count(location)
                confidence = min(count * 0.3, 1.0)

                body_locations.append(
                    {"location": location, "confidence": confidence, "mentions": count}
                )

        return body_locations

    async def _extract_temporal_factors(self, text: str) -> list[dict[str, Any]]:
        """提取时间因素"""
        temporal_factors = []

        # 时间表达式
        time_patterns = {
            "急性": ["突然", "刚刚", "今天", "昨天"],
            "亚急性": ["最近", "这周", "这个月", "近期"],
            "慢性": ["长期", "一直", "总是", "很久", "几个月", "几年"],
        }

        for category, patterns in time_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    temporal_factors.append(
                        {"category": category, "pattern": pattern, "confidence": 0.8}
                    )

        return temporal_factors

    def _calculate_symptom_confidence(
        self,
        symptom: str,
        text: str,
        severity: str,
        duration: int,
        context: dict[str, Any],
    ) -> float:
        """计算症状置信度"""
        factors = []

        # 基础匹配置信度
        base_confidence = 0.7
        factors.append(base_confidence)

        # 严重程度加权
        severity_weights = {"mild": 0.6, "moderate": 0.8, "severe": 1.0}
        severity_confidence = severity_weights.get(severity, 0.7)
        factors.append(severity_confidence)

        # 持续时间加权
        if duration > 0:
            duration_confidence = min(duration / 30, 1.0)  # 最多30天
            factors.append(duration_confidence)

        # 上下文加权
        if context and context.get("related_symptoms"):
            context_confidence = min(len(context["related_symptoms"]) * 0.2, 0.8)
            factors.append(context_confidence)

        # 文本中出现频率
        frequency = text.count(symptom)
        frequency_confidence = min(frequency * 0.2, 0.9)
        factors.append(frequency_confidence)

        return calculate_confidence(factors)

    def _calculate_overall_confidence(
        self,
        symptoms: list[SymptomInfo],
        body_locations: list[dict],
        temporal_factors: list[dict],
    ) -> float:
        """计算整体置信度"""
        factors = []

        # 症状置信度
        if symptoms:
            avg_symptom_confidence = sum(s.confidence for s in symptoms) / len(symptoms)
            factors.append(avg_symptom_confidence)

        # 身体部位置信度
        if body_locations:
            avg_location_confidence = sum(
                loc["confidence"] for loc in body_locations
            ) / len(body_locations)
            factors.append(avg_location_confidence)

        # 时间因素置信度
        if temporal_factors:
            avg_temporal_confidence = sum(
                tf["confidence"] for tf in temporal_factors
            ) / len(temporal_factors)
            factors.append(avg_temporal_confidence)

        if not factors:
            return 0.0

        return calculate_confidence(factors)

    def _load_symptom_keywords(self) -> list[str]:
        """加载症状关键词"""
        # 基础症状关键词
        keywords = [
            # 头部症状
            "头痛",
            "头晕",
            "头胀",
            "偏头痛",
            "头重",
            # 胸部症状
            "胸闷",
            "胸痛",
            "心悸",
            "气短",
            "憋气",
            "咳嗽",
            "咳痰",
            # 腹部症状
            "腹痛",
            "腹胀",
            "恶心",
            "呕吐",
            "腹泻",
            "便秘",
            "消化不良",
            # 四肢症状
            "关节痛",
            "肌肉酸痛",
            "肢体麻木",
            "腿软",
            "手脚冰凉",
            # 感官症状
            "视力下降",
            "听力下降",
            "耳鸣",
            "嗅觉减退",
            # 睡眠症状
            "失眠",
            "多梦",
            "易醒",
            "嗜睡",
            # 精神症状
            "焦虑",
            "抑郁",
            "烦躁",
            "易怒",
            "情绪波动",
            # 能量症状
            "疲劳",
            "乏力",
            "精神不振",
            "体力下降",
        ]

        # 按长度排序，优先匹配较长的症状
        keywords.sort(key=len, reverse=True)

        return keywords

    async def extract_with_knowledge_base(
        self, text: str, knowledge_base
    ) -> dict[str, Any]:
        """结合知识库的增强提取"""
        # 基础提取
        base_result = await self.extract(text)

        # 知识库验证和增强
        if knowledge_base:
            enhanced_symptoms = []

            for symptom_data in base_result["symptoms"]:
                symptom_name = symptom_data["name"]

                # 知识库验证
                if knowledge_base.validate_symptom(symptom_name):
                    # 获取相关信息
                    related_info = knowledge_base.get_symptom_info(symptom_name)
                    symptom_data["knowledge_base_info"] = related_info

                    # 调整置信度
                    symptom_data["confidence"] *= 1.1  # 知识库验证加权
                    symptom_data["confidence"] = min(symptom_data["confidence"], 1.0)

                    enhanced_symptoms.append(symptom_data)

            base_result["symptoms"] = enhanced_symptoms
            base_result["knowledge_base_enhanced"] = True

        return base_result
