#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A/B测试框架 - 用于测试不同的RAG策略和中医算法
"""

import time
import uuid
import hashlib
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import random
from loguru import logger

from ..observability.metrics import MetricsCollector

class ExperimentStatus(str, Enum):
    """实验状态"""
    DRAFT = "draft"             # 草稿
    ACTIVE = "active"           # 活跃
    PAUSED = "paused"           # 暂停
    COMPLETED = "completed"     # 完成
    CANCELLED = "cancelled"     # 取消

class TrafficSplitType(str, Enum):
    """流量分割类型"""
    RANDOM = "random"           # 随机分割
    USER_ID = "user_id"         # 基于用户ID
    SESSION_ID = "session_id"   # 基于会话ID
    GEOGRAPHIC = "geographic"   # 基于地理位置
    DEVICE_TYPE = "device_type" # 基于设备类型

class MetricType(str, Enum):
    """指标类型"""
    CONVERSION = "conversion"   # 转化率
    ENGAGEMENT = "engagement"   # 参与度
    PERFORMANCE = "performance" # 性能
    ACCURACY = "accuracy"       # 准确性
    SATISFACTION = "satisfaction" # 满意度

@dataclass
class ExperimentVariant:
    """实验变体"""
    id: str
    name: str
    description: str
    traffic_percentage: float   # 流量百分比 (0-100)
    config: Dict[str, Any]      # 变体配置
    is_control: bool = False    # 是否为对照组
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "traffic_percentage": self.traffic_percentage,
            "config": self.config,
            "is_control": self.is_control
        }

@dataclass
class ExperimentMetric:
    """实验指标"""
    name: str
    type: MetricType
    description: str
    target_value: Optional[float] = None    # 目标值
    improvement_threshold: float = 0.05     # 改进阈值
    statistical_significance: float = 0.95  # 统计显著性
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "type": self.type.value,
            "description": self.description,
            "target_value": self.target_value,
            "improvement_threshold": self.improvement_threshold,
            "statistical_significance": self.statistical_significance
        }

@dataclass
class Experiment:
    """实验定义"""
    id: str
    name: str
    description: str
    variants: List[ExperimentVariant]
    metrics: List[ExperimentMetric]
    traffic_split_type: TrafficSplitType = TrafficSplitType.RANDOM
    status: ExperimentStatus = ExperimentStatus.DRAFT
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    creator: str = "system"
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """验证实验配置"""
        # 验证流量分配总和为100%
        total_traffic = sum(v.traffic_percentage for v in self.variants)
        if abs(total_traffic - 100.0) > 0.01:
            raise ValueError(f"流量分配总和必须为100%，当前为{total_traffic}%")
        
        # 确保有且仅有一个对照组
        control_count = sum(1 for v in self.variants if v.is_control)
        if control_count != 1:
            raise ValueError(f"必须有且仅有一个对照组，当前有{control_count}个")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "variants": [v.to_dict() for v in self.variants],
            "metrics": [m.to_dict() for m in self.metrics],
            "traffic_split_type": self.traffic_split_type.value,
            "status": self.status.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "creator": self.creator,
            "tags": self.tags
        }

@dataclass
class ExperimentResult:
    """实验结果"""
    experiment_id: str
    variant_id: str
    user_id: str
    session_id: str
    timestamp: float
    metrics: Dict[str, float]   # 指标值
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "experiment_id": self.experiment_id,
            "variant_id": self.variant_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "metrics": self.metrics,
            "metadata": self.metadata
        }

@dataclass
class VariantStatistics:
    """变体统计"""
    variant_id: str
    sample_size: int
    metrics: Dict[str, Dict[str, float]]  # 指标名 -> {mean, std, min, max, count}
    conversion_rate: float = 0.0
    confidence_interval: Dict[str, tuple] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "variant_id": self.variant_id,
            "sample_size": self.sample_size,
            "metrics": self.metrics,
            "conversion_rate": self.conversion_rate,
            "confidence_interval": self.confidence_interval
        }

class TrafficSplitter:
    """流量分割器"""
    
    def __init__(self, split_type: TrafficSplitType = TrafficSplitType.RANDOM):
        self.split_type = split_type
    
    def assign_variant(
        self,
        experiment: Experiment,
        user_id: str,
        session_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ExperimentVariant:
        """分配变体"""
        if self.split_type == TrafficSplitType.RANDOM:
            return self._random_assignment(experiment)
        elif self.split_type == TrafficSplitType.USER_ID:
            return self._hash_assignment(experiment, user_id)
        elif self.split_type == TrafficSplitType.SESSION_ID:
            return self._hash_assignment(experiment, session_id)
        else:
            return self._random_assignment(experiment)
    
    def _random_assignment(self, experiment: Experiment) -> ExperimentVariant:
        """随机分配"""
        rand_value = random.random() * 100
        cumulative = 0.0
        
        for variant in experiment.variants:
            cumulative += variant.traffic_percentage
            if rand_value <= cumulative:
                return variant
        
        # 默认返回第一个变体
        return experiment.variants[0]
    
    def _hash_assignment(self, experiment: Experiment, key: str) -> ExperimentVariant:
        """基于哈希的确定性分配"""
        # 使用实验ID和key生成哈希
        hash_input = f"{experiment.id}:{key}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        bucket = (hash_value % 10000) / 100.0  # 0-100的值
        
        cumulative = 0.0
        for variant in experiment.variants:
            cumulative += variant.traffic_percentage
            if bucket <= cumulative:
                return variant
        
        return experiment.variants[0]

class ExperimentStorage:
    """实验存储"""
    
    def __init__(self):
        self.experiments: Dict[str, Experiment] = {}
        self.results: List[ExperimentResult] = []
        self.assignments: Dict[str, Dict[str, str]] = {}  # user_id -> {experiment_id: variant_id}
    
    async def save_experiment(self, experiment: Experiment) -> bool:
        """保存实验"""
        try:
            experiment.updated_at = time.time()
            self.experiments[experiment.id] = experiment
            logger.info(f"实验已保存: {experiment.name} ({experiment.id})")
            return True
        except Exception as e:
            logger.error(f"实验保存失败: {e}")
            return False
    
    async def get_experiment(self, experiment_id: str) -> Optional[Experiment]:
        """获取实验"""
        return self.experiments.get(experiment_id)
    
    async def get_active_experiments(self) -> List[Experiment]:
        """获取活跃实验"""
        return [exp for exp in self.experiments.values() if exp.status == ExperimentStatus.ACTIVE]
    
    async def save_result(self, result: ExperimentResult) -> bool:
        """保存实验结果"""
        try:
            self.results.append(result)
            return True
        except Exception as e:
            logger.error(f"实验结果保存失败: {e}")
            return False
    
    async def get_results(
        self,
        experiment_id: str,
        variant_id: Optional[str] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> List[ExperimentResult]:
        """获取实验结果"""
        results = [r for r in self.results if r.experiment_id == experiment_id]
        
        if variant_id:
            results = [r for r in results if r.variant_id == variant_id]
        
        if start_time:
            results = [r for r in results if r.timestamp >= start_time]
        
        if end_time:
            results = [r for r in results if r.timestamp <= end_time]
        
        return results
    
    async def save_assignment(self, user_id: str, experiment_id: str, variant_id: str):
        """保存用户分配"""
        if user_id not in self.assignments:
            self.assignments[user_id] = {}
        self.assignments[user_id][experiment_id] = variant_id
    
    async def get_assignment(self, user_id: str, experiment_id: str) -> Optional[str]:
        """获取用户分配"""
        return self.assignments.get(user_id, {}).get(experiment_id)

class StatisticalAnalyzer:
    """统计分析器"""
    
    def __init__(self):
        pass
    
    async def calculate_variant_statistics(
        self,
        results: List[ExperimentResult],
        metric_names: List[str]
    ) -> VariantStatistics:
        """计算变体统计"""
        if not results:
            return VariantStatistics(
                variant_id="unknown",
                sample_size=0,
                metrics={}
            )
        
        variant_id = results[0].variant_id
        sample_size = len(results)
        
        # 计算各指标统计
        metrics_stats = {}
        for metric_name in metric_names:
            values = [r.metrics.get(metric_name, 0) for r in results if metric_name in r.metrics]
            
            if values:
                metrics_stats[metric_name] = {
                    "mean": sum(values) / len(values),
                    "std": self._calculate_std(values),
                    "min": min(values),
                    "max": max(values),
                    "count": len(values)
                }
            else:
                metrics_stats[metric_name] = {
                    "mean": 0, "std": 0, "min": 0, "max": 0, "count": 0
                }
        
        # 计算转化率（假设有conversion指标）
        conversion_rate = 0.0
        if "conversion" in metrics_stats:
            conversion_rate = metrics_stats["conversion"]["mean"]
        
        return VariantStatistics(
            variant_id=variant_id,
            sample_size=sample_size,
            metrics=metrics_stats,
            conversion_rate=conversion_rate
        )
    
    def _calculate_std(self, values: List[float]) -> float:
        """计算标准差"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5
    
    async def compare_variants(
        self,
        control_stats: VariantStatistics,
        treatment_stats: VariantStatistics,
        metric_name: str
    ) -> Dict[str, Any]:
        """比较变体"""
        if metric_name not in control_stats.metrics or metric_name not in treatment_stats.metrics:
            return {"error": f"指标 {metric_name} 不存在"}
        
        control_mean = control_stats.metrics[metric_name]["mean"]
        treatment_mean = treatment_stats.metrics[metric_name]["mean"]
        
        # 计算改进百分比
        if control_mean != 0:
            improvement = (treatment_mean - control_mean) / control_mean * 100
        else:
            improvement = 0.0
        
        # 简化的统计显著性检验（实际应该使用t检验等）
        control_std = control_stats.metrics[metric_name]["std"]
        treatment_std = treatment_stats.metrics[metric_name]["std"]
        
        # 计算标准误差
        control_se = control_std / (control_stats.sample_size ** 0.5) if control_stats.sample_size > 0 else 0
        treatment_se = treatment_std / (treatment_stats.sample_size ** 0.5) if treatment_stats.sample_size > 0 else 0
        
        # 计算z分数
        pooled_se = (control_se ** 2 + treatment_se ** 2) ** 0.5
        z_score = (treatment_mean - control_mean) / pooled_se if pooled_se > 0 else 0
        
        # 简化的p值计算
        p_value = 2 * (1 - self._normal_cdf(abs(z_score)))
        
        return {
            "control_mean": control_mean,
            "treatment_mean": treatment_mean,
            "improvement_percent": improvement,
            "z_score": z_score,
            "p_value": p_value,
            "is_significant": p_value < 0.05,
            "sample_sizes": {
                "control": control_stats.sample_size,
                "treatment": treatment_stats.sample_size
            }
        }
    
    def _normal_cdf(self, x: float) -> float:
        """正态分布累积分布函数的近似"""
        # 简化实现，实际应该使用更精确的算法
        return 0.5 * (1 + self._erf(x / (2 ** 0.5)))
    
    def _erf(self, x: float) -> float:
        """误差函数的近似"""
        # 简化实现
        a1 =  0.254829592
        a2 = -0.284496736
        a3 =  1.421413741
        a4 = -1.453152027
        a5 =  1.061405429
        p  =  0.3275911
        
        sign = 1 if x >= 0 else -1
        x = abs(x)
        
        t = 1.0 / (1.0 + p * x)
        y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * ((-x * x) ** 0.5).real
        
        return sign * y

