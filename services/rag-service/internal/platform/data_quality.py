#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据质量管理器 - 支持数据质量监控、清洗、治理等功能
"""

import asyncio
import time
import json
import re
import hashlib
from typing import Dict, List, Any, Optional, Callable, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
import statistics
from loguru import logger

from ..observability.metrics import MetricsCollector
from ..observability.tracing import trace_operation, SpanKind


class DataQualityDimension(str, Enum):
    """数据质量维度"""
    COMPLETENESS = "completeness"           # 完整性
    ACCURACY = "accuracy"                   # 准确性
    CONSISTENCY = "consistency"             # 一致性
    VALIDITY = "validity"                   # 有效性
    UNIQUENESS = "uniqueness"               # 唯一性
    TIMELINESS = "timeliness"               # 及时性
    RELEVANCE = "relevance"                 # 相关性
    INTEGRITY = "integrity"                 # 完整性


class DataQualityLevel(str, Enum):
    """数据质量等级"""
    EXCELLENT = "excellent"                 # 优秀 (90-100%)
    GOOD = "good"                          # 良好 (80-90%)
    FAIR = "fair"                          # 一般 (70-80%)
    POOR = "poor"                          # 较差 (60-70%)
    CRITICAL = "critical"                   # 严重 (<60%)


class DataIssueType(str, Enum):
    """数据问题类型"""
    MISSING_VALUE = "missing_value"         # 缺失值
    INVALID_FORMAT = "invalid_format"       # 格式无效
    DUPLICATE_RECORD = "duplicate_record"   # 重复记录
    OUTLIER = "outlier"                     # 异常值
    INCONSISTENT_VALUE = "inconsistent_value"  # 不一致值
    STALE_DATA = "stale_data"              # 过期数据
    ENCODING_ERROR = "encoding_error"       # 编码错误
    SCHEMA_VIOLATION = "schema_violation"   # 模式违反


@dataclass
class DataQualityRule:
    """数据质量规则"""
    id: str
    name: str
    description: str
    dimension: DataQualityDimension
    field_name: str
    rule_type: str                          # regex, range, enum, custom
    rule_config: Dict[str, Any]
    severity: str = "medium"                # low, medium, high, critical
    enabled: bool = True
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "dimension": self.dimension.value,
            "field_name": self.field_name,
            "rule_type": self.rule_type,
            "rule_config": self.rule_config,
            "severity": self.severity,
            "enabled": self.enabled,
            "tags": self.tags
        }


@dataclass
class DataQualityIssue:
    """数据质量问题"""
    id: str
    rule_id: str
    rule_name: str
    issue_type: DataIssueType
    dimension: DataQualityDimension
    field_name: str
    record_id: Optional[str]
    issue_value: Any
    expected_value: Optional[Any]
    severity: str
    description: str
    created_at: float = field(default_factory=time.time)
    resolved_at: Optional[float] = None
    resolution_action: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "issue_type": self.issue_type.value,
            "dimension": self.dimension.value,
            "field_name": self.field_name,
            "record_id": self.record_id,
            "issue_value": self.issue_value,
            "expected_value": self.expected_value,
            "severity": self.severity,
            "description": self.description,
            "created_at": self.created_at,
            "resolved_at": self.resolved_at,
            "resolution_action": self.resolution_action,
            "metadata": self.metadata
        }


@dataclass
class DataQualityMetrics:
    """数据质量指标"""
    dimension: DataQualityDimension
    field_name: str
    total_records: int
    valid_records: int
    invalid_records: int
    quality_score: float                    # 0-100
    quality_level: DataQualityLevel
    issues_count: int
    last_updated: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "dimension": self.dimension.value,
            "field_name": self.field_name,
            "total_records": self.total_records,
            "valid_records": self.valid_records,
            "invalid_records": self.invalid_records,
            "quality_score": self.quality_score,
            "quality_level": self.quality_level.value,
            "issues_count": self.issues_count,
            "last_updated": self.last_updated
        }


class DataValidator:
    """数据验证器"""
    
    def __init__(self):
        self.validators = {
            "regex": self._validate_regex,
            "range": self._validate_range,
            "enum": self._validate_enum,
            "length": self._validate_length,
            "type": self._validate_type,
            "custom": self._validate_custom
        }
    
    async def validate_field(
        self, 
        value: Any, 
        rule: DataQualityRule
    ) -> Tuple[bool, Optional[str]]:
        """验证字段值"""
        if rule.rule_type not in self.validators:
            return False, f"不支持的验证类型: {rule.rule_type}"
        
        try:
            validator = self.validators[rule.rule_type]
            return await validator(value, rule.rule_config)
        except Exception as e:
            return False, f"验证异常: {str(e)}"
    
    async def _validate_regex(self, value: Any, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """正则表达式验证"""
        if value is None:
            return not config.get("required", False), "值为空"
        
        pattern = config.get("pattern", "")
        if not pattern:
            return False, "缺少正则表达式模式"
        
        try:
            if re.match(pattern, str(value)):
                return True, None
            else:
                return False, f"值 '{value}' 不匹配模式 '{pattern}'"
        except re.error as e:
            return False, f"正则表达式错误: {e}"
    
    async def _validate_range(self, value: Any, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """范围验证"""
        if value is None:
            return not config.get("required", False), "值为空"
        
        try:
            num_value = float(value)
            min_val = config.get("min")
            max_val = config.get("max")
            
            if min_val is not None and num_value < min_val:
                return False, f"值 {num_value} 小于最小值 {min_val}"
            
            if max_val is not None and num_value > max_val:
                return False, f"值 {num_value} 大于最大值 {max_val}"
            
            return True, None
            
        except (ValueError, TypeError):
            return False, f"值 '{value}' 不是有效数字"
    
    async def _validate_enum(self, value: Any, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """枚举值验证"""
        if value is None:
            return not config.get("required", False), "值为空"
        
        allowed_values = config.get("values", [])
        if value in allowed_values:
            return True, None
        else:
            return False, f"值 '{value}' 不在允许的值列表中: {allowed_values}"
    
    async def _validate_length(self, value: Any, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """长度验证"""
        if value is None:
            return not config.get("required", False), "值为空"
        
        try:
            length = len(str(value))
            min_len = config.get("min", 0)
            max_len = config.get("max", float('inf'))
            
            if length < min_len:
                return False, f"长度 {length} 小于最小长度 {min_len}"
            
            if length > max_len:
                return False, f"长度 {length} 大于最大长度 {max_len}"
            
            return True, None
            
        except Exception:
            return False, f"无法计算值 '{value}' 的长度"
    
    async def _validate_type(self, value: Any, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """类型验证"""
        if value is None:
            return not config.get("required", False), "值为空"
        
        expected_type = config.get("type", "str")
        type_mapping = {
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict
        }
        
        if expected_type not in type_mapping:
            return False, f"不支持的类型: {expected_type}"
        
        expected_class = type_mapping[expected_type]
        
        if isinstance(value, expected_class):
            return True, None
        else:
            return False, f"值 '{value}' 不是期望的类型 {expected_type}"
    
    async def _validate_custom(self, value: Any, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """自定义验证"""
        # 这里可以实现自定义验证逻辑
        # 例如：调用外部验证函数、复杂业务规则等
        return True, None


class DataCleaner:
    """数据清洗器"""
    
    def __init__(self):
        self.cleaners = {
            "trim": self._clean_trim,
            "normalize": self._clean_normalize,
            "remove_duplicates": self._clean_remove_duplicates,
            "fill_missing": self._clean_fill_missing,
            "fix_encoding": self._clean_fix_encoding,
            "standardize_format": self._clean_standardize_format
        }
    
    async def clean_data(
        self, 
        data: List[Dict[str, Any]], 
        cleaning_rules: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """清洗数据"""
        cleaned_data = data.copy()
        
        for rule in cleaning_rules:
            cleaner_type = rule.get("type")
            if cleaner_type in self.cleaners:
                cleaner = self.cleaners[cleaner_type]
                cleaned_data = await cleaner(cleaned_data, rule.get("config", {}))
        
        return cleaned_data
    
    async def _clean_trim(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """去除空白字符"""
        fields = config.get("fields", [])
        
        for record in data:
            for field in fields:
                if field in record and isinstance(record[field], str):
                    record[field] = record[field].strip()
        
        return data
    
    async def _clean_normalize(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """标准化数据"""
        fields = config.get("fields", [])
        case_type = config.get("case", "lower")  # lower, upper, title
        
        for record in data:
            for field in fields:
                if field in record and isinstance(record[field], str):
                    if case_type == "lower":
                        record[field] = record[field].lower()
                    elif case_type == "upper":
                        record[field] = record[field].upper()
                    elif case_type == "title":
                        record[field] = record[field].title()
        
        return data
    
    async def _clean_remove_duplicates(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """去除重复记录"""
        key_fields = config.get("key_fields", [])
        
        if not key_fields:
            # 基于所有字段去重
            seen = set()
            unique_data = []
            
            for record in data:
                record_hash = hashlib.md5(json.dumps(record, sort_keys=True).encode()).hexdigest()
                if record_hash not in seen:
                    seen.add(record_hash)
                    unique_data.append(record)
            
            return unique_data
        else:
            # 基于指定字段去重
            seen = set()
            unique_data = []
            
            for record in data:
                key_values = tuple(record.get(field) for field in key_fields)
                if key_values not in seen:
                    seen.add(key_values)
                    unique_data.append(record)
            
            return unique_data
    
    async def _clean_fill_missing(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """填充缺失值"""
        field_configs = config.get("fields", {})
        
        for record in data:
            for field, fill_config in field_configs.items():
                if field not in record or record[field] is None or record[field] == "":
                    fill_method = fill_config.get("method", "default")
                    
                    if fill_method == "default":
                        record[field] = fill_config.get("value", "")
                    elif fill_method == "mean":
                        # 计算平均值（仅适用于数值字段）
                        values = [r.get(field) for r in data if r.get(field) is not None]
                        numeric_values = []
                        for v in values:
                            try:
                                numeric_values.append(float(v))
                            except (ValueError, TypeError):
                                pass
                        if numeric_values:
                            record[field] = statistics.mean(numeric_values)
                    elif fill_method == "mode":
                        # 计算众数
                        values = [r.get(field) for r in data if r.get(field) is not None]
                        if values:
                            counter = Counter(values)
                            record[field] = counter.most_common(1)[0][0]
        
        return data
    
    async def _clean_fix_encoding(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """修复编码问题"""
        fields = config.get("fields", [])
        source_encoding = config.get("source_encoding", "utf-8")
        target_encoding = config.get("target_encoding", "utf-8")
        
        for record in data:
            for field in fields:
                if field in record and isinstance(record[field], str):
                    try:
                        # 尝试修复编码
                        if source_encoding != target_encoding:
                            encoded = record[field].encode(source_encoding)
                            record[field] = encoded.decode(target_encoding)
                    except (UnicodeEncodeError, UnicodeDecodeError):
                        # 编码修复失败，保持原值
                        pass
        
        return data
    
    async def _clean_standardize_format(self, data: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """标准化格式"""
        field_formats = config.get("fields", {})
        
        for record in data:
            for field, format_config in field_formats.items():
                if field in record and record[field] is not None:
                    format_type = format_config.get("type")
                    
                    if format_type == "date":
                        # 日期格式标准化
                        try:
                            from datetime import datetime
                            input_format = format_config.get("input_format", "%Y-%m-%d")
                            output_format = format_config.get("output_format", "%Y-%m-%d")
                            
                            dt = datetime.strptime(str(record[field]), input_format)
                            record[field] = dt.strftime(output_format)
                        except ValueError:
                            pass
                    
                    elif format_type == "phone":
                        # 电话号码格式标准化
                        phone = re.sub(r'[^\d]', '', str(record[field]))
                        if len(phone) == 11 and phone.startswith('1'):
                            record[field] = f"{phone[:3]}-{phone[3:7]}-{phone[7:]}"
        
        return data


class DataProfiler:
    """数据分析器"""
    
    def __init__(self):
        pass
    
    async def profile_dataset(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析数据集"""
        if not data:
            return {"error": "数据集为空"}
        
        profile = {
            "total_records": len(data),
            "fields": {},
            "data_types": {},
            "missing_values": {},
            "unique_values": {},
            "value_distributions": {},
            "quality_summary": {}
        }
        
        # 获取所有字段
        all_fields = set()
        for record in data:
            all_fields.update(record.keys())
        
        # 分析每个字段
        for field in all_fields:
            field_values = [record.get(field) for record in data]
            
            # 基本统计
            profile["fields"][field] = {
                "total_count": len(field_values),
                "non_null_count": sum(1 for v in field_values if v is not None),
                "null_count": sum(1 for v in field_values if v is None),
                "unique_count": len(set(v for v in field_values if v is not None))
            }
            
            # 数据类型分析
            type_counts = defaultdict(int)
            for value in field_values:
                if value is not None:
                    type_counts[type(value).__name__] += 1
            profile["data_types"][field] = dict(type_counts)
            
            # 缺失值比例
            null_ratio = profile["fields"][field]["null_count"] / len(field_values)
            profile["missing_values"][field] = {
                "count": profile["fields"][field]["null_count"],
                "ratio": null_ratio
            }
            
            # 唯一值分析
            non_null_values = [v for v in field_values if v is not None]
            if non_null_values:
                unique_ratio = len(set(non_null_values)) / len(non_null_values)
                profile["unique_values"][field] = {
                    "count": len(set(non_null_values)),
                    "ratio": unique_ratio
                }
                
                # 值分布（前10个最常见的值）
                value_counts = Counter(non_null_values)
                profile["value_distributions"][field] = dict(value_counts.most_common(10))
        
        # 质量总结
        profile["quality_summary"] = await self._calculate_quality_summary(profile)
        
        return profile
    
    async def _calculate_quality_summary(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """计算质量总结"""
        total_fields = len(profile["fields"])
        if total_fields == 0:
            return {}
        
        # 完整性评分（基于缺失值）
        completeness_scores = []
        for field, missing_info in profile["missing_values"].items():
            completeness_scores.append(1.0 - missing_info["ratio"])
        
        avg_completeness = statistics.mean(completeness_scores) if completeness_scores else 0
        
        # 唯一性评分
        uniqueness_scores = []
        for field, unique_info in profile["unique_values"].items():
            uniqueness_scores.append(min(unique_info["ratio"], 1.0))
        
        avg_uniqueness = statistics.mean(uniqueness_scores) if uniqueness_scores else 0
        
        # 总体质量评分
        overall_score = (avg_completeness * 0.6 + avg_uniqueness * 0.4) * 100
        
        return {
            "completeness_score": avg_completeness * 100,
            "uniqueness_score": avg_uniqueness * 100,
            "overall_score": overall_score,
            "quality_level": self._get_quality_level(overall_score)
        }
    
    def _get_quality_level(self, score: float) -> str:
        """获取质量等级"""
        if score >= 90:
            return DataQualityLevel.EXCELLENT.value
        elif score >= 80:
            return DataQualityLevel.GOOD.value
        elif score >= 70:
            return DataQualityLevel.FAIR.value
        elif score >= 60:
            return DataQualityLevel.POOR.value
        else:
            return DataQualityLevel.CRITICAL.value


class DataQualityManager:
    """数据质量管理器"""
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        self.metrics_collector = metrics_collector
        
        # 组件
        self.validator = DataValidator()
        self.cleaner = DataCleaner()
        self.profiler = DataProfiler()
        
        # 规则和问题
        self.rules: Dict[str, DataQualityRule] = {}
        self.issues: List[DataQualityIssue] = []
        self.metrics: Dict[str, DataQualityMetrics] = {}
        
        # 配置
        self.auto_clean = True
        self.issue_retention_days = 30
        
        # 后台任务
        self._monitoring_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # 运行状态
        self.running = False
    
    async def start(self):
        """启动数据质量管理器"""
        if self.running:
            return
        
        self.running = True
        
        # 启动后台任务
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("数据质量管理器已启动")
    
    async def stop(self):
        """停止数据质量管理器"""
        if not self.running:
            return
        
        self.running = False
        
        # 停止后台任务
        if self._monitoring_task:
            self._monitoring_task.cancel()
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        logger.info("数据质量管理器已停止")
    
    def add_rule(self, rule: DataQualityRule):
        """添加数据质量规则"""
        self.rules[rule.id] = rule
        logger.info(f"添加数据质量规则: {rule.name}")
    
    def remove_rule(self, rule_id: str) -> bool:
        """移除数据质量规则"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"移除数据质量规则: {rule_id}")
            return True
        return False
    
    @trace_operation("data_quality.validate", SpanKind.INTERNAL)
    async def validate_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """验证数据质量"""
        validation_results = {
            "total_records": len(data),
            "valid_records": 0,
            "invalid_records": 0,
            "issues": [],
            "metrics": {},
            "overall_score": 0.0
        }
        
        if not data:
            return validation_results
        
        # 按字段分组规则
        field_rules = defaultdict(list)
        for rule in self.rules.values():
            if rule.enabled:
                field_rules[rule.field_name].append(rule)
        
        # 验证每条记录
        record_issues = []
        for i, record in enumerate(data):
            record_id = record.get("id", str(i))
            record_valid = True
            
            for field_name, rules in field_rules.items():
                field_value = record.get(field_name)
                
                for rule in rules:
                    is_valid, error_message = await self.validator.validate_field(field_value, rule)
                    
                    if not is_valid:
                        record_valid = False
                        issue = DataQualityIssue(
                            id=f"{rule.id}_{record_id}_{int(time.time())}",
                            rule_id=rule.id,
                            rule_name=rule.name,
                            issue_type=self._get_issue_type(rule.rule_type),
                            dimension=rule.dimension,
                            field_name=field_name,
                            record_id=record_id,
                            issue_value=field_value,
                            expected_value=None,
                            severity=rule.severity,
                            description=error_message or "验证失败",
                            metadata={"record_index": i}
                        )
                        record_issues.append(issue)
                        validation_results["issues"].append(issue.to_dict())
            
            if record_valid:
                validation_results["valid_records"] += 1
            else:
                validation_results["invalid_records"] += 1
        
        # 保存问题
        self.issues.extend(record_issues)
        
        # 计算指标
        validation_results["metrics"] = await self._calculate_validation_metrics(data, field_rules)
        
        # 计算总体评分
        if validation_results["total_records"] > 0:
            validation_results["overall_score"] = (
                validation_results["valid_records"] / validation_results["total_records"]
            ) * 100
        
        # 记录指标
        if self.metrics_collector:
            await self.metrics_collector.record_histogram(
                "data_quality_score",
                validation_results["overall_score"],
                {"validation_type": "full"}
            )
            
            await self.metrics_collector.increment_counter(
                "data_quality_issues",
                {"count": len(record_issues)}
            )
        
        logger.info(f"数据质量验证完成: {validation_results['overall_score']:.2f}%")
        return validation_results
    
    async def clean_data(
        self, 
        data: List[Dict[str, Any]], 
        cleaning_rules: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """清洗数据"""
        if not cleaning_rules:
            # 使用默认清洗规则
            cleaning_rules = [
                {"type": "trim", "config": {"fields": ["*"]}},
                {"type": "remove_duplicates", "config": {}},
                {"type": "fill_missing", "config": {"fields": {}}}
            ]
        
        cleaned_data = await self.cleaner.clean_data(data, cleaning_rules)
        
        logger.info(f"数据清洗完成: {len(data)} -> {len(cleaned_data)} 条记录")
        return cleaned_data
    
    async def profile_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析数据"""
        profile = await self.profiler.profile_dataset(data)
        
        logger.info(f"数据分析完成: {profile.get('total_records', 0)} 条记录")
        return profile
    
    async def _calculate_validation_metrics(
        self, 
        data: List[Dict[str, Any]], 
        field_rules: Dict[str, List[DataQualityRule]]
    ) -> Dict[str, Any]:
        """计算验证指标"""
        metrics = {}
        
        for field_name, rules in field_rules.items():
            field_values = [record.get(field_name) for record in data]
            
            for rule in rules:
                valid_count = 0
                total_count = len(field_values)
                
                for value in field_values:
                    is_valid, _ = await self.validator.validate_field(value, rule)
                    if is_valid:
                        valid_count += 1
                
                quality_score = (valid_count / total_count) * 100 if total_count > 0 else 0
                quality_level = self._get_quality_level_from_score(quality_score)
                
                metric = DataQualityMetrics(
                    dimension=rule.dimension,
                    field_name=field_name,
                    total_records=total_count,
                    valid_records=valid_count,
                    invalid_records=total_count - valid_count,
                    quality_score=quality_score,
                    quality_level=quality_level,
                    issues_count=total_count - valid_count
                )
                
                metrics[f"{rule.dimension.value}_{field_name}"] = metric.to_dict()
                self.metrics[f"{rule.dimension.value}_{field_name}"] = metric
        
        return metrics
    
    def _get_issue_type(self, rule_type: str) -> DataIssueType:
        """根据规则类型获取问题类型"""
        type_mapping = {
            "regex": DataIssueType.INVALID_FORMAT,
            "range": DataIssueType.OUTLIER,
            "enum": DataIssueType.INVALID_FORMAT,
            "length": DataIssueType.INVALID_FORMAT,
            "type": DataIssueType.INVALID_FORMAT,
            "custom": DataIssueType.SCHEMA_VIOLATION
        }
        return type_mapping.get(rule_type, DataIssueType.SCHEMA_VIOLATION)
    
    def _get_quality_level_from_score(self, score: float) -> DataQualityLevel:
        """根据评分获取质量等级"""
        if score >= 90:
            return DataQualityLevel.EXCELLENT
        elif score >= 80:
            return DataQualityLevel.GOOD
        elif score >= 70:
            return DataQualityLevel.FAIR
        elif score >= 60:
            return DataQualityLevel.POOR
        else:
            return DataQualityLevel.CRITICAL
    
    async def _monitoring_loop(self):
        """监控循环"""
        while self.running:
            try:
                await asyncio.sleep(300)  # 5分钟监控一次
                
                # 这里可以添加定期监控逻辑
                # 例如：检查数据质量趋势、发送告警等
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"监控循环错误: {e}")
    
    async def _cleanup_loop(self):
        """清理循环"""
        while self.running:
            try:
                await asyncio.sleep(3600)  # 每小时清理一次
                
                current_time = time.time()
                retention_threshold = current_time - (self.issue_retention_days * 24 * 3600)
                
                # 清理过期问题
                self.issues = [
                    issue for issue in self.issues
                    if issue.created_at > retention_threshold
                ]
                
                logger.info("完成数据质量问题清理")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"清理循环错误: {e}")
    
    def get_quality_summary(self) -> Dict[str, Any]:
        """获取质量总结"""
        total_issues = len(self.issues)
        
        # 按严重程度统计
        severity_counts = defaultdict(int)
        for issue in self.issues:
            severity_counts[issue.severity] += 1
        
        # 按维度统计
        dimension_counts = defaultdict(int)
        for issue in self.issues:
            dimension_counts[issue.dimension.value] += 1
        
        # 按类型统计
        type_counts = defaultdict(int)
        for issue in self.issues:
            type_counts[issue.issue_type.value] += 1
        
        # 计算平均质量评分
        if self.metrics:
            avg_score = statistics.mean([m.quality_score for m in self.metrics.values()])
        else:
            avg_score = 0.0
        
        return {
            "total_issues": total_issues,
            "total_rules": len(self.rules),
            "average_quality_score": avg_score,
            "severity_distribution": dict(severity_counts),
            "dimension_distribution": dict(dimension_counts),
            "type_distribution": dict(type_counts),
            "quality_level": self._get_quality_level_from_score(avg_score).value
        }


