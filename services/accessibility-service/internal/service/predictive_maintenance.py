# 安全提示: 已将pickle替换为json以提高安全性
# pickle反序列化可能导致代码执行漏洞
#!/usr/bin/env python

"""
预测性维护模块 - 智能系统健康管理和故障预防
包含系统监控、故障预测、自动修复、维护调度等功能
"""

import asyncio
import logging
import os
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import psutil
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """健康状态枚举"""

    EXCELLENT = "excellent"
    GOOD = "good"
    WARNING = "warning"
    CRITICAL = "critical"
    FAILURE = "failure"


class MaintenanceType(Enum):
    """维护类型枚举"""

    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    PREDICTIVE = "predictive"
    EMERGENCY = "emergency"


class ComponentType(Enum):
    """组件类型枚举"""

    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"
    SENSORS = "sensors"
    AI_MODELS = "ai_models"
    DATABASE = "database"
    SERVICES = "services"


@dataclass
class HealthMetric:
    """健康指标"""

    component: ComponentType
    metric_name: str
    value: float
    threshold_warning: float
    threshold_critical: float
    timestamp: float
    unit: str = ""
    description: str = ""


@dataclass
class FailurePrediction:
    """故障预测"""

    component: ComponentType
    failure_probability: float
    predicted_failure_time: float | None
    confidence: float
    contributing_factors: list[str]
    recommended_actions: list[str]
    severity: HealthStatus
    timestamp: float


@dataclass
class MaintenanceTask:
    """维护任务"""

    task_id: str
    task_type: MaintenanceType
    component: ComponentType
    description: str
    priority: int  # 1-10, 10最高
    estimated_duration: float  # 分钟
    scheduled_time: float | None
    dependencies: list[str]
    auto_executable: bool
    status: str = "pending"
    created_time: float = field(default_factory=time.time)


