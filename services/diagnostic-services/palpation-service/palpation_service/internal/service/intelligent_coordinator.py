"""
intelligent_coordinator - 索克生活项目模块
"""

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from internal.model.ai_tcm_analyzer import AITCMAnalyzer
from internal.model.pulse_models import PulseDataPacket
from internal.signal.abdominal_analyzer import AbdominalAnalyzer
from internal.signal.enhanced_pulse_processor import EnhancedPulseProcessor
from internal.signal.skin_analyzer import SkinAnalyzer
from internal.signal.smart_device_manager import SmartDeviceManager
from typing import Any
import asyncio
import logging
import psutil
import time

#!/usr/bin/env python3

"""
智能服务协调器
作为触诊服务的核心控制器，统一管理所有子系统，提供智能调度、负载均衡和故障恢复功能
"""



logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """服务状态枚举"""

    INITIALIZING = auto()
    READY = auto()
    RUNNING = auto()
    DEGRADED = auto()
    ERROR = auto()
    MAINTENANCE = auto()


class TaskPriority(Enum):
    """任务优先级"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ServiceMetrics:
    """服务性能指标"""

    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    active_sessions: int = 0
    completed_sessions: int = 0
    error_count: int = 0
    average_response_time: float = 0.0
    throughput: float = 0.0  # 每秒处理的任务数
    uptime: timedelta = field(default_factory=lambda: timedelta())


@dataclass
class AnalysisTask:
    """分析任务"""

    task_id: str
    session_id: str
    task_type: str  # pulse, abdominal, skin, comprehensive
    priority: TaskPriority
    data: dict[str, Any]
    created_at: datetime
    timeout: float = 30.0
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class AnalysisResult:
    """分析结果"""

    task_id: str
    session_id: str
    result_type: str
    data: dict[str, Any]
    confidence: float
    processing_time: float
    timestamp: datetime
    metadata: dict[str, Any] = field(default_factory=dict)


class IntelligentCoordinator:
    """智能服务协调器"""

    def __init__(self, config: dict[str, Any]):
        """
        初始化智能协调器

        Args:
            config: 配置字典
        """
        self.config = config
        self.status = ServiceStatus.INITIALIZING

        # 核心组件
        self.pulse_processor: EnhancedPulseProcessor | None = None
        self.device_manager: SmartDeviceManager | None = None
        self.abdominal_analyzer: AbdominalAnalyzer | None = None
        self.skin_analyzer: SkinAnalyzer | None = None
        self.tcm_analyzer: AITCMAnalyzer | None = None

        # 任务管理
        self.task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.active_tasks: dict[str, AnalysisTask] = {}
        self.completed_tasks: dict[str, AnalysisResult] = {}

        # 会话管理
        self.active_sessions: dict[str, dict[str, Any]] = {}
        self.session_locks: dict[str, asyncio.Lock] = {}

        # 性能监控
        self.metrics = ServiceMetrics()
        self.performance_history: list[ServiceMetrics] = []

        # 配置参数
        self.max_concurrent_tasks = config.get("max_concurrent_tasks", 10)
        self.task_timeout = config.get("task_timeout", 30.0)
        self.health_check_interval = config.get("health_check_interval", 30)
        self.metrics_collection_interval = config.get("metrics_interval", 10)

        # 负载均衡配置
        self.load_balancing = config.get("load_balancing", {})
        self.cpu_threshold = self.load_balancing.get("cpu_threshold", 80.0)
        self.memory_threshold = self.load_balancing.get("memory_threshold", 80.0)

        # 故障恢复配置
        self.fault_tolerance = config.get("fault_tolerance", {})
        self.max_error_rate = self.fault_tolerance.get("max_error_rate", 0.1)
        self.recovery_timeout = self.fault_tolerance.get("recovery_timeout", 60)

        # 事件回调
        self.event_callbacks: dict[str, list[Callable]] = {
            "session_started": [],
            "session_completed": [],
            "task_completed": [],
            "error_occurred": [],
            "performance_alert": [],
        }

        # 后台任务
        self.background_tasks: list[asyncio.Task] = []
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.running = False

        # 启动时间
        self.start_time = datetime.now()

        logger.info("智能服务协调器初始化完成")

    async def initialize(self):
        """初始化所有子系统"""
        try:
            logger.info("开始初始化子系统...")

            # 初始化脉搏处理器
            pulse_config = self.config.get("pulse_processor", {})
            self.pulse_processor = EnhancedPulseProcessor(pulse_config)

            # 初始化设备管理器
            device_config = self.config.get("device_manager", {})
            self.device_manager = SmartDeviceManager(device_config)
            await self.device_manager.start()

            # 初始化腹诊分析器
            abdominal_config = self.config.get("abdominal_analyzer", {})
            self.abdominal_analyzer = AbdominalAnalyzer(abdominal_config)

            # 初始化皮肤分析器
            skin_config = self.config.get("skin_analyzer", {})
            self.skin_analyzer = SkinAnalyzer(skin_config)

            # 初始化中医分析器
            tcm_config = self.config.get("tcm_analyzer", {})
            self.tcm_analyzer = AITCMAnalyzer(tcm_config)

            self.status = ServiceStatus.READY
            logger.info("所有子系统初始化完成")

        except Exception as e:
            self.status = ServiceStatus.ERROR
            logger.error(f"子系统初始化失败: {e}")
            raise

    async def start(self):
        """启动协调器"""
        if self.running:
            return

        await self.initialize()
        self.running = True
        self.status = ServiceStatus.RUNNING

        # 启动后台任务
        self.background_tasks = [
            asyncio.create_task(self._task_processor()),
            asyncio.create_task(self._health_monitor()),
            asyncio.create_task(self._metrics_collector()),
            asyncio.create_task(self._performance_optimizer()),
            asyncio.create_task(self._cleanup_manager()),
        ]

        logger.info("智能协调器已启动")

    async def stop(self):
        """停止协调器"""
        if not self.running:
            return

        self.running = False
        self.status = ServiceStatus.MAINTENANCE

        # 完成所有活跃任务
        await self._complete_active_tasks()

        # 停止子系统
        if self.device_manager:
            await self.device_manager.stop()

        if self.pulse_processor:
            self.pulse_processor.cleanup()

        # 取消后台任务
        for task in self.background_tasks:
            task.cancel()

        await asyncio.gather(*self.background_tasks, return_exceptions=True)

        # 关闭线程池
        self.executor.shutdown(wait=True)

        logger.info("智能协调器已停止")

    async def start_palpation_session(
        self,
        session_id: str,
        user_profile: dict[str, Any],
        session_config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        开始触诊会话

        Args:
            session_id: 会话ID
            user_profile: 用户档案
            session_config: 会话配置

        Returns:
            会话启动结果
        """
        try:
            # 检查系统状态
            if self.status != ServiceStatus.RUNNING:
                raise RuntimeError(f"系统状态不可用: {self.status}")

            # 检查资源可用性
            if not await self._check_resource_availability():
                raise RuntimeError("系统资源不足，无法启动新会话")

            # 创建会话锁
            self.session_locks[session_id] = asyncio.Lock()

            async with self.session_locks[session_id]:
                # 初始化会话数据
                session_data = {
                    "session_id": session_id,
                    "user_profile": user_profile,
                    "config": session_config or {},
                    "start_time": datetime.now(),
                    "status": "active",
                    "device_id": None,
                    "pulse_data": [],
                    "abdominal_data": None,
                    "skin_data": None,
                    "analysis_results": {},
                }

                # 分配设备
                device_preference = (
                    session_config.get("device_preference") if session_config else None
                )
                device_id = await self.device_manager.start_session(session_id, device_preference)

                if not device_id:
                    raise RuntimeError("无法分配设备")

                session_data["device_id"] = device_id
                self.active_sessions[session_id] = session_data

                # 更新指标
                self.metrics.active_sessions += 1

                # 触发事件
                await self._trigger_event("session_started", session_id, session_data)

                logger.info(f"触诊会话已启动: {session_id}, 设备: {device_id}")

                return {
                    "status": "success",
                    "session_id": session_id,
                    "device_id": device_id,
                    "message": "会话启动成功",
                }

        except Exception as e:
            logger.error(f"会话启动失败: {session_id}, {e}")
            return {"status": "error", "session_id": session_id, "message": str(e)}

    async def process_pulse_data(
        self, session_id: str, pulse_data: PulseDataPacket
    ) -> dict[str, Any]:
        """
        处理脉搏数据

        Args:
            session_id: 会话ID
            pulse_data: 脉搏数据包

        Returns:
            处理结果
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"会话不存在: {session_id}")

        # 创建分析任务
        task = AnalysisTask(
            task_id=f"pulse_{session_id}_{int(time.time())}",
            session_id=session_id,
            task_type="pulse",
            priority=TaskPriority.NORMAL,
            data={"pulse_data": pulse_data},
            created_at=datetime.now(),
        )

        # 提交任务
        result = await self._submit_task(task)

        # 存储脉搏数据
        self.active_sessions[session_id]["pulse_data"].append(pulse_data)

        return result

    async def analyze_comprehensive_palpation(
        self, session_id: str, include_prediction: bool = True
    ) -> dict[str, Any]:
        """
        综合触诊分析

        Args:
            session_id: 会话ID
            include_prediction: 是否包含预测分析

        Returns:
            综合分析结果
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"会话不存在: {session_id}")

        session_data = self.active_sessions[session_id]

        # 创建综合分析任务
        task = AnalysisTask(
            task_id=f"comprehensive_{session_id}_{int(time.time())}",
            session_id=session_id,
            task_type="comprehensive",
            priority=TaskPriority.HIGH,
            data={"session_data": session_data, "include_prediction": include_prediction},
            created_at=datetime.now(),
            timeout=60.0,  # 综合分析需要更长时间
        )

        return await self._submit_task(task)

    async def _submit_task(self, task: AnalysisTask) -> dict[str, Any]:
        """提交分析任务"""
        # 检查系统负载
        if len(self.active_tasks) >= self.max_concurrent_tasks:
            # 等待任务完成或超时
            await asyncio.sleep(0.1)
            if len(self.active_tasks) >= self.max_concurrent_tasks:
                raise RuntimeError("系统负载过高，请稍后重试")

        # 添加到活跃任务
        self.active_tasks[task.task_id] = task

        # 添加到任务队列
        priority = -task.priority.value  # 负数用于优先队列排序
        await self.task_queue.put((priority, task.created_at, task))

        # 等待任务完成
        timeout = task.timeout
        start_time = time.time()

        while task.task_id not in self.completed_tasks:
            if time.time() - start_time > timeout:
                # 任务超时
                if task.task_id in self.active_tasks:
                    del self.active_tasks[task.task_id]
                raise TimeoutError(f"任务超时: {task.task_id}")

            await asyncio.sleep(0.1)

        # 获取结果
        result = self.completed_tasks.pop(task.task_id)

        return {
            "status": "success",
            "task_id": task.task_id,
            "result": result.data,
            "confidence": result.confidence,
            "processing_time": result.processing_time,
        }

    async def _task_processor(self):
        """任务处理器"""
        while self.running:
            try:
                # 获取任务
                try:
                    priority, created_at, task = await asyncio.wait_for(
                        self.task_queue.get(), timeout=1.0
                    )
                except TimeoutError:
                    continue

                # 处理任务
                await self._process_task(task)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"任务处理异常: {e}")
                await asyncio.sleep(1)

    async def _process_task(self, task: AnalysisTask):
        """处理单个任务"""
        start_time = time.time()

        try:
            # 根据任务类型选择处理器
            if task.task_type == "pulse":
                result_data = await self._process_pulse_task(task)
            elif task.task_type == "abdominal":
                result_data = await self._process_abdominal_task(task)
            elif task.task_type == "skin":
                result_data = await self._process_skin_task(task)
            elif task.task_type == "comprehensive":
                result_data = await self._process_comprehensive_task(task)
            else:
                raise ValueError(f"未知任务类型: {task.task_type}")

            processing_time = time.time() - start_time

            # 创建结果
            result = AnalysisResult(
                task_id=task.task_id,
                session_id=task.session_id,
                result_type=task.task_type,
                data=result_data,
                confidence=result_data.get("confidence", 0.8),
                processing_time=processing_time,
                timestamp=datetime.now(),
            )

            # 存储结果
            self.completed_tasks[task.task_id] = result

            # 从活跃任务中移除
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]

            # 更新指标
            self.metrics.completed_sessions += 1
            self._update_response_time(processing_time)

            # 触发事件
            await self._trigger_event("task_completed", task, result)

            logger.debug(f"任务完成: {task.task_id}, 耗时: {processing_time:.2f}s")

        except Exception as e:
            # 任务失败处理
            await self._handle_task_failure(task, e)

    async def _process_pulse_task(self, task: AnalysisTask) -> dict[str, Any]:
        """处理脉搏分析任务"""
        pulse_data = task.data["pulse_data"]

        # 使用增强版脉搏处理器
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(self.executor, self._analyze_pulse_data, pulse_data)

        return result

    def _analyze_pulse_data(self, pulse_data: PulseDataPacket) -> dict[str, Any]:
        """分析脉搏数据（在线程池中执行）"""
        # 提取特征
        features = self.pulse_processor.extract_features_optimized(pulse_data.signal_data)

        # 脉象分类
        classification = self.pulse_processor.classify_pulse_type_enhanced(features)

        # 中医分析
        tcm_patterns = asyncio.run(self.tcm_analyzer.analyze_pulse_pattern(features))

        return {
            "features": features,
            "classification": classification,
            "tcm_patterns": [pattern.__dict__ for pattern in tcm_patterns],
            "confidence": classification.get("confidence", 0.8),
            "timestamp": datetime.now().isoformat(),
        }

    async def _process_comprehensive_task(self, task: AnalysisTask) -> dict[str, Any]:
        """处理综合分析任务"""
        session_data = task.data["session_data"]
        include_prediction = task.data.get("include_prediction", True)

        # 收集所有分析结果
        pulse_results = []
        for pulse_data in session_data["pulse_data"]:
            pulse_result = await self._process_pulse_task(
                AnalysisTask(
                    task_id=f"temp_{int(time.time())}",
                    session_id=task.session_id,
                    task_type="pulse",
                    priority=TaskPriority.NORMAL,
                    data={"pulse_data": pulse_data},
                    created_at=datetime.now(),
                )
            )
            pulse_results.append(pulse_result)

        # 综合分析
        comprehensive_result = await self._perform_comprehensive_analysis(
            pulse_results, session_data, include_prediction
        )

        return comprehensive_result

    async def _perform_comprehensive_analysis(
        self,
        pulse_results: list[dict[str, Any]],
        session_data: dict[str, Any],
        include_prediction: bool,
    ) -> dict[str, Any]:
        """执行综合分析"""
        # 合并脉象特征
        all_features = {}
        all_patterns = []

        for result in pulse_results:
            # 合并特征（取平均值）
            for key, value in result["features"].items():
                if key in all_features:
                    all_features[key] = (all_features[key] + value) / 2
                else:
                    all_features[key] = value

            # 收集所有证型
            all_patterns.extend(result["tcm_patterns"])

        # 体质评估
        constitution = await self.tcm_analyzer.assess_constitution(
            all_features, session_data["user_profile"]
        )

        # 健康评估
        health_assessment = await self.tcm_analyzer.generate_health_assessment(
            [
                self.tcm_analyzer._create_ai_pattern(pattern["pattern_type"], pattern["confidence"])
                for pattern in all_patterns[:3]
            ],  # 取前3个主要证型
            constitution,
            session_data["user_profile"],
        )

        result = {
            "session_id": session_data["session_id"],
            "comprehensive_features": all_features,
            "constitution_type": constitution.value,
            "health_assessment": {
                "overall_score": health_assessment.overall_score,
                "primary_patterns": [p.__dict__ for p in health_assessment.primary_patterns],
                "risk_factors": health_assessment.risk_factors,
                "recommendations": health_assessment.recommendations,
                "follow_up_interval": health_assessment.follow_up_interval,
            },
            "confidence": 0.85,
            "analysis_timestamp": datetime.now().isoformat(),
        }

        # 预测分析（如果需要）
        if include_prediction:
            prediction_result = await self._perform_predictive_analysis(
                all_features, session_data["user_profile"]
            )
            result["prediction"] = prediction_result

        return result

    async def _perform_predictive_analysis(
        self, features: dict[str, Any], user_profile: dict[str, Any]
    ) -> dict[str, Any]:
        """执行预测分析"""
        # 这里应该实现基于历史数据的预测分析
        # 目前返回模拟结果
        return {
            "health_trend": "stable",
            "risk_prediction": {
                "cardiovascular_risk": 0.2,
                "metabolic_risk": 0.15,
                "immune_risk": 0.1,
            },
            "recommended_actions": ["保持当前的健康习惯", "定期监测心血管指标", "适当增加运动量"],
            "confidence": 0.75,
        }

    async def _check_resource_availability(self) -> bool:
        """检查资源可用性"""
        # 检查CPU使用率
        cpu_usage = psutil.cpu_percent(interval=1)
        if cpu_usage > self.cpu_threshold:
            return False

        # 检查内存使用率
        memory = psutil.virtual_memory()
        if memory.percent > self.memory_threshold:
            return False

        # 检查活跃任务数
        if len(self.active_tasks) >= self.max_concurrent_tasks:
            return False

        return True

    async def _health_monitor(self):
        """健康监控"""
        while self.running:
            try:
                await self._check_system_health()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"健康监控异常: {e}")
                await asyncio.sleep(5)

    async def _check_system_health(self):
        """检查系统健康状态"""
        # 检查子系统状态
        if self.device_manager:
            devices_status = await self.device_manager.get_all_devices_status()
            unhealthy_devices = [
                device_id
                for device_id, status in devices_status.items()
                if status and status.get("status") == "ERROR"
            ]

            if unhealthy_devices:
                logger.warning(f"发现不健康设备: {unhealthy_devices}")

        # 检查错误率
        if self.metrics.completed_sessions > 0:
            error_rate = self.metrics.error_count / self.metrics.completed_sessions
            if error_rate > self.max_error_rate:
                logger.warning(f"错误率过高: {error_rate:.2%}")
                await self._trigger_event("performance_alert", "high_error_rate", error_rate)

    async def _metrics_collector(self):
        """指标收集器"""
        while self.running:
            try:
                await self._collect_metrics()
                await asyncio.sleep(self.metrics_collection_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"指标收集异常: {e}")
                await asyncio.sleep(5)

    async def _collect_metrics(self):
        """收集性能指标"""
        # 系统资源指标
        self.metrics.cpu_usage = psutil.cpu_percent()
        self.metrics.memory_usage = psutil.virtual_memory().percent

        # 业务指标
        self.metrics.active_sessions = len(self.active_sessions)
        self.metrics.uptime = datetime.now() - self.start_time

        # 计算吞吐量
        current_time = time.time()
        if hasattr(self, "_last_metrics_time"):
            time_diff = current_time - self._last_metrics_time
            completed_diff = self.metrics.completed_sessions - getattr(
                self, "_last_completed_count", 0
            )
            self.metrics.throughput = completed_diff / time_diff if time_diff > 0 else 0

        self._last_metrics_time = current_time
        self._last_completed_count = self.metrics.completed_sessions

        # 保存历史指标
        self.performance_history.append(self.metrics)
        if len(self.performance_history) > 1000:  # 保留最近1000个数据点
            self.performance_history.pop(0)

    def _update_response_time(self, processing_time: float):
        """更新平均响应时间"""
        if self.metrics.average_response_time == 0:
            self.metrics.average_response_time = processing_time
        else:
            # 指数移动平均
            alpha = 0.1
            self.metrics.average_response_time = (
                alpha * processing_time + (1 - alpha) * self.metrics.average_response_time
            )

    async def _trigger_event(self, event_type: str, *args):
        """触发事件回调"""
        try:
            callbacks = self.event_callbacks.get(event_type, [])
            for callback in callbacks:
                if asyncio.iscoroutinefunction(callback):
                    await callback(*args)
                else:
                    callback(*args)
        except Exception as e:
            logger.error(f"事件回调异常: {event_type}, {e}")

    def register_event_callback(self, event_type: str, callback: Callable):
        """注册事件回调"""
        if event_type in self.event_callbacks:
            self.event_callbacks[event_type].append(callback)

    async def _complete_active_tasks(self):
        """完成所有活跃任务"""
        timeout = 30  # 30秒超时
        start_time = time.time()

        while self.active_tasks and (time.time() - start_time) < timeout:
            await asyncio.sleep(0.1)

        # 强制清理剩余任务
        for task_id in list(self.active_tasks.keys()):
            logger.warning(f"强制清理任务: {task_id}")
            del self.active_tasks[task_id]

    async def _handle_task_failure(self, task: AnalysisTask, error: Exception):
        """处理任务失败"""
        logger.error(f"任务失败: {task.task_id}, {error}")

        # 更新错误计数
        self.metrics.error_count += 1

        # 从活跃任务中移除
        if task.task_id in self.active_tasks:
            del self.active_tasks[task.task_id]

        # 重试逻辑
        if task.retry_count < task.max_retries:
            task.retry_count += 1
            logger.info(f"重试任务: {task.task_id}, 第{task.retry_count}次")

            # 重新提交任务
            priority = -task.priority.value
            await self.task_queue.put((priority, task.created_at, task))
        else:
            # 创建失败结果
            result = AnalysisResult(
                task_id=task.task_id,
                session_id=task.session_id,
                result_type=task.task_type,
                data={"error": str(error), "status": "failed"},
                confidence=0.0,
                processing_time=0.0,
                timestamp=datetime.now(),
            )

            self.completed_tasks[task.task_id] = result

            # 触发错误事件
            await self._trigger_event("error_occurred", task, error)

    async def _process_abdominal_task(self, task: AnalysisTask) -> dict[str, Any]:
        """处理腹诊分析任务"""
        abdominal_data = task.data["abdominal_data"]

        # 使用腹诊分析器
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor, self.abdominal_analyzer.analyze_abdominal_palpation, abdominal_data
        )

        return {
            "abdominal_analysis": result,
            "confidence": 0.8,
            "timestamp": datetime.now().isoformat(),
        }

    async def _process_skin_task(self, task: AnalysisTask) -> dict[str, Any]:
        """处理皮肤触诊分析任务"""
        skin_data = task.data["skin_data"]

        # 使用皮肤分析器
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor, self.skin_analyzer.analyze_skin_palpation, skin_data
        )

        return {"skin_analysis": result, "confidence": 0.8, "timestamp": datetime.now().isoformat()}

    async def _performance_optimizer(self):
        """性能优化器"""
        while self.running:
            try:
                await self._optimize_performance()
                await asyncio.sleep(60)  # 每分钟优化一次
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"性能优化异常: {e}")
                await asyncio.sleep(10)

    async def _optimize_performance(self):
        """执行性能优化"""
        # 检查系统负载
        if self.metrics.cpu_usage > self.cpu_threshold:
            # 减少并发任务数
            self.max_concurrent_tasks = max(1, self.max_concurrent_tasks - 1)
            logger.info(f"降低并发任务数至: {self.max_concurrent_tasks}")
        elif self.metrics.cpu_usage < self.cpu_threshold * 0.5:
            # 增加并发任务数
            max_allowed = self.config.get("max_concurrent_tasks", 10)
            self.max_concurrent_tasks = min(max_allowed, self.max_concurrent_tasks + 1)
            logger.info(f"提升并发任务数至: {self.max_concurrent_tasks}")

        # 清理过期的完成任务
        current_time = datetime.now()
        expired_tasks = []

        for task_id, result in self.completed_tasks.items():
            if (current_time - result.timestamp).total_seconds() > 3600:  # 1小时过期
                expired_tasks.append(task_id)

        for task_id in expired_tasks:
            del self.completed_tasks[task_id]

        if expired_tasks:
            logger.debug(f"清理过期任务: {len(expired_tasks)}个")

    async def _cleanup_manager(self):
        """清理管理器"""
        while self.running:
            try:
                await self._cleanup_resources()
                await asyncio.sleep(300)  # 每5分钟清理一次
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"资源清理异常: {e}")
                await asyncio.sleep(30)

    async def _cleanup_resources(self):
        """清理资源"""
        # 清理过期会话
        current_time = datetime.now()
        expired_sessions = []

        for session_id, session_data in self.active_sessions.items():
            session_start = session_data.get("start_time", current_time)
            if (current_time - session_start).total_seconds() > 7200:  # 2小时过期
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            await self._cleanup_session(session_id)

        # 清理性能历史数据
        if len(self.performance_history) > 1000:
            self.performance_history = self.performance_history[-500:]  # 保留最近500个

    async def _cleanup_session(self, session_id: str):
        """清理会话"""
        try:
            if session_id in self.active_sessions:
                session_data = self.active_sessions[session_id]
                device_id = session_data.get("device_id")

                # 停止设备会话
                if device_id and self.device_manager:
                    await self.device_manager.stop_session(session_id, device_id)

                # 移除会话数据
                del self.active_sessions[session_id]

                # 移除会话锁
                if session_id in self.session_locks:
                    del self.session_locks[session_id]

                # 更新指标
                self.metrics.active_sessions = len(self.active_sessions)

                logger.info(f"清理过期会话: {session_id}")

        except Exception as e:
            logger.error(f"会话清理失败: {session_id}, {e}")

    async def stop_palpation_session(self, session_id: str) -> dict[str, Any]:
        """
        停止触诊会话

        Args:
            session_id: 会话ID

        Returns:
            停止结果
        """
        try:
            if session_id not in self.active_sessions:
                return {"status": "error", "message": f"会话不存在: {session_id}"}

            await self._cleanup_session(session_id)

            # 触发事件
            await self._trigger_event("session_completed", session_id)

            return {"status": "success", "session_id": session_id, "message": "会话已停止"}

        except Exception as e:
            logger.error(f"停止会话失败: {session_id}, {e}")
            return {"status": "error", "session_id": session_id, "message": str(e)}

    async def get_session_status(self, session_id: str) -> dict[str, Any]:
        """获取会话状态"""
        if session_id not in self.active_sessions:
            return {"status": "not_found", "message": f"会话不存在: {session_id}"}

        session_data = self.active_sessions[session_id]
        current_time = datetime.now()
        duration = (current_time - session_data["start_time"]).total_seconds()

        return {
            "status": "active",
            "session_id": session_id,
            "device_id": session_data.get("device_id"),
            "duration": duration,
            "pulse_data_count": len(session_data.get("pulse_data", [])),
            "start_time": session_data["start_time"].isoformat(),
        }

    async def get_system_status(self) -> dict[str, Any]:
        """获取系统状态"""
        return {
            "status": self.status.name,
            "uptime": self.metrics.uptime.total_seconds(),
            "active_sessions": self.metrics.active_sessions,
            "completed_sessions": self.metrics.completed_sessions,
            "error_count": self.metrics.error_count,
            "cpu_usage": self.metrics.cpu_usage,
            "memory_usage": self.metrics.memory_usage,
            "average_response_time": self.metrics.average_response_time,
            "throughput": self.metrics.throughput,
            "active_tasks": len(self.active_tasks),
            "max_concurrent_tasks": self.max_concurrent_tasks,
        }