class ABTestingFramework:
    """A/B测试框架主类"""
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None):
        self.storage = ExperimentStorage()
        self.splitter = TrafficSplitter()
        self.analyzer = StatisticalAnalyzer()
        self.metrics_collector = metrics_collector
        self.active_experiments_cache: Dict[str, Experiment] = {}
        self.cache_ttl = 300  # 5分钟缓存
        self.last_cache_update = 0
    
    async def create_experiment(
        self,
        name: str,
        description: str,
        variants: List[ExperimentVariant],
        metrics: List[ExperimentMetric],
        traffic_split_type: TrafficSplitType = TrafficSplitType.RANDOM,
        creator: str = "system",
        tags: Optional[List[str]] = None
    ) -> str:
        """创建实验"""
        experiment_id = str(uuid.uuid4())
        
        experiment = Experiment(
            id=experiment_id,
            name=name,
            description=description,
            variants=variants,
            metrics=metrics,
            traffic_split_type=traffic_split_type,
            creator=creator,
            tags=tags or []
        )
        
        success = await self.storage.save_experiment(experiment)
        
        if success:
            logger.info(f"实验创建成功: {name} ({experiment_id})")
            
            # 记录指标
            if self.metrics_collector:
                await self.metrics_collector.increment_counter(
                    "ab_test_experiments_created",
                    {"creator": creator}
                )
        else:
            logger.error(f"实验创建失败: {name}")
        
        return experiment_id
    
    async def start_experiment(self, experiment_id: str) -> bool:
        """启动实验"""
        experiment = await self.storage.get_experiment(experiment_id)
        if not experiment:
            logger.error(f"实验不存在: {experiment_id}")
            return False
        
        experiment.status = ExperimentStatus.ACTIVE
        experiment.start_time = time.time()
        
        success = await self.storage.save_experiment(experiment)
        
        if success:
            # 清除缓存
            self.active_experiments_cache.clear()
            logger.info(f"实验已启动: {experiment.name} ({experiment_id})")
            
            # 记录指标
            if self.metrics_collector:
                await self.metrics_collector.increment_counter(
                    "ab_test_experiments_started",
                    {"experiment": experiment.name}
                )
        
        return success
    
    async def stop_experiment(self, experiment_id: str) -> bool:
        """停止实验"""
        experiment = await self.storage.get_experiment(experiment_id)
        if not experiment:
            return False
        
        experiment.status = ExperimentStatus.COMPLETED
        experiment.end_time = time.time()
        
        success = await self.storage.save_experiment(experiment)
        
        if success:
            # 清除缓存
            self.active_experiments_cache.clear()
            logger.info(f"实验已停止: {experiment.name} ({experiment_id})")
        
        return success
    
    async def get_variant_for_user(
        self,
        user_id: str,
        session_id: str,
        experiment_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """为用户获取实验变体"""
        # 更新活跃实验缓存
        await self._update_active_experiments_cache()
        
        # 如果指定了实验名称，只查找该实验
        if experiment_name:
            experiment = None
            for exp in self.active_experiments_cache.values():
                if exp.name == experiment_name:
                    experiment = exp
                    break
            
            if not experiment:
                return None
            
            return await self._assign_user_to_experiment(user_id, session_id, experiment, context)
        
        # 否则为所有活跃实验分配变体
        assignments = {}
        for experiment in self.active_experiments_cache.values():
            variant_info = await self._assign_user_to_experiment(user_id, session_id, experiment, context)
            if variant_info:
                assignments[experiment.name] = variant_info
        
        return assignments if assignments else None
    
    async def _assign_user_to_experiment(
        self,
        user_id: str,
        session_id: str,
        experiment: Experiment,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """为用户分配实验变体"""
        # 检查是否已有分配
        existing_assignment = await self.storage.get_assignment(user_id, experiment.id)
        
        if existing_assignment:
            # 找到对应的变体
            variant = None
            for v in experiment.variants:
                if v.id == existing_assignment:
                    variant = v
                    break
            
            if variant:
                return {
                    "experiment_id": experiment.id,
                    "experiment_name": experiment.name,
                    "variant_id": variant.id,
                    "variant_name": variant.name,
                    "config": variant.config,
                    "is_control": variant.is_control
                }
        
        # 新分配
        variant = self.splitter.assign_variant(experiment, user_id, session_id, context)
        
        # 保存分配
        await self.storage.save_assignment(user_id, experiment.id, variant.id)
        
        # 记录指标
        if self.metrics_collector:
            await self.metrics_collector.increment_counter(
                "ab_test_assignments",
                {
                    "experiment": experiment.name,
                    "variant": variant.name,
                    "is_control": str(variant.is_control)
                }
            )
        
        return {
            "experiment_id": experiment.id,
            "experiment_name": experiment.name,
            "variant_id": variant.id,
            "variant_name": variant.name,
            "config": variant.config,
            "is_control": variant.is_control
        }
    
    async def record_result(
        self,
        experiment_id: str,
        variant_id: str,
        user_id: str,
        session_id: str,
        metrics: Dict[str, float],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """记录实验结果"""
        result = ExperimentResult(
            experiment_id=experiment_id,
            variant_id=variant_id,
            user_id=user_id,
            session_id=session_id,
            timestamp=time.time(),
            metrics=metrics,
            metadata=metadata or {}
        )
        
        success = await self.storage.save_result(result)
        
        if success and self.metrics_collector:
            # 记录各项指标
            for metric_name, value in metrics.items():
                await self.metrics_collector.record_histogram(
                    f"ab_test_metric_{metric_name}",
                    value,
                    {
                        "experiment_id": experiment_id,
                        "variant_id": variant_id
                    }
                )
        
        return success
    
    async def get_experiment_analysis(self, experiment_id: str) -> Dict[str, Any]:
        """获取实验分析结果"""
        experiment = await self.storage.get_experiment(experiment_id)
        if not experiment:
            return {"error": "实验不存在"}
        
        # 获取所有结果
        all_results = await self.storage.get_results(experiment_id)
        
        if not all_results:
            return {"error": "暂无实验数据"}
        
        # 按变体分组
        variant_results = {}
        for result in all_results:
            if result.variant_id not in variant_results:
                variant_results[result.variant_id] = []
            variant_results[result.variant_id].append(result)
        
        # 计算各变体统计
        variant_stats = {}
        metric_names = [m.name for m in experiment.metrics]
        
        for variant_id, results in variant_results.items():
            stats = await self.analyzer.calculate_variant_statistics(results, metric_names)
            variant_stats[variant_id] = stats
        
        # 找到对照组
        control_variant = None
        for variant in experiment.variants:
            if variant.is_control:
                control_variant = variant
                break
        
        # 比较各变体与对照组
        comparisons = {}
        if control_variant and control_variant.id in variant_stats:
            control_stats = variant_stats[control_variant.id]
            
            for variant in experiment.variants:
                if not variant.is_control and variant.id in variant_stats:
                    treatment_stats = variant_stats[variant.id]
                    
                    variant_comparisons = {}
                    for metric in experiment.metrics:
                        comparison = await self.analyzer.compare_variants(
                            control_stats, treatment_stats, metric.name
                        )
                        variant_comparisons[metric.name] = comparison
                    
                    comparisons[variant.id] = variant_comparisons
        
        return {
            "experiment": experiment.to_dict(),
            "variant_statistics": {vid: stats.to_dict() for vid, stats in variant_stats.items()},
            "comparisons": comparisons,
            "total_samples": len(all_results),
            "analysis_time": time.time()
        }
    
    async def _update_active_experiments_cache(self):
        """更新活跃实验缓存"""
        current_time = time.time()
        
        if current_time - self.last_cache_update < self.cache_ttl:
            return
        
        active_experiments = await self.storage.get_active_experiments()
        self.active_experiments_cache = {exp.id: exp for exp in active_experiments}
        self.last_cache_update = current_time
    
    async def get_experiment_statistics(self) -> Dict[str, Any]:
        """获取实验统计信息"""
        all_experiments = list(self.storage.experiments.values())
        
        status_counts = {}
        for exp in all_experiments:
            status = exp.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        total_results = len(self.storage.results)
        total_assignments = sum(len(assignments) for assignments in self.storage.assignments.values())
        
        return {
            "total_experiments": len(all_experiments),
            "status_distribution": status_counts,
            "total_results": total_results,
            "total_assignments": total_assignments,
            "active_experiments": len(self.active_experiments_cache)
        }

# 全局A/B测试实例
_ab_testing_framework: Optional[ABTestingFramework] = None

def initialize_ab_testing(metrics_collector: Optional[MetricsCollector] = None) -> ABTestingFramework:
    """初始化A/B测试框架"""
    global _ab_testing_framework
    _ab_testing_framework = ABTestingFramework(metrics_collector)
    return _ab_testing_framework

def get_ab_testing_framework() -> Optional[ABTestingFramework]:
    """获取A/B测试框架实例"""
    return _ab_testing_framework

# 便捷的装饰器
def ab_test_variant(experiment_name: str, variant_config_key: str = "config"):
    """A/B测试变体装饰器"""
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            # 从kwargs中提取用户信息
            user_id = kwargs.get("user_id", "anonymous")
            session_id = kwargs.get("session_id", "default")
            
            if _ab_testing_framework:
                # 获取变体配置
                variant_info = await _ab_testing_framework.get_variant_for_user(
                    user_id=user_id,
                    session_id=session_id,
                    experiment_name=experiment_name
                )
                
                if variant_info and experiment_name in variant_info:
                    # 将变体配置注入到kwargs中
                    kwargs[variant_config_key] = variant_info[experiment_name]["config"]
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator 