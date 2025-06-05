#!/usr/bin/env python3
"""
数据处理管道模块

提供健康数据的验证、清洗、标准化、异常检测等处理功能。
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum

import numpy as np
import pandas as pd
from loguru import logger

from .config import get_settings
from .cache import cache_manager, cached
from ..models.health_data import DataType, DataSource

settings = get_settings()


class ProcessingStage(Enum):
    """处理阶段枚举"""
    VALIDATION = "validation"
    CLEANING = "cleaning"
    STANDARDIZATION = "standardization"
    ANOMALY_DETECTION = "anomaly_detection"
    QUALITY_ASSESSMENT = "quality_assessment"
    ENRICHMENT = "enrichment"


@dataclass
class ProcessingResult:
    """处理结果"""
    success: bool
    stage: ProcessingStage
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    errors: List[str]
    warnings: List[str]
    quality_score: float
    confidence_score: float
    processing_time: float
    timestamp: datetime


@dataclass
class PipelineConfig:
    """管道配置"""
    enabled_stages: List[ProcessingStage]
    validation_rules: Dict[str, Any]
    cleaning_rules: Dict[str, Any]
    standardization_rules: Dict[str, Any]
    anomaly_detection_config: Dict[str, Any]
    quality_thresholds: Dict[str, float]
    parallel_processing: bool = True
    max_workers: int = 4
    timeout: int = 30


class ProcessingStageBase(ABC):
    """处理阶段基类"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logger

    @abstractmethod
    async def process(self, data: Dict[str, Any], metadata: Dict[str, Any]) -> ProcessingResult:
        """处理数据"""
        pass

    def _calculate_processing_time(self, start_time: datetime) -> float:
        """计算处理时间"""
        return (datetime.now() - start_time).total_seconds()

    def _create_result(
        self,
        success: bool,
        stage: ProcessingStage,
        data: Dict[str, Any],
        metadata: Dict[str, Any],
        errors: List[str] = None,
        warnings: List[str] = None,
        quality_score: float = 0.0,
        confidence_score: float = 0.0,
        processing_time: float = 0.0
    ) -> ProcessingResult:
        """创建处理结果"""
        return ProcessingResult(
            success=success,
            stage=stage,
            data=data,
            metadata=metadata,
            errors=errors or [],
            warnings=warnings or [],
            quality_score=quality_score,
            confidence_score=confidence_score,
            processing_time=processing_time,
            timestamp=datetime.now()
        )


class ValidationStage(ProcessingStageBase):
    """数据验证阶段"""

    async def process(self, data: Dict[str, Any], metadata: Dict[str, Any]) -> ProcessingResult:
        """验证数据"""
        start_time = datetime.now()
        errors = []
        warnings = []
        quality_score = 1.0

        try:
            # 基本结构验证
            if not isinstance(data, dict):
                errors.append("数据必须是字典格式")
                return self._create_result(
                    False, ProcessingStage.VALIDATION, data, metadata,
                    errors=errors, processing_time=self._calculate_processing_time(start_time)
                )

            # 必需字段验证
            required_fields = self.config.get("required_fields", [])
            for field in required_fields:
                if field not in data:
                    errors.append(f"缺少必需字段: {field}")
                    quality_score -= 0.2

            # 数据类型验证
            field_types = self.config.get("field_types", {})
            for field, expected_type in field_types.items():
                if field in data:
                    if not isinstance(data[field], expected_type):
                        errors.append(f"字段 {field} 类型错误，期望 {expected_type.__name__}")
                        quality_score -= 0.1

            # 数值范围验证
            value_ranges = self.config.get("value_ranges", {})
            for field, (min_val, max_val) in value_ranges.items():
                if field in data and isinstance(data[field], (int, float)):
                    if data[field] < min_val or data[field] > max_val:
                        warnings.append(f"字段 {field} 值 {data[field]} 超出正常范围 [{min_val}, {max_val}]")
                        quality_score -= 0.05

            # 时间戳验证
            if "timestamp" in data:
                try:
                    if isinstance(data["timestamp"], str):
                        datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
                    elif isinstance(data["timestamp"], (int, float)):
                        datetime.fromtimestamp(data["timestamp"])
                except (ValueError, OSError):
                    errors.append("时间戳格式无效")
                    quality_score -= 0.1

            # 计算置信度
            confidence_score = max(0.0, 1.0 - len(errors) * 0.3 - len(warnings) * 0.1)

            success = len(errors) == 0
            processing_time = self._calculate_processing_time(start_time)

            return self._create_result(
                success, ProcessingStage.VALIDATION, data, metadata,
                errors=errors, warnings=warnings,
                quality_score=max(0.0, quality_score),
                confidence_score=confidence_score,
                processing_time=processing_time
            )

        except Exception as e:
            self.logger.error(f"数据验证失败: {e}")
            return self._create_result(
                False, ProcessingStage.VALIDATION, data, metadata,
                errors=[f"验证过程异常: {str(e)}"],
                processing_time=self._calculate_processing_time(start_time)
            )