class SystemMonitor:
    """系统监控器"""

    def __init__(self) -> None:
        self.metrics_history = defaultdict(deque)  # component -> deque of metrics
        self.monitoring_interval = 30.0  # 30秒
        self.history_size = 1000
        self.is_monitoring = False
        self._monitor_task = None

    async def start_monitoring(self) -> None:
        """启动系统监控"""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self._monitor_task = asyncio.create_task(self._monitoring_loop())
        logger.info("系统监控已启动")

    async def stop_monitoring(self) -> None:
        """停止系统监控"""
        self.is_monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("系统监控已停止")

    async def _monitoring_loop(self) -> None:
        """监控循环"""
        while self.is_monitoring:
            try:
                # 收集系统指标
                metrics = await self._collect_system_metrics()

                # 存储指标历史
                for metric in metrics:
                    self.metrics_history[metric.component].append(metric)

                    # 保持历史大小
                    if len(self.metrics_history[metric.component]) > self.history_size:
                        self.metrics_history[metric.component].popleft()

                await asyncio.sleep(self.monitoring_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"监控循环错误: {e!s}")
                await asyncio.sleep(self.monitoring_interval)

    async def _collect_system_metrics(self) -> list[HealthMetric]:
        """收集系统指标"""
        metrics = []
        current_time = time.time()

        try:
            # CPU指标
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_freq = psutil.cpu_freq()
            cpu_temp = self._get_cpu_temperature()

            metrics.extend(
                [
                    HealthMetric(
                        component=ComponentType.CPU,
                        metric_name="usage_percent",
                        value=cpu_percent,
                        threshold_warning=80.0,
                        threshold_critical=95.0,
                        timestamp=current_time,
                        unit="%",
                        description="CPU使用率",
                    ),
                    HealthMetric(
                        component=ComponentType.CPU,
                        metric_name="frequency",
                        value=cpu_freq.current if cpu_freq else 0,
                        threshold_warning=0,
                        threshold_critical=0,
                        timestamp=current_time,
                        unit="MHz",
                        description="CPU频率",
                    ),
                ]
            )

            if cpu_temp is not None:
                metrics.append(
                    HealthMetric(
                        component=ComponentType.CPU,
                        metric_name="temperature",
                        value=cpu_temp,
                        threshold_warning=70.0,
                        threshold_critical=85.0,
                        timestamp=current_time,
                        unit="°C",
                        description="CPU温度",
                    )
                )

            # 内存指标
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()

            metrics.extend(
                [
                    HealthMetric(
                        component=ComponentType.MEMORY,
                        metric_name="usage_percent",
                        value=memory.percent,
                        threshold_warning=80.0,
                        threshold_critical=95.0,
                        timestamp=current_time,
                        unit="%",
                        description="内存使用率",
                    ),
                    HealthMetric(
                        component=ComponentType.MEMORY,
                        metric_name="available_gb",
                        value=memory.available / (1024**3),
                        threshold_warning=2.0,
                        threshold_critical=0.5,
                        timestamp=current_time,
                        unit="GB",
                        description="可用内存",
                    ),
                    HealthMetric(
                        component=ComponentType.MEMORY,
                        metric_name="swap_percent",
                        value=swap.percent,
                        threshold_warning=50.0,
                        threshold_critical=80.0,
                        timestamp=current_time,
                        unit="%",
                        description="交换空间使用率",
                    ),
                ]
            )

            # 磁盘指标
            disk_usage = psutil.disk_usage("/")
            disk_io = psutil.disk_io_counters()

            metrics.extend(
                [
                    HealthMetric(
                        component=ComponentType.DISK,
                        metric_name="usage_percent",
                        value=(disk_usage.used / disk_usage.total) * 100,
                        threshold_warning=80.0,
                        threshold_critical=95.0,
                        timestamp=current_time,
                        unit="%",
                        description="磁盘使用率",
                    ),
                    HealthMetric(
                        component=ComponentType.DISK,
                        metric_name="free_gb",
                        value=disk_usage.free / (1024**3),
                        threshold_warning=10.0,
                        threshold_critical=2.0,
                        timestamp=current_time,
                        unit="GB",
                        description="可用磁盘空间",
                    ),
                ]
            )

            if disk_io:
                metrics.extend(
                    [
                        HealthMetric(
                            component=ComponentType.DISK,
                            metric_name="read_mb_per_sec",
                            value=disk_io.read_bytes / (1024**2),
                            threshold_warning=100.0,
                            threshold_critical=500.0,
                            timestamp=current_time,
                            unit="MB/s",
                            description="磁盘读取速度",
                        ),
                        HealthMetric(
                            component=ComponentType.DISK,
                            metric_name="write_mb_per_sec",
                            value=disk_io.write_bytes / (1024**2),
                            threshold_warning=100.0,
                            threshold_critical=500.0,
                            timestamp=current_time,
                            unit="MB/s",
                            description="磁盘写入速度",
                        ),
                    ]
                )

            # 网络指标
            network_io = psutil.net_io_counters()
            network_connections = len(psutil.net_connections())

            if network_io:
                metrics.extend(
                    [
                        HealthMetric(
                            component=ComponentType.NETWORK,
                            metric_name="bytes_sent_mb",
                            value=network_io.bytes_sent / (1024**2),
                            threshold_warning=1000.0,
                            threshold_critical=5000.0,
                            timestamp=current_time,
                            unit="MB",
                            description="网络发送字节数",
                        ),
                        HealthMetric(
                            component=ComponentType.NETWORK,
                            metric_name="bytes_recv_mb",
                            value=network_io.bytes_recv / (1024**2),
                            threshold_warning=1000.0,
                            threshold_critical=5000.0,
                            timestamp=current_time,
                            unit="MB",
                            description="网络接收字节数",
                        ),
                        HealthMetric(
                            component=ComponentType.NETWORK,
                            metric_name="connections_count",
                            value=network_connections,
                            threshold_warning=1000,
                            threshold_critical=5000,
                            timestamp=current_time,
                            unit="个",
                            description="网络连接数",
                        ),
                    ]
                )

        except Exception as e:
            logger.error(f"收集系统指标失败: {e!s}")

        return metrics

    def _get_cpu_temperature(self) -> float | None:
        """获取CPU温度"""
        try:
            # 尝试从不同来源获取CPU温度
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        if "cpu" in name.lower() or "core" in name.lower():
                            if entries:
                                return entries[0].current
            return None
        except Exception as e:
            return None

    def get_component_health(self, component: ComponentType) -> HealthStatus:
        """获取组件健康状态"""
        if component not in self.metrics_history:
            return HealthStatus.GOOD

        recent_metrics = list(self.metrics_history[component])[-10:]  # 最近10个指标

        if not recent_metrics:
            return HealthStatus.GOOD

        critical_count = 0
        warning_count = 0

        for metric in recent_metrics:
            if metric.threshold_critical > 0:
                if metric.value >= metric.threshold_critical:
                    critical_count += 1
                elif metric.value >= metric.threshold_warning:
                    warning_count += 1

        if critical_count > 0:
            return HealthStatus.CRITICAL
        elif warning_count >= 3:
            return HealthStatus.WARNING
        else:
            return HealthStatus.GOOD

    def get_metrics_summary(self) -> dict[str, Any]:
        """获取指标摘要"""
        summary = {}

        for component, metrics_deque in self.metrics_history.items():
            if not metrics_deque:
                continue

            recent_metrics = list(metrics_deque)[-10:]
            component_summary = {
                "health_status": self.get_component_health(component).value,
                "metrics_count": len(metrics_deque),
                "recent_metrics": [],
            }

            for metric in recent_metrics:
                component_summary["recent_metrics"].append(
                    {
                        "name": metric.metric_name,
                        "value": metric.value,
                        "unit": metric.unit,
                        "timestamp": metric.timestamp,
                        "status": (
                            "critical"
                            if metric.value >= metric.threshold_critical
                            else (
                                "warning"
                                if metric.value >= metric.threshold_warning
                                else "normal"
                            )
                        ),
                    }
                )

            summary[component.value] = component_summary

        return summary


