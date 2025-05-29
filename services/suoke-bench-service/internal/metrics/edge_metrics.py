"""端侧性能评测指标实现。"""

from dataclasses import dataclass
from typing import Any

import numpy as np

from .agent_metrics import MetricResult
from .metrics import Metric


@dataclass
class DeviceInfo:
    """设备信息数据类。"""

    device_id: str  # 设备ID
    model: str  # 设备型号
    os: str  # 操作系统
    os_version: str  # 系统版本
    cpu_info: dict[str, Any]  # CPU信息
    memory_size: int  # 内存大小(MB)
    storage_size: int  # 存储大小(MB)
    battery_capacity: int  # 电池容量(mAh)


@dataclass
class ModelInfo:
    """模型信息数据类。"""

    model_id: str  # 模型ID
    version: str  # 版本
    task_type: str  # 任务类型
    model_size: int  # 模型大小(MB)
    quantization: str | None  # 量化方式
    optimization: list[str]  # 优化方法


@dataclass
class PerformanceMetrics:
    """性能指标数据类。"""

    cpu_usage: float  # CPU使用率(%)
    memory_usage: float  # 内存使用(MB)
    power_usage: float  # 功耗(mW)
    battery_impact: float  # 电池影响(mAh/h)
    storage_io: float  # 存储IO(MB/s)
    network_io: float  # 网络IO(MB/s)
    temperature: float  # 温度(°C)


@dataclass
class InferenceMetrics:
    """推理性能指标数据类。"""

    latency: float  # 延迟(ms)
    throughput: float  # 吞吐量(samples/s)
    accuracy: float  # 准确率
    initialization_time: float  # 初始化时间(ms)
    memory_footprint: float  # 内存占用(MB)