class CleaningStage(ProcessingStageBase):
    """数据清洗阶段"""

    async def process(self, data: Dict[str, Any], metadata: Dict[str, Any]) -> ProcessingResult:
        """清洗数据"""
        start_time = datetime.now()
        cleaned_data = data.copy()
        warnings = []
        quality_score = 1.0

        try:
            # 移除空值
            if self.config.get("remove_null_values", True):
                original_count = len(cleaned_data)
                cleaned_data = {k: v for k, v in cleaned_data.items() if v is not None}
                removed_count = original_count - len(cleaned_data)
                if removed_count > 0:
                    warnings.append(f"移除了 {removed_count} 个空值字段")
                    quality_score -= removed_count * 0.05

            # 数值修正
            numeric_corrections = self.config.get("numeric_corrections", {})
            for field, correction_config in numeric_corrections.items():
                if field in cleaned_data and isinstance(cleaned_data[field], (int, float)):
                    original_value = cleaned_data[field]
                    
                    # 范围修正
                    if "clamp_range" in correction_config:
                        min_val, max_val = correction_config["clamp_range"]
                        cleaned_data[field] = max(min_val, min(max_val, cleaned_data[field]))
                        if cleaned_data[field] != original_value:
                            warnings.append(f"字段 {field} 值从 {original_value} 修正为 {cleaned_data[field]}")
                            quality_score -= 0.02
                    
                    # 精度修正
                    if "decimal_places" in correction_config:
                        decimal_places = correction_config["decimal_places"]
                        cleaned_data[field] = round(cleaned_data[field], decimal_places)

            # 字符串清洗
            string_cleaning = self.config.get("string_cleaning", {})
            for field, cleaning_config in string_cleaning.items():
                if field in cleaned_data and isinstance(cleaned_data[field], str):
                    original_value = cleaned_data[field]
                    
                    # 去除空白字符
                    if cleaning_config.get("strip", True):
                        cleaned_data[field] = cleaned_data[field].strip()
                    
                    # 转换大小写
                    case_conversion = cleaning_config.get("case")
                    if case_conversion == "lower":
                        cleaned_data[field] = cleaned_data[field].lower()
                    elif case_conversion == "upper":
                        cleaned_data[field] = cleaned_data[field].upper()
                    
                    # 移除特殊字符
                    if cleaning_config.get("remove_special_chars", False):
                        import re
                        cleaned_data[field] = re.sub(r'[^\w\s-]', '', cleaned_data[field])
                    
                    if cleaned_data[field] != original_value:
                        warnings.append(f"字段 {field} 字符串已清洗")

            # 重复值处理
            if self.config.get("handle_duplicates", False):
                # 这里可以实现重复值检测和处理逻辑
                pass

            # 计算置信度
            confidence_score = max(0.0, 1.0 - len(warnings) * 0.05)

            processing_time = self._calculate_processing_time(start_time)

            return self._create_result(
                True, ProcessingStage.CLEANING, cleaned_data, metadata,
                warnings=warnings,
                quality_score=max(0.0, quality_score),
                confidence_score=confidence_score,
                processing_time=processing_time
            )

        except Exception as e:
            self.logger.error(f"数据清洗失败: {e}")
            return self._create_result(
                False, ProcessingStage.CLEANING, data, metadata,
                errors=[f"清洗过程异常: {str(e)}"],
                processing_time=self._calculate_processing_time(start_time)
            )