# 全局数据质量管理器实例
_data_quality_manager: Optional[DataQualityManager] = None


def initialize_data_quality_manager(
    metrics_collector: Optional[MetricsCollector] = None
) -> DataQualityManager:
    """初始化数据质量管理器"""
    global _data_quality_manager
    _data_quality_manager = DataQualityManager(metrics_collector)
    return _data_quality_manager


def get_data_quality_manager() -> Optional[DataQualityManager]:
    """获取数据质量管理器实例"""
    return _data_quality_manager


# 便捷函数
def create_completeness_rule(
    rule_id: str,
    field_name: str,
    required: bool = True
) -> DataQualityRule:
    """创建完整性规则"""
    return DataQualityRule(
        id=rule_id,
        name=f"完整性检查: {field_name}",
        description=f"检查字段 {field_name} 是否完整",
        dimension=DataQualityDimension.COMPLETENESS,
        field_name=field_name,
        rule_type="custom",
        rule_config={"required": required}
    )


def create_format_rule(
    rule_id: str,
    field_name: str,
    pattern: str,
    description: str = ""
) -> DataQualityRule:
    """创建格式验证规则"""
    return DataQualityRule(
        id=rule_id,
        name=f"格式检查: {field_name}",
        description=description or f"检查字段 {field_name} 的格式",
        dimension=DataQualityDimension.VALIDITY,
        field_name=field_name,
        rule_type="regex",
        rule_config={"pattern": pattern}
    )


def create_range_rule(
    rule_id: str,
    field_name: str,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None
) -> DataQualityRule:
    """创建范围验证规则"""
    return DataQualityRule(
        id=rule_id,
        name=f"范围检查: {field_name}",
        description=f"检查字段 {field_name} 的值范围",
        dimension=DataQualityDimension.VALIDITY,
        field_name=field_name,
        rule_type="range",
        rule_config={"min": min_val, "max": max_val}
    ) 