class EdgePerformanceMetric(Metric):
    """端侧性能评测指标。"""

    def __init__(self, threshold: float = 0.8):
        super().__init__("edge_performance", threshold, "", True)
        self.description = "评估端侧计算性能"

    def calculate(
        self,
        device_info: DeviceInfo,
        model_info: ModelInfo,
        perf_metrics: list[PerformanceMetrics],
        infer_metrics: list[InferenceMetrics],
    ) -> MetricResult:
        """计算端侧性能的评测指标。"""

        # 计算资源使用指标
        resource_score = self._calculate_resource_score(device_info, perf_metrics)

        # 计算推理性能指标
        inference_score = self._calculate_inference_score(model_info, infer_metrics)

        # 计算能效指标
        energy_score = self._calculate_energy_score(device_info, perf_metrics)

        # 计算稳定性指标
        stability_score = self._calculate_stability_score(perf_metrics, infer_metrics)

        # 计算加权总分
        weights = {"resource": 0.3, "inference": 0.3, "energy": 0.2, "stability": 0.2}

        total_score = (
            weights["resource"] * resource_score["overall"]
            + weights["inference"] * inference_score["overall"]
            + weights["energy"] * energy_score["overall"]
            + weights["stability"] * stability_score["overall"]
        )

        return MetricResult(
            name=self.name,
            value=total_score,
            threshold=self.threshold,
            details={
                "resource_usage": resource_score,
                "inference_performance": inference_score,
                "energy_efficiency": energy_score,
                "stability": stability_score,
            },
        )

    def _calculate_resource_score(
        self, device_info: DeviceInfo, metrics: list[PerformanceMetrics]
    ) -> dict[str, float]:
        """计算资源使用指标。"""

        # 计算CPU使用率得分
        cpu_usage = np.mean([m.cpu_usage for m in metrics])
        cpu_score = max(0, 1 - (cpu_usage / 80))  # 基准80%

        # 计算内存使用率得分
        memory_usage = np.mean([m.memory_usage for m in metrics])
        memory_ratio = memory_usage / device_info.memory_size
        memory_score = max(0, 1 - (memory_ratio / 0.3))  # 基准30%

        # 计算存储IO得分
        storage_io = np.mean([m.storage_io for m in metrics])
        storage_score = max(0, 1 - (storage_io / 50))  # 基准50MB/s

        # 计算网络IO得分
        network_io = np.mean([m.network_io for m in metrics])
        network_score = max(0, 1 - (network_io / 10))  # 基准10MB/s

        # 计算整体资源使用分数
        weights = {"cpu": 0.4, "memory": 0.3, "storage": 0.15, "network": 0.15}

        overall = (
            weights["cpu"] * cpu_score
            + weights["memory"] * memory_score
            + weights["storage"] * storage_score
            + weights["network"] * network_score
        )

        return {
            "overall": overall,
            "cpu_score": cpu_score,
            "memory_score": memory_score,
            "storage_score": storage_score,
            "network_score": network_score,
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "storage_io": storage_io,
            "network_io": network_io,
        }

    def _calculate_inference_score(
        self, model_info: ModelInfo, metrics: list[InferenceMetrics]
    ) -> dict[str, float]:
        """计算推理性能指标。"""

        # 计算延迟得分
        latency = np.mean([m.latency for m in metrics])
        latency_score = max(0, 1 - (latency / 100))  # 基准100ms

        # 计算吞吐量得分
        throughput = np.mean([m.throughput for m in metrics])
        throughput_score = min(1.0, throughput / 50)  # 基准50samples/s

        # 计算准确率得分
        accuracy = np.mean([m.accuracy for m in metrics])
        accuracy_score = accuracy  # 直接使用准确率作为得分

        # 计算初始化时间得分
        init_time = np.mean([m.initialization_time for m in metrics])
        init_score = max(0, 1 - (init_time / 1000))  # 基准1000ms

        # 计算内存占用得分
        memory_footprint = np.mean([m.memory_footprint for m in metrics])
        footprint_ratio = memory_footprint / model_info.model_size
        footprint_score = max(0, 1 - (footprint_ratio / 2))  # 基准2倍模型大小

        # 计算整体推理性能分数
        weights = {
            "latency": 0.25,
            "throughput": 0.25,
            "accuracy": 0.2,
            "init": 0.15,
            "footprint": 0.15,
        }

        overall = (
            weights["latency"] * latency_score
            + weights["throughput"] * throughput_score
            + weights["accuracy"] * accuracy_score
            + weights["init"] * init_score
            + weights["footprint"] * footprint_score
        )

        return {
            "overall": overall,
            "latency_score": latency_score,
            "throughput_score": throughput_score,
            "accuracy_score": accuracy_score,
            "initialization_score": init_score,
            "footprint_score": footprint_score,
            "average_latency": latency,
            "average_throughput": throughput,
            "average_accuracy": accuracy,
        }

    def _calculate_energy_score(
        self, device_info: DeviceInfo, metrics: list[PerformanceMetrics]
    ) -> dict[str, float]:
        """计算能效指标。"""

        # 计算功耗得分
        power_usage = np.mean([m.power_usage for m in metrics])
        power_score = max(0, 1 - (power_usage / 1000))  # 基准1000mW

        # 计算电池影响得分
        battery_impact = np.mean([m.battery_impact for m in metrics])
        battery_ratio = battery_impact / device_info.battery_capacity
        battery_score = max(0, 1 - (battery_ratio / 0.01))  # 基准1%/h

        # 计算温度得分
        temperature = np.mean([m.temperature for m in metrics])
        temp_score = max(0, 1 - ((temperature - 25) / 15))  # 基准40°C

        # 计算整体能效分数
        weights = {"power": 0.4, "battery": 0.4, "temperature": 0.2}

        overall = (
            weights["power"] * power_score
            + weights["battery"] * battery_score
            + weights["temperature"] * temp_score
        )

        return {
            "overall": overall,
            "power_score": power_score,
            "battery_score": battery_score,
            "temperature_score": temp_score,
            "average_power": power_usage,
            "battery_impact": battery_impact,
            "average_temperature": temperature,
        }

    def _calculate_stability_score(
        self,
        perf_metrics: list[PerformanceMetrics],
        infer_metrics: list[InferenceMetrics],
    ) -> dict[str, float]:
        """计算稳定性指标。"""

        # 计算CPU使用率稳定性
        cpu_std = np.std([m.cpu_usage for m in perf_metrics])
        cpu_stability = max(0, 1 - (cpu_std / 10))  # 基准10%

        # 计算内存使用稳定性
        memory_std = np.std([m.memory_usage for m in perf_metrics])
        memory_stability = max(0, 1 - (memory_std / 50))  # 基准50MB

        # 计算延迟稳定性
        latency_std = np.std([m.latency for m in infer_metrics])
        latency_stability = max(0, 1 - (latency_std / 20))  # 基准20ms

        # 计算吞吐量稳定性
        throughput_std = np.std([m.throughput for m in infer_metrics])
        throughput_stability = max(0, 1 - (throughput_std / 10))  # 基准10samples/s

        # 计算整体稳定性分数
        weights = {"cpu": 0.25, "memory": 0.25, "latency": 0.25, "throughput": 0.25}

        overall = (
            weights["cpu"] * cpu_stability
            + weights["memory"] * memory_stability
            + weights["latency"] * latency_stability
            + weights["throughput"] * throughput_stability
        )

        return {
            "overall": overall,
            "cpu_stability": cpu_stability,
            "memory_stability": memory_stability,
            "latency_stability": latency_stability,
            "throughput_stability": throughput_stability,
            "cpu_std": cpu_std,
            "memory_std": memory_std,
            "latency_std": latency_std,
            "throughput_std": throughput_std,
        }