class StandardizationStage(ProcessingStageBase):
    """数据标准化阶段"""

    async def process(self, data: Dict[str, Any], metadata: Dict[str, Any]) -> ProcessingResult:
        """标准化数据"""
        start_time = datetime.now()
        standardized_data = data.copy()
        warnings = []
        quality_score = 1.0

        try:
            # 单位转换
            unit_conversions = self.config.get("unit_conversions", {})
            for field, conversion_config in unit_conversions.items():
                if field in standardized_data and isinstance(standardized_data[field], (int, float)):
                    from_unit = conversion_config.get("from_unit")
                    to_unit = conversion_config.get("to_unit")
                    factor = conversion_config.get("factor", 1.0)
                    
                    if from_unit and to_unit:
                        original_value = standardized_data[field]
                        standardized_data[field] = original_value * factor
                        warnings.append(f"字段 {field} 从 {from_unit} 转换为 {to_unit}")

            # 数值标准化
            normalization = self.config.get("normalization", {})
            for field, norm_config in normalization.items():
                if field in standardized_data and isinstance(standardized_data[field], (int, float)):
                    method = norm_config.get("method", "min_max")
                    
                    if method == "min_max":
                        min_val = norm_config.get("min", 0)
                        max_val = norm_config.get("max", 100)
                        current_min = norm_config.get("current_min", 0)
                        current_max = norm_config.get("current_max", 100)
                        
                        # Min-Max标准化
                        normalized_value = (standardized_data[field] - current_min) / (current_max - current_min)
                        standardized_data[field] = normalized_value * (max_val - min_val) + min_val
                    
                    elif method == "z_score":
                        mean = norm_config.get("mean", 0)
                        std = norm_config.get("std", 1)
                        standardized_data[field] = (standardized_data[field] - mean) / std

            # 时间格式标准化
            time_fields = self.config.get("time_fields", [])
            for field in time_fields:
                if field in standardized_data:
                    try:
                        if isinstance(standardized_data[field], str):
                            # 转换为ISO格式
                            dt = datetime.fromisoformat(standardized_data[field].replace('Z', '+00:00'))
                            standardized_data[field] = dt.isoformat()
                        elif isinstance(standardized_data[field], (int, float)):
                            # 时间戳转换为ISO格式
                            dt = datetime.fromtimestamp(standardized_data[field])
                            standardized_data[field] = dt.isoformat()
                    except (ValueError, OSError):
                        warnings.append(f"时间字段 {field} 标准化失败")
                        quality_score -= 0.1

            # 分类数据标准化
            categorical_mappings = self.config.get("categorical_mappings", {})
            for field, mapping in categorical_mappings.items():
                if field in standardized_data and standardized_data[field] in mapping:
                    standardized_data[field] = mapping[standardized_data[field]]

            # 计算置信度
            confidence_score = max(0.0, 1.0 - len(warnings) * 0.05)

            processing_time = self._calculate_processing_time(start_time)

            return self._create_result(
                True, ProcessingStage.STANDARDIZATION, standardized_data, metadata,
                warnings=warnings,
                quality_score=max(0.0, quality_score),
                confidence_score=confidence_score,
                processing_time=processing_time
            )

        except Exception as e:
            self.logger.error(f"数据标准化失败: {e}")
            return self._create_result(
                False, ProcessingStage.STANDARDIZATION, data, metadata,
                errors=[f"标准化过程异常: {str(e)}"],
                processing_time=self._calculate_processing_time(start_time)
            )