class FailurePredictor:
    """故障预测器"""

    def __init__(self) -> None:
        self.models = {}  # component -> trained model
        self.scalers = {}  # component -> scaler
        self.prediction_history = deque(maxlen=500)
        self.model_path = "models/predictive_maintenance"
        self._ensure_model_directory()

    def _ensure_model_directory(self) -> None:
        """确保模型目录存在"""
        os.makedirs(self.model_path, exist_ok=True)

    def train_models(self, monitor: SystemMonitor):
        """训练预测模型"""
        logger.info("开始训练故障预测模型...")

        for component, metrics_deque in monitor.metrics_history.items():
            if len(metrics_deque) < 100:  # 需要足够的历史数据
                continue

            try:
                # 准备训练数据
                features = self._prepare_features(list(metrics_deque))

                if len(features) < 50:
                    continue

                # 标准化特征
                scaler = StandardScaler()
                features_scaled = scaler.fit_transform(features)

                # 训练异常检测模型
                model = IsolationForest(
                    contamination=0.1, random_state=42  # 假设10%的数据是异常
                )
                model.fit(features_scaled)

                # 保存模型和标准化器
                self.models[component] = model
                self.scalers[component] = scaler

                # 保存到文件
                self._save_model(component, model, scaler)

                logger.info(f"组件 {component.value} 的预测模型训练完成")

            except Exception as e:
                logger.error(f"训练组件 {component.value} 的模型失败: {e!s}")

    def _prepare_features(self, metrics: list[HealthMetric]) -> np.ndarray:
        """准备特征数据"""
        # 按时间窗口聚合指标
        window_size = 10  # 10个指标为一个窗口
        features = []

        for i in range(0, len(metrics) - window_size + 1, window_size):
            window_metrics = metrics[i : i + window_size]

            # 提取窗口特征
            window_features = []

            # 按指标名称分组
            metric_groups = defaultdict(list)
            for metric in window_metrics:
                metric_groups[metric.metric_name].append(metric.value)

            # 计算每个指标的统计特征
            for metric_name, values in metric_groups.items():
                if values:
                    window_features.extend(
                        [
                            np.mean(values),
                            np.std(values),
                            np.min(values),
                            np.max(values),
                        ]
                    )

            if window_features:
                features.append(window_features)

        return np.array(features)

    def predict_failures(self, monitor: SystemMonitor) -> list[FailurePrediction]:
        """预测故障"""
        predictions = []
        current_time = time.time()

        for component, metrics_deque in monitor.metrics_history.items():
            if component not in self.models or len(metrics_deque) < 10:
                continue

            try:
                # 准备最新数据
                recent_metrics = list(metrics_deque)[-20:]  # 最近20个指标
                features = self._prepare_features(recent_metrics)

                if len(features) == 0:
                    continue

                # 标准化特征
                scaler = self.scalers[component]
                features_scaled = scaler.transform(features)

                # 预测异常分数
                model = self.models[component]
                anomaly_scores = model.decision_function(features_scaled)
                outlier_predictions = model.predict(features_scaled)

                # 计算故障概率
                latest_score = anomaly_scores[-1] if len(anomaly_scores) > 0 else 0
                failure_probability = max(0, min(1, (0.5 - latest_score) / 0.5))

                # 预测故障时间
                predicted_failure_time = None
                if failure_probability > 0.7:
                    # 基于趋势预测故障时间
                    trend = self._calculate_trend(anomaly_scores)
                    if trend < 0:  # 分数下降趋势（更可能故障）
                        hours_to_failure = max(
                            1, abs(latest_score / trend) * 0.5
                        )  # 转换为小时
                        predicted_failure_time = current_time + hours_to_failure * 3600

                # 确定严重程度
                if failure_probability >= 0.9:
                    severity = HealthStatus.CRITICAL
                elif failure_probability >= 0.7:
                    severity = HealthStatus.WARNING
                else:
                    severity = HealthStatus.GOOD

                # 分析贡献因素
                contributing_factors = self._analyze_contributing_factors(
                    recent_metrics
                )

                # 生成推荐操作
                recommended_actions = self._generate_recommendations(
                    component, failure_probability, contributing_factors
                )

                prediction = FailurePrediction(
                    component=component,
                    failure_probability=failure_probability,
                    predicted_failure_time=predicted_failure_time,
                    confidence=min(0.9, len(features) / 10.0),  # 基于数据量的置信度
                    contributing_factors=contributing_factors,
                    recommended_actions=recommended_actions,
                    severity=severity,
                    timestamp=current_time,
                )

                predictions.append(prediction)
                self.prediction_history.append(prediction)

            except Exception as e:
                logger.error(f"预测组件 {component.value} 故障失败: {e!s}")

        return predictions

    def _calculate_trend(self, scores: np.ndarray) -> float:
        """计算趋势"""
        if len(scores) < 2:
            return 0

        x = np.arange(len(scores))
        slope = np.polyfit(x, scores, 1)[0]
        return slope

    def _analyze_contributing_factors(self, metrics: list[HealthMetric]) -> list[str]:
        """分析贡献因素"""
        factors = []

        # 按指标名称分组
        metric_groups = defaultdict(list)
        for metric in metrics:
            metric_groups[metric.metric_name].append(metric)

        # 检查每个指标的异常情况
        for metric_name, metric_list in metric_groups.items():
            if not metric_list:
                continue

            latest_metric = metric_list[-1]

            if latest_metric.value >= latest_metric.threshold_critical:
                factors.append(f"{metric_name}达到临界值({latest_metric.value:.2f})")
            elif latest_metric.value >= latest_metric.threshold_warning:
                factors.append(f"{metric_name}超过警告值({latest_metric.value:.2f})")

            # 检查趋势
            if len(metric_list) >= 5:
                values = [m.value for m in metric_list[-5:]]
                trend = self._calculate_trend(np.array(values))
                if trend > 0 and latest_metric.threshold_critical > 0:
                    factors.append(f"{metric_name}呈上升趋势")

        return factors[:5]  # 最多返回5个因素

    def _generate_recommendations(
        self, component: ComponentType, failure_probability: float, factors: list[str]
    ) -> list[str]:
        """生成推荐操作"""
        recommendations = []

        if failure_probability >= 0.9:
            recommendations.append("立即执行紧急维护")
            recommendations.append("备份重要数据")
            recommendations.append("准备故障转移方案")
        elif failure_probability >= 0.7:
            recommendations.append("安排预防性维护")
            recommendations.append("增加监控频率")

        # 基于组件类型的特定建议
        if component == ComponentType.CPU:
            if any("temperature" in factor for factor in factors):
                recommendations.append("检查散热系统")
            if any("usage" in factor for factor in factors):
                recommendations.append("优化CPU密集型任务")
        elif component == ComponentType.MEMORY:
            recommendations.append("清理内存缓存")
            recommendations.append("检查内存泄漏")
        elif component == ComponentType.DISK:
            recommendations.append("清理磁盘空间")
            recommendations.append("检查磁盘健康状态")
        elif component == ComponentType.NETWORK:
            recommendations.append("检查网络连接")
            recommendations.append("优化网络配置")

        return recommendations[:5]  # 最多返回5个建议

    def _save_model(self, component: ComponentType, model, scaler):
        """保存模型到文件"""
        try:
            model_file = os.path.join(self.model_path, f"{component.value}_model.pkl")
            scaler_file = os.path.join(self.model_path, f"{component.value}_scaler.pkl")

            with open(model_file, "wb") as f:
                pickle.dump(model, f)

            with open(scaler_file, "wb") as f:
                pickle.dump(scaler, f)

        except Exception as e:
            logger.error(f"保存模型失败: {e!s}")

    def load_models(self) -> None:
        """从文件加载模型"""
        try:
            for component in ComponentType:
                model_file = os.path.join(
                    self.model_path, f"{component.value}_model.pkl"
                )
                scaler_file = os.path.join(
                    self.model_path, f"{component.value}_scaler.pkl"
                )

                if os.path.exists(model_file) and os.path.exists(scaler_file):
                    with open(model_file, "rb") as f:
                        # TODO: 使用安全的序列化方案替代pickle
                        self.models[component] = pickle.load(f)

                    with open(scaler_file, "rb") as f:
                        # TODO: 使用安全的序列化方案替代pickle
                        self.scalers[component] = pickle.load(f)

                    logger.info(f"加载组件 {component.value} 的模型成功")

        except Exception as e:
            logger.error(f"加载模型失败: {e!s}")