class AnomalyDetectionStage(ProcessingStageBase):
    """异常检测阶段"""

    async def process(self, data: Dict[str, Any], metadata: Dict[str, Any]) -> ProcessingResult:
        """检测异常"""
        start_time = datetime.now()
        warnings = []
        anomalies = []
        quality_score = 1.0

        try:
            # 统计异常检测
            statistical_rules = self.config.get("statistical_rules", {})
            for field, rules in statistical_rules.items():
                if field in data and isinstance(data[field], (int, float)):
                    value = data[field]
                    
                    # Z-score异常检测
                    if "z_score_threshold" in rules:
                        mean = rules.get("mean", 0)
                        std = rules.get("std", 1)
                        z_score = abs((value - mean) / std) if std > 0 else 0
                        
                        if z_score > rules["z_score_threshold"]:
                            anomalies.append({
                                "field": field,
                                "value": value,
                                "type": "statistical",
                                "method": "z_score",
                                "score": z_score,
                                "threshold": rules["z_score_threshold"]
                            })
                    
                    # IQR异常检测
                    if "iqr_multiplier" in rules:
                        q1 = rules.get("q1", 0)
                        q3 = rules.get("q3", 100)
                        iqr = q3 - q1
                        multiplier = rules["iqr_multiplier"]
                        
                        lower_bound = q1 - multiplier * iqr
                        upper_bound = q3 + multiplier * iqr
                        
                        if value < lower_bound or value > upper_bound:
                            anomalies.append({
                                "field": field,
                                "value": value,
                                "type": "statistical",
                                "method": "iqr",
                                "bounds": [lower_bound, upper_bound]
                            })

            # 规则基础异常检测
            rule_based_checks = self.config.get("rule_based_checks", {})
            for field, checks in rule_based_checks.items():
                if field in data:
                    value = data[field]
                    
                    # 范围检查
                    if "valid_range" in checks:
                        min_val, max_val = checks["valid_range"]
                        if isinstance(value, (int, float)) and (value < min_val or value > max_val):
                            anomalies.append({
                                "field": field,
                                "value": value,
                                "type": "rule_based",
                                "method": "range_check",
                                "valid_range": [min_val, max_val]
                            })
                    
                    # 枚举值检查
                    if "valid_values" in checks:
                        valid_values = checks["valid_values"]
                        if value not in valid_values:
                            anomalies.append({
                                "field": field,
                                "value": value,
                                "type": "rule_based",
                                "method": "enum_check",
                                "valid_values": valid_values
                            })

            # 时间序列异常检测
            time_series_config = self.config.get("time_series", {})
            if time_series_config.get("enabled", False):
                # 这里可以实现更复杂的时间序列异常检测
                pass

            # 计算异常分数
            anomaly_score = len(anomalies) / max(1, len(data)) if anomalies else 0.0
            is_anomaly = anomaly_score > self.config.get("anomaly_threshold", 0.3)

            # 更新质量分数
            if anomalies:
                quality_score -= len(anomalies) * 0.1
                for anomaly in anomalies:
                    warnings.append(f"检测到异常: {anomaly}")

            # 计算置信度
            confidence_score = max(0.0, 1.0 - anomaly_score)

            # 更新元数据
            metadata.update({
                "anomalies": anomalies,
                "anomaly_score": anomaly_score,
                "is_anomaly": is_anomaly
            })

            processing_time = self._calculate_processing_time(start_time)

            return self._create_result(
                True, ProcessingStage.ANOMALY_DETECTION, data, metadata,
                warnings=warnings,
                quality_score=max(0.0, quality_score),
                confidence_score=confidence_score,
                processing_time=processing_time
            )

        except Exception as e:
            self.logger.error(f"异常检测失败: {e}")
            return self._create_result(
                False, ProcessingStage.ANOMALY_DETECTION, data, metadata,
                errors=[f"异常检测过程异常: {str(e)}"],
                processing_time=self._calculate_processing_time(start_time)
            )


class QualityAssessmentStage(ProcessingStageBase):
    """质量评估阶段"""

    async def process(self, data: Dict[str, Any], metadata: Dict[str, Any]) -> ProcessingResult:
        """评估数据质量"""
        start_time = datetime.now()
        warnings = []
        quality_metrics = {}

        try:
            # 完整性评估
            completeness_score = self._assess_completeness(data)
            quality_metrics["completeness"] = completeness_score

            # 准确性评估
            accuracy_score = self._assess_accuracy(data, metadata)
            quality_metrics["accuracy"] = accuracy_score

            # 一致性评估
            consistency_score = self._assess_consistency(data)
            quality_metrics["consistency"] = consistency_score

            # 及时性评估
            timeliness_score = self._assess_timeliness(data, metadata)
            quality_metrics["timeliness"] = timeliness_score

            # 有效性评估
            validity_score = self._assess_validity(data)
            quality_metrics["validity"] = validity_score

            # 计算综合质量分数
            weights = self.config.get("quality_weights", {
                "completeness": 0.25,
                "accuracy": 0.25,
                "consistency": 0.2,
                "timeliness": 0.15,
                "validity": 0.15
            })

            overall_quality = sum(
                quality_metrics[metric] * weights.get(metric, 0.2)
                for metric in quality_metrics
            )

            # 质量等级
            quality_grade = self._get_quality_grade(overall_quality)

            # 更新元数据
            metadata.update({
                "quality_metrics": quality_metrics,
                "overall_quality": overall_quality,
                "quality_grade": quality_grade
            })

            # 生成警告
            for metric, score in quality_metrics.items():
                threshold = self.config.get("quality_thresholds", {}).get(metric, 0.7)
                if score < threshold:
                    warnings.append(f"质量指标 {metric} 分数 {score:.2f} 低于阈值 {threshold}")

            processing_time = self._calculate_processing_time(start_time)

            return self._create_result(
                True, ProcessingStage.QUALITY_ASSESSMENT, data, metadata,
                warnings=warnings,
                quality_score=overall_quality,
                confidence_score=overall_quality,
                processing_time=processing_time
            )

        except Exception as e:
            self.logger.error(f"质量评估失败: {e}")
            return self._create_result(
                False, ProcessingStage.QUALITY_ASSESSMENT, data, metadata,
                errors=[f"质量评估过程异常: {str(e)}"],
                processing_time=self._calculate_processing_time(start_time)
            )

    def _assess_completeness(self, data: Dict[str, Any]) -> float:
        """评估完整性"""
        required_fields = self.config.get("required_fields", [])
        if not required_fields:
            return 1.0
        
        present_fields = sum(1 for field in required_fields if field in data and data[field] is not None)
        return present_fields / len(required_fields)

    def _assess_accuracy(self, data: Dict[str, Any], metadata: Dict[str, Any]) -> float:
        """评估准确性"""
        # 基于异常检测结果
        anomaly_score = metadata.get("anomaly_score", 0.0)
        return max(0.0, 1.0 - anomaly_score)

    def _assess_consistency(self, data: Dict[str, Any]) -> float:
        """评估一致性"""
        # 检查数据内部一致性
        consistency_rules = self.config.get("consistency_rules", [])
        violations = 0
        
        for rule in consistency_rules:
            if not self._check_consistency_rule(data, rule):
                violations += 1
        
        return max(0.0, 1.0 - violations / max(1, len(consistency_rules)))

    def _assess_timeliness(self, data: Dict[str, Any], metadata: Dict[str, Any]) -> float:
        """评估及时性"""
        if "timestamp" not in data:
            return 0.5  # 无时间戳，中等分数
        
        try:
            if isinstance(data["timestamp"], str):
                timestamp = datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
            else:
                timestamp = datetime.fromtimestamp(data["timestamp"])
            
            # 计算数据新鲜度
            age = (datetime.now() - timestamp).total_seconds()
            max_age = self.config.get("max_data_age", 86400)  # 默认24小时
            
            return max(0.0, 1.0 - age / max_age)
            
        except (ValueError, OSError):
            return 0.0

    def _assess_validity(self, data: Dict[str, Any]) -> float:
        """评估有效性"""
        validation_rules = self.config.get("validation_rules", {})
        total_fields = len(data)
        valid_fields = 0
        
        for field, value in data.items():
            if field in validation_rules:
                if self._validate_field(value, validation_rules[field]):
                    valid_fields += 1
            else:
                valid_fields += 1  # 没有规则的字段认为有效
        
        return valid_fields / max(1, total_fields)

    def _check_consistency_rule(self, data: Dict[str, Any], rule: Dict[str, Any]) -> bool:
        """检查一致性规则"""
        # 实现具体的一致性检查逻辑
        return True

    def _validate_field(self, value: Any, rules: Dict[str, Any]) -> bool:
        """验证字段"""
        # 实现具体的字段验证逻辑
        return True

    def _get_quality_grade(self, score: float) -> str:
        """获取质量等级"""
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"