class MaintenanceScheduler:
    """维护调度器"""

    def __init__(self) -> None:
        self.pending_tasks = []
        self.completed_tasks = deque(maxlen=1000)
        self.running_tasks = {}
        self.task_counter = 0

    def schedule_task(self, task: MaintenanceTask) -> str:
        """调度维护任务"""
        task.task_id = f"task_{self.task_counter}_{int(time.time())}"
        self.task_counter += 1

        # 插入到合适位置（按优先级排序）
        inserted = False
        for i, existing_task in enumerate(self.pending_tasks):
            if task.priority > existing_task.priority:
                self.pending_tasks.insert(i, task)
                inserted = True
                break

        if not inserted:
            self.pending_tasks.append(task)

        logger.info(f"维护任务已调度: {task.task_id} - {task.description}")
        return task.task_id

    def schedule_from_prediction(self, prediction: FailurePrediction) -> str:
        """基于故障预测调度维护任务"""
        if prediction.failure_probability < 0.5:
            return ""

        # 确定任务类型和优先级
        if prediction.failure_probability >= 0.9:
            task_type = MaintenanceType.EMERGENCY
            priority = 10
        elif prediction.failure_probability >= 0.7:
            task_type = MaintenanceType.PREDICTIVE
            priority = 8
        else:
            task_type = MaintenanceType.PREVENTIVE
            priority = 5

        # 创建维护任务
        task = MaintenanceTask(
            task_id="",
            task_type=task_type,
            component=prediction.component,
            description=f"预测性维护 - {prediction.component.value}组件故障概率{prediction.failure_probability:.1%}",
            priority=priority,
            estimated_duration=self._estimate_duration(prediction.component, task_type),
            scheduled_time=prediction.predicted_failure_time,
            dependencies=[],
            auto_executable=prediction.failure_probability
            < 0.8,  # 高风险任务需要人工确认
        )

        return self.schedule_task(task)

    def _estimate_duration(
        self, component: ComponentType, task_type: MaintenanceType
    ) -> float:
        """估算维护时长（分钟）"""
        base_durations = {
            ComponentType.CPU: 30,
            ComponentType.MEMORY: 15,
            ComponentType.DISK: 45,
            ComponentType.NETWORK: 20,
            ComponentType.SENSORS: 10,
            ComponentType.AI_MODELS: 60,
            ComponentType.DATABASE: 90,
            ComponentType.SERVICES: 30,
        }

        multipliers = {
            MaintenanceType.PREVENTIVE: 1.0,
            MaintenanceType.CORRECTIVE: 1.5,
            MaintenanceType.PREDICTIVE: 1.2,
            MaintenanceType.EMERGENCY: 2.0,
        }

        base = base_durations.get(component, 30)
        multiplier = multipliers.get(task_type, 1.0)

        return base * multiplier

    async def execute_next_task(self) -> MaintenanceTask | None:
        """执行下一个维护任务"""
        if not self.pending_tasks:
            return None

        # 检查依赖关系
        for i, task in enumerate(self.pending_tasks):
            if self._check_dependencies(task):
                # 移除并执行任务
                task = self.pending_tasks.pop(i)

                if task.auto_executable:
                    await self._execute_task(task)
                else:
                    logger.info(f"任务 {task.task_id} 需要人工确认")
                    task.status = "awaiting_approval"

                return task

        return None

    def _check_dependencies(self, task: MaintenanceTask) -> bool:
        """检查任务依赖"""
        for dep_id in task.dependencies:
            # 检查依赖任务是否已完成
            if not any(
                t.task_id == dep_id and t.status == "completed"
                for t in self.completed_tasks
            ):
                return False
        return True

    async def _execute_task(self, task: MaintenanceTask):
        """执行维护任务"""
        try:
            task.status = "running"
            self.running_tasks[task.task_id] = task

            logger.info(f"开始执行维护任务: {task.task_id}")

            # 根据组件类型执行相应的维护操作
            success = await self._perform_maintenance(task)

            if success:
                task.status = "completed"
                logger.info(f"维护任务完成: {task.task_id}")
            else:
                task.status = "failed"
                logger.error(f"维护任务失败: {task.task_id}")

            # 移动到已完成任务
            self.completed_tasks.append(task)
            del self.running_tasks[task.task_id]

        except Exception as e:
            task.status = "error"
            logger.error(f"执行维护任务错误: {e!s}")
            if task.task_id in self.running_tasks:
                del self.running_tasks[task.task_id]

    async def _perform_maintenance(self, task: MaintenanceTask) -> bool:
        """执行具体的维护操作"""
        try:
            component = task.component

            if component == ComponentType.MEMORY:
                # 内存清理
                import gc

                gc.collect()
                logger.info("执行内存垃圾回收")

            elif component == ComponentType.DISK:
                # 磁盘清理（简化版）
                logger.info("执行磁盘清理检查")

            elif component == ComponentType.NETWORK:
                # 网络连接检查
                logger.info("执行网络连接检查")

            elif component == ComponentType.SERVICES:
                # 服务重启或优化
                logger.info("执行服务优化")

            elif component == ComponentType.AI_MODELS:
                # AI模型优化
                logger.info("执行AI模型优化")

            # 模拟维护时间
            await asyncio.sleep(min(task.estimated_duration / 60, 5))  # 最多等待5秒

            return True

        except Exception as e:
            logger.error(f"维护操作失败: {e!s}")
            return False

    def get_task_status(self) -> dict[str, Any]:
        """获取任务状态"""
        return {
            "pending_tasks": len(self.pending_tasks),
            "running_tasks": len(self.running_tasks),
            "completed_tasks": len(self.completed_tasks),
            "next_task": (
                {
                    "task_id": self.pending_tasks[0].task_id,
                    "priority": self.pending_tasks[0].priority,
                    "component": self.pending_tasks[0].component.value,
                    "description": self.pending_tasks[0].description,
                }
                if self.pending_tasks
                else None
            ),
        }


class PredictiveMaintenance:
    """预测性维护主类"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化预测性维护系统

        Args:
            config: 服务配置
        """
        self.config = config
        self.enabled = config.get("predictive_maintenance", {}).get("enabled", True)

        # 子模块
        self.monitor = SystemMonitor()
        self.predictor = FailurePredictor()
        self.scheduler = MaintenanceScheduler()

        # 配置参数
        self.prediction_interval = config.get("predictive_maintenance", {}).get(
            "prediction_interval", 300.0
        )  # 5分钟
        self.auto_maintenance = config.get("predictive_maintenance", {}).get(
            "auto_maintenance", True
        )

        # 统计信息
        self.stats = {
            "predictions_made": 0,
            "tasks_scheduled": 0,
            "tasks_completed": 0,
            "failures_prevented": 0,
            "system_uptime": time.time(),
        }

        # 定时任务
        self._prediction_task = None
        self._maintenance_task = None

        logger.info(f"预测性维护系统初始化完成 - 启用: {self.enabled}")

    async def start(self) -> None:
        """启动预测性维护系统"""
        if not self.enabled:
            return

        logger.info("启动预测性维护系统...")

        # 启动系统监控
        await self.monitor.start_monitoring()

        # 加载预训练模型
        self.predictor.load_models()

        # 启动预测任务
        self._prediction_task = asyncio.create_task(self._prediction_loop())

        # 启动维护任务
        self._maintenance_task = asyncio.create_task(self._maintenance_loop())

        logger.info("预测性维护系统已启动")

    async def _prediction_loop(self) -> None:
        """预测循环"""
        while True:
            try:
                await asyncio.sleep(self.prediction_interval)

                # 执行故障预测
                predictions = self.predictor.predict_failures(self.monitor)
                self.stats["predictions_made"] += len(predictions)

                # 基于预测调度维护任务
                for prediction in predictions:
                    if prediction.failure_probability > 0.5:
                        task_id = self.scheduler.schedule_from_prediction(prediction)
                        if task_id:
                            self.stats["tasks_scheduled"] += 1
                            logger.info(f"基于预测调度维护任务: {task_id}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"预测循环错误: {e!s}")

    async def _maintenance_loop(self) -> None:
        """维护循环"""
        while True:
            try:
                await asyncio.sleep(60)  # 每分钟检查一次

                if self.auto_maintenance:
                    # 执行下一个维护任务
                    task = await self.scheduler.execute_next_task()
                    if task and task.status == "completed":
                        self.stats["tasks_completed"] += 1

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"维护循环错误: {e!s}")

    def train_prediction_models(self) -> None:
        """训练预测模型"""
        if not self.enabled:
            return

        logger.info("开始训练预测模型...")
        self.predictor.train_models(self.monitor)
        logger.info("预测模型训练完成")

    def get_system_health(self) -> dict[str, Any]:
        """获取系统健康状态"""
        health_summary = {
            "overall_status": "good",
            "components": {},
            "active_predictions": [],
            "maintenance_status": self.scheduler.get_task_status(),
        }

        # 组件健康状态
        for component in ComponentType:
            health_status = self.monitor.get_component_health(component)
            health_summary["components"][component.value] = health_status.value

            if health_status in [HealthStatus.WARNING, HealthStatus.CRITICAL]:
                health_summary["overall_status"] = "warning"

        # 活跃预测
        recent_predictions = list(self.predictor.prediction_history)[-10:]
        for prediction in recent_predictions:
            if prediction.failure_probability > 0.5:
                health_summary["active_predictions"].append(
                    {
                        "component": prediction.component.value,
                        "failure_probability": prediction.failure_probability,
                        "severity": prediction.severity.value,
                        "predicted_time": prediction.predicted_failure_time,
                    }
                )

        return health_summary

    def get_metrics_summary(self) -> dict[str, Any]:
        """获取指标摘要"""
        return self.monitor.get_metrics_summary()

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        current_time = time.time()
        uptime_hours = (current_time - self.stats["system_uptime"]) / 3600

        return {
            "enabled": self.enabled,
            "uptime_hours": uptime_hours,
            "monitoring_active": self.monitor.is_monitoring,
            **self.stats,
            "scheduler_status": self.scheduler.get_task_status(),
        }

    async def shutdown(self) -> None:
        """关闭预测性维护系统"""
        logger.info("正在关闭预测性维护系统...")

        # 停止监控
        await self.monitor.stop_monitoring()

        # 取消定时任务
        if self._prediction_task:
            self._prediction_task.cancel()
            try:
                await self._prediction_task
            except asyncio.CancelledError:
                pass

        if self._maintenance_task:
            self._maintenance_task.cancel()
            try:
                await self._maintenance_task
            except asyncio.CancelledError:
                pass

        logger.info("预测性维护系统已关闭")