class DataProcessingPipeline:
    """数据处理管道"""

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.stages = self._initialize_stages()
        self.logger = logger

    def _initialize_stages(self) -> Dict[ProcessingStage, ProcessingStageBase]:
        """初始化处理阶段"""
        stages = {}
        
        if ProcessingStage.VALIDATION in self.config.enabled_stages:
            stages[ProcessingStage.VALIDATION] = ValidationStage(self.config.validation_rules)
        
        if ProcessingStage.CLEANING in self.config.enabled_stages:
            stages[ProcessingStage.CLEANING] = CleaningStage(self.config.cleaning_rules)
        
        if ProcessingStage.STANDARDIZATION in self.config.enabled_stages:
            stages[ProcessingStage.STANDARDIZATION] = StandardizationStage(self.config.standardization_rules)
        
        if ProcessingStage.ANOMALY_DETECTION in self.config.enabled_stages:
            stages[ProcessingStage.ANOMALY_DETECTION] = AnomalyDetectionStage(self.config.anomaly_detection_config)
        
        if ProcessingStage.QUALITY_ASSESSMENT in self.config.enabled_stages:
            stages[ProcessingStage.QUALITY_ASSESSMENT] = QualityAssessmentStage(self.config.quality_thresholds)
        
        return stages

    async def process(self, data: Dict[str, Any], metadata: Dict[str, Any] = None) -> List[ProcessingResult]:
        """处理数据"""
        if metadata is None:
            metadata = {}
        
        results = []
        current_data = data.copy()
        
        try:
            # 按顺序执行各个阶段
            for stage in self.config.enabled_stages:
                if stage in self.stages:
                    self.logger.info(f"执行处理阶段: {stage.value}")
                    
                    # 执行阶段处理
                    result = await asyncio.wait_for(
                        self.stages[stage].process(current_data, metadata),
                        timeout=self.config.timeout
                    )
                    
                    results.append(result)
                    
                    # 如果处理成功，更新数据
                    if result.success:
                        current_data = result.data
                        metadata.update(result.metadata)
                    else:
                        # 如果处理失败，记录错误但继续处理
                        self.logger.error(f"阶段 {stage.value} 处理失败: {result.errors}")
                        if stage == ProcessingStage.VALIDATION:
                            # 验证失败则停止处理
                            break
            
            return results
            
        except asyncio.TimeoutError:
            self.logger.error(f"数据处理超时")
            return results
        except Exception as e:
            self.logger.error(f"数据处理管道异常: {e}")
            return results

    async def process_batch(self, data_list: List[Dict[str, Any]]) -> List[List[ProcessingResult]]:
        """批量处理数据"""
        if self.config.parallel_processing:
            # 并行处理
            semaphore = asyncio.Semaphore(self.config.max_workers)
            
            async def process_single(data):
                async with semaphore:
                    return await self.process(data)
            
            tasks = [process_single(data) for data in data_list]
            return await asyncio.gather(*tasks, return_exceptions=True)
        else:
            # 串行处理
            results = []
            for data in data_list:
                result = await self.process(data)
                results.append(result)
            return results

    def get_stage_statistics(self, results: List[ProcessingResult]) -> Dict[str, Any]:
        """获取阶段统计信息"""
        stats = {}
        
        for stage in ProcessingStage:
            stage_results = [r for r in results if r.stage == stage]
            if stage_results:
                stats[stage.value] = {
                    "count": len(stage_results),
                    "success_rate": sum(1 for r in stage_results if r.success) / len(stage_results),
                    "avg_quality_score": sum(r.quality_score for r in stage_results) / len(stage_results),
                    "avg_confidence_score": sum(r.confidence_score for r in stage_results) / len(stage_results),
                    "avg_processing_time": sum(r.processing_time for r in stage_results) / len(stage_results),
                    "total_errors": sum(len(r.errors) for r in stage_results),
                    "total_warnings": sum(len(r.warnings) for r in stage_results)
                }
        
        return stats


# 预定义的管道配置
DEFAULT_PIPELINE_CONFIG = PipelineConfig(
    enabled_stages=[
        ProcessingStage.VALIDATION,
        ProcessingStage.CLEANING,
    ],
    validation_rules={
        "required_fields": ["user_id", "data_type"],
        "field_types": {
            "user_id": int,
            "data_type": str,
            "timestamp": (str, int, float)
        },
        "value_ranges": {
            "heart_rate": (30, 220),
            "blood_pressure_systolic": (70, 250),
            "blood_pressure_diastolic": (40, 150),
            "body_temperature": (35.0, 42.0),
            "weight": (1.0, 300.0),
            "height": (30.0, 250.0)
        }
    },
    cleaning_rules={
        "remove_null_values": True,
        "numeric_corrections": {
            "heart_rate": {"clamp_range": (30, 220)},
            "body_temperature": {"decimal_places": 1}
        },
        "string_cleaning": {
            "device_id": {"strip": True, "case": "upper"}
        }
    },
    standardization_rules={},
    anomaly_detection_config={},
    quality_thresholds={}
)


# 全局管道实例
pipeline = DataProcessingPipeline(DEFAULT_PIPELINE_CONFIG)


async def process_health_data(data: Dict[str, Any], metadata: Dict[str, Any] = None) -> List[ProcessingResult]:
    """处理健康数据"""
    return await pipeline.process(data, metadata)


@cached(key_prefix="pipeline_stats", expire=300)
async def get_pipeline_statistics() -> Dict[str, Any]:
    """获取管道统计信息（缓存5分钟）"""
    # 这里可以从数据库或缓存中获取历史统计信息
    return {
        "total_processed": 0,
        "success_rate": 0.0,
        "avg_quality_score": 0.0,
        "stage_performance": {}
    } 